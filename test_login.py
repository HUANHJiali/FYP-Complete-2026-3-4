"""
测试登录功能
"""
import requests

def test_login(username, password):
    """测试登录"""
    url = "http://127.0.0.1:8000/api/login/"
    data = {
        "userName": username,
        "passWord": password
    }

    print(f"\n测试登录: {username} / {'*' * len(password)}")
    print(f"请求URL: {url}")
    print(f"请求数据: {data}")

    try:
        response = requests.post(url, data=data, timeout=5)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        result = response.json()
        if result.get('code') == 0:
            print(f"[OK] Login success! Token: {result['data']['token']}")
            return True
        else:
            print(f"[FAIL] Login failed: {result.get('msg')}")
            return False
    except Exception as e:
        print(f"[ERROR] Request exception: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("登录功能测试")
    print("="*60)

    # 测试管理员
    test_login("python222", "123456")

    # 测试教师
    test_login("teacher", "123456")

    # 测试学生
    test_login("student", "123456")

    # 测试其他学生
    test_login("zhangwuji", "123456")

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
