"""
API限流中间件
使用django-ratelimit实现请求频率限制
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings


class RateLimitMiddleware:
    """
    简单的API限流中间件
    基于IP和端点的请求频率限制
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.trust_proxy_headers = getattr(settings, 'TRUST_PROXY_HEADERS', False)
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
        limit = self.get_rate_limit(path)
        
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

    def get_rate_limit(self, path):
        """根据请求路径解析限流阈值（精确匹配优先，其次前缀匹配，最后默认）。"""
        if path in self.rate_limits:
            return self.rate_limits[path]

        prefix_limits = [
            (prefix, limit)
            for prefix, limit in self.rate_limits.items()
            if prefix != 'default' and path.startswith(prefix)
        ]
        if prefix_limits:
            # 使用最长前缀，保证更具体的规则优先
            return max(prefix_limits, key=lambda item: len(item[0]))[1]

        return self.rate_limits['default']
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        if self.trust_proxy_headers:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                parts = [item.strip() for item in x_forwarded_for.split(',') if item.strip()]
                if parts:
                    return parts[0]

            x_real_ip = request.META.get('HTTP_X_REAL_IP')
            if x_real_ip and x_real_ip.strip():
                return x_real_ip.strip()

        remote_addr = request.META.get('REMOTE_ADDR')
        if remote_addr and str(remote_addr).strip():
            return str(remote_addr).strip()

        return 'unknown'
