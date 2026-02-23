"""
权限检查模块
提供角色基��的访问控制（RBAC）装饰器和辅助函数
"""
from functools import wraps
from typing import List, Optional, Callable
from django.core.cache import cache
from django.http import HttpRequest
from comm.BaseView import BaseView


def get_user_from_request(request: HttpRequest) -> Optional['models.Users']:
    """
    从请求中获取用户对象

    Args:
        request: Django HTTP 请求对象

    Returns:
        Users 对象或 None
    """
    from app import models

    # 从 GET 或 POST 或 Header 中获取 token
    token = (
        request.GET.get('token') or
        request.POST.get('token') or
        request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    )

    if not token:
        return None

    user_id = cache.get(token)
    if not user_id:
        return None

    return models.Users.objects.filter(id=user_id).first()


def require_role(allowed_roles: List[int]) -> Callable:
    """
    角色权限检查装饰器

    Args:
        allowed_roles: 允许的角色列表 [0-管理员, 1-教师, 2-学生]

    Example:
        @require_role([0])  # 仅管理员
        def admin_only_view(request):
            pass

        @require_role([0, 1])  # 管理员和教师
        def teacher_view(request):
            pass

    Returns:
        装饰器函数
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = get_user_from_request(request)

            if not user:
                return BaseView.error('用户未登录')

            if user.type not in allowed_roles:
                role_names = {0: '管理员', 1: '教师', 2: '学生'}
                user_role = role_names.get(user.type, '未知')
                return BaseView.error(f'权限不足：需要 {get_role_names(allowed_roles)} 权限，当前角色：{user_role}')

            # 将用户对象添加到 request 中，供后续使用
            request.user = user
            return view_func(request, *args, **kwargs)

        return wrapped
    return decorator


def require_admin(view_func: Callable) -> Callable:
    """管理员权限检查装饰器（快捷方式）"""
    return require_role([0])(view_func)


def require_teacher(view_func: Callable) -> Callable:
    """教师权限检查装饰器（快捷方式）"""
    return require_role([0, 1])(view_func)


def require_student(view_func: Callable) -> Callable:
    """学生权限检查装饰器（快捷方式）"""
    return require_role([0, 1, 2])(view_func)


def get_role_names(role_ids: List[int]) -> str:
    """
    获取角色名称列表（用于错误消息）

    Args:
        role_ids: 角色ID列表

    Returns:
        角色名称字符串，如 "管理员、教师"
    """
    role_names = {0: '管理员', 1: '教师', 2: '学生'}
    return '、'.join([role_names.get(rid, '未知') for rid in role_ids])


def check_resource_ownership(user, resource_obj, owner_field='user') -> bool:
    """
    检查用户是否拥有资源的所有权

    Args:
        user: 用户对象
        resource_obj: 资源对象（如 Exam, Task 等）
        owner_field: 所有者字段名，默认为 'user'

    Returns:
        True 如果用户拥有资源或是管理员

    Example:
        if not check_resource_ownership(user, exam, 'teacher'):
            return BaseView.error('无权访问此资源')
    """
    # 管理员可以访问所有资源
    if user.type == 0:
        return True

    # 检查资源所有权
    owner = getattr(resource_obj, owner_field, None)
    if owner == user:
        return True

    return False


def check_teacher_access(user, resource_obj) -> bool:
    """
    检查教师是否可以访问资源（自己的或所在班级的）

    Args:
        user: 用户对象（教师）
        resource_obj: 资源对象（如 Exam）

    Returns:
        True 如果教师可以访问
    """
    # 管理员可以访问
    if user.type == 0:
        return True

    # 教师只能访问自己创建的资源
    if hasattr(resource_obj, 'teacher'):
        return resource_obj.teacher == user

    return False
