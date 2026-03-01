from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminMessageManagementTest(TestCase):
    """管理员消息管理回归：发送/列表/已读详情/删除"""

    def setUp(self):
        self.client = Client()
        self.admin = models.Users.objects.create(
            id='AM_ADMIN_001',
            userName='am_admin',
            passWord=make_password('123456'),
            name='Admin Messenger',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        self.student = models.Users.objects.create(
            id='AM_STU_001',
            userName='am_student',
            passWord=make_password('123456'),
            name='Student Receiver',
            type=2,
            gender='女',
            age=20,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'am_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_admin_messages_minimal_flow(self):
        send_resp = self.client.post('/api/admin/messages/', {
            'token': self.token,
            'action': 'add',
            'title': '消息拆分回归测试',
            'content': '验证admin_message_views拆分后功能正常',
            'type': 'notice',
            'priority': 'medium',
            'userType': 'custom',
            'recipientIds[]': [self.student.id],
        })
        self.assertEqual(send_resp.status_code, 200)
        self.assertEqual(send_resp.json().get('code'), 0)

        list_resp = self.client.get('/api/admin/messages/', {
            'token': self.token,
            'page': 1,
            'size': 10,
        })
        self.assertEqual(list_resp.status_code, 200)
        list_body = list_resp.json()
        self.assertEqual(list_body.get('code'), 0)
        rows = list_body.get('data', {}).get('list', [])
        self.assertGreaterEqual(len(rows), 1)

        target = next((item for item in rows if item.get('title') == '消息拆分回归测试'), None)
        self.assertIsNotNone(target)
        message_id = target.get('id')

        readers_resp = self.client.get('/api/admin/message_readers/', {
            'token': self.token,
            'messageId': message_id,
            'page': 1,
            'pageSize': 10,
        })
        self.assertEqual(readers_resp.status_code, 200)
        readers_body = readers_resp.json()
        self.assertEqual(readers_body.get('code'), 0)
        reader_ids = [item.get('userId') for item in readers_body.get('data', {}).get('readers', [])]
        self.assertIn(self.student.id, reader_ids)

        del_resp = self.client.post('/api/admin/messages/', {
            'token': self.token,
            'action': 'delete',
            'id': message_id,
        })
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(del_resp.json().get('code'), 0)
        self.assertFalse(models.Messages.objects.filter(id=message_id).exists())
