"""
快速功能测试脚本
验证系统核心功能是否正常工作
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.test import Client
from app import models
from django.contrib.auth.hashers import make_password


def test_user_login():
    """测试用户登录功能"""
    print("\n[测试] 用户登录功能")
    client = Client()

    # 创建测试用户
    user = models.Users.objects.create(
        id='test001',
        userName='testuser',
        passWord=make_password('123456'),
        name='测试用户',
        type=2,
        gender='男',
        age=20
    )

    # 测试登录
    response = client.post('/api/login/', {
        'userName': 'testuser',
        'passWord': '123456'
    })

    data = response.json()
    print(f"  登录响应: {data}")
    assert data['code'] == 0, f"登录失��: {data}"
    print("  ✓ 登录成功")

    # 清理
    user.delete()
    return True


def test_question_types():
    """测试题目类型扩展"""
    print("\n[测试] 题目类型扩展（6种题型）")

    # 创建教师和学科
    teacher = models.Users.objects.create(
        id='teacher001',
        userName='teacher',
        passWord=make_password('123456'),
        name='测试教师',
        type=1,
        gender='男',
        age=35
    )
    project = models.Projects.objects.create(name='Python程序设计')

    # 测试6种题型
    question_types = {
        0: '选择题',
        1: '填空题',
        2: '判断题',
        3: '简答题',
        4: '编程题',
        5: '综合题'
    }

    for q_type, q_name in question_types.items():
        question = models.Practises.objects.create(
            name=f'测试{q_name}',
            type=q_type,
            project=project,
            answer='测试答案',
            analyse='测试解析',
            difficulty=2
        )
        print(f"  ✓ {q_name}创建成功 (type={q_type})")
        question.delete()

    # 清理
    teacher.delete()
    project.delete()
    return True


def test_student_profile_data():
    """测试学生个人数据（进步曲线和雷达图）"""
    print("\n[测试] 学生个人数据")

    # 创建学生
    student = models.Users.objects.create(
        id='student_test',
        userName='student_test',
        passWord=make_password('123456'),
        name='测试学生',
        type=2,
        gender='男',
        age=20
    )

    # 创建学科和考试
    project1 = models.Projects.objects.create(name='Python程序设计')
    project2 = models.Projects.objects.create(name='数据结构')

    exam1 = models.Exams.objects.create(
        name='Python期末考试',
        project=project1,
        teacher=student,
        examTime='2024-01-01 10:00:00',
        startTime='2024-01-01 10:00:00',
        endTime='2024-01-01 12:00:00'
    )

    exam2 = models.Exams.objects.create(
        name='数据结构期中考试',
        project=project2,
        teacher=student,
        examTime='2024-02-01 10:00:00',
        startTime='2024-02-01 10:00:00',
        endTime='2024-02-01 12:00:00'
    )

    # 创建考试记录
    log1 = models.ExamLogs.objects.create(
        examId=exam1,
        studentId=student,
        score=85.0,
        status=2  # 已完成
    )

    log2 = models.ExamLogs.objects.create(
        examId=exam2,
        studentId=student,
        score=90.0,
        status=2
    )

    print(f"  ✓ 创建2个考试记录")
    print(f"  ✓ Python成绩: {log1.score}")
    print(f"  ✓ 数据结构成绩: {log2.score}")

    # 清理
    log1.delete()
    log2.delete()
    exam1.delete()
    exam2.delete()
    project1.delete()
    project2.delete()
    student.delete()
    return True


def test_wrong_question_collection():
    """测试错题收集功能"""
    print("\n[测试] 错题收集功能")

    # 创建学生和题目
    student = models.Users.objects.create(
        id='student_wq',
        userName='student_wq',
        passWord=make_password('123456'),
        name='测试学生',
        type=2,
        gender='男',
        age=20
    )

    project = models.Projects.objects.create(name='Python')
    question = models.Practises.objects.create(
        name='测试错题',
        type=0,
        project=project,
        answer='A',
        analyse='解析',
        difficulty=2
    )

    # 创建错题记录
    wrong_q = models.WrongQuestions.objects.create(
        studentId=student,
        practiseId=question,
        wrongAnswer='B',
        wrongCount=1
    )

    print(f"  ✓ 错题记录创建成功")
    print(f"  ✓ 错题ID: {wrong_q.id}")

    # 清理
    wrong_q.delete()
    question.delete()
    student.delete()
    project.delete()
    return True


def test_organization_structure():
    """测试组织结构（学院、班级、学生）"""
    print("\n[测试] 组织结构")

    # 创建学院
    college = models.Colleges.objects.create(name='计算机学院')
    print(f"  ✓ 学院创建: {college.name}")

    # 创建班级
    grade = models.Grades.objects.create(name='软件工程1班')
    print(f"  ✓ 班级创建: {grade.name}")

    # 创建用户
    user = models.Users.objects.create(
        id='org_test',
        userName='org_test',
        passWord=make_password('123456'),
        name='测试学生',
        type=2,
        gender='男',
        age=20
    )

    # 创建学生记录
    student = models.Students.objects.create(
        user=user,
        grade=grade,
        college=college
    )

    print(f"  ✓ 学生创建: {user.name}")
    print(f"  ✓ 所属学院: {college.name}")
    print(f"  ✓ 所属班级: {grade.name}")

    # 清理
    student.delete()
    user.delete()
    grade.delete()
    college.delete()
    return True


def run_all_tests():
    """运行所有快速测试"""
    print("=" * 70)
    print("系统核心功能快速测试")
    print("=" * 70)

    tests = [
        ("用户登录", test_user_login),
        ("题目类型扩展", test_question_types),
        ("学生个人数据", test_student_profile_data),
        ("错题收集", test_wrong_question_collection),
        ("组织结构", test_organization_structure),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ 测试失败: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 70)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
