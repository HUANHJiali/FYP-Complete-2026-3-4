from django.test import TestCase, Client
from django.contrib.auth.hashers import make_password

from app import models
from comm.CommUtils import DateUtil


class RegressionBaselineTest(TestCase):
    """P1回归基线：登录、考试、练习、AI评分四条主链路。"""

    def setUp(self):
        self.client = Client()

    def test_login_flow(self):
        models.Users.objects.create(
            id='RB_ADMIN_001',
            userName='rb_admin',
            passWord=make_password('123456'),
            name='Regression Admin',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        response = self.client.post('/api/login/', {
            'userName': 'rb_admin',
            'passWord': '123456'
        })
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get('code'), 0)
        self.assertIn('token', body.get('data', {}))

    def test_exam_flow(self):
        teacher = models.Users.objects.create(
            id='RB_T_001',
            userName='rb_teacher',
            passWord=make_password('123456'),
            name='Regression Teacher',
            type=1,
            gender='男',
            age=35,
            createTime=DateUtil.getNowDateTime()
        )
        login = self.client.post('/api/login/', {
            'userName': 'rb_teacher',
            'passWord': '123456'
        }).json()
        token = login['data']['token']

        response = self.client.get('/api/exams/page/', {
            'token': token,
            'pageIndex': 1,
            'pageSize': 10
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('code'), 0)

    def test_practice_flow(self):
        models.Users.objects.create(
            id='RB_S_001',
            userName='rb_student',
            passWord=make_password('123456'),
            name='Regression Student',
            type=2,
            gender='女',
            age=20,
            createTime=DateUtil.getNowDateTime()
        )
        login = self.client.post('/api/login/', {
            'userName': 'rb_student',
            'passWord': '123456'
        }).json()
        token = login['data']['token']

        response = self.client.get('/api/practicepapers/page/', {
            'token': token,
            'pageIndex': 1,
            'pageSize': 10
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('code'), 0)

    def test_ai_scoring_flow(self):
        models.Users.objects.create(
            id='RB_AI_001',
            userName='rb_ai_teacher',
            passWord=make_password('123456'),
            name='Regression AI Teacher',
            type=1,
            gender='男',
            age=32,
            createTime=DateUtil.getNowDateTime()
        )
        login = self.client.post('/api/login/', {
            'userName': 'rb_ai_teacher',
            'passWord': '123456'
        }).json()
        token = login['data']['token']

        response = self.client.post('/api/ai/score/', {
            'token': token,
            'questionType': 0,
            'questionContent': 'Python是什么？',
            'studentAnswer': '一种编程语言',
            'rightAnswer': '高级编程语言'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.json())
