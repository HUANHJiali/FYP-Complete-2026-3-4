"""
管理员学科管理相关视图

从 admin 视图中拆分学科管理逻辑，降低单文件复杂度。
"""

from django.core.paginator import Paginator

from app import models
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil


class AdminSubjectView:
    """管理员学科管理接口集合"""

    @staticmethod
    def get_subjects(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')

            subjects_query = models.Projects.objects.all().order_by('-id')

            if search:
                subjects_query = subjects_query.filter(name__icontains=search)

            total = subjects_query.count()
            paginator = Paginator(subjects_query, size)
            subjects_page = paginator.get_page(page)

            subjects_data = []
            for subject in subjects_page:
                subjects_data.append({
                    'id': subject.id,
                    'name': subject.name,
                    'description': '',
                    'createTime': subject.createTime or ''
                })

            return BaseView.successData({
                'list': subjects_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取学科列表失败: {str(e)}')

    @staticmethod
    def manage_subjects(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name')

                if models.Projects.objects.filter(name=name).exists():
                    return BaseView.error('学科名称已存在')

                models.Projects.objects.create(name=name, createTime=DateUtil.getNowDateTime())
                return BaseView.success('学科创建成功')

            if action == 'update':
                subject_id = request.POST.get('id')
                subject = models.Projects.objects.filter(id=subject_id).first()
                if not subject:
                    return BaseView.error('学科不存在')

                subject.name = request.POST.get('name', subject.name)
                subject.save()
                return BaseView.success('学科更新成功')

            if action == 'delete':
                subject_id = request.POST.get('id')
                subject = models.Projects.objects.filter(id=subject_id).first()
                if not subject:
                    return BaseView.error('学科不存在')

                if models.Exams.objects.filter(project=subject).exists():
                    return BaseView.error('该学科下存在试卷，无法删除')
                if models.Practises.objects.filter(project=subject).exists():
                    return BaseView.error('该学科下存在题目，无法删除')

                subject.delete()
                return BaseView.success('学科删除成功')

            return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'学科操作失败: {str(e)}')
