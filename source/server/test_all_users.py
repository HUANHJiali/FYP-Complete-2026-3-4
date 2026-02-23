"""
全用户功能测试脚本
测试管理员、教师、学生三种角色的所有功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.test import Client
from django.contrib.auth.hashers import make_password
from app import models
import json


class UserFunctionTest:
    """用户功能测试类"""
    
    def __init__(self):
        self.client = Client()
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.test_data = {}
        
    def setup_test_data(self):
        """创建测试数据"""
        print("\n" + "="*70)
        print("准备测试数据...")
        print("="*70)
        
        # 创建学院
        self.test_data['college'] = models.Colleges.objects.create(
            name='测试学院'
        )
        print("  [OK] 创建学院")
        
        # 创建班级
        self.test_data['grade'] = models.Grades.objects.create(
            name='测试班级1班'
        )
        print("  [OK] 创建班级")
        
        # 创建学科
        self.test_data['project'] = models.Projects.objects.create(
            name='Python程序设计'
        )
        print("  [OK] 创建学科")
        
        # 创建管理员
        self.test_data['admin'] = models.Users.objects.create(
            id='TEST_ADMIN',
            userName='test_admin',
            passWord=make_password('123456'),
            name='测试管理员',
            type=0,
            gender='男',
            age=30
        )
        print("  [OK] 创建管理员")
        
        # 创建教师
        self.test_data['teacher'] = models.Users.objects.create(
            id='TEST_TEACHER',
            userName='test_teacher',
            passWord=make_password('123456'),
            name='测试教师',
            type=1,
            gender='女',
            age=35
        )
        print("  [OK] 创建教师")
        
        # 创建学生用户
        self.test_data['student_user'] = models.Users.objects.create(
            id='TEST_STUDENT',
            userName='test_student',
            passWord=make_password('123456'),
            name='测试学生',
            type=2,
            gender='男',
            age=20
        )
        
        # 创建学生记录
        self.test_data['student'] = models.Students.objects.create(
            user=self.test_data['student_user'],
            grade=self.test_data['grade'],
            college=self.test_data['college']
        )
        print("  [OK] 创建学生")
        
        print("\n测试数据准备完成！\n")
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n" + "="*70)
        print("清理测试数据...")
        print("="*70)
        
        try:
            # 删除学生记录
            if 'student' in self.test_data:
                self.test_data['student'].delete()
                print("  [OK] 删除学生记录")
            
            # 删除用户
            for user_key in ['student_user', 'teacher', 'admin']:
                if user_key in self.test_data:
                    self.test_data[user_key].delete()
                    print(f"  [OK] 删除{user_key}")
            
            # 删除其他数据
            for key in ['project', 'grade', 'college']:
                if key in self.test_data:
                    self.test_data[key].delete()
                    print(f"  [OK] 删除{key}")
            
            print("\n测试数据清理完成！\n")
        except Exception as e:
            print(f"  [WARN] 清理数据时出错: {e}")
    
    def test_login(self):
        """测试登录功能"""
        print("\n" + "="*70)
        print("测试1: 用户登录功能")
        print("="*70)
        
        # 测试管理员登录
        response = self.client.post('/api/login/', {
            'userName': 'test_admin',
            'passWord': '123456'
        })
        data = response.json()
        if data['code'] == 0:
            self.admin_token = data.get('token')
            print("  [OK] 管理员登录成功")
        else:
            print(f"  [FAIL] 管理员登录失败: {data['msg']}")
        
        # 测试教师登录
        response = self.client.post('/api/login/', {
            'userName': 'test_teacher',
            'passWord': '123456'
        })
        data = response.json()
        if data['code'] == 0:
            self.teacher_token = data.get('token')
            print("  [OK] 教师登录成功")
        else:
            print(f"  [FAIL] 教师登录失败: {data['msg']}")
        
        # 测试学生登录
        response = self.client.post('/api/login/', {
            'userName': 'test_student',
            'passWord': '123456'
        })
        data = response.json()
        if data['code'] == 0:
            self.student_token = data.get('token')
            print("  [OK] 学生登录成功")
        else:
            print(f"  [FAIL] 学生登录失败: {data['msg']}")
        
        # 测试错误密码
        response = self.client.post('/api/login/', {
            'userName': 'test_admin',
            'passWord': 'wrong_password'
        })
        data = response.json()
        if data['code'] != 0:
            print("  [OK] 错误密码正确被拒绝")
        else:
            print("  [FAIL] 错误密码应该被拒绝")
    
    def test_admin_functions(self):
        """测试管理员功能"""
        print("\n" + "="*70)
        print("测试2: 管理员功能")
        print("="*70)
        
        if not self.admin_token:
            print("  [SKIP] 未登录，跳过管理员功能测试")
            return
        
        # 测试获取所有学院
        response = self.client.get('/api/colleges/all/')
        data = response.json()
        if data['code'] == 0:
            print(f"  [OK] 获取学院列表: {len(data['data'])}个学院")
        else:
            print(f"  [FAIL] 获取学院列表失败: {data['msg']}")
        
        # 测试获取所有班级
        response = self.client.get('/api/grades/all/')
        data = response.json()
        if data['code'] == 0:
            print(f"  [OK] 获取班级列表: {len(data['data'])}个班级")
        else:
            print(f"  [FAIL] 获取班级列表失败: {data['msg']}")
        
        # 测试获取所有学生
        response = self.client.get('/api/students/page/', {
            'pageIndex': 1,
            'pageSize': 10
        })
        data = response.json()
        if data['code'] == 0:
            print(f"  [OK] 获取学生列表: {data['data']['count']}名学生")
        else:
            print(f"  [FAIL] 获取学生列表失败: {data['msg']}")
        
        # 测试获取所有教师
        response = self.client.get('/api/teachers/page/', {
            'pageIndex': 1,
            'pageSize': 10
        })
        data = response.json()
        if data['code'] == 0:
            print(f"  [OK] 获取教师列表: {data['data']['count']}名教师")
        else:
            print(f"  [FAIL] 获取教师列表失败: {data['msg']}")
    
    def test_teacher_functions(self):
        """测试教师功能"""
        print("\n" + "="*70)
        print("测试3: 教师功能")
        print("="*70)
        
        if not self.teacher_token:
            print("  [SKIP] 未登录，跳过教师功能测试")
            return
        
        # 测试创建题目
        response = self.client.post('/api/practises/add/', {
            'name': '测试题目',
            'type': 0,
            'projectId': self.test_data['project'].id,
            'answer': 'A',
            'analyse': '测试解析'
        })
        data = response.json()
        if data['code'] == 0:
            print("  [OK] 创建题目成功")
            self.test_data['question'] = models.Practises.objects.get(name='测试题目')
        else:
            print(f"  [FAIL] 创建题目失败: {data['msg']}")
        
        # 测试创建考试
        if 'question' in self.test_data:
            response = self.client.post('/api/exams/add/', {
                'name': '测试考试',
                'teacherId': self.test_data['teacher'].id,
                'projectId': self.test_data['project'].id,
                'gradeId': self.test_data['grade'].id,
                'examTime': '2026-03-01 10:00:00',
                'questionIds[]': [self.test_data['question'].id]
            })
            data = response.json()
            if data['code'] == 0:
                print("  [OK] 创建考试成功")
                self.test_data['exam'] = models.Exams.objects.get(name='测试考试')
            else:
                print(f"  [FAIL] 创建考试失败: {data['msg']}")
    
    def test_student_functions(self):
        """测试学生功能"""
        print("\n" + "="*70)
        print("测试4: 学生功能")
        print("="*70)
        
        if not self.student_token:
            print("  [SKIP] 未登录，跳过学生功能测试")
            return
        
        # 测试获取考试列表
        response = self.client.get('/api/exams/list/', {
            'studentId': self.test_data['student_user'].id
        })
        data = response.json()
        if data['code'] == 0:
            print(f"  [OK] 获取考试列表: {len(data['data'])}场考试")
        else:
            print(f"  [FAIL] 获取考试列表失败: {data['msg']}")
        
        # 测试获取个人成绩
        response = self.client.get('/api/students/scores/', {
            'studentId': self.test_data['student_user'].id
        })
        data = response.json()
        if data['code'] == 0:
            print("  [OK] 获取个人成绩成功")
        else:
            print(f"  [FAIL] 获取个人成绩失败: {data['msg']}")
    
    def test_common_functions(self):
        """测试通用功能"""
        print("\n" + "="*70)
        print("测试5: 通用功能")
        print("="*70)
        
        # 测试获取用户信息
        if self.admin_token:
            response = self.client.get('/api/info/', {
                'token': self.admin_token
            })
            data = response.json()
            if data['code'] == 0:
                print(f"  [OK] 获取用户信息: {data['data']['name']}")
            else:
                print(f"  [FAIL] 获取用户信息失败: {data['msg']}")
        
        # 测试修改密码
        if self.admin_token:
            response = self.client.post('/api/pwd/', {
                'token': self.admin_token,
                'oldPwd': '123456',
                'newPwd': '123456'
            })
            data = response.json()
            if data['code'] == 0:
                print("  [OK] 修改密码功能正常")
            else:
                print(f"  [FAIL] 修改密码失败: {data['msg']}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("全用户功能测试开始")
        print("="*70)
        
        try:
            # 准备测试数据
            self.setup_test_data()
            
            # 运行测试
            self.test_login()
            self.test_admin_functions()
            self.test_teacher_functions()
            self.test_student_functions()
            self.test_common_functions()
            
            # 统计结果
            print("\n" + "="*70)
            print("测试完成")
            print("="*70)
            print("所有测试已执行，请查看上述结果")
            
        finally:
            # 清理测试数据
            self.cleanup_test_data()


def main():
    """主函数"""
    tester = UserFunctionTest()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
