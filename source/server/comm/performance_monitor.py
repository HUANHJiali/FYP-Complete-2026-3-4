"""
性能监控中间件
记录API响应时间、数据库查询次数等性能指标
"""
import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from typing import Optional, Dict, Any
import json
from datetime import datetime

logger = logging.getLogger('performance')


class PerformanceMonitorMiddleware(MiddlewareMixin):
    """
    性能监控中间件

    功能：
    1. 记录API响应时间
    2. 记录数据库查询次数
    3. 记录慢查询
    4. 性能指标统计
    """

    # 慢查询阈值（毫秒）
    SLOW_QUERY_THRESHOLD = 1000

    # 慢数据库查询阈值（毫秒）
    SLOW_DB_QUERY_THRESHOLD = 100

    def process_request(self, request):
        """请求开始时记录"""
        request._performance_start_time = time.time()

        # 记录初始数据库查询数
        if hasattr(connection, 'queries'):
            request._initial_db_queries = len(connection.queries)
        else:
            request._initial_db_queries = 0

    def process_response(self, request, response):
        """请求结束时记录性能指标"""
        # 只监控API请求
        if not request.path.startswith('/api/'):
            return response

        # 计算执行时间
        if hasattr(request, '_performance_start_time'):
            execution_time = (time.time() - request._performance_start_time) * 1000  # 转换为毫秒
        else:
            execution_time = 0

        # 计算数据库查询次数
        if hasattr(connection, 'queries'):
            db_queries = len(connection.queries) - getattr(request, '_initial_db_queries', 0)
        else:
            db_queries = 0

        # 构建性能数据
        performance_data = {
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'execution_time_ms': round(execution_time, 2),
            'db_queries': db_queries,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 添加用户信息（如果有）
        if hasattr(request, 'user_id'):
            performance_data['user_id'] = request.user_id

        # 记录慢请求
        if execution_time > self.SLOW_QUERY_THRESHOLD:
            performance_data['warning'] = f'Slow request: {execution_time}ms > {self.SLOW_QUERY_THRESHOLD}ms'
            logger.warning(f"[SLOW] {json.dumps(performance_data, ensure_ascii=False)}")
        else:
            logger.info(f"[PERF] {json.dumps(performance_data, ensure_ascii=False)}")

        # 添加响应头（仅在DEBUG模式）
        from django.conf import settings
        if settings.DEBUG:
            response['X-Execution-Time'] = f"{execution_time:.2f}ms"
            response['X-DB-Queries'] = str(db_queries)

        return response
