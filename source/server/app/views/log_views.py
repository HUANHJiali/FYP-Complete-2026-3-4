"""
操作���志API视图
提供日志查询、删除、导出等功能
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator
from app.models import OperationLog
from app.permissions import get_user_from_request
from utils.OperationLogger import OperationLogger
from comm.BaseView import BaseView

logger = logging.getLogger(__name__)


class LogViews(BaseView):
    """操作日志管理视图"""

    def _require_admin(self, request):
        user = get_user_from_request(request)
        if not user:
            return None, BaseView.error('用户未登录')
        if user.type != 0:
            return None, BaseView.error('权限不足')
        return user, None

    def get(self, request):
        """
        查询操作日志
        支持分页和多种过滤条件
        """
        try:
            _, err = self._require_admin(request)
            if err:
                return err

            # 获取查询参数
            page_index = int(request.GET.get('pageIndex', 1))
            page_size = int(request.GET.get('pageSize', 10))
            user_id = request.GET.get('userId', '').strip()
            user_name = request.GET.get('userName', '').strip()
            operation_type = request.GET.get('operationType', '').strip()
            module_name = request.GET.get('moduleName', '').strip()
            status = request.GET.get('status', '').strip()
            start_date = request.GET.get('startDate', '').strip()
            end_date = request.GET.get('endDate', '').strip()

            # 构建查询条件
            query = Q()

            # 用户ID过滤
            if user_id:
                query &= Q(user_id__icontains=user_id)

            # 用户姓名过滤
            if user_name:
                query &= Q(user_name__icontains=user_name)

            # 操作类型过滤
            if operation_type:
                query &= Q(operation_type=operation_type)

            # 模块名称过滤
            if module_name:
                query &= Q(module_name=module_name)

            # 状态过滤
            if status:
                query &= Q(status=int(status))

            # 日期范围过滤
            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    query &= Q(created_at__gte=start_datetime)
                except ValueError:
                    pass

            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query &= Q(created_at__lt=end_datetime)
                except ValueError:
                    pass

            # 查询日志列表
            logs = OperationLog.objects.filter(query).order_by('-created_at')

            # 分页
            paginator = Paginator(logs, page_size)
            page_obj = paginator.get_page(page_index)

            # 格式化返回数据
            log_list = []
            for log in page_obj:
                log_list.append({
                    'id': log.id,
                    'userId': log.user_id,
                    'userName': log.user_name,
                    'userType': log.user_type,
                    'userTypeName': OperationLogger.get_user_type_name(log.user_type),
                    'operationType': log.operation_type,
                    'operationTypeName': OperationLogger.get_operation_type_name(log.operation_type),
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
                    'createdAt': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else None,
                })

            return HttpResponse(json.dumps({
                'code': 0,
                'msg': '查询成功',
                'data': {
                    'list': log_list,
                    'total': paginator.count,
                    'pageIndex': page_index,
                    'pageSize': page_size
                }
            }), content_type='application/json; charset=utf-8')

        except Exception as e:
            logger.error(f'查询操作日志失败: {str(e)}', exc_info=True)
            return BaseView.error(f'查询失败: {str(e)}')

    def delete(self, request):
        """
        批量删除操作日志
        """
        try:
            _, err = self._require_admin(request)
            if err:
                return err

            # 获取要删除的日志ID列表
            log_ids = request.GET.get('ids', '').strip()

            if not log_ids:
                return BaseView.warn('请选择要删除的日志')

            # 解析ID列表
            id_list = [int(id_str.strip()) for id_str in log_ids.split(',') if id_str.strip().isdigit()]

            if not id_list:
                return BaseView.warn('无效的日志ID')

            # 删除日志
            deleted_count = OperationLog.objects.filter(id__in=id_list).delete()[0]

            logger.info(f'批量删除操作日志: {deleted_count}条')

            return HttpResponse(json.dumps({
                'code': 0,
                'msg': f'成功删除{deleted_count}条日志',
                'data': {
                    'deletedCount': deleted_count
                }
            }), content_type='application/json; charset=utf-8')

        except Exception as e:
            logger.error(f'删除操作日志失败: {str(e)}', exc_info=True)
            return BaseView.error(f'删除失败: {str(e)}')

    def put(self, request):
        """
        导出操作日志为CSV文件
        """
        try:
            _, err = self._require_admin(request)
            if err:
                return err

            import json

            # 解析请求体
            body_data = json.loads(request.body)
            filters = body_data.get('filters', {})

            # 构建查询条件
            query = Q()

            if filters.get('userId'):
                query &= Q(user_id__icontains=filters['userId'])
            if filters.get('userName'):
                query &= Q(user_name__icontains=filters['userName'])
            if filters.get('operationType'):
                query &= Q(operation_type=filters['operationType'])
            if filters.get('moduleName'):
                query &= Q(module_name=filters['moduleName'])
            if filters.get('status') is not None:
                query &= Q(status=int(filters['status']))
            if filters.get('startDate'):
                try:
                    start_datetime = datetime.strptime(filters['startDate'], '%Y-%m-%d')
                    query &= Q(created_at__gte=start_datetime)
                except ValueError:
                    pass
            if filters.get('endDate'):
                try:
                    end_datetime = datetime.strptime(filters['endDate'], '%Y-%m-%d') + timedelta(days=1)
                    query &= Q(created_at__lt=end_datetime)
                except ValueError:
                    pass

            # 查询日志
            logs = OperationLog.objects.filter(query).order_by('-created_at')

            # 创建HTTP响应
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="operation_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

            # 写入CSV文件
            response.write('\xEF\xBB\xBF')  # UTF-8 BOM
            writer = csv.writer(response)

            # 写入表头
            writer.writerow([
                '日志ID', '用户ID', '用户姓名', '用户类型', '操作类型', '模块名称',
                '资源ID', '资源名称', '操作详情', '状态', '错误信息',
                'IP地址', '设备类型', '浏览器', '操作系统', '地理位置', '操作时间'
            ])

            # 写入数据
            for log in logs:
                writer.writerow([
                    log.id,
                    log.user_id,
                    log.user_name,
                    OperationLogger.get_user_type_name(log.user_type),
                    OperationLogger.get_operation_type_name(log.operation_type),
                    log.module_name,
                    log.resource_id or '',
                    log.resource_name or '',
                    log.operation_detail or '',
                    '成功' if log.status == 1 else '失败',
                    log.error_message or '',
                    log.ip_address or '',
                    log.device_type or '',
                    log.browser_type or '',
                    log.os_type or '',
                    log.location or '',
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
                ])

            logger.info(f'导出操作日志: {len(logs)}条')

            return response

        except Exception as e:
            logger.error(f'导出操作日志失败: {str(e)}', exc_info=True)
            return BaseView.error(f'导出失败: {str(e)}')
