"""
Redis缓存管理器
提供高性能的缓存功能，减少数据库查询
"""
from django.core.cache import cache
from django.conf import settings
from typing import Any, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

# 缓存时间常量（秒）
TIMEOUT_SHORT = 300      # 5分钟
TIMEOUT_MEDIUM = 1800    # 30分钟
TIMEOUT_LONG = 3600      # 1小时
TIMEOUT_DAILY = 86400    # 24小时


class CacheManager:
    """缓存管理器"""

    # 缓存键前缀
    KEY_PREFIX = 'fyp:'

    @staticmethod
    def make_key(*parts) -> str:
        """生成缓存键"""
        return f"{CacheManager.KEY_PREFIX}{':'.join(str(p) for p in parts)}"

    @staticmethod
    def get(key: str, default=None) -> Any:
        """
        获取缓存

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            缓存值或默认值
        """
        full_key = CacheManager.make_key(key)
        value = cache.get(full_key, default)
        return value

    @staticmethod
    def set(key: str, value: Any, timeout: int = TIMEOUT_MEDIUM) -> bool:
        """
        设��缓存

        Args:
            key: 缓存键
            value: 缓存值
            timeout: 过期时间（秒）

        Returns:
            是否设置成功
        """
        try:
            full_key = CacheManager.make_key(key)
            cache.set(full_key, value, timeout)
            logger.debug(f"Cache set: {full_key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {key}, error: {str(e)}")
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        try:
            full_key = CacheManager.make_key(key)
            cache.delete(full_key)
            logger.debug(f"Cache deleted: {full_key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {key}, error: {str(e)}")
            return False

    @staticmethod
    def get_or_set(
        key: str,
        callback,
        timeout: int = TIMEOUT_MEDIUM,
        *args,
        **kwargs
    ) -> Any:
        """
        获取缓存，如果不存在则执行回调函数并缓存结果

        Args:
            key: 缓存键
            callback: 回调函数
            timeout: 过期时间
            *args: 回调函数位置参数
            **kwargs: 回调函数关键字参数

        Returns:
            缓存值或回调函数返回值
        """
        value = CacheManager.get(key)
        if value is not None:
            return value

        # 执行回调函数
        result = callback(*args, **kwargs)

        # 缓存结果
        if result is not None:
            CacheManager.set(key, result, timeout)

        return result

    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """
        清除匹配模式的所有缓存

        Args:
            pattern: 缓存键模式（支持通配符）

        Returns:
            清除的缓存数量
        """
        try:
            from django.core.cache import cache
            # 注意：Django的默认缓存后端不支持模式匹配
            # 如果使用Redis，可以直接使用Redis的KEYS命令
            if hasattr(cache, 'delete_pattern'):
                return cache.delete_pattern(f"{CacheManager.KEY_PREFIX}{pattern}")
            else:
                logger.warning("Cache backend does not support pattern matching")
                return 0
        except Exception as e:
            logger.error(f"Cache clear pattern failed: {pattern}, error: {str(e)}")
            return 0


class ModelCache:
    """模型缓存管理"""

    @staticmethod
    def get_object(model_class, object_id, timeout: int = TIMEOUT_MEDIUM):
        """
        获取单个模型对象的缓存

        Args:
            model_class: 模型类
            object_id: 对象ID
            timeout: 过期时间

        Returns:
            模型对象或None
        """
        key = f"model:{model_class.__name__}:{object_id}"
        return CacheManager.get_or_set(
            key,
            lambda: model_class.objects.filter(id=object_id).first(),
            timeout
        )

    @staticmethod
    def get_queryset(
        model_class,
        filters: dict = None,
        timeout: int = TIMEOUT_SHORT
    ) -> List:
        """
        获取查询集的缓存

        Args:
            model_class: 模型类
            filters: 过滤条件
            timeout: 过期时间

        Returns:
            模型对象列表
        """
        # 生成缓存键
        filter_str = json.dumps(filters or {}, sort_keys=True)
        key = f"queryset:{model_class.__name__}:{hash(filter_str)}"

        def query():
            queryset = model_class.objects.all()
            if filters:
                queryset = queryset.filter(**filters)
            return list(queryset)

        return CacheManager.get_or_set(key, query, timeout)

    @staticmethod
    def invalidate_object(model_class, object_id):
        """
        使对象缓存失效

        Args:
            model_class: 模型类
            object_id: 对象ID
        """
        key = f"model:{model_class.__name__}:{object_id}"
        CacheManager.delete(key)


