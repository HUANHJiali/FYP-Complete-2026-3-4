from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class DirectRoutePermissionGuardTest(TestCase):
    """直连路由权限保护回归测试"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='DRPG_ADMIN_001',
            userName='drpg_admin',
            passWord=make_password('123456'),
            name='Direct Route Admin',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        models.Users.objects.create(
            id='DRPG_TEACHER_001',
            userName='drpg_teacher',
            passWord=make_password('123456'),
            name='Direct Route Teacher',
            type=1,
            gender='女',
            age=28,
            createTime=DateUtil.getNowDateTime()
        )

        admin_login = self.client.post('/api/login/', {
            'userName': 'drpg_admin',
            'passWord': '123456'
        }).json()
        self.admin_token = admin_login['data']['token']

        teacher_login = self.client.post('/api/login/', {
            'userName': 'drpg_teacher',
            'passWord': '123456'
        }).json()
        self.teacher_token = teacher_login['data']['token']

    def test_statistics_route_denies_teacher(self):
        resp = self.client.get('/api/statistics/compare_classes/', {
            'token': self.teacher_token,
            'gradeIds': '1,2',
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('权限不足', body.get('msg', ''))

    def test_statistics_route_denies_anonymous(self):
        resp = self.client.get('/api/statistics/compare_classes/', {
            'gradeIds': '1,2',
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('未登录', body.get('msg', ''))

    def test_logs_route_denies_teacher(self):
        resp = self.client.get('/api/logs/', {
            'token': self.teacher_token,
            'pageIndex': 1,
            'pageSize': 10,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('权限不足', body.get('msg', ''))

    def test_logs_route_allows_admin(self):
        resp = self.client.get('/api/logs/', {
            'token': self.admin_token,
            'pageIndex': 1,
            'pageSize': 10,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), 0)
