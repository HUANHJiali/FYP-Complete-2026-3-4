from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminQuestionIOManagementTest(TestCase):
    """管理员题目导入/导出/模板回归"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AQIO_ADMIN_001',
            userName='aqio_admin',
            passWord=make_password('123456'),
            name='Admin Question IO',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        self.project = models.Projects.objects.create(
            name='题目IO学科',
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'aqio_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_questions_template_export_import_minimal_flow(self):
        template_resp = self.client.post('/api/admin/questions_template/', {
            'token': self.token,
        })
        self.assertEqual(template_resp.status_code, 200)
        self.assertIn('questions_template.csv', template_resp.get('Content-Disposition', ''))

        question = models.Practises.objects.create(
            name='导出验证题目',
            type=1,
            project=self.project,
            answer='def',
            analyse='解析',
            createTime=DateUtil.getNowDateTime()
        )
        self.assertIsNotNone(question.id)

        export_resp = self.client.post('/api/admin/questions_export/', {
            'token': self.token,
            'subjectId': self.project.id,
        })
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn('questions_export.csv', export_resp.get('Content-Disposition', ''))
        self.assertIn('导出验证题目', export_resp.content.decode('utf-8'))

        csv_content = (
            'name,type,answer,analyse,subjectId\n'
            f'导入验证题目,1,keyword,解析,{self.project.id}\n'
        )
        upload = SimpleUploadedFile(
            'questions_import.csv',
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        import_resp = self.client.post('/api/admin/questions_import/', {
            'token': self.token,
            'subjectId': self.project.id,
            'file': upload,
        })
        self.assertEqual(import_resp.status_code, 200)
        body = import_resp.json()
        self.assertEqual(body.get('code'), 0)
        self.assertGreaterEqual(body.get('data', {}).get('created', 0), 1)
        self.assertTrue(models.Practises.objects.filter(name='导入验证题目').exists())

    def test_questions_import_rejects_invalid_type(self):
        csv_content = (
            'name,type,answer,analyse,subjectId\n'
            f'非法题型题目,not_a_valid_type,abc,解析,{self.project.id}\n'
        )
        upload = SimpleUploadedFile(
            'questions_import_invalid_type.csv',
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        import_resp = self.client.post('/api/admin/questions_import/', {
            'token': self.token,
            'subjectId': self.project.id,
            'file': upload,
        })

        self.assertEqual(import_resp.status_code, 200)
        body = import_resp.json()
        self.assertEqual(body.get('code'), 0)
        self.assertEqual(body.get('data', {}).get('created', 0), 0)
        failed = body.get('data', {}).get('failed', [])
        self.assertGreaterEqual(len(failed), 1)
        self.assertIn('无效的题目类型', failed[0].get('reason', ''))
        self.assertFalse(models.Practises.objects.filter(name='非法题型题目').exists())
