"""
Ralph循环新增功能测试用例
测试批量导入学生、进步曲线、雷达图可视化等新功能
"""
import os
import sys
import django
import tempfile
import csv

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from app import models
import json


class BatchImportStudentsTest(TestCase):
    """批量导入学生功能测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        # 创建管理员用户
        self.admin = models.Users.objects.create(
            id='ADMIN001',
            userName='admin',
            passWord=make_password('123456'),
            name='系统管理员',
            type=0,
            gender='男',
            age=30
        )
        # 创建学院和班级
        self.college = models.Colleges.objects.create(
            name='测试学院'
        )
        self.grade = models.Grades.objects.create(
            name='测试班级1班'
        )

    def test_batch_import_students_success(self):
        """测试批量导入学生成功"""
        print("\n[测试] 批量导入学生 - 成功场景")

        # 创建CSV文件
        csv_data = [
            ['学号', '账号', '姓名', '性别', '年龄', '学院ID', '班级ID'],
            ['2021001', 'student001', '张三', '男', '20', str(self.college.id), str(self.grade.id)],
            ['2021002', 'student002', '李四', '女', '19', str(self.college.id), str(self.grade.id)],
            ['2021003', 'student003', '王五', '男', '21', str(self.college.id), str(self.grade.id)],
        ]

        # 写入临时CSV文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            csv_path = f.name

        try:
            # 读取文件并上传
            with open(csv_path, 'rb') as f:
                csv_file = SimpleUploadedFile(
                    name='students.csv',
                    content=f.read(),
                    content_type='text/csv'
                )

            response = self.client.post('/api/students/import/', {
                'file': csv_file
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['code'], 0)
            self.assertIn('created', data['data'])
            self.assertEqual(data['data']['created'], 3)

            # 验证数据库中的学生
            self.assertEqual(models.Students.objects.count(), 3)
            print(f"  ✓ 成功导入3名学生")

        finally:
            # 清理临时文件
            if os.path.exists(csv_path):
                os.remove(csv_path)

    def test_batch_import_students_partial_failure(self):
        """测试批量导入部分失败"""
        print("\n[测试] 批量导入学生 - 部分失败场景")

        # 创建包含错误数据的CSV文件
        csv_data = [
            ['学号', '账号', '姓名', '性别', '年龄', '学院ID', '班级ID'],
            ['2021004', 'student004', '赵六', '男', '20', str(self.college.id), str(self.grade.id)],  # 正常
            ['', 'student005', '钱七', '女', '19', str(self.college.id), str(self.grade.id)],  # 学号为空
            ['2021006', 'student006', '孙八', '男', '21', '999', str(self.grade.id)],  # 学院不存在
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            csv_path = f.name

        try:
            with open(csv_path, 'rb') as f:
                csv_file = SimpleUploadedFile(
                    name='students.csv',
                    content=f.read(),
                    content_type='text/csv'
                )

            response = self.client.post('/api/students/import/', {
                'file': csv_file
            })

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['code'], 0)
            self.assertIn('created', data['data'])
            self.assertIn('failed', data['data'])
            self.assertEqual(data['data']['created'], 1)
            self.assertEqual(data['data']['failed'], 2)
            self.assertIn('errors', data['data'])

            print(f"  ✓ 成功1条，失败2条，错误详情已记录")

        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

    def test_batch_import_invalid_file_format(self):
        """测试无效文件格式"""
        print("\n[测试] 批量导入学生 - 无效文件格式")

        # 创建非CSV文件
        txt_file = SimpleUploadedFile(
            name='students.txt',
            content=b'This is not a CSV file',
            content_type='text/plain'
        )

        response = self.client.post('/api/students/import/', {
            'file': txt_file
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotEqual(data['code'], 0)
        print(f"  ✓ 正确拒绝非CSV文件")

    def test_download_students_template(self):
        """测试下载学生模板"""
        print("\n[测试] 下载学生导入模板")

        response = self.client.get('/api/admin/students_template/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        # 验证CSV内容
        content = response.content.decode('utf-8-sig')
        self.assertIn('学号', content)
        self.assertIn('账号', content)
        self.assertIn('姓名', content)

        print(f"  ✓ 模板下载成功，包含必需字段")


class ProgressChartTest(TestCase):
    """进步曲线功能测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        # 创建学生用户
        self.student = models.Users.objects.create(
            id='STUDENT001',
            userName='student',
            passWord=make_password('123456'),
            name='测试学生',
            type=2,
            gender='男',
            age=20
        )
        # 创建学科
        self.project = models.Projects.objects.create(
            name='Python程序设计'
        )
        # 创建考试
        self.exam1 = models.Exams.objects.create(
            name='期中考试',
            project=self.project,
            startTime='2024-01-01 10:00:00',
            endTime='2024-01-01 12:00:00',
            teacher=self.student
        )
        self.exam2 = models.Exams.objects.create(
            name='期末考试',
            project=self.project,
            startTime='2024-02-01 10:00:00',
            endTime='2024-02-01 12:00:00',
            teacher=self.student
        )
        # 创建考试记录
        models.ExamLogs.objects.create(
            examId=self.exam1,
            studentId=self.student,
            score=75.5,
            status=2  # 已完成
        )
        models.ExamLogs.objects.create(
            examId=self.exam2,
            studentId=self.student,
            score=85.0,
            status=2  # 已完成
        )

    def test_get_progress_data_exams(self):
        """测试获取考试进步数据"""
        print("\n[测试] 获取进步曲线数据 - 考试")

        response = self.client.get('/api/students/progress/', {
            'studentId': self.student.id,
            'type': 'exam',
            'timeRange': 'all'
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        self.assertIn('progressData', data['data'])
        self.assertIn('summary', data['data'])

        progress_data = data['data']['progressData']
        self.assertEqual(len(progress_data), 2)  # 两次考试
        self.assertAlmostEqual(progress_data[0]['score'], 75.5)
        self.assertAlmostEqual(progress_data[1]['score'], 85.0)

        print(f"  ✓ 成功获取进步数据，显示成绩提升")

    def test_get_progress_data_practice(self):
        """测试获取练习进步数据"""
        print("\n[测试] 获取进步曲线数据 - 练习")

        # 创建练习记录
        practice_paper = models.PracticePapers.objects.create(
            name='Python练习1',
            projectId=self.project
        )
        models.StudentPracticeLogs.objects.create(
            practicePaperId=practice_paper,
            studentId=self.student,
            score=80.0,
            status=2
        )

        response = self.client.get('/api/students/progress/', {
            'studentId': self.student.id,
            'type': 'practice',
            'timeRange': 'all'
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)
        self.assertIn('progressData', data['data'])

        print(f"  ✓ 成功获取练习进步数据")


class RadarChartVisualizationTest(TestCase):
    """雷达图可视化功能测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        # 创建学生用户
        self.student = models.Users.objects.create(
            id='STUDENT002',
            userName='student2',
            passWord=make_password('123456'),
            name='测试学生2',
            type=2,
            gender='男',
            age=20
        )
        # 创建多个学科
        self.project1 = models.Projects.objects.create(name='Python程序设计')
        self.project2 = models.Projects.objects.create(name='数据结构')
        self.project3 = models.Projects.objects.create(name='算法分析')
        # 创建考试
        exam1 = models.Exams.objects.create(
            name='Python期末考试',
            project=self.project1,
            startTime='2024-01-01 10:00:00',
            endTime='2024-01-01 12:00:00',
            teacher=self.student
        )
        exam2 = models.Exams.objects.create(
            name='数据结构期中考试',
            project=self.project2,
            startTime='2024-01-02 10:00:00',
            endTime='2024-01-02 12:00:00',
            teacher=self.student
        )
        exam3 = models.Exams.objects.create(
            name='算法分析期末考试',
            project=self.project3,
            startTime='2024-01-03 10:00:00',
            endTime='2024-01-03 12:00:00',
            teacher=self.student
        )
        # 创建考试记录（不同成绩）
        models.ExamLogs.objects.create(
            examId=exam1,
            studentId=self.student,
            score=85.0,
            status=2
        )
        models.ExamLogs.objects.create(
            examId=exam2,
            studentId=self.student,
            score=75.0,
            status=2
        )
        models.ExamLogs.objects.create(
            examId=exam3,
            studentId=self.student,
            score=90.0,
            status=2
        )

    def test_get_radar_chart_data(self):
        """测试获取雷达图数据"""
        print("\n[测试] 获取雷达图可视化数据")

        response = self.client.get('/api/students/radar_data/', {
            'studentId': self.student.id
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)
        self.assertIn('data', data)
        self.assertIn('dimensions', data['data'])
        self.assertIn('values', data['data'])
        self.assertIn('maxValue', data['data'])

        # 验证数据结构
        self.assertEqual(len(data['data']['dimensions']), 3)  # 3个学科
        self.assertEqual(len(data['data']['values']), 3)  # 3个成绩
        self.assertIn('summary', data['data'])

        print(f"  ✓ 成功获取雷达图数据，包含{len(data['data']['dimensions'])}个维度")


class ExtendedQuestionTypesTest(TestCase):
    """扩展题目类型功能测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        # 创建教师用户
        self.teacher = models.Users.objects.create(
            id='TEACHER001',
            userName='teacher',
            passWord=make_password('123456'),
            name='测试教师',
            type=1,
            gender='男',
            age=35
        )
        # 创建学科
        self.project = models.Projects.objects.create(name='Python程序设计')

    def test_create_short_answer_question(self):
        """测试创建简答题（type=3）"""
        print("\n[测试] 创建简答题")

        question = models.Practises.objects.create(
            name='请简述Python中装饰器的作用',
            type=3,  # 简答题
            project=self.project,
            answer='装饰器用于在不修改函数代码的情况下，为函数添加额外功能',
            analyse='装饰器是Python的高级特性',
            difficulty=2
        )

        # 验证数据库
        self.assertEqual(question.type, 3)
        self.assertEqual(question.name, '请简述Python中装饰器的作用')
        print(f"  ✓ 简答题创建成功")

    def test_create_comprehensive_question(self):
        """测试创建综合题（type=5）"""
        print("\n[测试] 创建综合题")

        question = models.Practises.objects.create(
            name='综合题：设计一个学生成绩管理系统',
            type=5,  # 综合题
            project=self.project,
            answer='1. 数据库设计\n2. 后端API设计\n3. 前端界面设计',
            analyse='考察综合运用能力',
            difficulty=3
        )

        # 验证数据库
        self.assertEqual(question.type, 5)
        self.assertEqual(question.name, '综合题：设计一个学生成绩管理系统')
        print(f"  ✓ 综合题创建成功")

    def test_get_questions_by_extended_type(self):
        """测试查询扩展类型的题目"""
        print("\n[测试] 查询扩展类型题目")

        # 创建不同类型的题目
        models.Practises.objects.create(
            name='简答题1',
            type=3,
            project=self.project,
            answer='答案1',
            analyse='解析1',
            difficulty='easy'
        )
        models.Practises.objects.create(
            name='综合题1',
            type=5,
            project=self.project,
            answer='答案2',
            analyse='解析2',
            difficulty='hard'
        )

        response = self.client.get('/api/questions/admin/list/', {
            'page': 1,
            'pageSize': 10,
            'questionType': 3  # 查询简答题
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['code'], 0)
        self.assertIn('list', data['data'])

        print(f"  ✓ 成功查询到扩展类型题目")


def run_tests():
    """运行所有测试"""
    print("=" * 70)
    print("Ralph循环新增功能测试套件")
    print("=" * 70)

    from django.test.utils import get_runner
    from django.conf import settings

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # 运行测试
    failures = test_runner.run_tests(["__main__"])

    if failures:
        print(f"\n❌ 测试完成，{failures} 个失败")
    else:
        print(f"\n✅ 所有测试通过！")

    return failures


if __name__ == '__main__':
    run_tests()
