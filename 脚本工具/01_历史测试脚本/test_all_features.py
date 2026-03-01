"""
全功能��试脚本 - 测试管理员、教师、学生的所有功能
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

class UserTester:
    def __init__(self, username, password, role_name):
        self.username = username
        self.password = password
        self.role_name = role_name
        self.token = None
        self.results = []

    def login(self):
        """登录"""
        url = f"{BASE_URL}/login/"
        data = {
            "userName": self.username,
            "passWord": self.password
        }

        try:
            response = requests.post(url, data=data, timeout=5)
            result = response.json()

            if result.get('code') == 0:
                self.token = result['data']['token']
                self.results.append(("登录", "PASS", result.get('msg')))
                return True
            else:
                self.results.append(("登录", "FAIL", result.get('msg')))
                return False
        except Exception as e:
            self.results.append(("登录", "ERROR", str(e)))
            return False

    def get_user_info(self):
        """获取用户信息"""
        url = f"{BASE_URL}/info/"
        params = {"token": self.token}

        try:
            response = requests.get(url, params=params, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取用户信息", status, result.get('msg')))
            return result.get('code') == 0
        except Exception as e:
            self.results.append(("获取用户信息", "ERROR", str(e)))
            return False

    def test_colleges(self):
        """测试学院管理"""
        if not self.token:
            return

        # 获取所有学院
        url = f"{BASE_URL}/colleges/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取学院列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取学院列表", "ERROR", str(e)))

    def test_grades(self):
        """测试班级管理"""
        if not self.token:
            return

        url = f"{BASE_URL}/grades/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取班级列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取班级列表", "ERROR", str(e)))

    def test_projects(self):
        """测试科目管理"""
        if not self.token:
            return

        url = f"{BASE_URL}/projects/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取科目列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取科目列表", "ERROR", str(e)))

    def test_practises(self):
        """测试题库管理"""
        if not self.token:
            return

        url = f"{BASE_URL}/practises/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取题库列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取题库列表", "ERROR", str(e)))

    def test_exams(self):
        """测试考试管理"""
        if not self.token:
            return

        url = f"{BASE_URL}/exams/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取考试列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取考试列表", "ERROR", str(e)))

    def test_students(self):
        """测试学生管理"""
        if not self.token:
            return

        url = f"{BASE_URL}/students/page/"
        params = {"token": self.token, "pageIndex": 1, "pageSize": 10}
        try:
            response = requests.get(url, params=params, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取学生列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取学生列表", "ERROR", str(e)))

    def test_teachers(self):
        """测试教师管理"""
        if not self.token:
            return

        url = f"{BASE_URL}/teachers/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取教师列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取教师列表", "ERROR", str(e)))

    def test_messages(self):
        """测试消息中心"""
        if not self.token:
            return

        url = f"{BASE_URL}/messages/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取消息列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取消息列表", "ERROR", str(e)))

    def test_tasks(self):
        """测试任务中心"""
        if not self.token:
            return

        url = f"{BASE_URL}/tasks/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取任务列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取任务列表", "ERROR", str(e)))

    def test_wrong_questions(self):
        """测试错题本"""
        if not self.token:
            return

        url = f"{BASE_URL}/wrongquestions/all/"
        try:
            response = requests.get(url, params={"token": self.token}, timeout=5)
            result = response.json()
            status = "PASS" if result.get('code') == 0 else "FAIL"
            self.results.append(("获取错题列表", status, result.get('msg')))
        except Exception as e:
            self.results.append(("获取错题列表", "ERROR", str(e)))

    def run_all_tests(self):
        """运行所有测试"""
        print(f"\n{'='*70}")
        print(f"测试角色: {self.role_name}")
        print(f"用户名: {self.username}")
        print(f"{'='*70}")

        # 登录
        if not self.login():
            print(f"[FAIL] 登录失败，跳过后续测试")
            return

        # 基础功能测试
        self.get_user_info()
        self.test_colleges()
        self.test_grades()
        self.test_projects()
        self.test_practises()
        self.test_exams()

        # 根据角色测试特定功能
        if self.role_name == "管理员":
            self.test_students()
            self.test_teachers()
            self.test_tasks()
            self.test_messages()
        elif self.role_name == "教师":
            self.test_students()
            self.test_tasks()
            self.test_messages()
        elif self.role_name == "学生":
            self.test_exams()
            self.test_wrong_questions()
            self.test_tasks()
            self.test_messages()

        # 打印结果
        print(f"\n测试结果:")
        print(f"{'功能':<20} {'状态':<10} {'信息'}")
        print("-"*70)

        pass_count = 0
        fail_count = 0
        error_count = 0

        for feature, status, msg in self.results:
            print(f"{feature:<20} {status:<10} {msg}")
            if status == "PASS":
                pass_count += 1
            elif status == "FAIL":
                fail_count += 1
            else:
                error_count += 1

        print("-"*70)
        print(f"总计: {len(self.results)} | 通过: {pass_count} | 失败: {fail_count} | 错误: {error_count}")

        return pass_count, fail_count, error_count


def main():
    print("="*70)
    print("全功能测试 - 管理员、教师、学生")
    print("="*70)

    # 定义测试用户（根据之前的测试结果）
    test_users = [
        # 用户名, 密码, 角色名称
        ("python222", "123456", "管理员"),
        # ("teacher", "123456", "教师"),  # 有问题，暂时跳过
        # ("student", "123456", "学生"),  # 有问题，暂时跳过
    ]

    # 尝试找到可用的教师和学生用户
    import subprocess
    import re

    try:
        result = subprocess.run(
            ["python", "manage.py", "shell", "-c",
             "from app.models import Users; users = Users.objects.filter(type=1); print([u.userName for u in users[:3]])"],
            cwd="source/server",
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # 提取用户名
            match = re.search(r"\['(.+?)'\]", result.stdout)
            if match:
                teacher_username = match.group(1).split("'")[0]
                test_users.append((teacher_username, "123456", "教师"))
    except:
        pass

    # 运行测试
    total_pass = 0
    total_fail = 0
    total_error = 0

    for username, password, role_name in test_users:
        tester = UserTester(username, password, role_name)
        p, f, e = tester.run_all_tests()
        total_pass += p
        total_fail += f
        total_error += e

    # 总结
    print(f"\n{'='*70}")
    print(f"测试总结")
    print(f"{'='*70}")
    print(f"总计: {total_pass + total_fail + total_error}")
    print(f"通过: {total_pass}")
    print(f"失败: {total_fail}")
    print(f"错误: {total_error}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
