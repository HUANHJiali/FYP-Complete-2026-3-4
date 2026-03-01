from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminExamManagementTest(TestCase):
    """管理员试卷管理回归：新增/列表/更新/删除"""

    def setUp(self):
        self.client = Client()
        self.admin = models.Users.objects.create(
            id='AE_ADMIN_001',
            userName='ae_admin',
            passWord=make_password('123456'),
            name='Admin Exam Manager',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        self.project = models.Projects.objects.create(
            name='试卷拆分学科',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade = models.Grades.objects.create(
            name='试卷拆分班级',
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'ae_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_admin_exams_crud_minimal_flow(self):
        add_resp = self.client.post('/api/admin/exams/', {
            'token': self.token,
            'action': 'add',
            'name': '拆分试卷回归测试',
            'project': self.project.id,
            'gradeId': self.grade.id,
        })
        self.assertEqual(add_resp.status_code, 200)
        add_body = add_resp.json()
        self.assertEqual(add_body.get('code'), 0)
        exam_id = add_body.get('data', {}).get('id')
        self.assertTrue(exam_id)

        list_resp = self.client.get('/api/admin/exams/', {
            'token': self.token,
            'page': 1,
            'size': 10,
            'search': '拆分试卷回归测试',
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        rows = list_body.get('data', {}).get('list', [])
        self.assertTrue(any(item.get('id') == exam_id for item in rows))

        update_resp = self.client.post('/api/admin/exams/', {
            'token': self.token,
            'action': 'update',
            'id': exam_id,
            'name': '拆分试卷回归测试-更新',
        })
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json().get('code'), 0)

        updated = models.Exams.objects.filter(id=exam_id).first()
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, '拆分试卷回归测试-更新')

        del_resp = self.client.post('/api/admin/exams/', {
            'token': self.token,
            'action': 'delete',
            'id': exam_id,
        })
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get('code'), 0)
        self.assertFalse(models.Exams.objects.filter(id=exam_id).exists())

    def test_admin_exams_add_with_frontend_payload_and_auth_header(self):
        resp = self.client.post('/api/admin/exams/', {
            'action': 'add',
            'title': '前端payload试卷',
            'type': 'fixed',
            'difficulty': 'medium',
            'duration': 60,
            'totalScore': 100,
            'project': str(self.project.id),
            'startTime': DateUtil.getNowDateTime(),
            'isActive': 'true',
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        exam_id = body.get('data', {}).get('id')
        self.assertTrue(exam_id)

        created = models.Exams.objects.filter(id=exam_id).first()
        self.assertIsNotNone(created)
        self.assertEqual(created.project_id, self.project.id)
        self.assertIsNotNone(created.grade_id)
