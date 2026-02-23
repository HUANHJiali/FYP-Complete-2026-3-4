"""
Query optimization utilities
Provides helpers for optimizing database queries
"""
from django.db import connection
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


def query_count(func):
    """
    Decorator to count and log database queries
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django.db import reset_queries
        try:
            reset_queries()
        except:
            pass
        
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        try:
            query_count = len(connection.queries)
            if query_count > 10:
                logger.warning(
                    f'{func.__name__}: {query_count} queries in {elapsed:.3f}s - '
                    f'Consider optimizing'
                )
            else:
                logger.debug(
                    f'{func.__name__}: {query_count} queries in {elapsed:.3f}s'
                )
        except:
            pass
        
        return result
    return wrapper


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """
    Apply select_related and prefetch_related optimizations to queryset
    
    Args:
        queryset: Django QuerySet
        select_related: List of fields for select_related
        prefetch_related: List of fields for prefetch_related
    
    Returns:
        Optimized queryset
    """
    if select_related:
        queryset = queryset.select_related(*select_related)
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    return queryset


def bulk_create_optimized(model, objects, batch_size=1000):
    """
    Bulk create objects with optimized batch size
    
    Args:
        model: Django model class
        objects: List of model instances
        batch_size: Number of objects to create per batch
    
    Returns:
        Number of objects created
    """
    created = 0
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        model.objects.bulk_create(batch)
        created += len(batch)
    return created


def get_or_create_cached(model, cache_key, defaults=None, timeout=300):
    """
    Get or create with caching
    
    Args:
        model: Django model class
        cache_key: Key for caching
        defaults: Default values for creation
        timeout: Cache timeout
    
    Returns:
        Tuple of (object, created)
    """
    from django.core.cache import cache
    
    cached = cache.get(cache_key)
    if cached:
        return cached, False
    
    obj, created = model.objects.get_or_create(**defaults)
    cache.set(cache_key, obj, timeout)
    return obj, created


class QueryOptimizationMiddleware:
    """
    Middleware to log slow queries and query counts
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        from django.conf import settings
        
        start_time = time.time()
        response = self.get_response(request)
        elapsed = time.time() - start_time
        
        # Log slow requests
        if elapsed > 1.0:
            try:
                query_count = len(connection.queries)
                logger.warning(
                    f'Slow request: {request.path} took {elapsed:.2f}s '
                    f'with {query_count} queries'
                )
            except:
                logger.warning(
                    f'Slow request: {request.path} took {elapsed:.2f}s'
                )
        
        return response


# Common optimization patterns
STUDENT_OPTIMIZATION = {
    'select_related': ['user', 'grade', 'college'],
}

TEACHER_OPTIMIZATION = {
    'select_related': ['user'],
}

EXAM_LOG_OPTIMIZATION = {
    'select_related': ['exam', 'student'],
    'prefetch_related': ['exam__project'],
}

WRONG_QUESTION_OPTIMIZATION = {
    'select_related': ['practise', 'practise__project'],
}
