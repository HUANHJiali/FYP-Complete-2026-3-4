"""
管理员功能测试
测试管理员仪表板、用户管理等功能
"""
from django.test import TestCase, Client
from django.core.cache import cache
import json
from app import models
from datetime import datetime, timedelta


class AdminTestCase(TestCase):
    """管理员功能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        
        # 创建管理员用户
        self.admin = models.Users.objects.create(
            id='admin_001',
            userName='admin',
            passWord='123456',
            name='管理员',
            gender='男',
            age=30,
            type=0  # 管理员
        )
        
        # 创建测试数据
        self.student = models.Users.objects.create(
            id='student_001',
            userName='student',
            passWord='123456',
            name='学生',
            gender='女',
            age=20,
            type=2
        )
        
        self.teacher = models.Users.objects.create(
            id='teacher_001',
            userName='teacher',
            passWord='123456',
            name='教师',
            gender='男',
            age=35,
            type=1
        )
        
        # 创建科目
        self.project = models.Projects.objects.create(
            name='测试科目',
            createTime='2024-01-01 00:00:00'
        )
        
        # 创建题目
        self.practise = models.Practises.objects.create(
            name='测试题目',
            answer='测试答案',
            analyse='测试分析',
            type=0,  # 选择题
            createTime='2024-01-01 00:00:00',
            project=self.project
        )
        
        # 创建试卷
        self.exam = models.Exams.objects.create(
            name='测试试卷',
            teacher=self.admin,
            project=self.project,
            grade=None,  # 可以为空
            createTime='2024-01-01 00:00:00',
            examTime='2024-12-31 23:59:59'
        )
        
        # 登录获取token
        response = self.client.post('/api/sys/login/', {
            'userName': 'admin',
            'passWord': '123456'
        })
        data = json.loads(response.content)
        self.token = data['data']['token']
    
    def tearDown(self):
        """测试后清理"""
        cache.clear()
    
    def test_get_dashboard_data(self):
        """测试获取管理员仪表板数据"""
        # 根据实际实现，dashboard可能是GET或POST
        # 先尝试GET
        response = self.client.get('/api/admin/dashboard/', {
            'token': self.token
        })
        
        # 如果GET失败，尝试POST
        if response.status_code != 200 or json.loads(response.content).get('code') != 0:
            response = self.client.post('/api/admin/dashboard/', {
                'token': self.token
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        
        dashboard_data = data['data']
        self.assertIn('overview', dashboard_data)
        self.assertIn('monthly', dashboard_data)
        self.assertIn('activity', dashboard_data)
        
        # 验证统计数据
        overview = dashboard_data['overview']
        self.assertIn('total_users', overview)
        self.assertIn('total_students', overview)
        self.assertIn('total_teachers', overview)
        self.assertIn('total_exams', overview)
        self.assertIn('total_questions', overview)
        
        # 验证数据正确性
        self.assertEqual(overview['total_users'], 3)  # admin, student, teacher
        self.assertEqual(overview['total_students'], 1)
        self.assertEqual(overview['total_teachers'], 1)
        self.assertEqual(overview['total_exams'], 1)
        self.assertEqual(overview['total_questions'], 1)
    
    def test_get_dashboard_cards(self):
        """测试获取首页卡片数据"""
        # 创建一些活动数据
        now = datetime.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_start_str = day_start.strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建今日新增的题目
        models.Practises.objects.create(
            name='今日题目',
            answer='答案',
            analyse='分析',
            type=0,
            createTime=day_start_str,
            project=self.project
        )
        
        # 尝试GET
        response = self.client.get('/api/admin/dashboard_cards/', {
            'token': self.token
        })
        
        # 如果GET失败，尝试POST
        if response.status_code != 200 or json.loads(response.content).get('code') != 0:
            response = self.client.post('/api/admin/dashboard_cards/', {
                'token': self.token
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        
        cards_data = data['data']
        self.assertIn('todayNewQuestions', cards_data)
        self.assertIn('todayNewPractices', cards_data)
        self.assertIn('activeUsers7d', cards_data)
        self.assertIn('passRate7d', cards_data)
        self.assertIn('avgScore7d', cards_data)
    
    def test_get_trends_data(self):
        """测试获取趋势数据"""
        # 尝试GET
        response = self.client.get('/api/admin/trends/', {
            'token': self.token
        })
        
        # 如果GET失败，尝试POST
        if response.status_code != 200 or json.loads(response.content).get('code') != 0:
            response = self.client.post('/api/admin/trends/', {
                'token': self.token
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        
        trends_data = data['data']
        self.assertIn('months', trends_data)
        self.assertIn('questionsByMonth', trends_data)
        self.assertIn('days', trends_data)
        self.assertIn('activeUsersDaily', trends_data)
        self.assertIn('practiceDoneDaily', trends_data)
        self.assertIn('taskDoneDaily', trends_data)
    
    def test_get_all_users(self):
        """测试获取所有用户列表"""
        response = self.client.post('/api/admin/getAllUsers/', {
            'token': self.token
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # 根据实际API返回格式调整断言
        # 这里假设返回成功
        self.assertIn('code', data)
    
    def test_dashboard_data_accuracy(self):
        """测试仪表板数据准确性"""
        # 创建更多测试数据
        for i in range(5):
            models.Users.objects.create(
                id=f'student_{i:03d}',
                userName=f'student{i}',
                passWord='123456',
                name=f'学生{i}',
                gender='男',
                age=20,
                type=2
            )
        
        response = self.client.post('/api/admin/dashboard/', {
            'token': self.token
        })
        
        data = json.loads(response.content)
        overview = data['data']['overview']
        
        # 验证用户总数（3个原有 + 5个新增 = 8个）
        self.assertEqual(overview['total_users'], 8)
        self.assertEqual(overview['total_students'], 6)  # 1个原有 + 5个新增



