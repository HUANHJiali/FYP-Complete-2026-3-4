"""
管理员操作日志相关视图

从 admin 视图中拆分日志查询逻辑，降低单文件复杂度。
"""

from django.core.paginator import Paginator

from app import models
from comm.BaseView import BaseView


class AdminLogView:
    """管理员日志管理接口集合"""

    @staticmethod
    def get_logs(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            user_id = request.GET.get('userId', '')
            user_name = request.GET.get('userName', '')
            operation_type = request.GET.get('operationType', '')
            module_name = request.GET.get('moduleName', '')
            status = request.GET.get('status', '')

            logs_query = models.OperationLog.objects.all().order_by('-created_at')

            if user_id:
                logs_query = logs_query.filter(user_id__icontains=user_id)
            if user_name:
                logs_query = logs_query.filter(user_name__icontains=user_name)
            if operation_type:
                logs_query = logs_query.filter(operation_type=operation_type)
            if module_name:
                logs_query = logs_query.filter(module_name=module_name)
            if status != '':
                logs_query = logs_query.filter(status=int(status))

            total = logs_query.count()
            paginator = Paginator(logs_query, size)
            logs_page = paginator.get_page(page)

            type_map = {0: '管理员', 1: '教师', 2: '学生'}
            logs_data = []
            for log in logs_page:
                logs_data.append({
                    'id': log.id,
                    'userId': log.user_id,
                    'userName': log.user_name,
                    'userType': log.user_type,
                    'userTypeName': type_map.get(log.user_type, '未知'),
                    'operationType': log.operation_type,
                    'operationTypeName': log.operation_type,
                    'moduleName': log.module_name,
                    'resourceId': log.resource_id,
                    'resourceName': log.resource_name,
                    'operationDetail': log.operation_detail,
                    'status': log.status,
                    'errorMessage': log.error_message,
                    'ipAddress': log.ip_address,
                    'deviceType': log.device_type,
                    'browserType': log.browser_type,
                    'osType': log.os_type,
                    'location': log.location,
                    'createdAt': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
                })

            return BaseView.successData({
                'list': logs_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取操作日志失败: {str(e)}')
