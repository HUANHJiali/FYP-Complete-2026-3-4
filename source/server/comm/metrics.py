"""
Prometheus监控指标导出器
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse

# API请求计数器
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# API响应时间直方图
api_response_time = Histogram(
    'api_response_time_seconds',
    'API response time in seconds',
    ['method', 'endpoint']
)

# 数据库查询时间
db_query_time = Histogram(
    'db_query_time_seconds',
    'Database query time in seconds',
    ['query_type']
)

# 活跃用户数
active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

# 考试数量
exams_total = Gauge(
    'exams_total',
    'Total number of exams'
)

# 任务数量
tasks_total = Gauge(
    'tasks_total',
    'Total number of tasks'
)

# 消息数量
messages_total = Gauge(
    'messages_total',
    'Total number of messages'
)

# 缓存命中率
cache_hits = Counter('cache_hits_total', 'Cache hits')
cache_misses = Counter('cache_misses_total', 'Cache misses')


class MetricsMiddleware:
    """监控指标中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 记录请求开始时间
        import time
        start_time = time.time()

        # 处理请求
        response = self.get_response(request)

        # 计算响应时间
        duration = time.time() - start_time

        # 记录指标
        if request.path.startswith('/api/'):
            # API请求计数
            api_requests_total.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code
            ).inc()

            # API响应时间
            api_response_time.labels(
                method=request.method,
                endpoint=request.path
            ).observe(duration)

        return response


def metrics_view(request):
    """Prometheus指标导出端点"""
    return HttpResponse(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST
    )


def update_metrics():
    """更新业务指标"""
    from app import models
    from django.core.cache import cache

    # 更新考试数量
    exams_total.set(models.Exams.objects.count())

    # 更新任务数量
    tasks_total.set(models.Tasks.objects.count())

    # 更新消息数量
    messages_total.set(models.Messages.objects.count())

    # 更新活跃用户数（使用缓存统计）
    active_users.set(len(cache.keys('fyp:*')))


class QueryTimer:
    """数据库查询计时器"""

    def __init__(self, query_type):
        self.query_type = query_type

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        db_query_time.labels(query_type=self.query_type).observe(duration)


class CacheTimer:
    """缓存操作计时器"""

    def __init__(self, operation):
        self.operation = operation

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            cache_hits.labels(operation=self.operation).inc()
        else:
            cache_misses.labels(operation=self.operation).inc()
