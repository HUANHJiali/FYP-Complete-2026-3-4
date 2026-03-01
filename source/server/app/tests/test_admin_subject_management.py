from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminSubjectManagementTest(TestCase):
    """管理员学科管理回归：新增/列表/更新/删除"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AS_ADMIN_001',
            userName='as_admin',
            passWord=make_password('123456'),
            name='Admin Subject Manager',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'as_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_admin_subjects_crud_minimal_flow(self):
        add_resp = self.client.post('/api/admin/subjects/', {
            'token': self.token,
            'action': 'add',
            'name': '拆分学科回归测试',
        })
        self.assertEqual(add_resp.status_code, 200)
        self.assertEqual(add_resp.json().get('code'), 0)

        list_resp = self.client.get('/api/admin/subjects/', {
            'token': self.token,
            'page': 1,
            'size': 10,
            'search': '拆分学科回归测试',
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        rows = list_body.get('data', {}).get('list', [])
        self.assertGreaterEqual(len(rows), 1)
        subject = next((item for item in rows if item.get('name') == '拆分学科回归测试'), None)
        self.assertIsNotNone(subject)
        subject_id = subject.get('id')

        update_resp = self.client.post('/api/admin/subjects/', {
            'token': self.token,
            'action': 'update',
            'id': subject_id,
            'name': '拆分学科回归测试-更新',
        })
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json().get('code'), 0)

        updated = models.Projects.objects.filter(id=subject_id).first()
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, '拆分学科回归测试-更新')

        del_resp = self.client.post('/api/admin/subjects/', {
            'token': self.token,
            'action': 'delete',
            'id': subject_id,
        })
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get('code'), 0)
        self.assertFalse(models.Projects.objects.filter(id=subject_id).exists())
