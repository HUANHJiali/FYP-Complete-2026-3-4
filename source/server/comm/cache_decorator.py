"""
API响应缓存装饰器
用于缓存频繁查询的API响应，提升性能
"""
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
import hashlib
import json

def cache_api_response(timeout=300, key_prefix='api_cache'):
    """
    API响应缓存装饰器
    
    Args:
        timeout: 缓存过期时间（秒），默认5分钟
        key_prefix: 缓存键前缀
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 生成缓存键
            # 基于请求路径、方法和参数
            cache_key_parts = [
                key_prefix,
                request.path,
                request.method,
            ]
            
            # 添加GET参数
            if request.GET:
                cache_key_parts.append(json.dumps(dict(request.GET), sort_keys=True))
            
            # 添加POST参数（仅用于GET请求的缓存，POST请求不缓存）
            if request.method == 'GET' and request.POST:
                cache_key_parts.append(json.dumps(dict(request.POST), sort_keys=True))
            
            cache_key = hashlib.md5('|'.join(cache_key_parts).encode()).hexdigest()
            full_cache_key = f"{key_prefix}:{cache_key}"
            
            # 尝试从缓存获取
            cached_response = cache.get(full_cache_key)
            if cached_response is not None:
                return JsonResponse(cached_response)
            
            # 执行视图函数
            response = view_func(request, *args, **kwargs)
            
            # 只缓存成功的GET请求
            if request.method == 'GET' and hasattr(response, 'content'):
                try:
                    import json as json_module
                    response_data = json_module.loads(response.content.decode('utf-8'))
                    # 只缓存成功的响应
                    if response_data.get('code') == 0:
                        cache.set(full_cache_key, response_data, timeout)
                except:
                    pass  # 如果解析失败，不缓存
            
            return response
        
        return wrapper
    return decorator


def cache_query_result(timeout=300, key_func=None):
    """
    查询结果缓存装饰器
    
    Args:
        timeout: 缓存过期时间（秒）
        key_func: 生成缓存键的函数，接收request参数
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(request)
            else:
                cache_key = f"query_cache:{request.path}:{request.method}"
                if request.GET:
                    import json
                    cache_key += f":{json.dumps(dict(request.GET), sort_keys=True)}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                from app.comm.BaseView import BaseView
                return BaseView.successData(cached_result)
            
            # 执行视图函数
            response = view_func(request, *args, **kwargs)
            
            # 缓存结果（只缓存GET请求的成功响应）
            if request.method == 'GET':
                try:
                    import json as json_module
                    if hasattr(response, 'content'):
                        response_data = json_module.loads(response.content.decode('utf-8'))
                        if response_data.get('code') == 0:
                            cache.set(cache_key, response_data.get('data'), timeout)
                except:
                    pass
            
            return response
        
        return wrapper
    return decorator

