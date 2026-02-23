"""
API限流中间件
使用django-ratelimit实现请求频率限制
"""
from django.core.cache import cache
from django.http import JsonResponse
from comm.BaseView import BaseView
import time


class RateLimitMiddleware:
    """
    简单的API限流中间件
    基于IP和端点的请求频率限制
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 限流配置：每分钟最多请求次数
        self.rate_limits = {
            '/api/login/': 10,  # 登录接口：每分钟10次
            '/api/sys/pwd': 5,  # 密码修改：每分钟5次
            '/api/admin/': 100,  # 管理员接口：每分钟100次
            'default': 60,  # 默认：每分钟60次
        }
    
    def __call__(self, request):
        # 获取客户端IP
        client_ip = self.get_client_ip(request)
        path = request.path
        
        # 获取该路径的限流配置
        limit = self.rate_limits.get(path) or self.rate_limits.get(
            path.split('/')[1] + '/', self.rate_limits['default']
        )
        
        # 检查是否超过限制
        cache_key = f'ratelimit:{client_ip}:{path}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            return JsonResponse({
                'code': 1,
                'msg': f'请求过于频繁，请稍后再试（限制：{limit}次/分钟）',
                'data': {}
            }, status=429)
        
        # 增加计数
        cache.set(cache_key, current_count + 1, 60)  # 60秒过期
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
