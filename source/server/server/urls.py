"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import sys
import os

# 添加项目根目录到 Python 路径（health_check.py 在 source/server/ 目录下）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from health_check import health_check
except ImportError:
    # 如果导入失败，创建一个简单的健康检查函数
    from django.http import JsonResponse
    def health_check(request):
        return JsonResponse({'status': 'healthy', 'message': 'Service is running'}, status=200)

# Swagger API文档配置
schema_view = get_schema_view(
    openapi.Info(
        title="FYP 学生考试系统 API",
        default_version='v1',
        description="""
        ## 智能学生考试系统 API 文档

        ### 主要功能
        - 用户认证（JWT Token）
        - 考试管理
        - 练习系统
        - 任务中心
        - 错题本
        - 消息中心
        - AI智能评分

        ### 认证方式
        大部分API需要在请求中包含token参数：
        ```
        POST /api/login/
        {
            "userName": "student",
            "passWord": "123456"
        }
        ```

        使用返回的token访问其他API：
        ```
        GET /api/exams/?token=your_token_here
        ```

        ### 默认测试账号
        - 管理员: admin / 123456
        - 教师: teacher / 123456
        - 学生: student / 123456
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    path('api/', include('app.urls')),
    # Swagger API文档
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
