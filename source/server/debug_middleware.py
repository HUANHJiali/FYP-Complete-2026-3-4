"""
临时调试中间件 - 用于调试登录问题
"""
import os
from django.utils.deprecation import MiddlewareMixin

class DebugLoginMiddleware(MiddlewareMixin):
    """记录所有登录请求的详细信息"""

    def process_request(self, request):
        # 只记录登录请求
        if 'login' in request.path:
            log_file = 'D:/download/debug_requests.txt'
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Path: {request.path}\n")
                f.write(f"Method: {request.method}\n")
                f.write(f"POST data: {dict(request.POST)}\n")
                f.write(f"GET data: {dict(request.GET)}\n")
                f.write(f"META Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}\n")
                f.write(f"Body: {request.body}\n")

        return None
