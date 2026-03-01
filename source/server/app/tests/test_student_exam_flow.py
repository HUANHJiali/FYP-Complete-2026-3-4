from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class StudentExamFlowTest(TestCase):
    """学生考试链路回归：学生可调用 exams/make 生成试卷"""

    def setUp(self):
        self.client = Client()

        self.project = models.Projects.objects.create(
            name='学生考试链路学科',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade = models.Grades.objects.create(
            name='学生考试链路班级',
            createTime=DateUtil.getNowDateTime()
        )

        self.teacher = models.Users.objects.create(
            id='SEF_TEA_001',
            userName='sef_teacher',
            passWord=make_password('123456'),
            name='SEF Teacher',
            type=1,
            gender='男',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        models.Teachers.objects.create(
            user=self.teacher,
            phone='13800000001',
            record='本科',
            job='讲师'
        )

        self.student = models.Users.objects.create(
            id='SEF_STU_001',
            userName='sef_student',
            passWord=make_password('123456'),
            name='SEF Student',
            type=2,
            gender='男',
            age=18,
            createTime=DateUtil.getNowDateTime()
        )
        college = models.Colleges.objects.create(name='SEF学院', createTime=DateUtil.getNowDateTime())
        models.Students.objects.create(user=self.student, grade=self.grade, college=college)

        # 为 make 生成试卷准备最小题库（选择10 / 填空10 / 判断10 / 编程2）
        for i in range(10):
            q = models.Practises.objects.create(
                name=f'选择题{i}',
                answer='A',
                analyse='解析',
                type=0,
                createTime=DateUtil.getNowDateTime(),
                project=self.project
            )
            models.Options.objects.create(name='A', practise=q)
            models.Options.objects.create(name='B', practise=q)
        for i in range(10):
            models.Practises.objects.create(
                name=f'填空题{i}',
                answer='答案',
                analyse='解析',
                type=1,
                createTime=DateUtil.getNowDateTime(),
                project=self.project
            )
        for i in range(10):
            models.Practises.objects.create(
                name=f'判断题{i}',
                answer='true',
                analyse='解析',
                type=2,
                createTime=DateUtil.getNowDateTime(),
                project=self.project
            )
        for i in range(2):
            models.Practises.objects.create(
                name=f'编程题{i}',
                answer='print(1)',
                analyse='解析',
                type=3,
                createTime=DateUtil.getNowDateTime(),
                project=self.project
            )

        login_resp = self.client.post('/api/login/', {
            'userName': 'sef_student',
            'passWord': '123456'
        }).json()
        self.token = login_resp['data']['token']

    def test_student_can_call_make_exam_paper(self):
        resp = self.client.post('/api/exams/make/', {
            'token': self.token,
            'projectId': self.project.id
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get('code'), 0)
        self.assertIn('item_0', body.get('data', {}))
