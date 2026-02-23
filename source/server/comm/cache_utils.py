"""
Cache utilities for performance optimization
Provides caching decorators and helpers
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cache_key(*args, **kwargs):
    """Generate a cache key from arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f'{k}={v}' for k, v in sorted(kwargs.items())])
    key_string = ':'.join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()[:32]


def cache_result(timeout=300, key_prefix='cache'):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f'{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}'
            
            # Try to get from cache
            result = cache.get(cache_key_str)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            try:
                cache.set(cache_key_str, result, timeout)
            except:
                pass  # Cache failures should not break functionality
            
            return result
        return wrapper
    return decorator


def cache_model_query(timeout=300):
    """
    Decorator for caching model query results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key_str = f'model_query:{func.__module__}:{func.__name__}:{cache_key(*args, **kwargs)}'
            
            result = cache.get(cache_key_str)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            
            # Convert QuerySet to list for caching
            if hasattr(result, '__iter__') and not isinstance(result, (list, dict)):
                try:
                    result = list(result)
                except:
                    pass
            
            try:
                cache.set(cache_key_str, result, timeout)
            except:
                pass
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern):
    """Invalidate cache entries matching pattern"""
    try:
        keys = cache.keys(f'*{pattern}*')
        if keys:
            cache.delete_many(keys)
    except:
        pass


def get_or_set_cache(key, default_func, timeout=300):
    """
    Get from cache or set using default function
    
    Args:
        key: Cache key
        default_func: Function to call if key not in cache
        timeout: Cache timeout in seconds
    """
    result = cache.get(key)
    if result is not None:
        return result
    
    result = default_func()
    try:
        cache.set(key, result, timeout)
    except:
        pass
    
    return result


# Pre-configured cache helpers for common data
def get_statistics_cache_key(stat_type, *args):
    return f'stats:{stat_type}:{":".join(str(a) for a in args)}'


def get_user_cache_key(user_id, data_type):
    return f'user:{user_id}:{data_type}'


# Cache statistics for dashboard (5 minutes)
DASHBOARD_CACHE_TIMEOUT = 300

# Cache user data (10 minutes)
USER_DATA_CACHE_TIMEOUT = 600

# Cache statistics (15 minutes)
STATS_CACHE_TIMEOUT = 900
