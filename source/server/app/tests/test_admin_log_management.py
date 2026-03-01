from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminLogManagementTest(TestCase):
    """管理员日志管理回归：列表与筛选"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='AL_ADMIN_001',
            userName='al_admin',
            passWord=make_password('123456'),
            name='Admin Logger',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'al_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

        models.OperationLog.objects.create(
            user_id='AL_ADMIN_001',
            user_name='Admin Logger',
            user_type=0,
            operation_type='create',
            module_name='tasks',
            resource_id='1',
            resource_name='task-1',
            operation_detail='创建任务',
            status=1,
            ip_address='127.0.0.1'
        )
        models.OperationLog.objects.create(
            user_id='AL_ADMIN_001',
            user_name='Admin Logger',
            user_type=0,
            operation_type='delete',
            module_name='messages',
            resource_id='2',
            resource_name='msg-2',
            operation_detail='删除消息',
            status=0,
            ip_address='127.0.0.1'
        )

    def test_admin_logs_list_and_filter(self):
        list_resp = self.client.get('/api/admin/logs/', {
            'token': self.token,
            'page': 1,
            'size': 10,
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        self.assertGreaterEqual(list_body.get('data', {}).get('total', 0), 2)

        filter_resp = self.client.get('/api/admin/logs/', {
            'token': self.token,
            'page': 1,
            'size': 10,
            'moduleName': 'tasks',
            'status': 1,
        })
        self.assertEqual(filter_resp.status_code, 200)
        filter_body = filter_resp.json()
        self.assertEqual(filter_body.get('code'), 0)
        rows = filter_body.get('data', {}).get('list', [])
        self.assertGreaterEqual(len(rows), 1)
        self.assertTrue(all(row.get('moduleName') == 'tasks' for row in rows))
        self.assertTrue(all(row.get('status') == 1 for row in rows))
