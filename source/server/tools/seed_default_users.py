import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from app import models


def run():
    college, _ = models.Colleges.objects.get_or_create(
        id=1,
        defaults={'name': '默认学院', 'createTime': '2026-01-01 00:00:00'}
    )
    grade, _ = models.Grades.objects.get_or_create(
        id=1,
        defaults={'name': '默认班级', 'createTime': '2026-01-01 00:00:00'}
    )

    admin, _ = models.Users.objects.get_or_create(
        id='ADMIN001',
        defaults={
            'userName': 'admin',
            'passWord': make_password('123456'),
            'name': '系统管理员',
            'gender': '男',
            'age': 30,
            'type': 0,
            'email': 'admin@example.com',
            'status': 0,
        }
    )
    teacher, _ = models.Users.objects.get_or_create(
        id='TEACHER001',
        defaults={
            'userName': 'teacher',
            'passWord': make_password('123456'),
            'name': '教师账户',
            'gender': '男',
            'age': 32,
            'type': 1,
            'email': 'teacher@example.com',
            'status': 0,
        }
    )
    student, _ = models.Users.objects.get_or_create(
        id='STUDENT001',
        defaults={
            'userName': 'student',
            'passWord': make_password('123456'),
            'name': '学生账户',
            'gender': '男',
            'age': 18,
            'type': 2,
            'email': 'student@example.com',
            'status': 0,
        }
    )

    models.Teachers.objects.get_or_create(
        user=teacher,
        defaults={'phone': '13800000000', 'record': '本科', 'job': '讲师'}
    )
    models.Students.objects.get_or_create(
        user=student,
        defaults={'grade': grade, 'college': college}
    )

    print('默认账号已就绪：admin/teacher/student')


if __name__ == '__main__':
    run()
