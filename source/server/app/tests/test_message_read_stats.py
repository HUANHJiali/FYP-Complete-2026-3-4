from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class MessageReadStatsTest(TestCase):
    """消息运营字段与学生消息隔离回归测试"""

    def setUp(self):
        self.client = Client()

        self.admin = models.Users.objects.create(
            id='MRS_ADMIN_001',
            userName='mrs_admin',
            passWord=make_password('123456'),
            name='消息管理员',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        self.student_a = models.Users.objects.create(
            id='MRS_STU_A_001',
            userName='mrs_student_a',
            passWord=make_password('123456'),
            name='学生A',
            type=2,
            gender='女',
            age=18,
            createTime=DateUtil.getNowDateTime()
        )
        self.student_b = models.Users.objects.create(
            id='MRS_STU_B_001',
            userName='mrs_student_b',
            passWord=make_password('123456'),
            name='学生B',
            type=2,
            gender='男',
            age=18,
            createTime=DateUtil.getNowDateTime()
        )

        admin_login = self.client.post('/api/login/', {
            'userName': 'mrs_admin',
            'passWord': '123456'
        }).json()
        self.admin_token = admin_login['data']['token']

        student_a_login = self.client.post('/api/login/', {
            'userName': 'mrs_student_a',
            'passWord': '123456'
        }).json()
        self.student_a_token = student_a_login['data']['token']

        message = models.Messages.objects.create(
            title='消息运营字段测试',
            content='测试已读统计能力',
            type='notice',
            priority='medium',
            sender=self.admin
        )

        models.MessageReads.objects.create(
            message=message,
            user=self.student_a,
            isRead=True
        )
        models.MessageReads.objects.create(
            message=message,
            user=self.student_b,
            isRead=False
        )

    def test_admin_message_list_contains_read_rate(self):
        resp = self.client.get('/api/admin/messages/', {
            'token': self.admin_token,
            'page': 1,
            'size': 10
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)

        rows = body.get('data', {}).get('list', [])
        target = next((item for item in rows if item.get('title') == '消息运营字段测试'), None)
        self.assertIsNotNone(target)
        self.assertEqual(target.get('totalRecipients'), 2)
        self.assertEqual(target.get('readCount'), 1)
        self.assertEqual(target.get('unreadCount'), 1)
        self.assertEqual(target.get('readRate'), 50)

    def test_student_messages_are_isolated_by_user(self):
        resp = self.client.get('/api/messages/', {
            'token': self.student_a_token,
            'type': 'notice'
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)

        rows = body.get('data', [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].get('title'), '消息运营字段测试')
        self.assertTrue(rows[0].get('isRead'))