class StatsCache:
    """统计数据缓存"""

    @staticmethod
    def get_dashboard_stats(timeout: int = TIMEOUT_MEDIUM):
        """
        获取仪表板统计数据

        Args:
            timeout: 过期时间

        Returns:
            统计数据字典
        """
        key = 'stats:dashboard'

        def calculate_stats():
            from app.models import (
                Users, Exams, Practises,
                Tasks, StudentPracticeLogs
            )
            from datetime import datetime, timedelta

            # 基础统计
            stats = {
                'total_users': Users.objects.count(),
                'total_students': Users.objects.filter(type=2).count(),
                'total_teachers': Users.objects.filter(type=1).count(),
                'total_exams': Exams.objects.count(),
                'total_questions': Practises.objects.count(),
                'total_tasks': Tasks.objects.count(),
            }

            # 本月新增
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            stats['monthly_exams'] = Exams.objects.filter(
                createTime__gte=month_start
            ).count()

            # 活跃用户（最近7天）
            week_ago = now - timedelta(days=7)
            active_students = StudentPracticeLogs.objects.filter(
                startTime__gte=week_ago
            ).values_list('student_id', flat=True).distinct()
            stats['active_users'] = len(active_students)

            return stats

        return CacheManager.get_or_set(key, calculate_stats, timeout)

    @staticmethod
    def get_question_stats(subject_id: int, timeout: int = TIMEOUT_LONG):
        """
        获取题目统计数据

        Args:
            subject_id: 科目ID
            timeout: 过期时间

        Returns:
            题目统计字典
        """
        key = f'stats:questions:{subject_id}'

        def calculate_stats():
            from app.models import Practises
            from django.db.models import Count

            questions = Practises.objects.filter(project_id=subject_id)
            return {
                'total': questions.count(),
                'by_type': dict(
                    questions.values('type').annotate(
                        count=Count('id')
                    ).values_list('type', 'count')
                )
            }

        return CacheManager.get_or_set(key, calculate_stats, timeout)


class ListCache:
    """列表数据缓存"""

    @staticmethod
    def get_all_grades(timeout: int = TIMEOUT_LONG):
        """获取所有班级（缓存）"""
        from app.models import Grades

        key = 'list:grades:all'

        def query():
            return list(Grades.objects.values())

        return CacheManager.get_or_set(key, query, timeout)

    @staticmethod
    def get_all_colleges(timeout: int = TIMEOUT_LONG):
        """获取所有学院（缓存）"""
        from app.models import Colleges

        key = 'list:colleges:all'

        def query():
            return list(Colleges.objects.values())

        return CacheManager.get_or_set(key, query, timeout)

    @staticmethod
    def get_all_subjects(timeout: int = TIMEOUT_LONG):
        """获取所有科目（缓存）"""
        from app.models import Projects

        key = 'list:subjects:all'

        def query():
            return list(Projects.objects.values())

        return CacheManager.get_or_set(key, query, timeout)


# 便捷装饰器
def cache_result(key_func=None, timeout=TIMEOUT_MEDIUM):
    """
    函数结果缓存装饰器

    Usage:
        @cache_result(key_func=lambda x: f"user:{x}", timeout=300)
        def get_user_info(user_id):
            return User.objects.get(id=user_id)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"function:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 尝试获取缓存
            result = CacheManager.get(key)
            if result is not None:
                return result

            # 执行函数
            result = func(*args, **kwargs)

            # 缓存结果
            if result is not None:
                CacheManager.set(key, result, timeout)

            return result
        return wrapper
    return decorator


# 使用示例
"""
# 基础缓存使用
from comm.cache_manager import CacheManager

# 设置缓存
CacheManager.set('user:123', user_data, timeout=300)

# 获取缓存
user = CacheManager.get('user:123')

# 获取或设置（推荐）
user = CacheManager.get_or_set(
    'user:123',
    lambda: User.objects.get(id=123),
    timeout=300
)


# 模型缓存
from comm.cache_manager import ModelCache

# 获取对象（带缓存）
user = ModelCache.get_object(User, 123)

# 使缓存失效
ModelCache.invalidate_object(User, 123)


# 统计数据缓存
from comm.cache_manager import StatsCache

# 获取仪表板统计（带缓存）
stats = StatsCache.get_dashboard_stats()


# 列表缓存
from comm.cache_manager import ListCache

# 获取所有班级（带缓存）
grades = ListCache.get_all_grades()


# 使用装饰器
@cache_result(key_func=lambda user_id: f"user_profile:{user_id}", timeout=600)
def get_user_profile(user_id):
    return UserProfile.objects.get(user_id=user_id)
"""
