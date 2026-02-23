"""
基础API功能测试
测试API的基本功能、错误处理等
"""
from django.test import TestCase, Client
from django.core.cache import cache
import json
from app import models


class BasicAPITestCase(TestCase):
    """基础API功能测试用例"""
    
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
            type=2
        )
        
        # 创建基础数据
        self.project = models.Projects.objects.create(
            name='测试科目',
            createTime='2024-01-01 00:00:00'
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
    
    def test_api_response_format(self):
        """测试API响应格式"""
        response = self.client.get('/api/sys/info/', {
            'token': self.token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # 验证响应格式
        self.assertIn('code', data)
        self.assertIn('msg', data)
        self.assertIsInstance(data['code'], int)
        self.assertIsInstance(data['msg'], str)
    
    def test_api_success_response(self):
        """测试成功响应格式"""
        response = self.client.get('/api/sys/info/', {
            'token': self.token
        })
        
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
    
    def test_api_error_response(self):
        """测试错误响应格式"""
        response = self.client.get('/api/sys/info/', {
            'token': 'invalid_token'
        })
        
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
        self.assertIn('msg', data)
        self.assertIsInstance(data['msg'], str)
    
    def test_api_missing_params(self):
        """测试缺少参数的处理"""
        response = self.client.get('/api/sys/info/', {})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 1)
    
    def test_api_invalid_method(self):
        """测试无效的HTTP方法"""
        # 某些API可能只支持POST
        response = self.client.get('/api/sys/info/')
        
        # 根据实际实现，GET可能返回405或错误
        # 这里只验证不会导致500错误
        self.assertNotEqual(response.status_code, 500)
    
    def test_api_json_content_type(self):
        """测试API返回JSON格式"""
        response = self.client.post('/api/sys/info/', {
            'token': self.token
        })
        
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        # 验证可以解析为JSON
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
    
    def test_api_unicode_support(self):
        """测试API支持中文等Unicode字符"""
        # 更新用户名为中文
        response = self.client.post('/api/sys/updUserInfo/', {
            'token': self.token,
            'userName': 'testuser',
            'name': '测试用户中文名字',
            'gender': '男',
            'age': '25'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        
        # 验证中文已正确保存
        user = models.Users.objects.get(id='user_001')
        self.assertEqual(user.name, '测试用户中文名字')
    
    def test_api_concurrent_requests(self):
        """测试并发请求处理"""
        import threading
        
        results = []
        
        def make_request():
            response = self.client.get('/api/sys/info/', {
                'token': self.token
            })
            data = json.loads(response.content)
            results.append(data['code'])
        
        # 创建5个并发请求
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 5)
        self.assertTrue(all(code == 0 for code in results))
    
    def test_api_error_handling(self):
        """测试错误处理机制"""
        # 测试不存在的API端点
        response = self.client.post('/api/nonexistent/endpoint/', {})
        
        # 应该返回404或适当的错误响应，而不是500
        self.assertNotEqual(response.status_code, 500)



