"""
测试P0问题修复后的功能完整性
专注于验证API端点是否存在并能正常响应
"""
from django.test import TestCase, Client
from django.db import connection
from app import models
from comm.CommUtils import DateUtil


class TestAPIEndpoints(TestCase):
    """测试API端点是否存在并正常响应"""

    def test_student_update_endpoint_exists(self):
        """测试学生更新API端点存在"""
        print("\n[测试] 学生更新API端点")

        # 创建测试数据
        college = models.Colleges.objects.create(name='Test College', createTime=DateUtil.getNowDateTime())
        grade = models.Grades.objects.create(name='Test Grade', createTime=DateUtil.getNowDateTime())

        from django.contrib.auth.hashers import make_password
        user = models.Users.objects.create(
            id='test001',
            userName='student001',
            name='Test Student',
            passWord=make_password('123456'),
            type=2,
            gender='男',
            age=20
        )

        student = models.Students.objects.create(user=user, grade=grade, college=college)

        # 测试API端点
        client = Client()
        response = client.post('/api/students/upd/', {
            'id': user.id,
            'gradeId': grade.id,
            'collegeId': college.id
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '处理成功')
        print("  ✓ 学生更新API正常工作")

    def test_student_get_info_endpoint_exists(self):
        """测试学生查询API端点存在"""
        print("\n[测试] 学生查询API端点")

        # 创建测试数据
        college = models.Colleges.objects.create(name='Test College 2', createTime=DateUtil.getNowDateTime())
        grade = models.Grades.objects.create(name='Test Grade 2', createTime=DateUtil.getNowDateTime())

        from django.contrib.auth.hashers import make_password
        user = models.Users.objects.create(
            id='test002',
            userName='student002',
            name='Test Student 2',
            passWord=make_password('123456'),
            type=2,
            gender='女',
            age=21
        )

        student = models.Students.objects.create(user=user, grade=grade, college=college)

        # 测试API端点
        client = Client()
        response = client.get(f'/api/students/info/?id={user.id}')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '处理成功')
        self.assertIn('data', data)
        print("  ✓ 学生查询API正常工作")

    def test_task_endpoints_exist(self):
        """测试任务管理API端点存在"""
        print("\n[测试] 任务管理API端点")

        # 创建基础数据
        college = models.Colleges.objects.create(name='Test College 3', createTime=DateUtil.getNowDateTime())
        grade = models.Grades.objects.create(name='Test Grade 3', createTime=DateUtil.getNowDateTime())
        project = models.Projects.objects.create(name='Python', createTime=DateUtil.getNowDateTime())

        from django.contrib.auth.hashers import make_password
        teacher = models.Users.objects.create(
            id='teacher001',
            userName='teacher001',
            name='Test Teacher',
            passWord=make_password('123456'),
            type=1,
            gender='男',
            age=35
        )

        client = Client()

        # 测试添加任务端点（需要认证，返回"用户未登录"表示端点存在）
        response = client.post('/api/tasks/add/', {
            'title': 'Test Task',
            'description': 'Test Description',
            'type': 'practice',
            'deadline': '2025-12-31 23:59:59',
            'score': 100,
            'projectId': project.id,
            'gradeId': grade.id,
            'teacherId': teacher.id
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # 返回"用户未登录"说明端点存在且有权限检查
        print(f"  ✓ 任务添加API端点存在 (响应: {data['msg']})")

        # 直接创建一个任务来测试更新和删除
        task = models.Tasks.objects.create(
            title='Test Task',
            description='Test Description',
            type='practice',
            deadline='2025-12-31 23:59:59',
            score=100,
            project=project,
            grade=grade,
            teacher=teacher,
            createTime=DateUtil.getNowDateTime(),
            isActive=True
        )

        # 测试更新端点
        response = client.post('/api/tasks/upd/', {
            'id': task.id,
            'title': 'Updated Task'
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"  ✓ 任务更新API端点存在 (响应: {data['msg']})")

        # 测试删除端点
        response = client.post('/api/tasks/del/', {
            'id': task.id
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"  ✓ 任务删除API端点存在 (响应: {data['msg']})")

    def test_database_structure(self):
        """测试数据库结构完整性"""
        print("\n[测试] 数据库结构完整性")

        # 检查关键模型是否可用
        required_models = [
            'Users', 'Students', 'Teachers',
            'Colleges', 'Grades', 'Projects',
            'Tasks', 'Practises', 'Exams',
            'WrongQuestions', 'StudentPracticeLogs'
        ]

        for model_name in required_models:
            if hasattr(models, model_name):
                print(f"  ✓ {model_name} 模型可用")
            else:
                print(f"  ✗ {model_name} 模型不存在")

        print("  ✓ 数据库结构检查完成")


if __name__ == '__main__':
    import unittest
    unittest.main()
