"""
增强的���误处理模块
提供标准化的错误响应和日志记录
"""
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import DatabaseError


# 配置日志
logger = logging.getLogger(__name__)


class ErrorHandler:
    """统一错误处理器"""

    # 错误码定义
    ERROR_CODES = {
        'VALIDATION_ERROR': 400,
        'AUTHENTICATION_ERROR': 401,
        'PERMISSION_ERROR': 403,
        'NOT_FOUND_ERROR': 404,
        'METHOD_NOT_ALLOWED': 405,
        'DATABASE_ERROR': 500,
        'SERVER_ERROR': 500,
        'AI_SERVICE_ERROR': 503,
    }

    @staticmethod
    def create_error_response(
        code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_type: str = 'Error'
    ) -> JsonResponse:
        """
        创建标准错误响应

        Args:
            code: HTTP状态码
            message: 错误消息
            details: 详细错误信息
            error_type: 错误类型

        Returns:
            JsonResponse
        """
        response_data = {
            'code': code,
            'msg': message,
            'errorType': error_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if details:
            response_data['details'] = details

        return JsonResponse(response_data, status=code)

    @staticmethod
    def validation_error(message: str, errors: Optional[Dict] = None) -> JsonResponse:
        """处理验证错误"""
        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['VALIDATION_ERROR'],
            message=message,
            details=errors,
            error_type='ValidationError'
        )

    @staticmethod
    def authentication_error(message: str = '认证失败，请重新登录') -> JsonResponse:
        """处理认证错误"""
        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['AUTHENTICATION_ERROR'],
            message=message,
            error_type='AuthenticationError'
        )

    @staticmethod
    def permission_error(message: str = '权限不足') -> JsonResponse:
        """处理权限错误"""
        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['PERMISSION_ERROR'],
            message=message,
            error_type='PermissionError'
        )

    @staticmethod
    def not_found_error(message: str = '资源不存在') -> JsonResponse:
        """处理404错误"""
        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['NOT_FOUND_ERROR'],
            message=message,
            error_type='NotFoundError'
        )

    @staticmethod
    def database_error(message: str = '数据库操作失败') -> JsonResponse:
        """处��数据库错误"""
        logger.error(f"Database error: {message}")

        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['DATABASE_ERROR'],
            message=message,
            error_type='DatabaseError'
        )

    @staticmethod
    def ai_service_error(message: str = 'AI服务暂时不可用') -> JsonResponse:
        """处理AI服务错误"""
        logger.warning(f"AI service error: {message}")

        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['AI_SERVICE_ERROR'],
            message=message,
            error_type='AIServiceError'
        )

    @staticmethod
    def server_error(message: str = '服务器内部错误') -> JsonResponse:
        """处理服务器错误"""
        logger.error(f"Server error: {message}")

        return ErrorHandler.create_error_response(
            code=ErrorHandler.ERROR_CODES['SERVER_ERROR'],
            message=message,
            error_type='ServerError'
        )

    @staticmethod
    def handle_exception(exception: Exception, context: str = "") -> JsonResponse:
        """
        统一异常处理

        Args:
            exception: 异常对象
            context: 错误上下文信息

        Returns:
            JsonResponse
        """
        # 记录详细错误日志
        error_trace = traceback.format_exc()
        logger.error(f"Exception in {context}: {str(exception)}\n{error_trace}")

        # 根据异常类型返回相应的错误响应
        if isinstance(exception, ValidationError):
            return ErrorHandler.validation_error(
                message='数据验证失败',
                errors=exception.message_dict if hasattr(exception, 'message_dict') else str(exception)
            )

        elif isinstance(exception, PermissionDenied):
            return ErrorHandler.permission_error()

        elif isinstance(exception, DatabaseError):
            return ErrorHandler.database_error('数据库操作失败，请稍后重试')

        else:
            # 其他未知错误
            return ErrorHandler.server_error('服务器内部错误，请稍后重试')


    @staticmethod
    def log_api_request(request, response, execution_time: float = None):
        """
        记录API请求日志

        Args:
            request: Django请求对象
            response: Django响应对象
            execution_time: 执行时间（毫秒）
        """
        try:
            log_data = {
                'method': request.method,
                'path': request.path,
                'user_id': getattr(request, 'user_id', None),
                'status_code': response.status_code,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            if execution_time is not None:
                log_data['execution_time_ms'] = round(execution_time, 2)

            # 根据状态码选择日志级别
            if response.status_code >= 500:
                logger.error(f"API Request: {log_data}")
            elif response.status_code >= 400:
                logger.warning(f"API Request: {log_data}")
            else:
                logger.info(f"API Request: {log_data}")

        except Exception as e:
            logger.error(f"Failed to log API request: {str(e)}")


class APIExceptionHandler:
    """API异常处理装饰器"""

    @staticmethod
    def handle_errors(func):
        """
        函数装饰器，自动捕获并处理异常

        Usage:
            @APIExceptionHandler.handle_errors
            def my_view(request):
                # 业务逻辑
                pass
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 获取上下文信息
                context = f"{func.__name__}"
                if args and hasattr(args[0], '__class__'):
                    context = f"{args[0].__class__.__name__}.{func.__name__}"

                return ErrorHandler.handle_exception(e, context)

        return wrapper


    @staticmethod
    def validate_request(*required_fields):
        """
        请求参数验证装饰器

        Usage:
            @APIExceptionHandler.validate_request('token', 'examId')
            def my_view(request):
                # 如果token或examId缺失，会自动返回错误
                pass
        """
        def decorator(func):
            def wrapper(request, *args, **kwargs):
                # 从GET或POST中获取参数
                request_data = {}
                if request.method == 'GET':
                    request_data = request.GET.dict()
                elif request.method in ['POST', 'PUT', 'PATCH']:
                    request_data = request.POST.dict()
                    # 尝试解析JSON
                    import json
                    try:
                        if request.body:
                            request_data.update(json.loads(request.body))
                    except:
                        pass

                # 检查必需字段
                missing_fields = [field for field in required_fields if field not in request_data or not request_data[field]]

                if missing_fields:
                    return ErrorHandler.validation_error(
                        message=f'缺少必需参数: {", ".join(missing_fields)}',
                        details={'missing_fields': missing_fields}
                    )

                return func(request, *args, **kwargs)

            return wrapper
        return decorator


# 便捷函数
def success_response(data=None, message='操作成功'):
    """成功响应"""
    response_data = {
        'code': 0,
        'msg': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    if data is not None:
        response_data['data'] = data

    return JsonResponse(response_data)


def error_response(message='操作失败', code=500, details=None):
    """错误响应"""
    return ErrorHandler.create_error_response(
        code=code,
        message=message,
        details=details,
        error_type='Error'
    )
