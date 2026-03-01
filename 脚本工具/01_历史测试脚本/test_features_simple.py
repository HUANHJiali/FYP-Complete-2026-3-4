"""
简化的全功能测试
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_api(endpoint, token=None, params=None, method="GET"):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"

    if params is None:
        params = {}
    if token:
        params["token"] = token

    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        else:
            response = requests.post(url, data=params, timeout=5)

        result = response.json()
        status = "PASS" if result.get('code') == 0 else "FAIL"
        msg = result.get('msg', 'No message')
        return status, msg
    except Exception as e:
        return "ERROR", str(e)

def main():
    print("="*80)
    print("系统功能测试报告")
    print("="*80)

    # 测试登录并获取管理员token
    print("\n[1] 测试登录功能")
    print("-"*80)

    login_data = {"userName": "python222", "passWord": "123456"}
    try:
        response = requests.post(f"{BASE_URL}/login/", data=login_data, timeout=5)
        result = response.json()

        if result.get('code') == 0:
            admin_token = result['data']['token']
            print(f"  python222 (管理员): PASS - {result.get('msg')}")
        else:
            print(f"  python222 (管理员): FAIL - {result.get('msg')}")
            print("\n无法获取管理员token，终止测试")
            return
    except Exception as e:
        print(f"  python222 (管理员): ERROR - {e}")
        return

    # 测试其他用户登录
    test_users = [("teacher", "123456", "教师"), ("student", "123456", "学生")]
    teacher_token = None
    student_token = None

    for username, password, role in test_users:
        try:
            response = requests.post(f"{BASE_URL}/login/",
                                   data={"userName": username, "passWord": password},
                                   timeout=5)
            result = response.json()

            if result.get('code') == 0:
                token = result['data']['token']
                print(f"  {username} ({role}): PASS - {result.get('msg')}")
                if role == "教师":
                    teacher_token = token
                else:
                    student_token = token
            else:
                print(f"  {username} ({role}): FAIL - {result.get('msg')}")
        except Exception as e:
            print(f"  {username} ({role}): ERROR - {e}")

    # 管理员功能测试
    print("\n[2] 管理员功能测试")
    print("-"*80)

    admin_tests = [
        ("获取用户信息", "/info/"),
        ("学院列表", "/colleges/all/"),
        ("班级列表", "/grades/all/"),
        ("科目列表", "/projects/all/"),
        ("学生分页", "/students/page/", {"pageIndex": 1, "pageSize": 10}),
        ("教师列表", "/teachers/all/"),
        ("题库列表", "/practises/all/"),
        ("考试列表", "/exams/all/"),
        ("任务列表", "/tasks/all/"),
        ("消息列表", "/messages/"),
        ("操作日志", "/logs/all/"),
    ]

    for name, endpoint, *args in admin_tests:
        params = args[0] if args else {}
        status, msg = test_api(endpoint, admin_token, params)
        print(f"  {name:<12} {status:<8} {msg}")

    # 学生功能测试（如果有token）
    if student_token:
        print("\n[3] 学生功能测试")
        print("-"*80)

        student_tests = [
            ("获取用户信息", "/info/"),
            ("考试列表", "/exams/all/"),
            ("练习试卷", "/practicepapers/all/"),
            ("错题列表", "/wrongquestions/all/"),
            ("任务列表", "/tasks/all/"),
            ("消息列表", "/messages/"),
            ("考试记录", "/examlogs/all/"),
        ]

        for name, endpoint, *args in student_tests:
            params = args[0] if args else {}
            status, msg = test_api(endpoint, student_token, params)
            print(f"  {name:<12} {status:<8} {msg}")
    else:
        print("\n[3] 学生功能测试 - SKIP (无法登录)")

    # 教师功能测试（如果有token）
    if teacher_token:
        print("\n[4] 教师功能测试")
        print("-"*80)

        teacher_tests = [
            ("获取用户信息", "/info/"),
            ("学生列表", "/students/page/", {"pageIndex": 1, "pageSize": 10}),
            ("题库管理", "/practises/all/"),
            ("考试管理", "/exams/all/"),
            ("任务管理", "/tasks/all/"),
            ("消息列表", "/messages/"),
        ]

        for name, endpoint, *args in teacher_tests:
            params = args[0] if args else {}
            status, msg = test_api(endpoint, teacher_token, params)
            print(f"  {name:<12} {status:<8} {msg}")
    else:
        print("\n[4] 教师功能测试 - SKIP (无法登录)")

    # 测试API功能
    print("\n[5] AI功能测试")
    print("-"*80)

    ai_tests = [
        ("AI评分", "/ai/score/", {
            "questionContent": "测试题目",
            "correctAnswer": "正确答案",
            "studentAnswer": "学生答案",
            "questionType": 0,
            "maxScore": 10
        }, "POST"),
        ("AI生成题目", "/ai/generate/", {
            "subject": "数学",
            "topic": "代数",
            "difficulty": "easy",
            "questionType": 0,
            "count": 1
        }, "POST"),
    ]

    for name, endpoint, params, method in ai_tests:
        params["token"] = admin_token
        status, msg = test_api(endpoint, None, params, method)
        print(f"  {name:<12} {status:<8} {msg[:50]}...")

    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
