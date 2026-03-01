"""
管理员任务管理相关视图

从 admin_views.py 拆分任务管理逻辑，降低文件复杂度。
"""
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.cache import cache

from app import models
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil


class AdminTaskView:
    """管理员任务管理接口集合"""

    @staticmethod
    def _normalize_deadline(value):
        if value in [None, '']:
            return DateUtil.getNowDateTime()
        text = str(value).strip()
        if len(text) >= 19:
            return text[:19]
        return text

    @staticmethod
    def get_tasks(request):
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('pageSize', 10))
            keyword = request.GET.get('keyword', '')
            task_type = request.GET.get('type', '')
            project_id = request.GET.get('project', '')

            query = models.Tasks.objects.select_related('project', 'grade', 'teacher').all()

            if keyword:
                query = query.filter(
                    Q(title__icontains=keyword) | Q(description__icontains=keyword)
                )
            if task_type:
                query = query.filter(type=task_type)
            if project_id:
                query = query.filter(project_id=project_id)

            query = query.order_by('-id')
            total = query.count()
            paginator = Paginator(query, page_size)
            tasks = paginator.get_page(page)

            task_list = []
            for task in tasks:
                task_list.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or '',
                    'type': task.type,
                    'deadline': task.deadline,
                    'score': task.score,
                    'project': task.project.id if task.project else None,
                    'projectName': task.project.name if task.project else '',
                    'grade': task.grade.id if task.grade else None,
                    'gradeName': task.grade.name if task.grade else '',
                    'isActive': task.isActive,
                    'createTime': task.createTime,
                })

            return BaseView.successData({
                'list': task_list,
                'total': total,
                'page': page,
                'pageSize': page_size,
            })
        except Exception as e:
            return BaseView.error(f'获取任务列表失败: {str(e)}')

    @staticmethod
    def manage_tasks(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                title = request.POST.get('title', '').strip()
                if not title:
                    return BaseView.error('任务标题不能为空')

                project_id = request.POST.get('project') or request.POST.get('projectId')
                grade_id = request.POST.get('grade') or request.POST.get('gradeId')
                project = models.Projects.objects.filter(id=project_id).first() if project_id else None
                grade = models.Grades.objects.filter(id=grade_id).first() if grade_id else None

                if not project:
                    return BaseView.error('所选学科不存在')
                if not grade:
                    return BaseView.error('所选班级不存在')

                teacher_id = cache.get(request.POST.get('token')) if request.POST.get('token') else None
                teacher_user = models.Users.objects.filter(id=teacher_id).first() if teacher_id else None
                if not teacher_user:
                    teacher_user = models.Users.objects.filter(type=0).first()
                if not teacher_user:
                    return BaseView.error('未找到可用的任务创建者')

                task = models.Tasks.objects.create(
                    title=title,
                    description=request.POST.get('description', ''),
                    type=request.POST.get('type', 'practice'),
                    deadline=AdminTaskView._normalize_deadline(request.POST.get('deadline')),
                    score=int(request.POST.get('score', 100)),
                    project=project,
                    grade=grade,
                    teacher=teacher_user,
                    createTime=DateUtil.getNowDateTime(),
                    isActive=str(request.POST.get('isActive', 'true')).lower() == 'true',
                )
                return BaseView.successData({'id': task.id, 'message': '任务创建成功'})

            if action == 'update':
                task_id = request.POST.get('id')
                task = models.Tasks.objects.filter(id=task_id).first()
                if not task:
                    return BaseView.error('任务不存在')

                task.title = request.POST.get('title', task.title)
                task.description = request.POST.get('description', task.description)
                task.type = request.POST.get('type', task.type)
                task.deadline = AdminTaskView._normalize_deadline(request.POST.get('deadline', task.deadline))
                task.score = int(request.POST.get('score', task.score))

                project_id = request.POST.get('project') or request.POST.get('projectId')
                grade_id = request.POST.get('grade') or request.POST.get('gradeId')
                if project_id:
                    project = models.Projects.objects.filter(id=project_id).first()
                    if project:
                        task.project = project
                if grade_id:
                    grade = models.Grades.objects.filter(id=grade_id).first()
                    if grade:
                        task.grade = grade
                if request.POST.get('isActive') is not None:
                    task.isActive = str(request.POST.get('isActive')).lower() == 'true'
                task.save()
                return BaseView.success('任务更新成功')

            if action == 'delete':
                task_id = request.POST.get('id')
                task = models.Tasks.objects.filter(id=task_id).first()
                if not task:
                    return BaseView.error('任务不存在')

                if models.StudentTaskLogs.objects.filter(task=task).exists():
                    return BaseView.error('该任务存在执行记录，无法删除')

                task.delete()
                return BaseView.success('任务删除成功')

            return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'任务操作失败: {str(e)}')
