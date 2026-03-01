from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminUserManagementTest(TestCase):
    """管理员用户管理回归：新增/列表/更新/删除"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AU_ADMIN_001',
            userName='au_admin',
            passWord=make_password('123456'),
            name='Admin User Manager',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'au_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_admin_users_crud_minimal_flow(self):
        add_resp = self.client.post('/api/admin/users/', {
            'token': self.token,
            'action': 'add',
            'type': 1,
            'userName': 'au_teacher_01',
            'passWord': '123456',
            'name': 'Teacher Split',
            'gender': '女',
            'age': 28,
            'phone': '13800000000',
            'record': '硕士',
            'job': '讲师',
        })
        self.assertEqual(add_resp.status_code, 200)
        self.assertEqual(add_resp.json().get('code'), 0)

        list_resp = self.client.get('/api/admin/users/', {
            'token': self.token,
            'page': 1,
            'size': 10,
            'search': 'au_teacher_01',
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        rows = list_body.get('data', {}).get('list', [])
        self.assertEqual(len(rows), 1)
        user_id = rows[0].get('id')

        update_resp = self.client.post('/api/admin/users/', {
            'token': self.token,
            'action': 'update',
            'id': user_id,
            'name': 'Teacher Split Updated',
            'age': 29,
            'phone': '13900000000',
        })
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json().get('code'), 0)

        updated = models.Users.objects.filter(id=user_id).first()
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, 'Teacher Split Updated')

        del_resp = self.client.post('/api/admin/users/', {
            'token': self.token,
            'action': 'delete',
            'id': user_id,
        })
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get('code'), 0)
        self.assertFalse(models.Users.objects.filter(id=user_id).exists())
