"""
统一错误处理模块
提供统一的错误处理装饰器和工具函数
"""
import logging
from functools import wraps
from django.core.cache import cache
from comm.BaseView import BaseView

logger = logging.getLogger('app.views')


def handle_exceptions(func):
    """
    统一异常处理装饰器
    自动捕获异常并返回统一的错误响应
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"参数错误 in {func.__name__}: {str(e)}")
            return BaseView.warn(f'参数错误: {str(e)}')
        except Exception as e:
            # 动态导入models避免循环导入
            from app import models
            if hasattr(models, 'Users') and isinstance(e, models.Users.DoesNotExist):
                logger.warning(f"用户不存在 in {func.__name__}")
                return BaseView.error('用户不存在')
            elif hasattr(models, 'DoesNotExist') and isinstance(e, models.DoesNotExist):
                logger.warning(f"数据不存在 in {func.__name__}: {str(e)}")
                return BaseView.error('数据不存在')
            else:
                logger.error(f"系统错误 in {func.__name__}: {str(e)}", exc_info=True)
                return BaseView.error('系统错误，请稍后重试')
    return wrapper


def validate_required_fields(request, fields, method='POST'):
    """
    验证必需字段
    
    Args:
        request: Django请求对象
        fields: 必需字段列表
        method: 请求方法 ('POST' 或 'GET')
        
    Returns:
        tuple: (is_valid, missing_field) - (是否有效, 缺失的字段名)
    """
    data = request.POST if method == 'POST' else request.GET
    
    for field in fields:
        if not data.get(field):
            return False, field
    
    return True, None


def validate_user_token(request):
    """
    验证用户token并返回用户对象
    
    Args:
        request: Django请求对象
        
    Returns:
        tuple: (is_valid, user) - (是否有效, 用户对象或None)
    """
    from app import models
    
    token = request.POST.get('token') or request.GET.get('token')
    if not token:
        return False, None
    
    user_id = cache.get(token)
    if not user_id:
        return False, None
    
    try:
        user = models.Users.objects.filter(id=user_id).first()
        if not user:
            return False, None
        return True, user
    except Exception:
        return False, None


def sanitize_input(text, max_length=None, allowed_chars=None):
    """
    清理输入文本
    
    Args:
        text: 输入文本
        max_length: 最大长度
        allowed_chars: 允许的字符（正则表达式）
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ''
    
    import re
    
    # 移除危险字符
    if allowed_chars:
        text = re.sub(f'[^{allowed_chars}]', '', text)
    
    # 限制长度
    if max_length:
        text = text[:max_length]
    
    return text.strip()


def log_execution_time(func):
    """
    执行时间监控装饰器
    记录函数执行时间，超过阈值时发出警告
    """
    import time
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:
            logger.warning(
                f"Slow execution: {func.__name__} took {execution_time:.2f}s"
            )
        else:
            logger.debug(
                f"{func.__name__} executed in {execution_time:.3f}s"
            )
        
        return result
    return wrapper


def retry_on_failure(max_retries=3, delay=1, exceptions=(Exception,)):
    """
    重试装饰器
    在指定异常发生时自动重试
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 触发重试的异常类型元组
    """
    import time
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {str(e)}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} retries failed for {func.__name__}: {str(e)}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


def cache_result(timeout=300):
    """
    结果缓存装饰器
    缓存函数返回结果
    
    Args:
        timeout: 缓存时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"cache:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache set for {func.__name__}")
            
            return result
        return wrapper
    return decorator


class APIResponse:
    """
    统一API响应格式
    """
    
    @staticmethod
    def success(data=None, msg='操作成功'):
        return {
            'code': 0,
            'msg': msg,
            'data': data
        }
    
    @staticmethod
    def error(msg='操作失败', code=1):
        return {
            'code': code,
            'msg': msg,
            'data': None
        }
    
    @staticmethod
    def warn(msg='警告', code=2):
        return {
            'code': code,
            'msg': msg,
            'data': None
        }
    
    @staticmethod
    def paginated(items, total, page, page_size):
        return {
            'code': 0,
            'msg': '查询成功',
            'data': {
                'items': items,
                'total': total,
                'page': page,
                'pageSize': page_size,
                'totalPages': (total + page_size - 1) // page_size
            }
        }


def validate_file_upload(file, allowed_extensions, max_size_mb=10):
    """
    验证文件上传
    
    Args:
        file: 上传的文件对象
        allowed_extensions: 允许的扩展名列表
        max_size_mb: 最大文件大小（MB）
        
    Returns:
        tuple: (is_valid, error_message)
    """
    import os
    
    if not file:
        return False, '请选择文件'
    
    # 检查文件扩展名
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        return False, f'不支持的文件类型: {ext}'
    
    # 检查文件大小
    if file.size > max_size_mb * 1024 * 1024:
        return False, f'文件大小不能超过{max_size_mb}MB'
    
    return True, None


def log_api_call(func):
    """
    API调用日志装饰器
    记录API调用详情
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # 获取请求信息
        method = request.method
        path = request.path
        user_id = request.POST.get('userId') or request.GET.get('userId') or 'anonymous'
        
        logger.info(
            f"API Call: {method} {path} by user {user_id}"
        )
        
        try:
            result = func(request, *args, **kwargs)
            logger.debug(f"API Response: {path} - Success")
            return result
        except Exception as e:
            logger.error(
                f"API Error: {path} - {str(e)}",
                exc_info=True
            )
            raise
    
    return wrapper
