"""
健康检查��图
提供系统健康状态检查API
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
import os
import sys
from datetime import datetime


@require_http_methods(["GET"])
def health_check(request):
    """
    系统健康检查API

    ---
    tags:
      - 系统管理
    summary:
      系统健康检查
    description:
      检查系统各组件的健康状态，包括数据库、缓存、服务等
    responses:
      200:
        description: 系统健康或降级
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [healthy, degraded, unhealthy]
              description: 系统状态
            timestamp:
              type: string
              format: date-time
              description: 检查时间
            version:
              type: string
              description: 系统版本
            environment:
              type: string
              description: 运行环境
            python_version:
              type: string
              description: Python版本
            components:
              type: object
              properties:
                database:
                  type: string
                  description: 数据库状态
                cache:
                  type: string
                  description: 缓存状态
    """
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.getenv('DJANGO_SETTINGS_MODULE', 'unknown'),
        'python_version': sys.version,
        'components': {}
    }

    # 检查数据库
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status['components']['database'] = 'healthy'
    except Exception as e:
        status['components']['database'] = f'unhealthy: {str(e)[:50]}'
        status['status'] = 'degraded'

    # 检查缓存
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            status['components']['cache'] = 'healthy'
        else:
            status['components']['cache'] = 'degraded: read failed'
            status['status'] = 'degraded'
    except Exception as e:
        status['components']['cache'] = f'unhealthy: {str(e)[:50]}'
        status['status'] = 'degraded'

    return JsonResponse(status)


@require_http_methods(["GET"])
def health_check_simple(request):
    """
    简单健康检查（用于负载均衡器）

    ---
    tags:
      - 系统管理
    summary:
      简单健康检查
    description:
      返回简单的OK状态，用于负载均衡器健康检查
    responses:
      200:
        description: 服务正常
        schema:
          type: object
          properties:
            status:
              type: string
              example: "ok"
    """
    return JsonResponse({'status': 'ok'})
