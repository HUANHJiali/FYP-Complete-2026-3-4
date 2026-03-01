from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminPermissionGuardTest(TestCase):
    """管理员路由权限保护回归测试"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='APG_ADMIN_001',
            userName='apg_admin',
            passWord=make_password('123456'),
            name='Admin Guard',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        models.Users.objects.create(
            id='APG_TEACHER_001',
            userName='apg_teacher',
            passWord=make_password('123456'),
            name='Teacher Guard',
            type=1,
            gender='女',
            age=28,
            createTime=DateUtil.getNowDateTime()
        )

        admin_login = self.client.post('/api/login/', {
            'userName': 'apg_admin',
            'passWord': '123456'
        }).json()
        self.admin_token = admin_login['data']['token']

        teacher_login = self.client.post('/api/login/', {
            'userName': 'apg_teacher',
            'passWord': '123456'
        }).json()
        self.teacher_token = teacher_login['data']['token']

    def test_admin_route_allows_admin(self):
        resp = self.client.get('/api/admin/users/', {
            'token': self.admin_token,
            'page': 1,
            'size': 10,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('code'), 0)

    def test_admin_route_denies_teacher(self):
        resp = self.client.get('/api/admin/users/', {
            'token': self.teacher_token,
            'page': 1,
            'size': 10,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('权限不足', body.get('msg', ''))

    def test_admin_route_denies_anonymous(self):
        resp = self.client.get('/api/admin/users/', {
            'page': 1,
            'size': 10,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('未登录', body.get('msg', ''))
