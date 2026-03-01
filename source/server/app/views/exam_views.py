"""
考试系统视图
处理考试、考试记录、答题记录等考试相关功能

⚠️ 安全：添加/修改/删除考试仅教师（type=1）和管理员（type=0）可操作
"""
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from datetime import datetime
import os

from app import models
from app.permissions import get_user_from_request
from comm import ExamUtils
from comm.BaseView import BaseView
from comm.CommUtils import SysUtil, DateUtil
from comm.lifecycle_status import resolve_exam_lifecycle, status_text, exam_status_code
from comm.cache_decorator import cache_api_response
from django.core.cache import cache
from utils.OperationLogger import OperationLogger


def _log_exam_operation(request, operation_type, resource_id, resource_name, status=1):
    """记录考试操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name='exam',
                resource_id=str(resource_id),
                resource_name=resource_name,
                status=status,
                request=request
            )
    except Exception:
        pass


class ExamsView(BaseView):
    """考试管理视图"""

    @staticmethod
    def _normalize_datetime_text(value):
        """将前端传入的时间值规范化为 YYYY-MM-DD HH:MM:SS（长度19）。"""
        if value in [None, '']:
            return None

        # datetime对象直接格式化
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')

        text = str(value).strip()
        if not text:
            return None

        # 兼容 ISO 字符串与毫秒/时区后缀
        text = text.replace('T', ' ')
        if '.' in text:
            text = text.split('.', 1)[0]
        if '+' in text:
            text = text.split('+', 1)[0]
        if text.endswith('Z'):
            text = text[:-1]

        # 再次尝试解析为datetime后格式化
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
            try:
                dt = datetime.strptime(text, fmt)
                if fmt == '%Y-%m-%d':
                    dt = dt.replace(hour=0, minute=0, second=0)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                continue

        # 最后兜底，避免写入超长导致 1406
        return text[:19] if text else None

    def _check_teacher_permission(self, request):
        """检查教师权限（教师和管理员可访问）"""
        user = get_user_from_request(request)
        if not user:
            return False, BaseView.error('用户未登录')
        if user.type not in [0, 1]:  # 0-管理员, 1-教师
            return False, BaseView.error(f'权限不足：需要教师权限，当前角色：{self._get_role_name(user.type)}')
        return True, None

    @staticmethod
    def _get_role_name(user_type):
        """获取角色名称"""
        role_names = {0: '管理员', 1: '教师', 2: '学生'}
        return role_names.get(user_type, '未知')

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return self.get_page_infos(request)
        elif module == 'info':
            return self.get_info(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        # ✅ 权限控制：
        # - add / create_from_practice_paper：仅教师和管理员
        # - make：登录用户可调用（学生答题页需要按科目生成试卷）
        if module in ['add', 'create_from_practice_paper']:
            allowed, error_response = self._check_teacher_permission(request)
            if not allowed:
                return error_response
        elif module == 'make':
            user = get_user_from_request(request)
            if not user:
                return BaseView.error('用户未登录')

        if module == 'add':
            return self.add_info(request)
        elif module == 'make':
            return self.create_exam_paper(request)
        elif module == 'create_from_practice_paper':
            return self.create_from_practice_paper(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取考试信息"""
        exam = models.Exams.objects.filter(id=request.GET.get('id')).first()

        return BaseView.successData({
            'id': exam.id,
            'name': exam.name,
            'createTime': exam.createTime,
            'examTime': exam.examTime,
            'startTime': getattr(exam, 'startTime', None),
            'endTime': getattr(exam, 'endTime', None),
            'teacherId': exam.teacher.id,
            'teacherName': exam.teacher.name,
            'projectId': exam.project.id,
            'projectName': exam.project.name,
            'gradeId': exam.grade.id,
            'gradeName': exam.grade.name,
        })

    @staticmethod
    @cache_api_response(timeout=60, key_prefix='exams_page')
    def get_page_infos(request):
        """分页查询考试信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        gradeId = request.GET.get('gradeId')
        projectId = request.GET.get('projectId')
        teacherId = request.GET.get('teacherId')

        query = Q()
        if SysUtil.isExit(teacherId):
            query = query & Q(teacher__id=teacherId)
        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)
        if SysUtil.isExit(gradeId):
            query = query & Q(grade__id=gradeId)
        if SysUtil.isExit(projectId):
            query = query & Q(project__id=projectId)

        data = models.Exams.objects.filter(query).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            # 查询当前年级下每个学生的个人考试状态
            student_status = None
            try:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                student_id = cache.get(token) if token else None
                if student_id:
                    q = Q(student__id=student_id) & Q(exam__id=item.id)
                    log = models.ExamLogs.objects.filter(q).order_by('-id').first()
                    if log:
                        student_status = log.status
            except Exception:
                student_status = None

            lifecycle_status = resolve_exam_lifecycle(
                start_time=getattr(item, 'startTime', None),
                end_time=getattr(item, 'endTime', None),
                legacy_exam_time=item.examTime
            )
            if student_status == 2:
                lifecycle_status = 'completed'

            resl.append({
                'id': item.id,
                'name': item.name,
                'examTime': item.examTime,
                'startTime': getattr(item, 'startTime', None),
                'endTime': getattr(item, 'endTime', None),
                'createTime': item.createTime,
                'projectId': item.project.id,
                'projectName': item.project.name,
                'teacherId': item.teacher.id,
                'teacherName': item.teacher.name,
                'gradeId': item.grade.id,
                'gradeName': item.grade.name,
                'studentStatus': student_status,
                'status': exam_status_code(lifecycle_status),
                'lifecycleStatus': lifecycle_status,
                'lifecycleStatusText': status_text(lifecycle_status)
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def add_info(request):
        """添加考试信息"""
        project_id = request.POST.get('projectId') or request.POST.get('project') or request.POST.get('subjectId')
        grade_id = request.POST.get('gradeId') or request.POST.get('grade')
        teacher_id = request.POST.get('teacherId')
        exam_name = request.POST.get('name') or request.POST.get('title')

        if not exam_name:
            return BaseView.error('考试名称不能为空')
        if not project_id:
            return BaseView.error('考核科目不能为空')
        if not grade_id:
            return BaseView.error('考核班级不能为空')

        if not ExamUtils.CheckPractiseTotal.check(project_id):
            return BaseView.warn('相关题目数量不足，无法准备考试')

        project = models.Projects.objects.filter(id=project_id).first()
        grade = models.Grades.objects.filter(id=grade_id).first()
        if not project:
            return BaseView.warn('指定科目不存在')
        if not grade:
            return BaseView.warn('指定班级不存在')

        teacher = models.Users.objects.filter(id=teacher_id).first() if teacher_id else None
        if not teacher:
            token = request.POST.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            login_user_id = cache.get(token) if token else None
            teacher = models.Users.objects.filter(id=login_user_id).first() if login_user_id else None
        if not teacher:
            teacher = models.Users.objects.filter(type=1).first() or models.Users.objects.filter(type=0).first()
        if not teacher:
            return BaseView.warn('未找到可用教师账号')

        exam = models.Exams.objects.create(
            name=exam_name,
            examTime=ExamsView._normalize_datetime_text(request.POST.get('examTime')) or DateUtil.getNowDateTime(),
            startTime=ExamsView._normalize_datetime_text(request.POST.get('startTime')),
            endTime=ExamsView._normalize_datetime_text(request.POST.get('endTime')),
            project=project,
            teacher=teacher,
            grade=grade,
            createTime=DateUtil.getNowDateTime()
        )
        _log_exam_operation(request, 'create', exam.id, exam.name)
        return BaseView.success()

    @staticmethod
    def create_exam_paper(request):
        """生成考试试卷"""
        projectId = request.POST.get('projectId')
        paper = ExamUtils.MakeExam.make(projectId)

        return BaseView.successData(paper)

    @staticmethod
    def create_from_practice_paper(request):
        """从练习试卷一键创建考试"""
        try:
            paper_id = request.POST.get('paperId') or request.POST.get('practicePaperId') or request.POST.get('id')
            name = request.POST.get('name')
            teacher_id = request.POST.get('teacherId') or request.POST.get('teacher_id')
            grade_id = request.POST.get('gradeId') or request.POST.get('grade_id')
            exam_time = request.POST.get('examTime')

            if not all([paper_id, teacher_id, grade_id]):
                return BaseView.error('缺少必要参数：paperId/teacherId/gradeId')

            paper = models.PracticePapers.objects.filter(id=paper_id, isActive=True).first()
            if not paper:
                return BaseView.error('练习试卷不存在或未启用')

            # 检查教师存在
            if not models.Teachers.objects.filter(user__id=teacher_id).exists():
                return BaseView.warn('指定工号的教师不存在')
            teacher_user = models.Users.objects.filter(id=teacher_id).first()
            if not teacher_user:
                return BaseView.warn('教师用户不存在')

            # 检查年级存在
            grade_obj = models.Grades.objects.filter(id=grade_id).first()
            if not grade_obj:
                return BaseView.warn('指定的年级不存在')

            exam = models.Exams.objects.create(
                name=name or f"{paper.title}-考试",
                examTime=ExamsView._normalize_datetime_text(exam_time) or DateUtil.getNowDateTime(),
                startTime=ExamsView._normalize_datetime_text(request.POST.get('startTime')),
                endTime=ExamsView._normalize_datetime_text(request.POST.get('endTime')),
                project=paper.project,
                teacher=teacher_user,
                grade=grade_obj,
                createTime=DateUtil.getNowDateTime()
            )
            _log_exam_operation(request, 'create', exam.id, exam.name)

            return BaseView.successData({'examId': exam.id, 'name': exam.name})
        except Exception as e:
            return BaseView.error(f'创建考试失败: {str(e)}')


class ExamLogsView(BaseView):
    """考试记录视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'pagestu':
            return self.get_page_student_logs(request)
        elif module == 'pagetea':
            return self.get_page_teacher_logs(request)
        elif module == 'info':
            return self.get_info(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'put':
            return self.put_exam_log(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取指定考试记录"""
        # 使用select_related优化查询
        examLogs = models.ExamLogs.objects.filter(
            id=request.GET.get('id')
        ).select_related('exam', 'exam__project', 'exam__teacher', 'exam__grade').first()

        answers = []
        query = Q()
        query = query & Q(student__id=request.GET.get('studentId'))
        query = query & Q(exam__id=examLogs.exam.id)
        # 使用select_related和prefetch_related优化查询
        temps = models.AnswerLogs.objects.filter(query).select_related(
            'practise', 'practise__project'
        ).prefetch_related('practise__options').order_by('no')

        # 批量获取选项，避免循环中查询
        practise_ids = [item.practise.id for item in temps]
        options_dict = {}
        if practise_ids:
            all_options = models.Options.objects.filter(practise_id__in=practise_ids)
            for option in all_options:
                if option.practise_id not in options_dict:
                    options_dict[option.practise_id] = []
                options_dict[option.practise_id].append({
                    'id': option.id,
                    'name': option.name,
                    'practise_id': option.practise_id
                })

        for item in temps:
            answers.append({
                'id': item.id,
                'score': item.score,
                'status': item.status,
                'answer': item.answer,
                'no': item.no,
                'practiseId': item.practise.id,
                'practiseName': item.practise.name,
                'practiseAnswer': item.practise.answer,
                'practiseAnalyse': item.practise.analyse,
                'options': options_dict.get(item.practise.id, []),
            })

        return BaseView.successData({
            'id': examLogs.id,
            'status': examLogs.status,
            'score': examLogs.score,
            'createTime': examLogs.createTime,
            'examId': examLogs.exam.id,
            'examName': examLogs.exam.name,
            'projectId': examLogs.exam.project.id,
            'projectName': examLogs.exam.project.name,
            'teacherId': examLogs.exam.teacher.id,
            'teacherName': examLogs.exam.teacher.name,
            'gradeId': examLogs.exam.grade.id,
            'gradeName': examLogs.exam.grade.name,
            'answers': answers
        })

    @staticmethod
    def get_page_student_logs(request):
        """分页获取学生考试记录（管理员/教师可查看全部，学生只查看自身）"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        examName = request.GET.get('examName')
        studentId = request.GET.get('studentId')
        projectId = request.GET.get('projectId')

        query = Q()
        if SysUtil.isExit(studentId):
            query = query & Q(student__id=studentId)
        if SysUtil.isExit(examName):
            query = query & Q(exam__name__contains=examName)
        if SysUtil.isExit(projectId):
            query = query & Q(exam__project__id=projectId)

        # 使用select_related优化外键查询，避免N+1问题
        data = models.ExamLogs.objects.filter(query).select_related(
            'exam', 'exam__teacher', 'exam__project', 'student'
        ).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'status': item.status,
                'createTime': item.createTime,
                'score': item.score,
                'examId': item.exam.id,
                'examName': item.exam.name,
                'studentId': item.student.id,
                'studentName': item.student.name,
                'teacherId': item.exam.teacher.id,
                'teacherName': item.exam.teacher.name,
                'projectId': item.exam.project.id,
                'projectName': item.exam.project.name,
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def get_page_teacher_logs(request):
        """分页获取教师审核记录"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        examName = request.GET.get('examName')
        token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        gradeId = request.GET.get('gradeId')
        projectId = request.GET.get('projectId')

        query = Q(exam__teacher__id=cache.get(token))
        if SysUtil.isExit(examName):
            query = query & Q(exam__name__contains=examName)
        if SysUtil.isExit(gradeId):
            query = query & Q(exam__grade__id=gradeId)
        if SysUtil.isExit(projectId):
            query = query & Q(exam__project__id=projectId)

        # 使用select_related优化外键查询，避免N+1问题
        data = models.ExamLogs.objects.filter(query).select_related(
            'exam', 'exam__project', 'exam__grade', 'student'
        ).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'status': item.status,
                'createTime': item.createTime,
                'score': item.score,
                'examId': item.exam.id,
                'examName': item.exam.name,
                'studentId': item.student.id,
                'studentName': item.student.name,
                'projectId': item.exam.project.id,
                'projectName': item.exam.project.name,
                'gradeId': item.exam.grade.id,
                'gradeName': item.exam.grade.name,
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def add_info(request):
        """添加考试记录"""
        models.ExamLogs.objects.create(
            student=models.Users.objects.get(id=cache.get(request.POST.get('token'))),
            exam=models.Exams.objects.get(id=request.POST.get('examId')),
            status=0,
            score=0,
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    @staticmethod
    def upd_info(request):
        """修改考试记录"""
        models.ExamLogs.objects.filter(id=request.POST.get('id')).update(
            status=request.POST.get('status')
        )
        return BaseView.success()

    @staticmethod
    def put_exam_log(request):
        """公布学生考核成绩"""
        studentId = request.POST.get('studentId')
        examId = request.POST.get('examId')

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)

        total = 0.0
        # 使用select_related预加载practise外键，避免N+1查询
        answers = models.AnswerLogs.objects.filter(query).select_related('practise')
        for item in answers:

            if item.practise.type == 0:
                temp = 2 if item.practise.answer == item.answer else 0
                total = total + temp
                models.AnswerLogs.objects.filter(id=item.id).update(
                    status=1,
                    score=temp
                )
            elif item.practise.type == 1:
                total = total + item.score
            elif item.practise.type == 2:
                temp = 2 if item.practise.answer == item.answer else 0
                total = total + temp
                models.AnswerLogs.objects.filter(id=item.id).update(
                    status=1,
                    score=temp
                )
            elif item.practise.type == 3:
                total = total + item.score

        models.ExamLogs.objects.filter(query).update(
            status=2,
            score=total
        )
        return BaseView.success()


class AnswerLogsView(BaseView):
    """答题记录视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return self.get_info(request)
        elif module == 'answers':
            return self.get_answers(request)
        elif module == 'check':
            return self.check_answers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'audit':
            return self.aduit_answer(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取指定答题记录"""
        log_id = request.GET.get('id')

        if not log_id:
            return BaseView.error('缺少答题记录ID')

        # 获取答题记录
        try:
            log_id = int(log_id)
        except ValueError:
            return BaseView.error('ID格式错误')

        exam_log = models.ExamLogs.objects.filter(id=log_id).first()
        if not exam_log:
            return BaseView.warn('答题记录不存在')

        # 获取考试基本信息
        exam = exam_log.exam
        student = exam_log.student

        # 获取学生的所有答案
        answers = models.AnswerLogs.objects.filter(
            exam=exam,
            student=student
        ).select_related('practise')

        # 构建答案详情
        answer_details = []
        for answer in answers:
            practise = answer.practise
            answer_details.append({
                'questionId': practise.id,
                'questionName': practise.name,
                'questionType': practise.type,
                'questionScore': 2.0 if practise.type != 3 else 20.0,  # 默认分值
                'studentAnswer': answer.answer or '',
                'correctAnswer': practise.answer or '',
                'isCorrect': answer.score > 0,
                'score': answer.score,
                'aiFeedback': answer.aiFeedback,
                'aiAnalysis': answer.aiAnalysis,
                'aiConfidence': answer.aiConfidence
            })

        return BaseView.successData({
            'examId': exam.id,
            'examName': exam.name,
            'studentId': student.id,
            'studentName': student.name,
            'startTime': exam_log.startTime,
            'endTime': exam_log.endTime,
            'status': exam_log.status,
            'score': exam_log.score,
            'accuracy': exam_log.accuracy,
            'usedTime': exam_log.usedTime,
            'answers': answer_details
        })

    @staticmethod
    def get_answers(request):
        """获取指定的答案列表"""
        studentId = request.GET.get('studentId')
        type = request.GET.get('type')
        examId = request.GET.get('examId')

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)

        resl = []
        data = models.AnswerLogs.objects.filter(query).order_by('no')
        for item in data:
            resl.append({
                'id': item.id,
                'practiseId': item.practise.id,
                'practiseName': item.practise.name,
                'practiseAnswer': item.practise.answer,
                'answer': item.answer,
                'score': item.score,
                'status': item.status,
                'no': item.no,
                'type': item.practise.type
            })

        # 若请求了具体类型，过滤返回
        if type in ('1', '3'):
            t = int(type)
            resl = [x for x in resl if x['type'] == t]

        return BaseView.successData(resl)

    @staticmethod
    def check_answer_type(studentId, examId, type):
        """按照类型检查答题"""
        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)
        query = query & Q(status=0)
        query = query & Q(practise__type=type)

        return models.AnswerLogs.objects.filter(query).exists()

    @staticmethod
    def check_answers(request):
        """检查手动审核题目"""
        studentId = request.GET.get('studentId')
        examId = request.GET.get('examId')

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)
        query = query & Q(status=0)
        query = query & Q(practise__type=1)
        query = query | Q(practise__type=3)

        if AnswerLogsView.check_answer_type(studentId, examId, 1):
            return BaseView.successData({'flag': True, 'msg': '填空题还有未审核的内容'})
        elif AnswerLogsView.check_answer_type(studentId, examId, 3):
            return BaseView.successData({'flag': True, 'msg': '编程题还有未审核的内容'})
        else:
            return BaseView.successData({'flag': False, 'msg': '手动审核部分已完成'})

    @staticmethod
    @transaction.atomic
    def add_info(request):
        """添加答题记录"""
        # 兼容 JSON 与 form-data 两种提交方式
        import json as _json
        try:
            body = request.body.decode('utf-8') if request.body else ''
            data = _json.loads(body) if body else {}
        except Exception:
            data = {}

        answers = data.get('answers') if isinstance(data, dict) else None
        nos = data.get('nos') if isinstance(data, dict) else None
        practiseIds = data.get('practiseIds') if isinstance(data, dict) else None
        examId = data.get('examId') if isinstance(data, dict) else None
        token = data.get('token') if isinstance(data, dict) else None

        # 若 JSON 为空，回退到表单
        if not answers:
            answers = request.POST.getlist('answers')
        if not nos:
            nos = request.POST.getlist('nos')
        if not practiseIds:
            practiseIds = request.POST.getlist('practiseIds')
        if not examId:
            examId = request.POST.get('examId')
        if not token:
            token = request.POST.get('token')

        if answers is None or nos is None or practiseIds is None or not examId or not token:
            return BaseView.error('参数不完整，无法提交答卷')

        student_id = cache.get(token)
        if not student_id:
            return BaseView.error('登录状态失效，请重新登录后再试')

        try:
            student_obj = models.Users.objects.get(id=student_id)
            exam_obj = models.Exams.objects.get(id=examId)
        except Exception:
            return BaseView.error('考试或学生信息不存在，无法提交')

        # 统一将 nos/ids/answers 全部转为列表
        if isinstance(nos, str):
            nos = [x for x in nos.split(',') if x != '']
        if isinstance(practiseIds, str):
            practiseIds = [x for x in practiseIds.split(',') if x != '']
        if isinstance(answers, str):
            try:
                tmp = _json.loads(answers)
                if isinstance(tmp, list):
                    answers = tmp
            except Exception:
                answers = [answers]

        # 覆盖式提交：先清理该学生本场考试旧答案，避免重复累积导致后续提交越来越慢
        query = Q(exam__id=examId) & Q(student__id=student_id)
        models.AnswerLogs.objects.filter(query).delete()

        # 写入答案
        created_answers = []
        for no in nos:
            idx = int(no) - 1
            if idx < 0 or idx >= len(practiseIds) or idx >= len(answers):
                continue
            try:
                created_answers.append(models.AnswerLogs(
                    student=student_obj,
                    exam=exam_obj,
                    practise=models.Practises.objects.get(id=practiseIds[idx]),
                    status=0,
                    answer=answers[idx] if answers[idx] is not None else '',
                    no=no
                ))
            except Exception:
                continue

        if created_answers:
            models.AnswerLogs.objects.bulk_create(created_answers)

        # 评分策略：客观题即时评分；主观题默认待审核（避免AI同步评分阻塞导致超时）
        enable_sync_ai = str(os.environ.get('ENABLE_SYNC_AI_SCORING', 'false')).lower() in ['1', 'true', 'yes', 'on']
        ai_utils = None
        if enable_sync_ai:
            try:
                from comm.AIUtils import AIUtils as _AI
                ai_utils = _AI()
            except Exception:
                ai_utils = None

        answers_qs = models.AnswerLogs.objects.filter(query).select_related('practise')
        total = 0.0
        pending_manual = 0
        for item in answers_qs:
            practise = item.practise
            if practise.type in [0, 2]:
                # 选择/判断：对比正确答案
                score = 2 if str(practise.answer).strip().lower() == str(item.answer).strip().lower() else 0
                item.score = score
                item.status = 1
                item.save(update_fields=['score', 'status'])
                total += score
            elif practise.type in [1, 3]:
                # 填空/编程：默认待审核，避免同步AI评分导致请求超时
                if ai_utils:
                    try:
                        ai_res = ai_utils.ai_score_answer(
                            question_content=practise.name,
                            correct_answer=practise.answer or '',
                            student_answer=item.answer or '',
                            question_type=practise.type,
                            max_score=2.0 if practise.type == 1 else 20.0
                        )
                        score = float(ai_res.get('score', 0))
                        item.score = score
                        item.status = 1
                        item.save(update_fields=['score', 'status'])
                        total += score
                    except Exception:
                        item.score = 0.0
                        item.status = 0
                        item.save(update_fields=['score', 'status'])
                        pending_manual += 1
                else:
                    item.score = 0.0
                    item.status = 0
                    item.save(update_fields=['score', 'status'])
                    pending_manual += 1

        # 学生交卷后置为“待发布”(status=1)，由教师审核/发布后再置为2
        models.ExamLogs.objects.filter(query).update(status=1, score=total)
        return BaseView.successData({'score': total, 'pendingManual': pending_manual})

    @staticmethod
    def aduit_answer(request):
        """审核答题"""
        if int(request.POST.get('type')) == 1:

            models.AnswerLogs.objects.filter(id=request.POST.get('id')).update(
                status=1,
                score=2 if int(request.POST.get('flag')) == 0 else 0,
            )
        else:
            models.AnswerLogs.objects.filter(id=request.POST.get('id')).update(
                status=1,
                score=20 if int(request.POST.get('flag')) == 0 else 0,
            )

        return BaseView.success()
