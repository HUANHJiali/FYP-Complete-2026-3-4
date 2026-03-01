from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminTaskManagementTest(TestCase):
    """管理员任务管理回归：列表/新增/删除"""

    def setUp(self):
        self.client = Client()
        self.admin = models.Users.objects.create(
            id='AT_ADMIN_001',
            userName='at_admin',
            passWord=make_password('123456'),
            name='Admin Tester',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        self.project = models.Projects.objects.create(
            name='自动化测试科目',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade = models.Grades.objects.create(
            name='自动化测试班级',
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'at_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_admin_tasks_crud_minimal_flow(self):
        add_resp = self.client.post('/api/admin/tasks/', {
            'token': self.token,
            'action': 'add',
            'title': '任务拆分回归测试',
            'description': '验证admin_task_views拆分后功能正常',
            'type': 'practice',
            'deadline': DateUtil.getNowDateTime(),
            'score': 100,
            'project': self.project.id,
            'grade': self.grade.id,
            'isActive': 'true',
        })
        self.assertEqual(add_resp.status_code, 200)
        add_body = add_resp.json()
        self.assertEqual(add_body.get('code'), 0)
        task_id = add_body.get('data', {}).get('id')
        self.assertTrue(task_id)

        list_resp = self.client.get('/api/admin/tasks/', {
            'token': self.token,
            'page': 1,
            'pageSize': 10,
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        task_ids = [item.get('id') for item in list_body.get('data', {}).get('list', [])]
        self.assertIn(task_id, task_ids)

        del_resp = self.client.post('/api/admin/tasks/', {
            'token': self.token,
            'action': 'delete',
            'id': task_id,
        })
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get('code'), 0)
        self.assertFalse(models.Tasks.objects.filter(id=task_id).exists())

    def test_admin_tasks_add_with_frontend_payload_and_auth_header(self):
        resp = self.client.post('/api/admin/tasks/', {
            'action': 'add',
            'title': '前端payload任务',
            'description': '任务描述',
            'type': 'practice',
            'project': str(self.project.id),
            'grade': str(self.grade.id),
            'deadline': DateUtil.getNowDateTime(),
            'score': 100,
            'isActive': 'true',
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        task_id = body.get('data', {}).get('id')
        self.assertTrue(task_id)

        created = models.Tasks.objects.filter(id=task_id).first()
        self.assertIsNotNone(created)
        self.assertEqual(created.project_id, self.project.id)
        self.assertEqual(created.grade_id, self.grade.id)
