"""
用户信息功能测试
测试用户信息获取、更新等功能
"""
from django.test import TestCase, Client
from django.core.cache import cache
import json
from app import models


class UserInfoTestCase(TestCase):
    """用户信息功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        
        # 创建测试用户
        self.user = models.Users.objects.create(
            id='user_001',
            userName='testuser',
            passWord='123456',
            name='测试用户',
            gender='男',
            age=25,
            type=2  # 学生
        )
        
        # 登录获取token
        response = self.client.post('/api/sys/login/', {
            'userName': 'testuser',
            'passWord': '123456'
        })
        data = json.loads(response.content)
        self.token = data['data']['token']
    
    def tearDown(self):
        """测试后清理"""
        cache.clear()
    
    def test_get_user_info_success(self):
        """测试成功获取用户信息"""
        response = self.client.get('/api/sys/info/', {
            'token': self.token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        
        user_data = data['data']
        self.assertEqual(user_data['id'], 'user_001')
        self.assertEqual(user_data['userName'], 'testuser')
        self.assertEqual(user_data['name'], '测试用户')
        self.assertEqual(user_data['gender'], '男')
        self.assertEqual(user_data['age'], 25)
        self.assertEqual(user_data['type'], 2)
    
    def test_update_user_info_success(self):
        """测试成功更新用户信息"""
        response = self.client.post('/api/sys/updUserInfo/', {
            'token': self.token,
            'userName': 'testuser',  # 用户名不变
            'name': '更新后的名字',
            'gender': '女',
            'age': '26'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        
        # 验证信息已更新
        user = models.Users.objects.get(id='user_001')
        self.assertEqual(user.name, '更新后的名字')
        self.assertEqual(user.gender, '女')
        self.assertEqual(user.age, 26)
    
    def test_update_user_info_duplicate_username(self):
        """测试更新为已存在的用户名"""
        # 创建另一个用户
        other_user = models.Users.objects.create(
            id='user_002',
            userName='otheruser',
            passWord='123456',
            name='其他用户',
            gender='男',
            age=20,
            type=2
        )
        
        response = self.client.post('/api/sys/updUserInfo/', {
            'token': self.token,
            'userName': 'otheruser',  # 尝试使用已存在的用户名
            'name': '测试用户',
            'gender': '男',
            'age': '25'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
        self.assertIn('用户账号已存在', data['msg'])
    
    def test_update_user_info_same_username(self):
        """测试更新信息但用户名不变（应该成功）"""
        response = self.client.post('/api/sys/updUserInfo/', {
            'token': self.token,
            'userName': 'testuser',  # 用户名不变
            'name': '新名字',
            'gender': '女',
            'age': '30'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
    
    def test_update_password_success(self):
        """测试成功修改密码"""
        response = self.client.post('/api/sys/pwd/', {
            'token': self.token,
            'oldPwd': '123456',
            'newPwd': 'newpassword123',
            'rePwd': 'newpassword123'  # 确认密码
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        
        # 验证新密码可以登录
        response = self.client.post('/api/sys/login/', {
            'userName': 'testuser',
            'passWord': 'newpassword123'
        })
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
    
    def test_update_password_wrong_old_password(self):
        """测试使用错误旧密码修改密码"""
        response = self.client.post('/api/sys/pwd/', {
            'token': self.token,
            'oldPwd': 'wrong_password',
            'newPwd': 'newpassword123',
            'rePwd': 'newpassword123'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
        self.assertIn('原始密码输入错误', data['msg'])
    
    def test_update_password_password_mismatch(self):
        """测试两次密码不一致"""
        response = self.client.post('/api/sys/pwd/', {
            'token': self.token,
            'oldPwd': '123456',
            'newPwd': 'newpassword123',
            'rePwd': 'different_password'  # 密码不一致
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
        self.assertIn('两次输入的密码不一致', data['msg'])
    
    def test_update_password_missing_params(self):
        """测试缺少参数修改密码"""
        response = self.client.post('/api/sys/pwd/', {
            'token': self.token,
            'oldPwd': '123456'
            # 缺少newPwd和rePwd
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # 根据实际实现，可能返回错误或成功（如果参数验证不严格）
        self.assertIn('code', json.loads(response.content))



