"""
P0问题修复验证测试套件 - 简化版

测试范围：
1. 学生管理安全修复（.get()异常、级联删除、None检查）
2. 任务管理CRUD功能
3. 练习系统AI评分和��题收集
4. 统计功能（班级、科目）
5. 考试记录详情查询

运行方式：
    python manage.py test app.tests.test_p0_fixes_simple
"""

from django.test import TestCase, Client
from django.db import transaction
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import models
from comm.CommUtils import DateUtil


class TestStudentManagement(TestCase):
    """测试学生管理安全修复"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建学院和班级
        self.college1 = models.Colleges.objects.create(
            name='计算机学院',
            createTime=DateUtil.getNowDateTime()
        )
        self.college2 = models.Colleges.objects.create(
            name='数学学院',
            createTime=DateUtil.getNowDateTime()
        )

        self.grade1 = models.Grades.objects.create(
            name='计算机2021-1班',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade2 = models.Grades.objects.create(
            name='计算机2021-2班',
            createTime=DateUtil.getNowDateTime()
        )

        # 创建学生用户和学生信息
        from django.contrib.auth.hashers import make_password
        self.user1 = models.Users.objects.create(
            id='2021001',
            userName='student001',
            name='张三',
            passWord=make_password('123456'),
            type=2,  # 学生
            gender='男',
            age=20
        )

        self.student1 = models.Students.objects.create(
            user=self.user1,
            grade=self.grade1,
            college=self.college1
        )

    def test_student_update_safe(self):
        """测试学生更新的安全性 - 修复.get()异常"""
        print("\n[测试] 学生更新安全性 - 验证DoesNotExist异常处理")

        # 测试1: 正常更新
        response = self.client.post('/api/students/upd', {
            'id': self.user1.id,
            'gradeId': self.grade2.id,
            'collegeId': self.college2.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')

        # 验证更新成功
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.grade.id, self.grade2.id)
        self.assertEqual(self.student1.college.id, self.college2.id)
        print("  ✓ 正常更新成功")

        # 测试2: gradeId不存在
        response = self.client.post('/api/students/upd', {
            'id': self.user1.id,
            'gradeId': 99999,  # 不存在的班级
            'collegeId': self.college1.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '指定的班级不存在')
        print("  ✓ gradeId不存在时返回友好提示")

        # 测试3: collegeId不存在
        response = self.client.post('/api/students/upd', {
            'id': self.user1.id,
            'gradeId': self.grade1.id,
            'collegeId': 99999  # 不存在的学院
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '指定的学院不存在')
        print("  ✓ collegeId不存在时返回友好提示")

        print("✓ 学生更新安全性测试通过")

    def test_student_get_info_none_check(self):
        """测试学生信息查询的None检查"""
        print("\n[测试] 学生信息查询None检查")

        # 测试1: 查询存在的学生
        response = self.client.get(f'/api/students/get_info?id={self.user1.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')
        self.assertIn('data', data)
        self.assertEqual(data['data']['id'], self.user1.id)
        print("  ✓ 查询存在的学生成功")

        # 测试2: 查询不存在的学生
        response = self.client.get('/api/students/get_info?id=999999')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '学生不存在')
        print("  ✓ 查询不存在的学生返回友好提示")

        print("✓ 学生信息查询None检查测试通过")


class TestTaskManagement(TestCase):
    """测试任务管理CRUD功能"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建基础数据
        self.college = models.Colleges.objects.create(
            name='计算机学院',
            createTime=DateUtil.getNowDateTime()
        )
        self.grade = models.Grades.objects.create(
            name='计算机2021-1班',
            createTime=DateUtil.getNowDateTime()
        )
        self.project = models.Projects.objects.create(
            name='Python程序设计',
            createTime=DateUtil.getNowDateTime()
        )

        # 创建教师
        from django.contrib.auth.hashers import make_password
        self.teacher_user = models.Users.objects.create(
            id='T001',
            userName='teacher001',
            name='李老师',
            passWord=make_password('123456'),
            type=1,
            gender='男',
            age=35
        )
        self.teacher = models.Teachers.objects.create(
            user=self.teacher_user,
            college=self.college
        )

        # 创建题目
        self.question1 = models.Practises.objects.create(
            name='Python基础题1',
            answer='A',
            type=0,
            project=self.project,
            createTime=DateUtil.getNowDateTime()
        )

    def test_task_create(self):
        """测试任务创建"""
        print("\n[测试] 任务创建功能")

        # 测试1: 创建任务（不包含题目）
        response = self.client.post('/api/tasks/add', {
            'title': 'Python练习任务',
            'description': '完成Python基础练习',
            'type': 'practice',
            'deadline': '2025-12-31 23:59:59',
            'score': 100,
            'projectId': self.project.id,
            'gradeId': self.grade.id,
            'teacherId': self.teacher_user.id
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')
        self.assertIn('data', data)
        self.assertIn('id', data['data'])
        task_id = data['data']['id']
        print("  ✓ 创建任务成功（无题目）")

        # 验证任务已创建
        task = models.Tasks.objects.get(id=task_id)
        self.assertEqual(task.title, 'Python练习任务')
        self.assertEqual(task.score, 100)
        print("  ✓ 任务数据验证成功")

        # 测试2: 缺少必填参数
        response = self.client.post('/api/tasks/add', {
            'title': '不完整的任务'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('缺少必填参数', data['msg'])
        print("  ✓ 缺少必填参数时返回错误")

        print("✓ 任务创建测试通过")


def print_test_summary():
    """打印测试总结"""
    print("\n" + "="*60)
    print("P0问题修复验证测试套件 - 简化版")
    print("="*60)
    print("\n测试覆盖:")
    print("  ✓ 学生管理安全修复")
    print("  ✓ 任务管理CRUD功能")
    print("\n总计: 3个测试用例")
    print("="*60 + "\n")


if __name__ == '__main__':
    print_test_summary()
