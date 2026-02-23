"""
初始化生产环境数据
Django management command: python manage.py init_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app import models


class Command(BaseCommand):
    help = '初始化生产环境所需的基础数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化生产数据...')

        # 创建学院
        colleges_data = [
            {'id': 1, 'name': '软件工程'}
        ]
        for data in colleges_data:
            obj, created = models.Colleges.objects.get_or_create(
                id=data['id'],
                defaults=data
            )
            if created:
                self.stdout.write(f'创建学院: {data["name"]}')

        # 创建年级
        grades_data = [
            {'id': 1, 'name': '一年级一班'},
            {'id': 2, 'name': '一年级二班'},
            {'id': 3, 'name': '二年级一班'},
            {'id': 4, 'name': '二年级二班'},
        ]
        for data in grades_data:
            obj, created = models.Grades.objects.get_or_create(
                id=data['id'],
                defaults={'name': data['name']}
            )
            if created:
                self.stdout.write(f'创建年级: {data["name"]}')

        # 创建项目
        project_data = {
            'id': 1,
            'name': 'Python全栈开发'
        }
        project, created = models.Projects.objects.get_or_create(
            id=project_data['id'],
            defaults=project_data
        )
        if created:
            self.stdout.write(f'创建项目: {project_data["name"]}')

        # 创建管理员账户
        admin_data = {
            'id': 'ADMIN001',
            'userName': 'admin',
            'passWord': make_password('123456'),
            'name': '管理员',
            'gender': '男',
            'age': 30,
            'type': 0,
            'email': 'admin@example.com'
        }
        admin, created = models.Users.objects.get_or_create(
            id=admin_data['id'],
            defaults=admin_data
        )
        if created:
            self.stdout.write('创建管理员账户: admin/123456')

        # 创建教师账户
        teacher_data = {
            'id': 'TEACHER001',
            'userName': 'teacher',
            'passWord': make_password('123456'),
            'name': '教师账户',
            'gender': '女',
            'age': 35,
            'type': 1,
            'email': 'teacher@example.com'
        }
        teacher, created = models.Users.objects.get_or_create(
            id=teacher_data['id'],
            defaults=teacher_data
        )
        if created:
            models.Teachers.objects.get_or_create(
                user_id=teacher_data['id'],
                defaults={'college_id': 1, 'title': '讲师'}
            )
            self.stdout.write('创建教师账户: teacher/123456')

        # 创建学生账户
        student_data = {
            'id': 'STUDENT001',
            'userName': 'student',
            'passWord': make_password('123456'),
            'name': '学生账户',
            'gender': '男',
            'age': 20,
            'type': 2,
        }
        student, created = models.Users.objects.get_or_create(
            id=student_data['id'],
            defaults=student_data
        )
        if created:
            models.Students.objects.get_or_create(
                user_id=student_data['id'],
                defaults={'grade_id': 1, 'college_id': 1}
            )
            self.stdout.write('创建学生账户: student/123456')

        # 创建演示考试 (Exams模型使用name字段)
        from django.utils import timezone
        from datetime import datetime
        
        exam_name = '期中测试考试'
        exam_defaults = {
            'name': exam_name,
            'examTime': 60,
            'grade_id': 3,
            'project_id': 1,
            'teacher_id': 'TEACHER001',
            'startTime': datetime(2026, 1, 1, 10, 0, 0),
            'endTime': datetime(2026, 12, 31, 18, 0, 0),
        }
        
        exam, created = models.Exams.objects.get_or_create(
            name=exam_name,
            defaults=exam_defaults
        )
        if created:
            self.stdout.write(f'创建演示考试: {exam_name}')

        # 创建演示题目
        if created:
            practise = models.Practises.objects.create(
                name='Python基础题目',
                type=0,
                difficulty=1
            )
            models.Options.objects.create(
                practise=practise,
                title='Python是什么类型的语言？',
                optionA='编译型',
                optionB='解释型',
                optionC='汇编型',
                optionD='机器型',
                answer='B',
                scores=10
            )
            exam.questions.add(practise)
            self.stdout.write('创建演示题目')

        self.stdout.write(self.style.SUCCESS('生产数据初始化完成！'))
