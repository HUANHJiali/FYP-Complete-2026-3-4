"""
CRUD服务层
提供通用的增删改查操作

该模块提供了通用的CRUD（创建、读取、更新、删除）操作服务，
用于减少代码重复并统一业务逻辑处理。
"""
from typing import Type, Dict, Any, Optional, List, Callable, Tuple
from django.db import models as django_models
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from comm.CommUtils import SysUtil, DateUtil
from comm.BaseView import BaseView
from utils.OperationLogger import OperationLogger
from app.permissions import get_user_from_request


class CRUDService:
    """通用CRUD服务类"""
    
    MODULE_MAPPING = {
        'Projects': 'project',
        'Colleges': 'college',
        'Grades': 'grade',
        'Teachers': 'teacher',
        'Students': 'student',
        'Exams': 'exam',
        'Practises': 'question',
        'PracticePapers': 'practice',
        'Tasks': 'task',
        'Messages': 'message',
    }
    
    @staticmethod
    def _log_operation(request: HttpRequest, operation_type: str, module_name: str, 
                       resource_id: Any = None, resource_name: str = None, 
                       operation_detail: Dict = None, status: int = 1):
        """记录操作日志"""
        try:
            user = get_user_from_request(request)
            if user:
                OperationLogger.log(
                    user_id=user.id,
                    user_name=user.name,
                    user_type=user.type,
                    operation_type=operation_type,
                    module_name=module_name,
                    resource_id=str(resource_id) if resource_id else None,
                    resource_name=resource_name or '',
                    operation_detail=operation_detail or {},
                    status=status,
                    request=request
                )
        except Exception:
            pass
    
    @staticmethod
    def _get_module_name(model_class: Type[django_models.Model]) -> str:
        """获取模块名称"""
        model_name = model_class.__name__
        return CRUDService.MODULE_MAPPING.get(model_name, model_name.lower())
    
    @staticmethod
    def get_page_infos(
        model_class: Type[django_models.Model],
        request: HttpRequest,
        search_fields: Optional[List[str]] = None,
        order_by: str = '-createTime',
        select_related: Optional[List[str]] = None,
        serializer_func: Optional[Callable[[Any], Dict[str, Any]]] = None
    ) -> HttpResponse:
        """
        分页获取信息（通用方法）
        
        Args:
            model_class: 模型类
            request: Django请求对象
            search_fields: 可搜索的字段列表
            order_by: 排序字段
            select_related: 需要预加载的外键字段
            serializer_func: 序列化函数
            
        Returns:
            BaseView响应
        """
        from app.services.pagination_service import PaginationService
        
        page_index = request.GET.get('pageIndex', 1)
        page_size = request.GET.get('pageSize', 10)
        
        # 构建查询
        query = Q()
        
        if search_fields:
            for field in search_fields:
                value = request.GET.get(field)
                if SysUtil.isExit(value):
                    query = query & Q(**{f'{field}__contains': value})
        
        # 执行查询
        queryset = model_class.objects.filter(query)
        
        # 预加载关联对象
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        # 排序
        if order_by:
            queryset = queryset.order_by(order_by)
        
        # 分页
        page_data = PaginationService.paginate_queryset(
            queryset,
            page_index,
            page_size,
            serializer_func
        )
        
        return BaseView.successData(page_data)
    
    @staticmethod
    def add_info(
        model_class: Type[django_models.Model],
        request: HttpRequest,
        fields_mapping: Optional[Dict[str, str]] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        validate_func: Optional[Callable[[HttpRequest], Tuple[bool, Optional[str]]]] = None
    ) -> HttpResponse:
        """
        添加信息（通用方法）
        
        Args:
            model_class: 模型类
            request: Django请求对象
            fields_mapping: 字段映射字典 {model_field: request_field}
            extra_data: 额外数据字典
            validate_func: 验证函数
            
        Returns:
            BaseView响应
        """
        # 执行验证
        if validate_func:
            is_valid, error_msg = validate_func(request)
            if not is_valid:
                return BaseView.warn(error_msg)
        
        # 准备数据
        data = {}
        
        if fields_mapping:
            for model_field, request_field in fields_mapping.items():
                value = request.POST.get(request_field)
                if value is not None:
                    data[model_field] = value
        
        # 添加额外数据
        if extra_data:
            data.update(extra_data)
        
        # 如果没有createTime字段，自动添加
        if 'createTime' not in data and hasattr(model_class, 'createTime'):
            data['createTime'] = DateUtil.getNowDateTime()
        
        # 创建对象
        try:
            obj = model_class.objects.create(**data)
            module_name = CRUDService._get_module_name(model_class)
            resource_name = data.get('name') or str(obj.id)
            CRUDService._log_operation(
                request, OperationLogger.OPERATION_CREATE, 
                module_name, obj.id, resource_name, 
                operation_detail={'fields': data}
            )
            return BaseView.success()
        except Exception as e:
            CRUDService._log_operation(
                request, OperationLogger.OPERATION_CREATE,
                CRUDService._get_module_name(model_class),
                None, None, {'error': str(e)}, status=0
            )
            return BaseView.error(f'创建失败: {str(e)}')
    
    @staticmethod
    def upd_info(
        model_class: Type[django_models.Model],
        request: HttpRequest,
        fields_mapping: Optional[Dict[str, str]] = None,
        filter_field: str = 'id'
    ) -> HttpResponse:
        """
        修改信息（通用方法）
        
        Args:
            model_class: 模型类
            request: Django请求对象
            fields_mapping: 字段映射字典 {model_field: request_field}
            filter_field: 过滤字段名
            
        Returns:
            BaseView响应
        """
        filter_value = request.POST.get(filter_field)
        if not filter_value:
            return BaseView.error(f'{filter_field}不能为空')
        
        # 准备更新数据
        update_data = {}
        
        if fields_mapping:
            for model_field, request_field in fields_mapping.items():
                value = request.POST.get(request_field)
                if value is not None:
                    update_data[model_field] = value
        
        # 执行更新
        try:
            obj = model_class.objects.filter(**{filter_field: filter_value}).first()
            old_data = None
            if obj:
                old_data = {f.name: getattr(obj, f.name) for f in obj._meta.fields if f.name != 'id'}
            
            model_class.objects.filter(**{filter_field: filter_value}).update(**update_data)
            
            module_name = CRUDService._get_module_name(model_class)
            resource_name = old_data.get('name') if old_data else filter_value
            CRUDService._log_operation(
                request, OperationLogger.OPERATION_UPDATE,
                module_name, filter_value, resource_name,
                operation_detail={'old': old_data, 'new': update_data}
            )
            return BaseView.success()
        except Exception as e:
            CRUDService._log_operation(
                request, OperationLogger.OPERATION_UPDATE,
                CRUDService._get_module_name(model_class),
                filter_value, None, {'error': str(e)}, status=0
            )
            return BaseView.error(f'更新失败: {str(e)}')
    
    @staticmethod
    def del_info(
        model_class: Type[django_models.Model],
        request: HttpRequest,
        filter_field: str = 'id',
        check_relations: Optional[List[Dict[str, Any]]] = None
    ) -> HttpResponse:
        """
        删除信息（通用方法）
        
        Args:
            model_class: 模型类
            request: Django请求对象
            filter_field: 过滤字段名
            check_relations: 检查关联关系的列表 [{'model': Model, 'field': 'field_name', 'message': 'error_msg'}]
            
        Returns:
            BaseView响应
        """
        filter_value = request.POST.get(filter_field)
        if not filter_value:
            return BaseView.error(f'{filter_field}不能为空')
        
        # 检查关联关系
        if check_relations:
            for relation in check_relations:
                related_model = relation['model']
                related_field = relation['field']
                error_msg = relation.get('message', '存在关联记录无法移除')
                
                if related_model.objects.filter(**{related_field: filter_value}).exists():
                    return BaseView.warn(error_msg)
        
        # 执行删除
        try:
            obj = model_class.objects.filter(**{filter_field: filter_value}).first()
            resource_name = None
            if obj and hasattr(obj, 'name'):
                resource_name = obj.name
            
            model_class.objects.filter(**{filter_field: filter_value}).delete()
            
            module_name = CRUDService._get_module_name(model_class)
            CRUDService._log_operation(
                request, OperationLogger.OPERATION_DELETE,
                module_name, filter_value, resource_name or str(filter_value)
            )
            return BaseView.success()
        except Exception as e:
            CRUDService._log_operation(
                request, OperationLogger.OPERATION_DELETE,
                CRUDService._get_module_name(model_class),
                filter_value, None, {'error': str(e)}, status=0
            )
            return BaseView.error(f'删除失败: {str(e)}')
