"""
组织架构视图
处理学院、年级等组织架构管理
"""
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction

from app import models
from app.services.crud_service import CRUDService
from comm.BaseView import BaseView
from comm.CommUtils import SysUtil, DateUtil


class CollegesView(BaseView):
    """学院管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return self.get_all(request)
        elif module == 'page':
            return self.get_page_infos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'del':
            return self.del_info(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_all(request):
        """获取所有学院信息"""
        colleges = models.Colleges.objects.all()
        return BaseView.successData(list(colleges.values()))

    @staticmethod
    def get_page_infos(request):
        """分页获取学院信息（使用服务层）"""
        def serializer(item):
            return {
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            }

        return CRUDService.get_page_infos(
            model_class=models.Colleges,
            request=request,
            search_fields=['name'],
            serializer_func=serializer
        )

    @staticmethod
    def add_info(request):
        """添加学院信息（使用服务层）"""
        return CRUDService.add_info(
            model_class=models.Colleges,
            request=request,
            fields_mapping={'name': 'name'}
        )

    @staticmethod
    def upd_info(request):
        """修改学院信息（使用服务层）"""
        return CRUDService.upd_info(
            model_class=models.Colleges,
            request=request,
            fields_mapping={'name': 'name'}
        )

    @staticmethod
    def del_info(request):
        """删除学院信息（使用服务层）"""
        return CRUDService.del_info(
            model_class=models.Colleges,
            request=request,
            check_relations=[
                {
                    'model': models.Students,
                    'field': 'college__id',
                    'message': '存在关联记录无法移除'
                }
            ]
        )


class GradesView(BaseView):
    """年级管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return self.get_all(request)
        elif module == 'page':
            return self.get_page_infos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'del':
            return self.del_info(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_all(request):
        """获取所有年级信息"""
        grades = models.Grades.objects.all()
        return BaseView.successData(list(grades.values()))

    @staticmethod
    def get_page_infos(request):
        """分页获取年级信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        query = Q()

        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)

        data = models.Grades.objects.filter(query).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def add_info(request):
        """添加年级信息"""
        models.Grades.objects.create(
            name=request.POST.get('name'),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    @staticmethod
    def upd_info(request):
        """修改年级信息"""
        models.Grades.objects.filter(id=request.POST.get('id')).update(
            name=request.POST.get('name')
        )
        return BaseView.success()

    @staticmethod
    def del_info(request):
        """删除年级信息"""
        id = request.POST.get('id')
        
        # 检查所有关联表，防止孤立数据
        if models.Students.objects.filter(grade__id=id).exists():
            return BaseView.warn('存在关联学生无法移除')
        
        if models.Exams.objects.filter(grade__id=id).exists():
            return BaseView.warn('存在关联考试无法移除')
        
        if models.Tasks.objects.filter(grade__id=id).exists():
            return BaseView.warn('存在关联任务无法移除')
        
        models.Grades.objects.filter(id=id).delete()
        return BaseView.success()
