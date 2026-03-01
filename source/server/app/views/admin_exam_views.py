"""
管理员试卷管理相关视图

从 admin 视图中拆分试卷管理逻辑，降低单文件复杂度。
"""

from django.core.cache import cache
from django.core.paginator import Paginator

from app import models
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil
from comm.lifecycle_status import resolve_exam_lifecycle, status_text


class AdminExamView:
    """管理员试卷管理接口集合"""

    @staticmethod
    def _normalize_datetime(value):
        if value in [None, '']:
            return None
        text = str(value).strip()
        if len(text) >= 19:
            return text[:19]
        return text

    @staticmethod
    def get_exams(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search') or request.GET.get('keyword', '')
            subject_id = request.GET.get('subjectId') or request.GET.get('project', '')

            exams_query = models.Exams.objects.select_related('project', 'grade', 'teacher').all().order_by('-id')

            if search:
                exams_query = exams_query.filter(name__icontains=search)
            if subject_id:
                exams_query = exams_query.filter(project_id=subject_id)

            total = exams_query.count()
            paginator = Paginator(exams_query, size)
            exams_page = paginator.get_page(page)

            exams_data = []
            for exam in exams_page:
                lifecycle_status = resolve_exam_lifecycle(
                    start_time=getattr(exam, 'startTime', None),
                    end_time=getattr(exam, 'endTime', None),
                    legacy_exam_time=exam.examTime
                )
                exams_data.append({
                    'id': exam.id,
                    'title': exam.name,
                    'name': exam.name,
                    'description': '',
                    'type': 'fixed',
                    'subjectId': exam.project.id if exam.project else None,
                    'project': exam.project.id if exam.project else None,
                    'projectId': exam.project.id if exam.project else None,
                    'subjectName': exam.project.name if exam.project else '',
                    'projectName': exam.project.name if exam.project else '',
                    'gradeId': exam.grade.id if exam.grade else None,
                    'gradeName': exam.grade.name if exam.grade else '',
                    'teacherId': exam.teacher.id if exam.teacher else None,
                    'teacherName': exam.teacher.name if exam.teacher else '',
                    'difficulty': 'medium',
                    'duration': 120,
                    'totalScore': 100,
                    'isActive': True,
                    'startTime': exam.examTime or '',
                    'endTime': '',
                    'examTime': exam.examTime or '',
                    'createTime': exam.createTime or '',
                    'lifecycleStatus': lifecycle_status,
                    'lifecycleStatusText': status_text(lifecycle_status)
                })

            return BaseView.successData({
                'list': exams_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取试卷列表失败: {str(e)}')

    @staticmethod
    def manage_exams(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name') or request.POST.get('title')
                project_id = request.POST.get('subjectId') or request.POST.get('project') or request.POST.get('projectId')
                grade_id = request.POST.get('gradeId') or request.POST.get('grade')
                teacher_id = request.POST.get('teacherId')
                exam_time = AdminExamView._normalize_datetime(
                    request.POST.get('examTime') or request.POST.get('startTime') or DateUtil.getNowDateTime()
                )

                if not name:
                    return BaseView.error('试卷名称不能为空')
                if not project_id:
                    return BaseView.error('学科不能为空')
                subject = models.Projects.objects.filter(id=project_id).first()
                grade = models.Grades.objects.filter(id=grade_id).first() if grade_id else None
                teacher = models.Users.objects.filter(id=teacher_id).first() if teacher_id else None

                if not subject:
                    return BaseView.error('学科不存在')
                if not grade:
                    grade = models.Grades.objects.order_by('id').first()
                if not grade:
                    return BaseView.error('系统内无可用年级，请先创建年级')

                if not teacher:
                    token = request.POST.get('token')
                    login_user_id = cache.get(token) if token else None
                    teacher = models.Users.objects.filter(id=login_user_id).first() if login_user_id else None
                if not teacher:
                    teacher = models.Users.objects.filter(type=1).first() or models.Users.objects.filter(type=0).first()
                if not teacher:
                    return BaseView.error('未找到可用教师账号')

                exam = models.Exams.objects.create(
                    name=name,
                    teacher=teacher,
                    project=subject,
                    grade=grade,
                    createTime=DateUtil.getNowDateTime(),
                    examTime=exam_time
                )
                return BaseView.successData({'id': exam.id, 'message': '试卷创建成功'})

            if action == 'update':
                exam_id = request.POST.get('id')
                exam = models.Exams.objects.filter(id=exam_id).first()
                if not exam:
                    return BaseView.error('试卷不存在')

                exam.name = request.POST.get('name') or request.POST.get('title') or exam.name
                project_id = request.POST.get('subjectId') or request.POST.get('project') or request.POST.get('projectId')
                grade_id = request.POST.get('gradeId') or request.POST.get('grade')
                teacher_id = request.POST.get('teacherId')
                exam_time = AdminExamView._normalize_datetime(request.POST.get('examTime') or request.POST.get('startTime'))

                if project_id:
                    subject = models.Projects.objects.filter(id=project_id).first()
                    if subject:
                        exam.project = subject
                if grade_id:
                    grade = models.Grades.objects.filter(id=grade_id).first()
                    if grade:
                        exam.grade = grade
                if teacher_id:
                    teacher = models.Users.objects.filter(id=teacher_id).first()
                    if teacher:
                        exam.teacher = teacher
                if exam_time:
                    exam.examTime = exam_time
                exam.save()
                return BaseView.success('试卷更新成功')

            if action == 'delete':
                exam_id = request.POST.get('id')
                exam = models.Exams.objects.filter(id=exam_id).first()
                if not exam:
                    return BaseView.error('试卷不存在')

                if models.ExamLogs.objects.filter(exam=exam).exists():
                    return BaseView.error('该试卷存在考试记录，无法删除')

                exam.delete()
                return BaseView.success('试卷删除成功')

            return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'试卷操作失败: {str(e)}')
