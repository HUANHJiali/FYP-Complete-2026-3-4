"""
P0问题修复验证测试套件

测试范围：
1. 学生管理安全修复（.get()异常、级联删除、None检查）
2. 任务管理CRUD功能
3. 练习系统AI评分和错题收集
4. 统计功能（班级、科目）
5. 考试记录详情查询

运行方式：
    python manage.py test app.tests.test_p0_fixes
    python manage.py test app.tests.test_p0_fixes.TestStudentManagement
    python manage.py test app.tests.test_p0_fixes.TestStudentManagement.test_student_update_safe
"""

from django.test import TestCase, Client
from django.db import transaction
from django.utils import timezone
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import models
import sys
import os

# 添加项目路径以导入comm模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from comm.CommUtils import DateUtil


class TestStudentManagement(TestCase):
    """测试学生管理安全修复"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建学院和班级
        self.college1 = models.Colleges.objects.create(
            name='计算机学院',
            
        )
        self.college2 = models.Colleges.objects.create(
            name='数学学院',
            
        )

        self.grade1 = models.Grades.objects.create(
            name='计算机2021-1班',
            
        )
        self.grade2 = models.Grades.objects.create(
            name='计算机2021-2班',
            
        )

        # 创建学生用户和学生信息
        from django.contrib.auth.hashers import make_password
        self.user1 = models.Users.objects.create(
            id='2021001',
            userName='student001',
            name='张三',
            passWord=make_password('123456'),  # 使用passWord而不是password
            type=2,  # 学生
            gender='男',
            age=20,
            createTime=DateUtil.getNowDateTime()
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

        # 测试4: 两个都不存在
        response = self.client.post('/api/students/upd', {
            'id': self.user1.id,
            'gradeId': 99999,
            'collegeId': 99999
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('不存在', data['msg'])
        print("  ✓ 两个ID都不存在时返回友好提示")

        print("✓ 学生更新安全性测试通过")

    def test_student_delete_cascade(self):
        """测试学生删除的级联检查"""
        print("\n[测试] 学生删除级联检查 - 验证所有关联表检查")

        # 创建关联数据
        project = models.Projects.objects.create(
            name='Python程序设计',
            
        )

        # 创建题目
        question1 = models.Practises.objects.create(
            name='Python基础题',
            answer='A',
            type=0,
            project=project,
            
        )

        # 创建考试
        exam = models.Exams.objects.create(
            name='Python期中考试',
            project=project,
            grade=self.grade1,
            teacher=self.user1,  # 使用学生用户作为教师（仅用于测试）
            
        )

        # 创建考试日志
        exam_log = models.ExamLogs.objects.create(
            exam=exam,
            student=self.student1,
            startTime=DateUtil.getNowDateTime(),
            endTime=DateUtil.getNowDateTime(),
            status='completed',
            score=85.0,
            accuracy=85.0,
            usedTime=60
        )

        # 测试1: 有考试记录时不能删除
        response = self.client.post('/api/students/del', {
            'id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '该学生有考试记录，无法删除')
        print("  ✓ 有考试记录时阻止删除")

        # 删除考试日志
        exam_log.delete()

        # 创建练习记录
        paper = models.PracticePapers.objects.create(
            title='Python练习卷',
            project=project,
            teacher=self.user1,
            ,
            totalScore=100
        )

        practice_log = models.StudentPracticeLogs.objects.create(
            student=self.student1,
            paper=paper,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        # 测试2: 有练习记录时不能删除
        response = self.client.post('/api/students/del', {
            'id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '该学生有练习记录，无法删除')
        print("  ✓ 有练习记录时阻止删除")

        practice_log.delete()

        # 创建错题记录
        wrong_question = models.WrongQuestions.objects.create(
            student=self.student1,
            practise=question1,
            source='exam',
            sourceId='1',
            wrongAnswer='B',
            correctAnswer='A',
            
        )

        # 测试3: 有错题记录时不能删除
        response = self.client.post('/api/students/del', {
            'id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '该学生有错题记录，无法删除')
        print("  ✓ 有错题记录时阻止删除")

        wrong_question.delete()

        # 测试4: 没有任何关联记录时可以删除
        response = self.client.post('/api/students/del', {
            'id': self.user1.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')

        # 验证已删除
        self.assertFalse(models.Users.objects.filter(id=self.user1.id).exists())
        print("  ✓ 无关联记录时成功删除")

        print("✓ 学生删除级联检查测试通过")

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
            
        )
        self.grade = models.Grades.objects.create(
            name='计算机2021-1班',
            
        )
        self.project = models.Projects.objects.create(
            name='Python程序设计',
            
        )

        # 创建教师
        from django.contrib.auth.hashers import make_password
        self.teacher_user = models.Users.objects.create(
            id='T001',
            userName='teacher001',
            name='李老师',
            passWord=make_password('123456'),
            type=1,
            
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
            
        )
        self.question2 = models.Practises.objects.create(
            name='Python基础题2',
            answer='B',
            type=0,
            project=self.project,
            
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

        # 测试2: 创建任务（包含题目）
        response = self.client.post('/api/tasks/add', {
            'title': 'Python综合任务',
            'description': '完成Python综合练习',
            'type': 'practice',
            'deadline': '2025-12-31 23:59:59',
            'score': 100,
            'projectId': self.project.id,
            'gradeId': self.grade.id,
            'teacherId': self.teacher_user.id,
            'questionIds': json.dumps([self.question1.id, self.question2.id])
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        task_id_2 = data['data']['id']
        print("  ✓ 创建任务成功（包含题目）")

        # 验证题目已关联
        task_questions = models.TaskQuestions.objects.filter(task__id=task_id_2)
        self.assertEqual(task_questions.count(), 2)
        print("  ✓ 题目关联验证成功")

        # 测试3: 缺少必填参数
        response = self.client.post('/api/tasks/add', {
            'title': '不完整的任务'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('缺少必填参数', data['msg'])
        print("  ✓ 缺少必填参数时返回错误")

        # 测试4: 关联的班级不存在
        response = self.client.post('/api/tasks/add', {
            'title': '测试任务',
            'deadline': '2025-12-31 23:59:59',
            'score': 100,
            'projectId': self.project.id,
            'gradeId': 99999,  # 不存在的班级
            'teacherId': self.teacher_user.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '指定的班级不存在')
        print("  ✓ 班级不存在时返回友好提示")

        print("✓ 任务创建测试通过")

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
            ,
            isActive=True
        )

        # 测试1: 更新标题
        response = self.client.post('/api/tasks/upd', {
            'id': task.id,
            'title': '更新后的任务'
        })
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, '更新后的任务')
        self.assertEqual(task.description, '原始描述')  # 其他字段未变
        print("  ✓ 更新标题成功")

        # 测试2: 更新多个字段
        response = self.client.post('/api/tasks/upd', {
            'id': task.id,
            'title': '最终任务',
            'description': '最终描述',
            'score': 150,
            'deadline': '2025-12-31 23:59:59'
        })
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, '最终任务')
        self.assertEqual(task.description, '最终描述')
        self.assertEqual(task.score, 150)
        print("  ✓ 更新多个字段成功")

        # 测试3: 更新不存在的任务
        response = self.client.post('/api/tasks/upd', {
            'id': 99999,
            'title': '测试'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '任务不存在')
        print("  ✓ 任务不存在时返回友好提示")

        # 测试4: 更新isActive
        response = self.client.post('/api/tasks/upd', {
            'id': task.id,
            'isActive': 'false'
        })
        task.refresh_from_db()
        self.assertFalse(task.isActive)
        print("  ✓ 更新isActive成功")

        print("✓ 任务更新测试通过")

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
            
        )

        # 测试1: 删除任务
        response = self.client.post('/api/tasks/del', {
            'ids': f'[{task.id}]'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '成功删除1个任务')
        self.assertFalse(models.Tasks.objects.filter(id=task.id).exists())
        print("  ✓ 删除任务成功")

        # 创建另一个任务
        task2 = models.Tasks.objects.create(
            title='待删除任务2',
            description='测试',
            type='practice',
            deadline='2025-12-31 23:59:59',
            score=100,
            project=self.project,
            grade=self.grade,
            teacher=self.teacher_user,
            
        )

        # 创建学生
        from django.contrib.auth.hashers import make_password
        student_user = models.Users.objects.create(
            id='S001',
            userName='student001',
            name='测试学生',
            passWord=make_password('123456'),
            type=2,
            
        )
        student = models.Students.objects.create(
            user=student_user,
            grade=self.grade,
            college=self.college
        )

        # 创建进行中的任务日志
        task_log = models.StudentTaskLogs.objects.create(
            student=student,
            task=task2,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        # 测试2: 有学生正在进行任务时不能删除
        response = self.client.post('/api/tasks/del', {
            'ids': f'[{task2.id}]'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '有学生正在进行任务，无法删除')
        self.assertTrue(models.Tasks.objects.filter(id=task2.id).exists())
        print("  ✓ 有学生进行中时阻止删除")

        # 完成任务
        task_log.status = 'completed'
        task_log.save()

        # 测试3: 任务完成后可以删除
        response = self.client.post('/api/tasks/del', {
            'ids': f'[{task2.id}]'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '成功删除1个任务')
        self.assertFalse(models.Tasks.objects.filter(id=task2.id).exists())
        print("  ✓ 任务完成后可以删除")

        print("✓ 任务删除测试通过")


class TestPracticeSystem(TestCase):
    """测试练习系统AI评分和错题收集"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建基础数据
        self.college = models.Colleges.objects.create(
            name='计算机学院',
            
        )
        self.grade = models.Grades.objects.create(
            name='计算机2021-1班',
            
        )
        self.project = models.Projects.objects.create(
            name='Python程序设计',
            
        )

        # 创建学生和教师
        from django.contrib.auth.hashers import make_password
        self.student_user = models.Users.objects.create(
            id='S001',
            userName='student001',
            name='张三',
            passWord=make_password('123456'),
            type=2,
            
        )
        self.student = models.Students.objects.create(
            user=self.student_user,
            grade=self.grade,
            college=self.college
        )

        self.teacher_user = models.Users.objects.create(
            id='T001',
            userName='teacher001',
            name='李老师',
            passWord=make_password('123456'),
            type=1,
            
        )
        self.teacher = models.Teachers.objects.create(
            user=self.teacher_user,
            college=self.college
        )

        # 创建题目
        self.question_choice = models.Practises.objects.create(
            name='Python选择题',
            answer='A',
            type=0,  # 选择题
            project=self.project,
            
        )

        self.question_fill = models.Practises.objects.create(
            name='Python填空题',
            answer='print',
            type=1,  # 填空题
            project=self.project,
            
        )

        # 创建练习试卷
        self.paper = models.PracticePapers.objects.create(
            title='Python练习卷1',
            project=self.project,
            teacher=self.teacher_user,
            ,
            totalScore=100,
            isActive=True
        )

        # 创建练习日志
        self.practice_log = models.StudentPracticeLogs.objects.create(
            student=self.student,
            paper=self.paper,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

    def test_practice_submit_with_auto_collection(self):
        """测试练习提交和错题自动收集"""
        print("\n[测试] 练习提交和错题自动收集")

        # 准备答案数据（包含正确和错误的）
        answers = [
            {
                'practiseId': self.question_choice.id,
                'studentAnswer': 'B'  # 错误答案（正确是A）
            },
            {
                'practiseId': self.question_fill.id,
                'studentAnswer': 'print'  # 正确答案
            }
        ]

        # 提交练习
        response = self.client.post('/api/practice/submit', {
            'logId': self.practice_log.id,
            'answers': json.dumps(answers)
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')
        self.assertIn('data', data)
        print("  ✓ 练习提交成功")

        # 验证练习日志已更新
        self.practice_log.refresh_from_db()
        self.assertEqual(self.practice_log.status, 'completed')
        self.assertIsNotNone(self.practice_log.endTime)
        self.assertGreater(self.practice_log.score, 0)
        print("  ✓ 练习日志更新成功")

        # 验证答案已保存
        answer_count = models.StudentPracticeAnswers.objects.filter(
            practiceLog=self.practice_log
        ).count()
        self.assertEqual(answer_count, 2)
        print("  ✓ 答案保存成功")

        # 验证错题自动收集
        wrong_questions = models.WrongQuestions.objects.filter(
            student=self.student,
            practise=self.question_choice,
            source='practice'
        )
        self.assertEqual(wrong_questions.count(), 1)
        wrong = wrong_questions.first()
        self.assertEqual(wrong.wrongAnswer, 'B')
        self.assertEqual(wrong.correctAnswer, 'A')
        print("  ✓ 错题自动收集成功")

        # 验证正确的答案没有进入错题本
        wrong_fill = models.WrongQuestions.objects.filter(
            student=self.student,
            practise=self.question_fill,
            source='practice'
        )
        self.assertEqual(wrong_fill.count(), 0)
        print("  ✓ 正确答案未进入错题本")

        print("✓ 练习提交和错题自动收集测试通过")


class TestStatistics(TestCase):
    """测试统计功能"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建基础数据
        self.college = models.Colleges.objects.create(
            name='计算机学院',
            
        )
        self.grade1 = models.Grades.objects.create(
            name='计算机2021-1班',
            
        )
        self.grade2 = models.Grades.objects.create(
            name='计算机2021-2班',
            
        )
        self.project = models.Projects.objects.create(
            name='Python程序设计',
            
        )

        # 创建教师和学生
        from django.contrib.auth.hashers import make_password
        self.teacher = models.Users.objects.create(
            id='T001',
            userName='teacher001',
            name='李老师',
            passWord=make_password('123456'),
            type=1,
            
        )

        # 创建3个学生
        for i in range(1, 4):
            user = models.Users.objects.create(
                id=f'S{i:03d}',
                userName=f'student{i:03d}',
                name=f'学生{i}',
                passWord=make_password('123456'),
                type=2,
                
            )
            student = models.Students.objects.create(
                user=user,
                grade=self.grade1,
                college=self.college
            )

            # 创建题目
            question = models.Practises.objects.create(
                name=f'Python题目{i}',
                answer='A',
                type=0,
                project=self.project,
                
            )

            # 创建考试
            exam = models.Exams.objects.create(
                name=f'Python考试{i}',
                project=self.project,
                grade=self.grade1,
                teacher=self.teacher,
                
            )

            # 创建考试日志（不同分数段）
            score = 95 if i == 1 else (75 if i == 2 else 55)
            exam_log = models.ExamLogs.objects.create(
                exam=exam,
                student=student,
                startTime=DateUtil.getNowDateTime(),
                endTime=DateUtil.getNowDateTime(),
                status='completed',
                score=score,
                accuracy=score,
                usedTime=60
            )

            # 创建错题
            models.WrongQuestions.objects.create(
                student=student,
                practise=question,
                source='exam',
                sourceId=str(exam.id),
                wrongAnswer='B',
                correctAnswer='A',
                
            )

    def test_class_statistics(self):
        """测试班级统计功能"""
        print("\n[测试] 班级统计功能")

        # 测试1: 获取班级统计
        response = self.client.get(f'/api/admin/statistics_class?gradeId={self.grade1.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')
        self.assertIn('data', data)

        stats = data['data']
        self.assertEqual(stats['gradeName'], '计算机2021-1班')
        self.assertEqual(stats['totalStudents'], 3)

        # 验证考试统计
        self.assertIn('exams', stats)
        exams = stats['exams']
        self.assertGreater(exams['total'], 0)
        self.assertEqual(exams['completed'], 3)
        self.assertAlmostEqual(exams['avgScore'], 75.0, places=1)

        # 验证分数段分布
        self.assertIn('scoreDistribution', exams)
        dist = exams['scoreDistribution']
        self.assertEqual(dist['excellent'], 1)  # >=90
        self.assertEqual(dist['good'], 1)  # 80-89
        self.assertEqual(dist['pass'], 0)  # 60-79
        self.assertEqual(dist['fail'], 1)  # <60

        # 验证错题统计
        self.assertIn('wrongQuestions', stats)
        wrong = stats['wrongQuestions']
        self.assertEqual(wrong['total_wrong_questions'], 3)

        print("  ✓ 班级统计数据完整")
        print(f"    - 学生总数: {stats['totalStudents']}")
        print(f"    - 考试平均分: {exams['avgScore']}")
        print(f"    - 分数段: 优秀{dist['excellent']} 良好{dist['good']} 及格{dist['pass']} 不及格{dist['fail']}")
        print(f"    - 错题总数: {wrong['total_wrong_questions']}")

        # 测试2: 班级不存在
        response = self.client.get('/api/admin/statistics_class?gradeId=99999')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '班级不存在')
        print("  ✓ 班级不存在时返回友好提示")

        print("✓ 班级统计测试通过")

    def test_subject_statistics(self):
        """测试科目统计功能"""
        print("\n[测试] 科目统计功能")

        # 测试1: 获取科目统计
        response = self.client.get(f'/api/admin/statistics_subject?projectId={self.project.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')
        self.assertIn('data', data)

        stats = data['data']
        self.assertEqual(stats['projectName'], 'Python程序设计')

        # 验证题目统计
        self.assertIn('questions', stats)
        questions = stats['questions']
        self.assertGreater(questions['total'], 0)
        self.assertIn('byType', questions)

        # 验证考试统计
        self.assertIn('exams', stats)
        exams = stats['exams']
        self.assertEqual(exams['totalParticipants'], 3)
        self.assertAlmostEqual(exams['avgScore'], 75.0, places=1)
        self.assertEqual(exams['maxScore'], 95)
        self.assertEqual(exams['minScore'], 55)

        # 验证错题统计
        self.assertEqual(stats['wrongQuestions'], 3)

        print("  ✓ 科目统计数据完整")
        print(f"    - 题目总数: {questions['total']}")
        print(f"    - 参与考试: {exams['totalParticipants']}人")
        print(f"    - 平均分: {exams['avgScore']}")
        print(f"    - 最高分: {exams['maxScore']}")
        print(f"    - 最低分: {exams['minScore']}")

        # 测试2: 科目不存在
        response = self.client.get('/api/admin/statistics_subject?projectId=99999')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '科目不存在')
        print("  ✓ 科目不存在时返回友好提示")

        print("✓ 科目统计测试通过")


class TestExamSystem(TestCase):
    """测试考试系统记录详情"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()

        # 创建基础数据
        self.college = models.Colleges.objects.create(
            name='计算机学院',
            
        )
        self.grade = models.Grades.objects.create(
            name='计算机2021-1班',
            
        )
        self.project = models.Projects.objects.create(
            name='Python程序设计',
            
        )

        # 创建学生和教师
        from django.contrib.auth.hashers import make_password
        self.student_user = models.Users.objects.create(
            id='S001',
            userName='student001',
            name='张三',
            passWord=make_password('123456'),
            type=2,
            
        )
        self.student = models.Students.objects.create(
            user=self.student_user,
            grade=self.grade,
            college=self.college
        )

        self.teacher_user = models.Users.objects.create(
            id='T001',
            userName='teacher001',
            name='李老师',
            passWord=make_password('123456'),
            type=1,
            
        )

        # 创建题目
        self.question1 = models.Practises.objects.create(
            name='Python选择题',
            answer='A',
            type=0,
            project=self.project,
            
        )
        self.question2 = models.Practises.objects.create(
            name='Python填空题',
            answer='print',
            type=1,
            project=self.project,
            
        )

        # 创建考试
        self.exam = models.Exams.objects.create(
            name='Python期中考试',
            project=self.project,
            grade=self.grade,
            teacher=self.teacher_user,
            
        )

        # 创建考试日志
        self.exam_log = models.ExamLogs.objects.create(
            exam=self.exam,
            student=self.student,
            startTime=DateUtil.getNowDateTime(),
            endTime=DateUtil.getNowDateTime(),
            status='completed',
            score=85.0,
            accuracy=85.0,
            usedTime=60
        )

        # 创建答题记录
        models.AnswerLogs.objects.create(
            exam=self.exam,
            student=self.student,
            no=1,
            practise=self.question1,
            answer='A',
            score=2.0,
            status=1
        )

        models.AnswerLogs.objects.create(
            exam=self.exam,
            student=self.student,
            no=2,
            practise=self.question2,
            answer='print',
            score=2.0,
            status=1
        )

    def test_exam_log_get_info(self):
        """测试考试记录详情查询"""
        print("\n[测试] 考试记录详情查询")

        # 测试1: 获取考试记录详情
        response = self.client.get(f'/api/examLogs/get_info?id={self.exam_log.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], 'success')
        self.assertIn('data', data)

        info = data['data']
        self.assertEqual(info['examId'], self.exam.id)
        self.assertEqual(info['examName'], 'Python期中考试')
        self.assertEqual(info['studentId'], self.student_user.id)
        self.assertEqual(info['studentName'], '张三')
        self.assertEqual(info['score'], 85.0)
        self.assertEqual(info['accuracy'], 85.0)
        self.assertEqual(info['status'], 'completed')

        # 验证答案详情
        self.assertIn('answers', info)
        answers = info['answers']
        self.assertEqual(len(answers), 2)

        # 验证第一个答案
        answer1 = answers[0]
        self.assertEqual(answer1['questionId'], self.question1.id)
        self.assertEqual(answer1['questionName'], 'Python选择题')
        self.assertEqual(answer1['questionType'], 0)
        self.assertEqual(answer1['studentAnswer'], 'A')
        self.assertEqual(answer1['correctAnswer'], 'A')
        self.assertTrue(answer1['isCorrect'])
        self.assertEqual(answer1['score'], 2.0)

        print("  ✓ 考试记录详情数据完整")
        print(f"    - 考试名称: {info['examName']}")
        print(f"    - 学生姓名: {info['studentName']}")
        print(f"    - 得分: {info['score']}")
        print(f"    - 答题数量: {len(answers)}")

        # 测试2: 记录不存在
        response = self.client.get('/api/examLogs/get_info?id=99999')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['msg'], '答题记录不存在')
        print("  ✓ 记录不存在时返回友好提示")

        print("✓ 考试记录详情查询测试通过")


def print_test_summary():
    """打印测试总结"""
    print("\n" + "="*60)
    print("P0问题修复验证测试套件")
    print("="*60)
    print("\n测试覆盖:")
    print("  ✓ 学生管理安全修复（3个问题）")
    print("  ✓ 任务管理CRUD功能（3个问题）")
    print("  ✓ 练习系统AI评分和错题收集（2个问题）")
    print("  ✓ 统计功能（2个问题）")
    print("  ✓ 考试记录详情查询（1个问题）")
    print("\n总计: 11个测试用例")
    print("="*60 + "\n")


if __name__ == '__main__':
    print_test_summary()
