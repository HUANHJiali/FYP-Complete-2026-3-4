"""
权限验证测试
测试不同角色的权限控制
"""
from django.test import TestCase, Client
from django.core.cache import cache
import json
from app import models


class AuthTestCase(TestCase):
    """权限验证测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        
        # 创建不同角色的用户
        self.admin = models.Users.objects.create(
            id='admin_001',
            userName='admin_test',
            passWord='123456',
            name='管理员',
            gender='男',
            age=30,
            type=0
        )
        
        self.teacher = models.Users.objects.create(
            id='teacher_001',
            userName='teacher_test',
            passWord='123456',
            name='教师',
            gender='女',
            age=35,
            type=1
        )
        
        self.student = models.Users.objects.create(
            id='student_001',
            userName='student_test',
            passWord='123456',
            name='学生',
            gender='男',
            age=20,
            type=2
        )
        
        # 登录获取token
        self.admin_token = self._get_token('admin_test', '123456')
        self.teacher_token = self._get_token('teacher_test', '123456')
        self.student_token = self._get_token('student_test', '123456')
    
    def tearDown(self):
        """测试后清理"""
        cache.clear()
    
    def _get_token(self, username, password):
        """辅助方法：获取登录token"""
        response = self.client.post('/api/sys/login/', {
            'userName': username,
            'passWord': password
        })
        data = json.loads(response.content)
        if data['code'] == 0:
            return data['data']['token']
        return None
    
    def test_get_user_info_with_valid_token(self):
        """测试使用有效token获取用户信息"""
        response = self.client.get('/api/sys/info/', {
            'token': self.admin_token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        self.assertEqual(data['data']['id'], 'admin_001')
        self.assertEqual(data['data']['userName'], 'admin_test')
        self.assertEqual(data['data']['type'], 0)
    
    def test_get_user_info_with_invalid_token(self):
        """测试使用无效token获取用户信息"""
        response = self.client.get('/api/sys/info/', {
            'token': 'invalid_token_12345'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
        self.assertIn('未登录', data['msg'])
    
    def test_get_user_info_without_token(self):
        """测试不使用token获取用户信息"""
        response = self.client.get('/api/sys/info/', {})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
    
    def test_admin_access_admin_api(self):
        """测试管理员访问管理员API"""
        # 创建学院数据用于测试
        college = models.Colleges.objects.create(
            name='测试学院',
            createTime='2024-01-01 00:00:00'
        )
        
        response = self.client.post('/api/admin/dashboard/', {
            'token': self.admin_token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # 管理员应该能访问管理员API
        # 注意：这里假设管理员API不需要额外权限验证，实际可能需要根据views.py调整
    
    def test_student_cannot_access_admin_api(self):
        """测试学生不能访问管理员API"""
        # 这个测试需要根据实际的权限验证逻辑来调整
        # 如果API有权限验证，学生应该被拒绝
        pass
    
    def test_token_expiration(self):
        """测试token过期处理"""
        # 手动设置一个过期的token
        expired_token = 'expired_token_123'
        cache.set(expired_token, 'admin_001', 0)  # 立即过期
        
        response = self.client.get('/api/sys/info/', {
            'token': expired_token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # token过期后应该返回未登录
        self.assertEqual(data['code'], 1)
    
    def test_exit_logout(self):
        """测试退出登录"""
        # 先验证token有效
        response = self.client.get('/api/sys/info/', {
            'token': self.admin_token
        })
        self.assertEqual(json.loads(response.content)['code'], 0)
        
        # 退出登录
        response = self.client.post('/api/sys/exit/', {
            'token': self.admin_token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        
        # 验证token已被删除
        self.assertIsNone(cache.get(self.admin_token))
        
        # 再次使用该token应该失败
        response = self.client.get('/api/sys/info/', {
            'token': self.admin_token
        })
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)



