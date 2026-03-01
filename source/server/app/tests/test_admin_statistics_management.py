from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminStatisticsManagementTest(TestCase):
    """管理员统计接口回归：缺参校验。"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='ASTAT_ADMIN_001',
            userName='astat_admin',
            passWord=make_password('123456'),
            name='Admin Statistics',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'astat_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_statistics_exam_validate_required_params(self):
        resp = self.client.get('/api/admin/statistics_exam/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.json().get('code'), 0)

    def test_statistics_student_validate_required_params(self):
        resp = self.client.get('/api/admin/statistics_student/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.json().get('code'), 0)

    def test_statistics_class_validate_required_params(self):
        resp = self.client.get('/api/admin/statistics_class/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.json().get('code'), 0)

    def test_statistics_subject_validate_required_params(self):
        resp = self.client.get('/api/admin/statistics_subject/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp.json().get('code'), 0)
