from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class TaskSubmissionRulesTest(TestCase):
    """任务一次性提交与截止时间规则回归测试"""

    def setUp(self):
        self.client = Client()

        self.project = models.Projects.objects.create(
            name='数学',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade = models.Grades.objects.create(
            name='高一(1)班',
            createTime=DateUtil.getNowDateTime()
        )

        self.teacher = models.Users.objects.create(
            id='TSR_T_001',
            userName='tsr_teacher',
            passWord=make_password('123456'),
            name='任务教师',
            type=1,
            gender='女',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )

        self.student = models.Users.objects.create(
            id='TSR_S_001',
            userName='tsr_student',
            passWord=make_password('123456'),
            name='任务学生',
            type=2,
            gender='男',
            age=18,
            createTime=DateUtil.getNowDateTime()
        )

        self.student_token = 'token_task_rules_student'
        cache.set(self.student_token, self.student.id, 3600)

        self.choice_question = models.Practises.objects.create(
            name='1+1=？',
            answer='A',
            analyse='基础加法',
            type=0,
            createTime=DateUtil.getNowDateTime(),
            project=self.project
        )

    def _create_task_and_log(self, deadline):
        task = models.Tasks.objects.create(
            title='规则测试任务',
            description='测试任务提交规则',
            type='practice',
            deadline=deadline,
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )

        log = models.StudentTaskLogs.objects.create(
            student=self.student,
            task=task,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        models.StudentTaskAnswers.objects.create(
            taskLog=log,
            practise=self.choice_question,
            studentAnswer='A',
            answerTime=DateUtil.getNowDateTime()
        )

        return task, log

    def test_submit_task_first_time_allowed(self):
        future_deadline = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        _, log = self._create_task_and_log(future_deadline)

        resp = self.client.post('/api/tasks/submit/', {
            'token': self.student_token,
            'logId': log.id
        })
        body = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body.get('code'), 0)
        log.refresh_from_db()
        self.assertEqual(log.status, 'completed')

    def test_submit_task_repeat_denied(self):
        future_deadline = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        _, log = self._create_task_and_log(future_deadline)

        first_resp = self.client.post('/api/tasks/submit/', {
            'token': self.student_token,
            'logId': log.id
        })
        self.assertEqual(first_resp.json().get('code'), 0)

        second_resp = self.client.post('/api/tasks/submit/', {
            'token': self.student_token,
            'logId': log.id
        })
        second_body = second_resp.json()

        self.assertNotEqual(second_body.get('code'), 0)
        self.assertIn('不能重复提交', second_body.get('msg', ''))

    def test_submit_task_after_deadline_denied(self):
        past_deadline = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        _, log = self._create_task_and_log(past_deadline)

        resp = self.client.post('/api/tasks/submit/', {
            'token': self.student_token,
            'logId': log.id
        })
        body = resp.json()

        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('任务已截止', body.get('msg', ''))

    def test_start_task_after_deadline_denied(self):
        past_deadline = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        task = models.Tasks.objects.create(
            title='逾期开始测试',
            description='测试逾期不可开始',
            type='practice',
            deadline=past_deadline,
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )

        resp = self.client.post('/api/tasks/start/', {
            'token': self.student_token,
            'taskId': task.id
        })
        body = resp.json()

        self.assertNotEqual(body.get('code'), 0)
        self.assertIn('任务已截止', body.get('msg', ''))
