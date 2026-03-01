from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.test import Client, TestCase

from app import models
from comm.CommUtils import DateUtil


class LifecycleStatusFieldsTest(TestCase):
    """P0-1 统一生命周期字段回归测试"""

    def setUp(self):
        self.client = Client()

        self.project = models.Projects.objects.create(
            name='生命周期学科',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade = models.Grades.objects.create(
            name='生命周期班级',
            createTime=DateUtil.getNowDateTime()
        )
        self.college = models.Colleges.objects.create(
            name='生命周期学院',
            createTime=DateUtil.getNowDateTime()
        )

        self.teacher = models.Users.objects.create(
            id='LFS_T_001',
            userName='lfs_teacher',
            passWord=make_password('123456'),
            name='生命周期教师',
            type=1,
            gender='女',
            age=30,
            createTime=DateUtil.getNowDateTime()
        )
        self.student = models.Users.objects.create(
            id='LFS_S_001',
            userName='lfs_student',
            passWord=make_password('123456'),
            name='生命周期学生',
            type=2,
            gender='男',
            age=18,
            createTime=DateUtil.getNowDateTime()
        )

        models.Students.objects.create(
            user=self.student,
            grade=self.grade,
            college=self.college
        )

        self.token = 'token_lifecycle_student'
        cache.set(self.token, self.student.id, 3600)

        self.practice_question = models.Practises.objects.create(
            name='生命周期题目',
            answer='A',
            analyse='测试',
            type=0,
            createTime=DateUtil.getNowDateTime(),
            project=self.project
        )

    def test_exams_page_returns_lifecycle_status(self):
        future_time = (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        past_time = (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')

        models.Exams.objects.create(
            name='未开始考试',
            teacher=self.teacher,
            project=self.project,
            grade=self.grade,
            createTime=DateUtil.getNowDateTime(),
            examTime=future_time
        )
        finished_exam = models.Exams.objects.create(
            name='已结束考试',
            teacher=self.teacher,
            project=self.project,
            grade=self.grade,
            createTime=DateUtil.getNowDateTime(),
            examTime=past_time
        )

        models.ExamLogs.objects.create(
            student=self.student,
            exam=finished_exam,
            status=2,
            score=88,
            createTime=DateUtil.getNowDateTime()
        )

        resp = self.client.get('/api/exams/page/', {
            'pageIndex': 1,
            'pageSize': 10,
            'token': self.token
        })
        body = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body.get('code'), 0)

        rows = body.get('data', {}).get('data', [])
        status_map = {row.get('name'): row.get('lifecycleStatus') for row in rows}

        self.assertEqual(status_map.get('未开始考试'), 'not_started')
        self.assertEqual(status_map.get('已结束考试'), 'completed')

    def test_student_practice_and_task_return_lifecycle_status(self):
        practice_paper = models.PracticePapers.objects.create(
            title='生命周期练习',
            description='测试生命周期字段',
            type='fixed',
            difficulty='easy',
            duration=30,
            totalScore=100,
            project=self.project,
            teacher=self.teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )
        models.StudentPracticeLogs.objects.create(
            student=self.student,
            paper=practice_paper,
            startTime=DateUtil.getNowDateTime(),
            endTime=DateUtil.getNowDateTime(),
            status='completed',
            score=95,
            accuracy=95,
            usedTime=20
        )

        overdue_deadline = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        in_progress_deadline = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        overdue_task = models.Tasks.objects.create(
            title='逾期任务',
            description='测试逾期',
            type='practice',
            deadline=overdue_deadline,
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )
        in_progress_task = models.Tasks.objects.create(
            title='进行中任务',
            description='测试进行中',
            type='practice',
            deadline=in_progress_deadline,
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )
        models.StudentTaskLogs.objects.create(
            student=self.student,
            task=in_progress_task,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        practice_resp = self.client.get('/api/practicepapers/student/', {
            'token': self.token
        })
        practice_body = practice_resp.json()
        self.assertEqual(practice_body.get('code'), 0)
        practice_rows = practice_body.get('data', [])
        self.assertEqual(practice_rows[0].get('lifecycleStatus'), 'completed')

        task_resp = self.client.get('/api/tasks/student/', {
            'token': self.token
        })
        task_body = task_resp.json()
        self.assertEqual(task_body.get('code'), 0)

        task_rows = task_body.get('data', [])
        task_status_map = {row.get('title'): row.get('lifecycleStatus') for row in task_rows}
        self.assertEqual(task_status_map.get(overdue_task.title), 'overdue')
        self.assertEqual(task_status_map.get(in_progress_task.title), 'in_progress')
