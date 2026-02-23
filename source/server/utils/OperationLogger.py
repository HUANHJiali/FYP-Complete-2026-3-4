"""
操作日志工具类
用于记录系统中的用户操作，包括登录、登出、增删改等操作
"""

import json
import logging
from datetime import datetime
from django.utils import timezone
from app.models import OperationLog

logger = logging.getLogger(__name__)


class OperationLogger:
    """操作日志记录工具类"""

    # 操作类型常量
    OPERATION_LOGIN = 'login'           # 登录
    OPERATION_LOGOUT = 'logout'         # 登出
    OPERATION_CREATE = 'create'         # 创建
    OPERATION_UPDATE = 'update'         # 更新
    OPERATION_DELETE = 'delete'         # 删除
    OPERATION_QUERY = 'query'           # 查询
    OPERATION_SUBMIT = 'submit'         # 提交
    OPERATION_EXPORT = 'export'         # 导出
    OPERATION_IMPORT = 'import'         # 导入

    # 模块名称常量
    MODULE_USER = 'user'                # 用户管理
    MODULE_EXAM = 'exam'                # 考试管理
    MODULE_QUESTION = 'question'        # 题目管理
    MODULE_STUDENT = 'student'          # 学生管理
    MODULE_TEACHER = 'teacher'          # 教师管理
    MODULE_GRADE = 'grade'              # 班级管理
    MODULE_PROJECT = 'project'          # 科目管理
    MODULE_TASK = 'task'                # 任务管理
    MODULE_PRACTICE = 'practice'        # 练习管理
    MODULE_SYSTEM = 'system'            # 系统管理

    # 用户类型常量
    USER_TYPE_ADMIN = 0                 # 管理员
    USER_TYPE_TEACHER = 1               # 教师
    USER_TYPE_STUDENT = 2               # 学生

    # 操作状态常量
    STATUS_SUCCESS = 1                  # 成功
    STATUS_FAILURE = 0                  # 失败

    @staticmethod
    def log(
        user_id,
        user_name,
        user_type,
        operation_type,
        module_name,
        resource_id=None,
        resource_name=None,
        operation_detail=None,
        status=STATUS_SUCCESS,
        error_message=None,
        request=None
    ):
        """
        记录操作日志

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型 (0-管理员, 1-教师, 2-学生)
            operation_type: 操作类型 (login/logout/create/update/delete/submit等)
            module_name: 模块名称 (user/exam/question/student等)
            resource_id: 资源ID (可选)
            resource_name: 资源名称 (可选)
            operation_detail: 操作详情 (可选，可以是dict或str)
            status: 操作状态 (1-成功, 0-失败)
            error_message: 错误信息 (可选，失败时提供)
            request: Django request对象 (可选，用于获取IP和User-Agent)

        Returns:
            OperationLog对象或None
        """
        try:
            # 处理operation_detail，如果是dict则转换为JSON字符串
            if isinstance(operation_detail, dict):
                operation_detail = json.dumps(operation_detail, ensure_ascii=False)

            # 提取请求信息
            ip_address = None
            user_agent = None
            device_type = None
            browser_type = None
            os_type = None

            if request:
                ip_address = OperationLogger._get_client_ip(request)
                user_agent_str = request.META.get('HTTP_USER_AGENT', '')
                user_agent = user_agent_str[:500] if user_agent_str else None

                # 解析User-Agent
                device_info = OperationLogger._parse_user_agent(user_agent_str)
                device_type = device_info.get('device_type')
                browser_type = device_info.get('browser_type')
                os_type = device_info.get('os_type')

            # 创建日志记录
            log_entry = OperationLog.objects.create(
                user_id=str(user_id)[:50],
                user_name=str(user_name)[:100],
                user_type=int(user_type),
                operation_type=str(operation_type)[:50],
                module_name=str(module_name)[:50],
                resource_id=str(resource_id)[:100] if resource_id else None,
                resource_name=str(resource_name)[:255] if resource_name else None,
                operation_detail=operation_detail,
                status=int(status),
                error_message=error_message,
                ip_address=ip_address[:50] if ip_address else None,
                user_agent=user_agent,
                device_type=device_type[:50] if device_type else None,
                browser_type=browser_type[:50] if browser_type else None,
                os_type=os_type[:50] if os_type else None,
            )

            logger.info(f"Operation log success: {user_name} - {operation_type} - {module_name}")
            return log_entry

        except Exception as e:
            logger.error(f"操作日志记录失败: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def log_login(user_id, user_name, user_type, status, request=None, error_message=None):
        """
        记录登录日志

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型
            status: 登录状态 (1-成功, 0-失败)
            request: Django request对象
            error_message: 错误信息 (失败时提供)
        """
        return OperationLogger.log(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            operation_type=OperationLogger.OPERATION_LOGIN,
            module_name=OperationLogger.MODULE_SYSTEM,
            status=status,
            error_message=error_message,
            request=request
        )

    @staticmethod
    def log_logout(user_id, user_name, user_type, request=None):
        """
        记录登出日志

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型
            request: Django request对象
        """
        return OperationLogger.log(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            operation_type=OperationLogger.OPERATION_LOGOUT,
            module_name=OperationLogger.MODULE_SYSTEM,
            status=OperationLogger.STATUS_SUCCESS,
            request=request
        )

    @staticmethod
    def log_create(user_id, user_name, user_type, module_name, resource_id, resource_name,
                   operation_detail=None, request=None):
        """
        记录创建操作日志

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型
            module_name: 模块名称
            resource_id: 资源ID
            resource_name: 资源名称
            operation_detail: 操作详情
            request: Django request对象
        """
        return OperationLogger.log(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            operation_type=OperationLogger.OPERATION_CREATE,
            module_name=module_name,
            resource_id=resource_id,
            resource_name=resource_name,
            operation_detail=operation_detail,
            status=OperationLogger.STATUS_SUCCESS,
            request=request
        )

    @staticmethod
    def log_update(user_id, user_name, user_type, module_name, resource_id, resource_name,
                   operation_detail=None, request=None):
        """
        记录更新操作日志

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型
            module_name: 模块名称
            resource_id: 资源ID
            resource_name: 资源名称
            operation_detail: 操作详情
            request: Django request对象
        """
        return OperationLogger.log(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            operation_type=OperationLogger.OPERATION_UPDATE,
            module_name=module_name,
            resource_id=resource_id,
            resource_name=resource_name,
            operation_detail=operation_detail,
            status=OperationLogger.STATUS_SUCCESS,
            request=request
        )

    @staticmethod
    def log_delete(user_id, user_name, user_type, module_name, resource_id, resource_name,
                   operation_detail=None, request=None):
        """
        记录删除操作日志

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型
            module_name: 模块名称
            resource_id: 资源ID
            resource_name: 资源名称
            operation_detail: 操作详情
            request: Django request对象
        """
        return OperationLogger.log(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            operation_type=OperationLogger.OPERATION_DELETE,
            module_name=module_name,
            resource_id=resource_id,
            resource_name=resource_name,
            operation_detail=operation_detail,
            status=OperationLogger.STATUS_SUCCESS,
            request=request
        )

    @staticmethod
    def log_submit(user_id, user_name, user_type, module_name, resource_id, resource_name,
                   operation_detail=None, status=STATUS_SUCCESS, error_message=None, request=None):
        """
        记录提交操作日志（考试提交、作业提交等）

        Args:
            user_id: 用户ID
            user_name: 用户姓名
            user_type: 用户类型
            module_name: 模块名称
            resource_id: 资源ID
            resource_name: 资源名称
            operation_detail: 操作详情
            status: 操作状态
            error_message: 错误信息
            request: Django request对象
        """
        return OperationLogger.log(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            operation_type=OperationLogger.OPERATION_SUBMIT,
            module_name=module_name,
            resource_id=resource_id,
            resource_name=resource_name,
            operation_detail=operation_detail,
            status=status,
            error_message=error_message,
            request=request
        )

    @staticmethod
    def _get_client_ip(request):
        """
        获取客户端IP地址

        Args:
            request: Django request对象

        Returns:
            IP地址字符串
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def _parse_user_agent(user_agent_string):
        """
        解析User-Agent字符串，提取设备类型、浏览器、操作系统信息

        Args:
            user_agent_string: User-Agent字符串

        Returns:
            包含device_type, browser_type, os_type的字典
        """
        if not user_agent_string:
            return {}

        user_agent_lower = user_agent_string.lower()

        # 解析设备类型
        device_type = 'PC'
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
            device_type = 'Mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            device_type = 'Tablet'

        # 解析操作系统
        os_type = 'Unknown'
        if 'windows' in user_agent_lower:
            os_type = 'Windows'
        elif 'mac os x' in user_agent_lower or 'macos' in user_agent_lower:
            os_type = 'macOS'
        elif 'linux' in user_agent_lower:
            os_type = 'Linux'
        elif 'android' in user_agent_lower:
            os_type = 'Android'
        elif 'iphone' in user_agent_lower or 'ios' in user_agent_lower:
            os_type = 'iOS'

        # 解析浏览器
        browser_type = 'Unknown'
        if 'micromessenger' in user_agent_lower:
            browser_type = 'WeChat'
        elif 'edge' in user_agent_lower:
            browser_type = 'Edge'
        elif 'chrome' in user_agent_lower and 'edge' not in user_agent_lower:
            browser_type = 'Chrome'
        elif 'firefox' in user_agent_lower:
            browser_type = 'Firefox'
        elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
            browser_type = 'Safari'
        elif 'opera' in user_agent_lower or 'opr' in user_agent_lower:
            browser_type = 'Opera'
        elif 'trident' in user_agent_lower or 'msie' in user_agent_lower:
            browser_type = 'IE'

        return {
            'device_type': device_type,
            'browser_type': browser_type,
            'os_type': os_type
        }

    @staticmethod
    def get_user_type_name(user_type):
        """获取用户类型名称"""
        type_map = {
            OperationLogger.USER_TYPE_ADMIN: '管理员',
            OperationLogger.USER_TYPE_TEACHER: '教师',
            OperationLogger.USER_TYPE_STUDENT: '学生',
        }
        return type_map.get(user_type, '未知')

    @staticmethod
    def get_operation_type_name(operation_type):
        """获取操作类型名称"""
        type_map = {
            OperationLogger.OPERATION_LOGIN: '登录',
            OperationLogger.OPERATION_LOGOUT: '登出',
            OperationLogger.OPERATION_CREATE: '创建',
            OperationLogger.OPERATION_UPDATE: '更新',
            OperationLogger.OPERATION_DELETE: '删除',
            OperationLogger.OPERATION_QUERY: '查询',
            OperationLogger.OPERATION_SUBMIT: '提交',
            OperationLogger.OPERATION_EXPORT: '导出',
            OperationLogger.OPERATION_IMPORT: '导入',
        }
        return type_map.get(operation_type, operation_type)
