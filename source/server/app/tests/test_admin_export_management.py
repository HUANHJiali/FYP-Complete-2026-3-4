from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminExportManagementTest(TestCase):
    """管理员导入导出回归：关键缺参与空文件校验。"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AEX_ADMIN_001',
            userName='aex_admin',
            passWord=make_password('123456'),
            name='Admin Export',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'aex_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_export_exam_results_validate_required_params(self):
        resp = self.client.get('/api/admin/export_exam_results/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)

    def test_export_practice_results_validate_required_params(self):
        resp = self.client.get('/api/admin/export_practice_results/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)

    def test_students_import_validate_file_required(self):
        resp = self.client.post('/api/admin/students_import/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
