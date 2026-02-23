"""
Health check endpoint for the exam system
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Comprehensive health check endpoint
    Returns 200 if all systems are healthy, 500 otherwise
    """
    health_status = {
        'status': 'healthy',
        'checks': {},
        'timestamp': None
    }
    
    try:
        from django.utils import timezone
        health_status['timestamp'] = timezone.now().isoformat()
    except Exception as e:
        health_status['timestamp'] = 'unknown'
        logger.error(f"Failed to get timestamp: {e}")
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                health_status['checks']['database'] = 'healthy'
            else:
                health_status['checks']['database'] = 'unhealthy'
                health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {e}")
    
    # Cache check (if Redis is configured)
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'healthy'
        else:
            health_status['checks']['cache'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        logger.warning(f"Cache health check failed: {e}")
    
    # AI Service check (optional)
    try:
        from comm.AIUtils import test_ai_connection
        if test_ai_connection():
            health_status['checks']['ai_service'] = 'healthy'
        else:
            health_status['checks']['ai_service'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['ai_service'] = f'unhealthy: {str(e)}'
        logger.warning(f"AI service health check failed: {e}")
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 500
    
    return JsonResponse(health_status, status=status_code)
