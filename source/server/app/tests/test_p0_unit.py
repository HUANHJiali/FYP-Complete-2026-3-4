"""
P0问题修复验证 - 单元测试版本

直接测试视图函数逻辑，不通过HTTP请求
"""

from django.test import TestCase
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 修复Windows控制台编码问题
try:
    from app.utils.encoding_fix import fix_console_encoding
    fix_console_encoding()
except ImportError:
    pass

from app import models
from app.views.user_views import StudentsView
from app.views.task_views import TasksView
from comm.CommUtils import DateUtil
from django.contrib.auth.hashers import make_password
from django.test import RequestFactory
from unittest.mock import MagicMock


class TestStudentManagementUnit(TestCase):
    """学生管理单元测试"""

    def setUp(self):
        """设置测试数据"""
        # 创建学院和班级
        self.college1 = models.Colleges.objects.create(
            name='计算��学院',
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
            name='计算机2021-2���',
            createTime=DateUtil.getNowDateTime()
        )

        # 创建学生用户和学生信息
        self.user1 = models.Users.objects.create(
            id='2021001',
            userName='student001',
            name='张三',
            passWord=make_password('123456'),
            type=2,
            gender='男',
            age=20
        )

        self.student1 = models.Students.objects.create(
            user=self.user1,
            grade=self.grade1,
            college=self.college1
        )

        self.factory = RequestFactory()

    def test_student_update_safe(self):
        """测试学生更新安全性"""
        print("\n[测试] 学生更新安全性 - 验证异常处理")

        # 测试1: 正常更新
        request = self.factory.post('/students/upd/', {
            'id': self.user1.id,
            'gradeId': str(self.grade2.id),
            'collegeId': str(self.college2.id)
        })
        response = StudentsView.upd_info(request)
        
        # Django HttpResponse需要使用json.loads()而不是.json()
        import json
        data = json.loads(response.content)

        self.assertIn(data['msg'], ['success', '处理成功'])
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.grade.id, self.grade2.id)
        print("  [OK] 正常更新成功")

        # 测试2: gradeId不存在
        request = self.factory.post('/students/upd/', {
            'id': self.user1.id,
            'gradeId': '99999',
            'collegeId': str(self.college1.id)
        })
        response = StudentsView.upd_info(request)
        data = json.loads(response.content)

        self.assertEqual(data['msg'], '指定的班级不存在')
        print("  [OK] gradeId不存在时返回友好提示")

        # 测试3: collegeId不存在
        request = self.factory.post('/students/upd/', {
            'id': self.user1.id,
            'gradeId': str(self.grade1.id),
            'collegeId': '99999'
        })
        response = StudentsView.upd_info(request)
        data = json.loads(response.content)

        self.assertEqual(data['msg'], '指定的学院不存在')
        print("  [OK] collegeId不存在时返回友好提示")

        print("[OK] 学生更新安全性测试通过")

    def test_student_get_info_none_check(self):
        """测试学生信息查询None检查"""
        print("\n[测试] 学生信息查询None检查")

        # 测试1: 查询存在的学生
        request = self.factory.get(f'/students/get_info?id={self.user1.id}')
        response = StudentsView.get_info(request)
        
        import json
        data = json.loads(response.content)

        self.assertIn(data['msg'], ['success', '处理成功'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['id'], self.user1.id)
        print("  [OK] 查询存在的学生成功")

        # 测试2: 查询不存在的学生
        request = self.factory.get('/students/get_info?id=999999')
        response = StudentsView.get_info(request)
        data = json.loads(response.content)

        self.assertEqual(data['msg'], '学生不存在')
        print("  [OK] 查询不存在的学生返回友好提示")

        print("[OK] 学生信息查询None检查测试通过")


class TestTaskManagementUnit(TestCase):
    """任务管理单元测试"""

    def setUp(self):
        """设置测试数据"""
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
            phone='13800138000',
            record='博士',
            job='副教授'
        )

        # 创建题目
        self.question1 = models.Practises.objects.create(
            name='Python基础题1',
            answer='A',
            type=0,
            project=self.project,
            createTime=DateUtil.getNowDateTime()
        )

        self.factory = RequestFactory()

    def test_task_create(self):
        """测试任务创建"""
        print("\n[测试] 任务创建功能")

        # 测试1: 创建任务（不包含题目）
        request = self.factory.post('/tasks/add_info/', {
            'title': 'Python练习任务',
            'description': '完成Python基础练习',
            'type': 'practice',
            'deadline': '2025-12-31 23:59:59',
            'score': '100',
            'projectId': str(self.project.id),
            'gradeId': str(self.grade.id),
            'teacherId': str(self.teacher_user.id)
        })

        response = TasksView.add_info(request)
        data = json.loads(response.content)

        self.assertIn(data['msg'], ['success', '处理成功'])
        self.assertIn('data', data)
        self.assertIn('id', data['data'])
        task_id = data['data']['id']
        print("  [OK] 创建任务成功")

        # 验证任务已创建
        task = models.Tasks.objects.get(id=task_id)
        self.assertEqual(task.title, 'Python练习任务')
        self.assertEqual(task.score, 100)
        print("  [OK] 任务数据验证成功")

        # 测试2: 缺少必填参数
        request = self.factory.post('/tasks/add_info/', {
            'title': '不完整的任务'
        })
        response = TasksView.add_info(request)
        data = json.loads(response.content)

        self.assertIn('缺少必填参数', data['msg'])
        print("  [OK] 缺少必填参数时返回错误")

        print("[OK] 任务创建测试通过")

    def test_task_update(self):
        """测试任务更新"""
        print("\n[测试] 任务更新功能")

        # 先创建一个任务
        task = models.Tasks.objects.create(
            title='原始任务',
            description='原始描述',
            type='practice',
            deadline='2025-06-30 23:59:59',
            score=50,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher_user,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )

        # 测试1: 更新标题
        request = self.factory.post('/tasks/upd_info/', {
            'id': str(task.id),
            'title': '更新后的任务'
        })
        response = TasksView.upd_info(request)
        data = json.loads(response.content)

        self.assertIn(data['msg'], ['success', '处理成功'])
        task.refresh_from_db()
        self.assertEqual(task.title, '更新后的任务')
        print("  [OK] 更新标题成功")

        # 测试2: 更新多个字段
        request = self.factory.post('/tasks/upd_info/', {
            'id': str(task.id),
            'title': '最终任务',
            'description': '最终描述',
            'score': '150'
        })
        response = TasksView.upd_info(request)

        task.refresh_from_db()
        self.assertEqual(task.title, '最终任务')
        self.assertEqual(task.description, '最终描述')
        self.assertEqual(task.score, 150)
        print("  [OK] 更新多个字段成功")

        print("[OK] 任务更新测试通过")

    def test_task_delete(self):
        """测试任务删除"""
        print("\n[测试] 任务删除功能")

        # 创建任务
        task = models.Tasks.objects.create(
            title='待删除任务',
            description='测试',
            type='practice',
            deadline='2025-12-31 23:59:59',
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher_user,
            createTime=DateUtil.getNowDateTime()
        )

        # 测试1: 删除任务
        request = self.factory.post('/tasks/del_info/', {
            'ids': f'[{task.id}]'
        })
        response = TasksView.del_info(request)
        data = json.loads(response.content)

        self.assertIn('成功删除', data['msg'])
        self.assertFalse(models.Tasks.objects.filter(id=task.id).exists())
        print("  [OK] 删除任务成功")

        # 创建另一个任务和学生
        task2 = models.Tasks.objects.create(
            title='待删除任务2',
            description='测试',
            type='practice',
            deadline='2025-12-31 23:59:59',
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher_user,
            createTime=DateUtil.getNowDateTime()
        )

        student_user = models.Users.objects.create(
            id='S001',
            userName='student001',
            name='测试学生',
            passWord=make_password('123456'),
            type=2,
            gender='男',
            age=20
        )
        student = models.Students.objects.create(
            user=student_user,
            grade=self.grade,
            college=self.college
        )

        # 创建进行中的任务日志
        task_log = models.StudentTaskLogs.objects.create(
            student=student_user,  # 使用Users对象而不是Students对象
            task=task2,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        # 测试2: 有学生正在进行任务时不能删除
        request = self.factory.post('/tasks/del_info/', {
            'ids': f'[{task2.id}]'
        })
        response = TasksView.del_info(request)
        data = json.loads(response.content)

        self.assertEqual(data['msg'], '有学生正在进行任务，无法删除')
        self.assertTrue(models.Tasks.objects.filter(id=task2.id).exists())
        print("  [OK] 有学生进行中时阻止删除")

        # 完成任务
        task_log.status = 'completed'
        task_log.save()

        # 测试3: 任务完成后可以删除
        request = self.factory.post('/tasks/del_info/', {
            'ids': f'[{task2.id}]'
        })
        response = TasksView.del_info(request)

        self.assertFalse(models.Tasks.objects.filter(id=task2.id).exists())
        print("  [OK] 任务完成后可以删除")

        print("[OK] 任务删除测试通过")


def print_summary():
    """打印测试总结"""
    print("\n" + "="*60)
    print("P0问题修复验证 - 单元测试版")
    print("="*60)
    print("\n测试覆盖:")
    print("  [OK] 学生管理安全修复（2个测试）")
    print("  [OK] 任务管理CRUD功能（3个测试）")
    print("\n总计: 5个测试用例")
    print("测试方式: 直接调用视图函数（单元测试）")
    print("="*60 + "\n")


if __name__ == '__main__':
    print_summary()
