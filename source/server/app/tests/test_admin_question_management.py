from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminQuestionManagementTest(TestCase):
    """管理员题目管理回归：新增/列表/更新/删除"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AQ_ADMIN_001',
            userName='aq_admin',
            passWord=make_password('123456'),
            name='Admin Question Manager',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        self.project = models.Projects.objects.create(
            name='题目拆分学科',
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'aq_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_admin_questions_crud_minimal_flow(self):
        add_resp = self.client.post('/api/admin/questions/', {
            'token': self.token,
            'action': 'add',
            'name': '拆分题目回归测试',
            'type': 1,
            'subjectId': self.project.id,
            'answer': 'def',
            'analyse': '函数定义关键字',
        })
        self.assertEqual(add_resp.status_code, 200)
        add_body = add_resp.json()
        self.assertEqual(add_body.get('code'), 0)
        question_id = add_body.get('data', {}).get('id')
        self.assertTrue(question_id)

        list_resp = self.client.get('/api/admin/questions/', {
            'token': self.token,
            'page': 1,
            'size': 10,
            'search': '拆分题目回归测试',
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        rows = list_body.get('data', {}).get('list', [])
        self.assertTrue(any(item.get('id') == question_id for item in rows))

        update_resp = self.client.post('/api/admin/questions/', {
            'token': self.token,
            'action': 'update',
            'id': question_id,
            'name': '拆分题目回归测试-更新',
            'answer': 'class',
        })
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json().get('code'), 0)

        updated = models.Practises.objects.filter(id=question_id).first()
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, '拆分题目回归测试-更新')

        del_resp = self.client.post('/api/admin/questions/', {
            'token': self.token,
            'action': 'delete',
            'id': question_id,
        })
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get('code'), 0)
        self.assertFalse(models.Practises.objects.filter(id=question_id).exists())

    def test_admin_questions_add_with_frontend_payload_and_auth_header(self):
        resp = self.client.post('/api/admin/questions/', {
            'action': 'add',
            'name': '前端payload选择题',
            'type': 0,
            'project': str(self.project.id),
            'analysis': '解析内容',
            'answer': '',
            'options[]': ['选项A', '选项B', '选项C'],
            'correctOptions[]': ['1'],
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        question_id = body.get('data', {}).get('id')
        self.assertTrue(question_id)

        created = models.Practises.objects.filter(id=question_id).first()
        self.assertIsNotNone(created)
        self.assertEqual(int(created.type), 0)
        self.assertEqual(created.project_id, self.project.id)