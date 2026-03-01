from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminQuestionFillAllSubjectsManagementTest(TestCase):
    """管理员全学科补齐回归：无学科时应安全返回。"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AQFAS_ADMIN_001',
            userName='aqfas_admin',
            passWord=make_password('123456'),
            name='Admin Fill All Subjects',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'aqfas_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_fill_all_subjects_no_subjects_returns_success_empty(self):
        resp = self.client.post('/api/admin/fill_all_subjects/', {
            'token': self.token,
            'counts': '0:0,1:0,2:0,3:0'
        })
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        data = body.get('data', {})
        self.assertEqual(data.get('createdTotal'), 0)
        self.assertEqual(data.get('list'), [])
