from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminDashboardManagementTest(TestCase):
    """管理员看板回归：dashboard/cards/trends 基础可用。"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='ADASH_ADMIN_001',
            userName='adash_admin',
            passWord=make_password('123456'),
            name='Admin Dashboard',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'adash_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_dashboard_endpoint_available(self):
        resp = self.client.get('/api/admin/dashboard/', {'token': self.token})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        self.assertIn('overview', body.get('data', {}))

    def test_dashboard_cards_endpoint_available(self):
        resp = self.client.get('/api/admin/dashboard_cards/', {'token': self.token})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        self.assertIn('activeUsers7d', body.get('data', {}))

    def test_trends_endpoint_available(self):
        resp = self.client.get('/api/admin/trends/', {'token': self.token})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        self.assertIn('months', body.get('data', {}))
