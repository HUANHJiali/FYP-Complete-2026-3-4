"""
分页服务层
提供统一的分页处理逻辑

该模块提供了标准化的分页处理功能，支持自定义序列化函数
和灵活的查询集处理。
"""
from typing import List, Dict, Any, Optional, Callable
from django.core.paginator import Paginator
from django.db.models import QuerySet
from comm.BaseView import BaseView


class PaginationService:
    """分页服务类"""
    
    @staticmethod
    def paginate_queryset(
        queryset: QuerySet,
        page_index: int = 1,
        page_size: int = 10,
        serializer_func: Optional[Callable[[Any], Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        分页查询集
        
        Args:
            queryset: Django查询集
            page_index: 页码（从1开始）
            page_size: 每页大小
            serializer_func: 可选的序列化函数，用于转换每个对象
            
        Returns:
            dict: 分页数据
        """
        try:
            page_index = int(page_index)
            page_size = int(page_size)
        except (ValueError, TypeError):
            page_index = 1
            page_size = 10
        
        paginator = Paginator(queryset, page_size)
        
        # 确保页码在有效范围内
        if page_index < 1:
            page_index = 1
        elif page_index > paginator.num_pages and paginator.num_pages > 0:
            page_index = paginator.num_pages
        
        page = paginator.page(page_index)
        
        # 序列化数据
        if serializer_func:
            resl = [serializer_func(item) for item in page]
        else:
            resl = list(page.values())
        
        # 使用BaseView的分页方法
        page_data = BaseView.parasePage(
            page_index,
            page_size,
            paginator.num_pages,
            paginator.count,
            resl
        )
        
        return page_data
    
    @staticmethod
    def create_serializer(fields: List[str]) -> Callable[[Any], Dict[str, Any]]:
        """
        创建简单的序列化函数
        
        Args:
            fields: 要序列化的字段列表
            
        Returns:
            Callable: 序列化函数，接受对象并返回字典
            
        Example:
            >>> serializer = PaginationService.create_serializer(['id', 'name', 'grade'])
            >>> result = serializer(student_obj)
            >>> # result: {'id': 1, 'name': 'John', 'gradeId': 2, 'gradeName': 'Grade 1'}
        """
        def serializer(obj: Any) -> Dict[str, Any]:
            result = {}
            for field in fields:
                value = getattr(obj, field, None)
                # 处理外键字段
                if hasattr(value, 'id'):
                    result[field + 'Id'] = value.id
                    if hasattr(value, 'name'):
                        result[field + 'Name'] = value.name
                else:
                    result[field] = value
            return result
        
        return serializer
