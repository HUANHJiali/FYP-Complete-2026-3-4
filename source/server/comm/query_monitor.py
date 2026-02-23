"""
数据库查询监控中间件
用于监控和记录慢查询
"""
import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('django.db.backends')

class QueryMonitorMiddleware(MiddlewareMixin):
    """
    数据库查询监控中间件
    记录慢查询和查询统计信息
    """
    
    SLOW_QUERY_THRESHOLD = 0.1  # 慢查询阈值（秒）
    
    def process_request(self, request):
        """请求开始时重置查询计数"""
        request._query_start_time = time.time()
        request._query_count_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """请求结束时记录查询统计"""
        if hasattr(request, '_query_start_time'):
            elapsed_time = time.time() - request._query_start_time
            query_count = len(connection.queries) - request._query_count_start
            
            # 记录慢查询
            if elapsed_time > self.SLOW_QUERY_THRESHOLD:
                logger.warning(
                    f"慢查询检测: {request.path} - "
                    f"耗时: {elapsed_time:.3f}s, "
                    f"查询次数: {query_count}"
                )
            
            # 记录查询详情（仅在DEBUG模式下）
            if hasattr(request, 'META') and 'HTTP_X_DEBUG_QUERIES' in request.META:
                queries = connection.queries[request._query_count_start:]
                if queries:
                    logger.info(f"查询详情 ({request.path}):")
                    for i, query in enumerate(queries, 1):
                        logger.info(f"  [{i}] {query['sql'][:100]}... ({query['time']}s)")
        
        return response
    
    def process_exception(self, request, exception):
        """异常时也记录查询信息"""
        if hasattr(request, '_query_start_time'):
            elapsed_time = time.time() - request._query_start_time
            query_count = len(connection.queries) - request._query_count_start
            logger.error(
                f"异常查询: {request.path} - "
                f"耗时: {elapsed_time:.3f}s, "
                f"查询次数: {query_count}, "
                f"异常: {str(exception)}"
            )
        return None

