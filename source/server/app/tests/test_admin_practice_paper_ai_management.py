from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class AdminPracticePaperAIManagementTest(TestCase):
    """管理员AI练习试卷生成回归：缺参校验（不依赖外部AI）"""

    def setUp(self):
        self.client = Client()
        models.Users.objects.create(
            id='APAI_ADMIN_001',
            userName='apai_admin',
            passWord=make_password('123456'),
            name='Admin Practice AI',
            type=0,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        login_resp = self.client.post('/api/login/', {
            'userName': 'apai_admin',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_generate_ai_practice_paper_validate_required_params(self):
        resp = self.client.post('/api/admin/generate_ai_practice_paper/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)

    def test_generate_ai_practice_paper_counts_validate_required_params(self):
        resp = self.client.post('/api/admin/generate_ai_practice_paper_counts/', {
            'token': self.token,
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get('code'), 0)
