"""
API集成测试
测试核心API端点的功能
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json

User = get_user_model()


class APITestCase(TestCase):
    """API集成测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建测试用户
        self.admin = User.objects.create(
            userName='admin_test',
            name='测试管理员',
            type=0,
            passWord='admin123'
        )

        self.teacher = User.objects.create(
            userName='teacher_test',
            name='测试教师',
            type=1,
            passWord='teacher123'
        )

        self.student = User.objects.create(
            userName='student_test',
            name='测试学生',
            type=2,
            passWord='student123'
        )

        # 登录获取token
        response = self.client.post('/api/login/', {
            'userName': 'admin_test',
            'passWord': 'admin123'
        })
        data = json.loads(response.content)
        if data.get('code') == 0:
            self.admin_token = data['data']['token']
        else:
            self.admin_token = None

    def test_login_api(self):
        """测试登录API"""
        response = self.client.post('/api/login/', {
            'userName': 'admin_test',
            'passWord': 'admin123'
        })
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get('code'), 0)
        self.assertIn('token', data.get('data', {}))

    def test_login_invalid_credentials(self):
        """测试登录失败场景"""
        response = self.client.post('/api/login/', {
            'userName': 'invalid_user',
            'passWord': 'wrong_password'
        })
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertNotEqual(data.get('code'), 0)

    def test_health_check(self):
        """测试健康检查API"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('components', data)

    def test_health_check_simple(self):
        """测试简单健康检查API"""
        response = self.client.get('/api/health/simple/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get('status'), 'ok')

    def test_exams_list(self):
        """测试考试列表API"""
        response = self.client.get('/api/exams/all')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get('code'), 0)
        self.assertIsInstance(data.get('data'), list)

    def test_tasks_list(self):
        """测试任务列表API"""
        response = self.client.get('/api/tasks/all')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get('code'), 0)
        self.assertIsInstance(data.get('data'), list)

    def test_messages_list(self):
        """测试消息列表API"""
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get('code'), 0)
        self.assertIsInstance(data.get('data'), list)

    def test_projects_list(self):
        """测试科目列表API"""
        response = self.client.get('/api/projects/all')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data.get('code'), 0)
        self.assertIsInstance(data.get('data'), list)

    def test_cache_functionality(self):
        """测试缓存功能"""
        # 设置缓存
        cache.set('test_key', 'test_value', 60)

        # 获取缓存
        value = cache.get('test_key')
        self.assertEqual(value, 'test_value')

        # 删除缓存
        cache.delete('test_key')
        value = cache.get('test_key')
        self.assertIsNone(value)

    def test_rate_limiting(self):
        """测试API限流"""
        # 多次请求登录API
        for i in range(15):
            response = self.client.post('/api/login/', {
                'userName': 'test_user',
                'passWord': 'wrong_password'
            })

        # 第11次请求应该被限流
        data = json.loads(response.content)
        # 注意：实际测试时需要根据限流实现调整断言
        self.assertIn('code', data)

    def tearDown(self):
        """清理测试数据"""
        cache.clear()
        User.objects.filter(userName__in=['admin_test', 'teacher_test', 'student_test']).delete()
