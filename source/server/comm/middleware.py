"""
JWT认证中间件

提供基于JWT的请求认证功���。
中间件会自动验证请求中的JWT token，并将用户信息添加到request对象中。

使用方法：
1. 在settings.py中添加此中间件
2. 在需要认证的视图函数中使用request.user_id

作者：Claude AI
创建时间：2026-02-20
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
import logging

from comm.auth_utils import JWTUtils

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    JWT认证中间件

    从请求中提取并验证JWT token，支持多种token传递方式：
    1. Authorization header: Bearer <token>
    2. Query parameter: ?token=<token>
    3. POST form data: token=<token>
    4. Custom header: X-Auth-Token
    """

    # 不需要认证的路径
    EXEMPT_PATHS = [
        '/api/login',
        '/api/health',
        '/api/metrics',
        '/admin/',
        '/swagger',
        '/redoc',
    ]

    def process_request(self, request):
        """
        处理请求，提取并验证token

        验证成功后，在request对象中添加：
        - user_id: 用户ID
        - user_type: 用户类型
        - token_payload: 完整的token payload
        """
        # 检查是否是豁免路径
        if self._is_exempt_path(request.path):
            return None

        # 提取token
        token = self._extract_token(request)
        if not token:
            # 对于需要认证的请求，不强制返回401，让视图自己决定
            # 这样可以支持可选认证的端点
            request.user_id = None
            request.user_type = None
            request.token_payload = None
            return None

        # 验证token
        payload = JWTUtils.verify_token(token)
        if not payload:
            # Token无效，但也不强制返回401
            request.user_id = None
            request.user_type = None
            request.token_payload = None
            return None

        # 检查token是否在黑名单中
        if JWTUtils.is_token_blacklisted(token):
            logger.warning(f"Token已撤销: path={request.path}")
            request.user_id = None
            request.user_type = None
            request.token_payload = None
            return None

        # 将用户信息添加到request对象
        request.user_id = payload.get('user_id')
        request.user_type = payload.get('user_type')
        request.token_payload = payload

        return None

    def _is_exempt_path(self, path):
        """检查路径是否豁免认证"""
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False

    def _extract_token(self, request):
        """
        从请求中提取token

        支持多种提取方式（按优先级）：
        1. Authorization header (Bearer token)
        2. X-Auth-Token header
        3. Query parameter
        4. POST form data
        """
        # 1. Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # 去掉 'Bearer ' 前缀

        # 2. X-Auth-Token header
        custom_token = request.META.get('HTTP_X_AUTH_TOKEN', '')
        if custom_token:
            return custom_token

        # 3. Query parameter
        query_token = request.GET.get('token')
        if query_token:
            return query_token

        # 4. POST form data
        if request.method == 'POST':
            form_token = request.POST.get('token')
            if form_token:
                return form_token

        return None


class RequireAuthenticationMixin:
    """
    需要认证的视图混入类

    使用此混入类的视图会自动要求用户认证。
    如果用户未认证，返回401错误。

    使用示例：
    class MyView(RequireAuthenticationMixin, BaseView):
        def get(self, request):
            # 此时request.user_id一定存在
            user_id = request.user_id
            ...
    """

    def dispatch(self, request, *args, **kwargs):
        """在处理请求前检查认证"""
        # 先调用中间件处理
        response = super().dispatch(request, *args, **kwargs)
        if response:
            return response

        # 检查是否已认证
        if not getattr(request, 'user_id', None):
            return JsonResponse({
                'success': False,
                'code': 401,
                'message': '未登录或登录已过期',
            }, status=401)

        return None


def login_required(view_func):
    """
    登录要求装饰器

    使用示例：
    @login_required
    def my_view(request):
        user_id = request.user_id
        ...
    """
    def wrapped_view(request, *args, **kwargs):
        if not getattr(request, 'user_id', None):
            return JsonResponse({
                'success': False,
                'code': 401,
                'message': '未登录或登录已过期',
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def require_roles(*allowed_roles):
    """
    角色权限装饰器

    使用示例：
    @require_roles(UserType.ADMIN, UserType.TEACHER)
    def admin_view(request):
        # 只有管理员和教师可以访问
        ...
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # 检查是否已登录
            if not getattr(request, 'user_id', None):
                return JsonResponse({
                    'success': False,
                    'code': 401,
                    'message': '未登录或登录已过期',
                }, status=401)

            # 检查角色权限
            user_type = getattr(request, 'user_type', None)
            if user_type not in allowed_roles:
                return JsonResponse({
                    'success': False,
                    'code': 403,
                    'message': '权限不足',
                }, status=403)

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
