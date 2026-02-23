"""
任务中心视图
处理学习任务的发布、领取、提交、审核等功能
"""
from django.core.paginator import Paginator
from django.db.models import Q
import json

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil
from django.core.cache import cache
from utils.OperationLogger import OperationLogger


def _log_task_operation(request, operation_type, resource_id, resource_name, status=1):
    """记录任务操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name='task',
                resource_id=str(resource_id),
                resource_name=resource_name,
                status=status,
                request=request
            )
    except Exception:
        pass


class TasksView(BaseView):
    """任务管理视图"""

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
        if module == 'info':
            return self.get_info(request)
        elif module in ['getPageInfos', 'page']:
            return self.get_page_infos(request)
        elif module == 'student':
            return self.get_student_tasks(request)
        elif module in ['getTaskQuestions', 'questions']:
            return self.get_task_questions(request)
        elif module in ['getTaskLogs', 'logs']:
            return self.get_task_logs(request)
        elif module == 'loginfo':
            return self.get_task_log_info(request)
        elif module == 'answers':
            return self.get_task_answers(request)
        elif module == 'pending':
            return self.get_pending_answers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        # ✅ 安全检查：添加/修改/删除/审核���务需要教师权限
        # 但学生可以 start/save/submit 任务
        teacher_only_modules = ['addInfo', 'add', 'updInfo', 'upd', 'delInfo', 'del', 'review']

        if module in teacher_only_modules:
            allowed, error_response = self._check_teacher_permission(request)
            if not allowed:
                return error_response

        if module in ['addInfo', 'add']:
            return self.add_info(request)
        elif module in ['updInfo', 'upd']:
            return self.upd_info(request)
        elif module in ['delInfo', 'del']:
            return self.del_info(request)
        elif module in ['startTask', 'start']:
            return self.start_task(request)
        elif module in ['saveTaskProgress', 'save']:
            return self.save_task_progress(request)
        elif module in ['submitTask', 'submit']:
            return self.submit_task(request)
        elif module == 'review':
            return self.review_answer(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取任务信息"""
        taskId = request.GET.get('id')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        task = models.Tasks.objects.filter(id=taskId).first()
        if not task:
            return BaseView.error('任务不存在')

        resl = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'type': task.type,
            'deadline': task.deadline,
            'score': task.score,
            'projectId': task.project.id,
            'projectName': task.project.name,
            'gradeId': task.grade.id,
            'gradeName': task.grade.name,
            'teacherId': task.teacher.id,
            'teacherName': task.teacher.name,
            'createTime': task.createTime,
            'isActive': task.isActive
        }

        return BaseView.successData(resl)

    @staticmethod
    def get_page_infos(request):
        """分页获取任务列表"""
        pageIndex = int(request.GET.get('pageIndex', 1))
        pageSize = int(request.GET.get('pageSize', 10))
        title = request.GET.get('title', '')
        type = request.GET.get('type', '')
        projectId = request.GET.get('projectId', '')
        gradeId = request.GET.get('gradeId', '')

        query = models.Tasks.objects.all()

        if title:
            query = query.filter(title__icontains=title)
        if type:
            query = query.filter(type=type)
        if projectId:
            query = query.filter(project__id=projectId)
        if gradeId:
            query = query.filter(grade__id=gradeId)

        query = query.order_by('-createTime')

        paginator = Paginator(query, pageSize)
        page = paginator.get_page(pageIndex)

        resl = []
        for task in page:
            resl.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'type': task.type,
                'deadline': task.deadline,
                'score': task.score,
                'projectName': task.project.name,
                'gradeName': task.grade.name,
                'teacherName': task.teacher.name,
                'createTime': task.createTime,
                'isActive': task.isActive
            })

        return BaseView.successData({
            'list': resl,
            'total': paginator.count,
            'pageIndex': pageIndex,
            'pageSize': pageSize,
            'totalPages': paginator.num_pages
        })

    @staticmethod
    def get_student_tasks(request):
        """获取学生可做的任务"""
        studentId = cache.get(request.GET.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        # 获取学生信息
        student = models.Students.objects.filter(user__id=studentId).first()
        if not student:
            return BaseView.error('学生信息不存在')

        # 使用select_related优化外键查询
        tasks = models.Tasks.objects.filter(
            grade=student.grade,
            isActive=True
        ).select_related('project', 'teacher').order_by('-createTime')

        # 批量获取任务日志
        task_ids = [task.id for task in tasks]
        existing_logs = {}
        if task_ids:
            logs = models.StudentTaskLogs.objects.filter(
                student__id=studentId,
                task_id__in=task_ids
            ).select_related('task')
            for log in logs:
                existing_logs[log.task_id] = log

        resl = []
        for task in tasks:
            existingLog = existing_logs.get(task.id)

            taskData = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'type': task.type,
                'deadline': task.deadline,
                'score': task.score,
                'projectName': task.project.name,
                'teacherName': task.teacher.name,
                'createTime': task.createTime,
                'status': 'not_started' if not existingLog else existingLog.status,
                'logId': existingLog.id if existingLog else None,
                'startTime': existingLog.startTime if existingLog else None,
                'endTime': existingLog.endTime if existingLog else None,
                'score': existingLog.score if existingLog else None,
                'accuracy': existingLog.accuracy if existingLog else None
            }

            resl.append(taskData)

        return BaseView.successData(resl)

    @staticmethod
    def get_task_questions(request):
        """获取任务题目"""
        taskId = request.GET.get('taskId')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        taskQuestions = models.TaskQuestions.objects.filter(
            task__id=taskId
        ).order_by('questionOrder')

        resl = []
        for tq in taskQuestions:
            practise = tq.practise
            questionData = {
                'id': practise.id,
                'name': practise.name,
                'type': practise.type,
                'score': tq.score,
                'questionOrder': tq.questionOrder
            }

            # 如果是选择题，获取选项
            if practise.type == 0:
                options = models.Options.objects.filter(practise=practise)
                questionData['options'] = [opt.name for opt in options]

            resl.append(questionData)

        return BaseView.successData(resl)

    @staticmethod
    def start_task(request):
        """开始任务"""
        studentId = cache.get(request.POST.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        taskId = request.POST.get('taskId')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        # 检查任务是否存在
        task = models.Tasks.objects.filter(id=taskId).first()
        if not task:
            return BaseView.error('任务不存在')

        # 检查学生是否已经做过这个任务
        existingLog = models.StudentTaskLogs.objects.filter(
            student__id=studentId,
            task=task
        ).first()

        if existingLog:
            if existingLog.status == 'completed':
                return BaseView.error('该任务已完成，不能重复开始')
            # 如果进行中，返回现有记录
            return BaseView.successData({
                'logId': existingLog.id,
                'message': '继续现有任务'
            })

        # 创建新的任务记录
        taskLog = models.StudentTaskLogs.objects.create(
            student_id=studentId,
            task=task,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        return BaseView.successData({
            'logId': taskLog.id,
            'message': '任务开始成功'
        })

    @staticmethod
    def save_task_progress(request):
        """保存任务进度"""
        logId = request.POST.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')

        # 获取任务记录
        taskLog = models.StudentTaskLogs.objects.filter(id=logId).first()
        if not taskLog:
            return BaseView.error('任务记录不存在')

        # 保存答案
        answers = request.POST.getlist('answers[]') or request.POST.getlist('answers')
        practiseIds = request.POST.getlist('practiseIds[]') or request.POST.getlist('practiseIds')

        if len(answers) != len(practiseIds):
            return BaseView.error('答案和题目数量不匹配')

        for i in range(len(answers)):
            practiseId = practiseIds[i]
            answer = answers[i]

            # 检查是否已有答案记录
            answerRecord = models.StudentTaskAnswers.objects.filter(
                taskLog=taskLog,
                practise_id=practiseId
            ).first()

            if answerRecord:
                # 更新现有答案
                answerRecord.studentAnswer = answer
                answerRecord.answerTime = DateUtil.getNowDateTime()
                answerRecord.save()
            else:
                # 创建新的答案记录
                models.StudentTaskAnswers.objects.create(
                    taskLog=taskLog,
                    practise_id=practiseId,
                    studentAnswer=answer,
                    answerTime=DateUtil.getNowDateTime()
                )

        return BaseView.successData('进度保存成功')

    @staticmethod
    def submit_task(request):
        """提交任务"""
        logId = request.POST.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')

        taskLog = models.StudentTaskLogs.objects.filter(id=logId).first()
        if not taskLog:
            return BaseView.error('任务记录不存在')

        if taskLog.status == 'completed':
            return BaseView.error('任务已完成，不能重复提交')

        # 自动评分并计算正确率
        answers = models.StudentTaskAnswers.objects.filter(taskLog=taskLog)
        correct_count = 0
        total_count = answers.count()

        for answer in answers:
            practise = answer.practise
            # 简单的自动评分：选择和判断题
            if practise.type in [0, 2]:
                if str(answer.studentAnswer).strip() == str(practise.answer).strip():
                    answer.isCorrect = True
                    correct_count += 1
                else:
                    answer.isCorrect = False
                answer.save()

        # 计算正确率
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0

        # 更新任务记录
        taskLog.status = 'completed'
        taskLog.endTime = DateUtil.getNowDateTime()
        taskLog.accuracy = accuracy
        # 简单的评分逻辑
        taskLog.score = taskLog.task.score * (accuracy / 100)
        taskLog.save()

        return BaseView.successData({
            'score': taskLog.score,
            'accuracy': accuracy
        })

    @staticmethod
    def add_info(request):
        """添加任务"""
        # 获取参数
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        task_type = request.POST.get('type', 'practice')
        deadline = request.POST.get('deadline')
        score = request.POST.get('score')
        project_id = request.POST.get('projectId')
        grade_id = request.POST.get('gradeId')
        teacher_id = request.POST.get('teacherId')
        question_ids = request.POST.get('questionIds', '[]')

        # 验证必填参数
        if not all([title, deadline, score, project_id, grade_id, teacher_id]):
            return BaseView.error('缺少必填参数：title, deadline, score, projectId, gradeId, teacherId')

        # 验证数字参数
        try:
            score = float(score)
            project_id = int(project_id)
            grade_id = int(grade_id)
        except (ValueError, TypeError):
            return BaseView.error('参数格式错误：score和ID必须为数字')

        # 验证关联对象是否存在
        try:
            project = models.Projects.objects.get(id=project_id)
        except models.Projects.DoesNotExist:
            return BaseView.warn('指定的科目不存在')

        try:
            grade = models.Grades.objects.get(id=grade_id)
        except models.Grades.DoesNotExist:
            return BaseView.warn('指定的班级不存在')

        try:
            teacher = models.Users.objects.get(id=teacher_id)
        except models.Users.DoesNotExist:
            return BaseView.warn('指定的教师不存在')

        # 创建任务
        task = models.Tasks.objects.create(
            title=title,
            description=description,
            type=task_type,
            deadline=deadline,
            score=score,
            project=project,
            grade=grade,
            teacher=teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )

        # 添加题目（如果提供）
        try:
            questions = json.loads(question_ids)
            for idx, q_id in enumerate(questions):
                try:
                    practise = models.Practises.objects.get(id=int(q_id))
                    models.TaskQuestions.objects.create(
                        task=task,
                        practise=practise,
                        questionOrder=idx + 1,
                        score=2.0  # 默认每题2分
                    )
                except models.Practises.DoesNotExist:
                    continue  # 跳过不存在的题目
        except (json.JSONDecodeError, ValueError):
            pass  # 如果questionIds格式错误，只创建任务不添加题目

        _log_task_operation(request, 'create', task.id, task.title)
        return BaseView.successData({
            'id': task.id,
            'title': task.title
        })

    @staticmethod
    def upd_info(request):
        """更新任务"""
        task_id = request.POST.get('id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        score = request.POST.get('score')
        is_active = request.POST.get('isActive')

        if not task_id:
            return BaseView.error('缺少任务ID')

        try:
            task = models.Tasks.objects.get(id=int(task_id))
        except models.Tasks.DoesNotExist:
            return BaseView.warn('任务不存在')
        
        old_title = task.title

        if title:
            task.title = title
        if description is not None:
            task.description = description
        if deadline:
            task.deadline = deadline
        if score:
            try:
                task.score = float(score)
            except ValueError:
                return BaseView.error('分值必须为数字')
        if is_active is not None:
            task.isActive = is_active.lower() == 'true'

        task.save()

        _log_task_operation(request, 'update', task.id, old_title)
        return BaseView.successData({
            'id': task.id,
            'title': task.title
        })

    @staticmethod
    def del_info(request):
        """删除任务"""
        ids = request.POST.get('ids')

        if not ids:
            return BaseView.error('缺少任务ID列表')

        try:
            id_list = json.loads(ids)
            if not isinstance(id_list, list):
                id_list = [int(ids)]
            else:
                id_list = [int(id) for id in id_list]
        except (json.JSONDecodeError, ValueError):
            return BaseView.error('ID格式错误')

        if models.StudentTaskLogs.objects.filter(
            task__id__in=id_list,
            status='in_progress'
        ).exists():
            return BaseView.warn('有学生正在进行任务，无法删除')

        tasks = list(models.Tasks.objects.filter(id__in=id_list).values_list('title', flat=True))
        deleted_count = models.Tasks.objects.filter(id__in=id_list).delete()[0]

        if deleted_count == 0:
            return BaseView.warn('任务不存在')

        _log_task_operation(request, 'delete', ','.join(map(str, id_list)), ', '.join(tasks))
        return BaseView.success(f'成功删除{deleted_count}个任务')

    @staticmethod
    def get_task_logs(request):
        """获取任务日志"""
        # 实现获取任务日志的逻辑
        return BaseView.successData([])

    @staticmethod
    def get_task_log_info(request):
        """获取任务日志详情"""
        # 实现获取任务日志详情的逻辑
        return BaseView.successData({})

    @staticmethod
    def get_task_answers(request):
        """获取任务答案"""
        # 实现获取任务答案的逻辑
        return BaseView.successData([])

    @staticmethod
    def get_pending_answers(request):
        """获取待审核答案"""
        # 实现获取待审核答案的逻辑
        return BaseView.successData([])

    @staticmethod
    def review_answer(request):
        """审核答案"""
        # 获取参数
        answer_id = request.POST.get('answerId')
        is_correct = request.POST.get('isCorrect')
        feedback = request.POST.get('feedback', '')
        score = request.POST.get('score')

        # 验证必填参数
        if not all([answer_id, is_correct is not None]):
            return BaseView.error('缺少必填参数：answerId, isCorrect')

        # 查找答题记录
        try:
            answer = models.StudentTaskAnswers.objects.get(id=int(answer_id))
        except models.StudentTaskAnswers.DoesNotExist:
            return BaseView.warn('答题记录不存在')

        # 更新审核结果
        answer.isCorrect = is_correct.lower() == 'true'
        if score:
            try:
                answer.score = float(score)
            except ValueError:
                return BaseView.error('分值必须为数字')

        # 如果有反馈，可以添加到AI反馈字段（或创建专门的审核反馈字段）
        if feedback:
            answer.aiFeedback = f"[教师审核] {feedback}"

        answer.save()

        # 重新计算任务总分
        task_log = answer.taskLog
        all_answers = models.StudentTaskAnswers.objects.filter(taskLog=task_log)
        total_score = sum([a.score for a in all_answers if a.score])
        task_log.score = total_score

        # 计算正确率
        correct_count = all_answers.filter(isCorrect=True).count()
        total_count = all_answers.count()
        if total_count > 0:
            task_log.accuracy = round(correct_count / total_count * 100, 2)

        # 如果所有答案都审核完成，更新状态为已完成
        if models.StudentTaskAnswers.objects.filter(
            taskLog=task_log,
            isCorrect__isnull=True
        ).count() == 0:
            task_log.status = 'completed'
            task_log.endTime = DateUtil.getNowDateTime()

        task_log.save()

        return BaseView.success('审核完成')
