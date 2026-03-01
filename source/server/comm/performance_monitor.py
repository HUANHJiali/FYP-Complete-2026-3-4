"""
性能监控中间件
记录API响应时间、数据库查询次数等性能指标
"""
import time
import logging
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
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

    @staticmethod
    def _parse_query_time_ms(query):
        """将 connection.queries 中的 time 字段解析为毫秒"""
        raw_time = query.get('time', 0)
        try:
            return float(raw_time) * 1000
        except (TypeError, ValueError):
            return 0.0

    def process_request(self, request):
        """请求开始时记录"""
        request._performance_start_time = time.time()
        request._performance_threshold_ms = getattr(settings, 'SLOW_REQUEST_THRESHOLD_MS', 1000)
        request._slow_db_threshold_ms = getattr(settings, 'SLOW_DB_QUERY_THRESHOLD_MS', 200)

        observe_db_queries = getattr(settings, 'ENABLE_DB_QUERY_OBSERVE', settings.DEBUG)
        request._observe_db_queries = observe_db_queries

        request._previous_force_debug_cursor = getattr(connection, 'force_debug_cursor', False)
        if observe_db_queries:
            connection.force_debug_cursor = True

        # 记录初始数据库查询数
        if hasattr(connection, 'queries'):
            request._initial_db_queries = len(connection.queries)
        else:
            request._initial_db_queries = 0

    def process_response(self, request, response):
        """请求结束时记录性能指标"""
        previous_force_debug_cursor = getattr(request, '_previous_force_debug_cursor', False)
        if hasattr(connection, 'force_debug_cursor'):
            connection.force_debug_cursor = previous_force_debug_cursor

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
            current_queries = connection.queries[getattr(request, '_initial_db_queries', 0):]
        else:
            db_queries = 0
            current_queries = []

        slow_db_threshold = getattr(request, '_slow_db_threshold_ms', 200)
        slow_queries = []
        if getattr(request, '_observe_db_queries', False):
            for query in current_queries:
                query_time_ms = self._parse_query_time_ms(query)
                if query_time_ms >= slow_db_threshold:
                    slow_queries.append({
                        'time_ms': round(query_time_ms, 2),
                        'sql': (query.get('sql') or '')[:600]
                    })

        # 构建性能数据
        performance_data = {
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'execution_time_ms': round(execution_time, 2),
            'db_queries': db_queries,
            'slow_db_queries': len(slow_queries),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 添加用户信息（如果有）
        if hasattr(request, 'user_id'):
            performance_data['user_id'] = request.user_id

        if slow_queries:
            performance_data['slow_query_samples'] = slow_queries[:3]

        # 记录慢请求
        slow_request_threshold = getattr(request, '_performance_threshold_ms', 1000)
        if execution_time > slow_request_threshold:
            performance_data['warning'] = f'Slow request: {execution_time}ms > {slow_request_threshold}ms'
            logger.warning(f"[SLOW] {json.dumps(performance_data, ensure_ascii=False)}")
        else:
            logger.info(f"[PERF] {json.dumps(performance_data, ensure_ascii=False)}")

        if slow_queries:
            logger.warning(
                f"[SLOW-DB] path={request.path} count={len(slow_queries)} "
                f"threshold_ms={slow_db_threshold} samples={json.dumps(slow_queries[:3], ensure_ascii=False)}"
            )

        # 添加响应头（仅在DEBUG模式）
        from django.conf import settings
        if settings.DEBUG:
            response['X-Execution-Time'] = f"{execution_time:.2f}ms"
            response['X-DB-Queries'] = str(db_queries)
            response['X-Slow-DB-Queries'] = str(len(slow_queries))

        return response
