"""
FYP项目核心功能单元测试
测试覆盖率提升计划
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from app.models import (
    Users, Students, Teachers, Exams,
    Practises, ExamLogs, StudentPracticeLogs
)
from datetime import datetime
import json


class UserAuthenticationTest(TestCase):
    """用户认证测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()
        # 创建测试用户
        self.admin = Users.objects.create(
            userName='test_admin',
            passWord='test123',
            type=0
        )
        self.teacher = Users.objects.create(
            userName='test_teacher',
            passWord='test123',
            type=1
        )
        self.student = Users.objects.create(
            userName='test_student',
            passWord='test123',
            type=2
        )

    def test_admin_login(self):
        """测试管理员登录"""
        response = self.client.post('/api/login/', {
            'userName': 'test_admin',
            'passWord': 'test123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        self.assertIn('token', data['data'])

    def test_student_login(self):
        """测试学生登录"""
        response = self.client.post('/api/login/', {
            'userName': 'test_student',
            'passWord': 'test123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)

    def test_login_wrong_password(self):
        """测试错误密码登录"""
        response = self.client.post('/api/login/', {
            'userName': 'test_student',
            'passWord': 'wrong_password'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotEqual(data['code'], 0)


class ExamManagementTest(TestCase):
    """考试管理测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()
        # 创建教师和考试
        self.teacher = Users.objects.create(
            userName='exam_teacher',
            passWord='test123',
            type=1
        )
        # 登录获取token
        response = self.client.post('/api/login/', {
            'userName': 'exam_teacher',
            'passWord': 'test123'
        })
        self.token = response.json()['data']['token']

    def test_create_exam(self):
        """测试创建考试"""
        response = self.client.post('/api/exams/add', {
            'token': self.token,
            'title': '测试考试',
            'examTime': 60,
            'projectId': 1
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)

    def test_get_exam_list(self):
        """测试获取考试列表"""
        response = self.client.get('/api/exams/all', {
            'token': self.token
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)


class PracticeSystemTest(TestCase):
    """练习系统测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.student = Users.objects.create(
            userName='practice_student',
            passWord='test123',
            type=2
        )
        response = self.client.post('/api/login/', {
            'userName': 'practice_student',
            'passWord': 'test123'
        })
        self.token = response.json()['data']['token']

    def test_get_practice_papers(self):
        """测试获取练习试卷列表"""
        response = self.client.get('/api/practice/papers/all', {
            'token': self.token
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)

    def test_submit_practice_answer(self):
        """测试提交练习答案"""
        # 这个测试需要实际的练习数据
        # 可以先创建测试数据
        practice_id = 1
        response = self.client.post('/api/practice/answer/submit', {
            'token': self.token,
            'practiseId': practice_id,
            'studentAnswer': 'A'
        })
        # 根据实际情况验证结果


class AIIntegrationTest(TestCase):
    """AI功能集成测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.teacher = Users.objects.create(
            userName='ai_teacher',
            passWord='test123',
            type=1
        )
        response = self.client.post('/api/login/', {
            'userName': 'ai_teacher',
            'passWord': 'test123'
        })
        self.token = response.json()['data']['token']

    def test_ai_score_answer(self):
        """测试AI智能评分"""
        # 这个测试需要配置真实的API密钥
        # 在CI/CD环境中可以使用mock
        response = self.client.post('/api/ai/score', {
            'token': self.token,
            'questionType': 0,
            'questionContent': 'Python是什么？',
            'studentAnswer': 'Python是一种编程语言',
            'rightAnswer': 'Python是一种高级编程语言'
        })
        # 验证AI评分功能


class CacheManagerTest(TestCase):
    """缓存管理器测试"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        from comm.cache_manager import CacheManager

        # 设置缓存
        result = CacheManager.set('test_key', 'test_value', timeout=60)
        self.assertTrue(result)

        # 获取缓存
        value = CacheManager.get('test_key')
        self.assertEqual(value, 'test_value')

    def test_cache_get_or_set(self):
        """测试缓存获取或设置"""
        from comm.cache_manager import CacheManager

        # 第一次调用应该执行回调
        call_count = [0]

        def callback():
            call_count[0] += 1
            return 'callback_result'

        result1 = CacheManager.get_or_set('test_callback', callback)
        self.assertEqual(result1, 'callback_result')
        self.assertEqual(call_count[0], 1)

        # 第二次调用应该使用缓存
        result2 = CacheManager.get_or_set('test_callback', callback)
        self.assertEqual(result2, 'callback_result')
        self.assertEqual(call_count[0], 1)  # 没有再次调用

    def test_cache_delete(self):
        """测试缓存删除"""
        from comm.cache_manager import CacheManager

        CacheManager.set('test_delete', 'value')
        value = CacheManager.get('test_delete')
        self.assertIsNotNone(value)

        CacheManager.delete('test_delete')
        value = CacheManager.get('test_delete')
        self.assertIsNone(value)


class QueryOptimizerTest(TestCase):
    """查询优化器测试"""

    def test_exam_logs_optimization(self):
        """测试考试记录查询优化"""
        from comm.query_optimizer import QueryOptimizer
        from app.models import ExamLogs

        # 创建测试数据
        student = Users.objects.create(
            userName='test_student_opt',
            passWord='test123',
            type=2
        )

        # 使用优化查询
        from django.db import connection
        from django.test.utils import override_settings

        with override_settings(DEBUG=True):
            # 重置查询计数
            connection.queries_executed = 0

            # 执行优化查询
            logs = QueryOptimizer.get_exam_logs_with_related(
                student_id=student.id
            )

            # 强制评估
            list(logs)

            # 验证查询次数较少（应该<=2次）
            query_count = len(connection.queries)
            self.assertLessEqual(query_count, 2,
                f"Query optimization failed: {query_count} queries executed")


class ErrorHandlerTest(TestCase):
    """错误处理器测试"""

    def test_validation_error(self):
        """测试验证错误"""
        from comm.error_handler_enhanced import ErrorHandler

        response = ErrorHandler.validation_error(
            message='验证失败',
            errors={'field': ['错误信息']}
        )
        self.assertEqual(response.status_code, 400)

    def test_not_found_error(self):
        """测试404错误"""
        from comm.error_handler_enhanced import ErrorHandler

        response = ErrorHandler.not_found_error('资源不存在')
        self.assertEqual(response.status_code, 404)

    def test_permission_error(self):
        """测试权限错误"""
        from comm.error_handler_enhanced import ErrorHandler

        response = ErrorHandler.permission_error('权限不足')
        self.assertEqual(response.status_code, 403)


class ModelTest(TestCase):
    """模型测试"""

    def test_user_creation(self):
        """测试用户创建"""
        user = Users.objects.create(
            userName='model_test_user',
            passWord='test123',
            type=2
        )
        self.assertEqual(user.userName, 'model_test_user')
        self.assertEqual(user.type, 2)

    def test_exam_creation(self):
        """测试考试创建"""
        exam = Exams.objects.create(
            title='模型测试考试',
            examTime=60,
            createTime=datetime.now()
        )
        self.assertEqual(exam.title, '模型测试考试')
        self.assertEqual(exam.examTime, 60)


class APITest(TestCase):
    """API端点测试"""

    def setUp(self):
        """测试前准备"""
        self.client = Client()

    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')

    def test_swagger_docs(self):
        """测试Swagger文档可访问"""
        response = self.client.get('/swagger/')
        self.assertEqual(response.status_code, 200)

    def test_redoc_docs(self):
        """测试ReDoc文档可访问"""
        response = self.client.get('/redoc/')
        self.assertEqual(response.status_code, 200)


# 运行测试的命令
"""
运行所有测试:
    python manage.py test

运行特定测试类:
    python manage.py test app.tests.test_core_views.UserAuthenticationTest

运行特定测试方法:
    python manage.py test app.tests.test_core_views.UserAuthenticationTest.test_admin_login

查看测试覆盖率:
    coverage run --source='app' manage.py test
    coverage report
    coverage html

预期覆盖率提升:
    当前: ~40%
    目标: ~60-70%
"""
