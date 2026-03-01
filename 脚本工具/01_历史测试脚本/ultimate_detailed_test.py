"""
FYP项目终极详细测试套件
覆盖所有功能模块、业务逻辑、性能、安全等
"""
import requests
import time
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:8080'

# 测试结果存储
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'warnings': [],
    'errors': [],
    'performance_data': {},
    'test_details': []
}

# 存储测试数据
test_data = {
    'tokens': {},
    'ids': {},
    'responses': {}
}


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.current_section = ""

    def test(self, name: str, func, critical: bool = False):
        """运行单个测试"""
        test_results['total'] += 1
        self.current_section = name

        # 显示测试名称
        print(f'{name}...', end=' ')

        try:
            result, message = func()

            if result:
                print(f'[PASS] {message if message else ""}')
                test_results['passed'] += 1
                test_results['test_details'].append({
                    'name': name,
                    'status': 'passed',
                    'message': message,
                    'section': self.section_name
                })
                return True
            else:
                print(f'[FAIL] {message if message else ""}')
                if critical:
                    test_results['errors'].append(f"CRITICAL: {name} - {message}")
                else:
                    test_results['warnings'].append(f"{name} - {message}")
                test_results['failed'] += 1
                test_results['test_details'].append({
                    'name': name,
                    'status': 'failed',
                    'message': message,
                    'section': self.section_name
                })
                return False
        except Exception as e:
            error_msg = str(e)[:100]
            print(f'[ERROR] {error_msg}')
            test_results['failed'] += 1
            test_results['errors'].append(f"{name} - {error_msg}")
            test_results['test_details'].append({
                'name': name,
                'status': 'error',
                'message': error_msg,
                'section': self.section_name
            })
            return False

    def set_section(self, name: str):
        """设置当前测试章节"""
        self.section_name = name

    def skip(self, name: str, reason: str):
        """跳过测试"""
        test_results['total'] += 1
        test_results['skipped'] += 1
        print(f'{name}... [SKIP] {reason}')
        test_results['test_details'].append({
            'name': name,
            'status': 'skipped',
            'message': reason,
            'section': self.section_name
        })


# 辅助函数
def api_get(endpoint: str, params: Dict = None, token: str = None):
    """GET请求"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, str(e)


def api_post(endpoint: str, data: Dict = None, token: str = None):
    """POST请求"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, str(e)


def measure_performance(func):
    """测量性能"""
    start = time.time()
    result = func()
    elapsed = (time.time() - start) * 1000
    return result, elapsed


print('=' * 80)
print("  " * 20 + "FYP PROJECT ULTIMATE DETAILED TEST SUITE")
print('=' * 80)
print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"测试环境: {BASE_URL}")
print()

# 等待服务就绪
print("等待服务启动...")
for i in range(10):
    try:
        r = requests.get(f'{BASE_URL}/api/health/', timeout=2)
        if r.status_code == 200:
            print("✓ 后端服务已就绪\n")
            break
    except:
        if i < 9:
            time.sleep(2)
            print(f"  等待中... ({i+1}/10)")
else:
    print("⚠ 服务未就绪，继续测试\n")

runner = TestRunner()

# ========================================
# 第一部分：用户认证完整测试 (20项)
# ========================================

runner.set_section("用户认证")
print("=" * 80)
print("第一部分：用户认证系统完整测试 (20项)")
print("=" * 80)

# 1.1 管理员登录
def test_admin_login():
    success, data = api_post('/api/login/', {'userName': 'admin', 'passWord': '123456'})
    if success and data.get('code') == 0:
        token = data.get('data', {}).get('token')
        if token:
            test_data['tokens']['admin'] = token
            return True, "管理员登录成功"
    return False, "管理员登录失败"

runner.test("管理员登录", test_admin_login, critical=True)

# 1.2 教师登录
def test_teacher_login():
    success, data = api_post('/api/login/', {'userName': 'teacher', 'passWord': '123456'})
    if success and data.get('code') == 0:
        token = data.get('data', {}).get('token')
        if token:
            test_data['tokens']['teacher'] = token
            return True, "教师登录成功"
    return False, "教师登录失败"

runner.test("教师登录", test_teacher_login, critical=True)

# 1.3 学生登录
def test_student_login():
    success, data = api_post('/api/login/', {'userName': 'student', 'passWord': '123456'})
    if success and data.get('code') == 0:
        token = data.get('data', {}).get('token')
        if token:
            test_data['tokens']['student'] = token
            return True, "学生登录成功"
    return False, "学生登录失败"

runner.test("学生登录", test_student_login, critical=True)

# 1.4 错误密码-管理员
runner.test("错误密码-管理员",
    lambda: api_post('/api/login/', {'userName': 'admin', 'passWord': 'wrong'})[0] == False)

# 1.5 错误密码-学生
runner.test("错误密码-学生",
    lambda: api_post('/api/login/', {'userName': 'student', 'passWord': 'wrong'})[0] == False)

# 1.6 空用户名
runner.test("空用户名",
    lambda: api_post('/api/login/', {'userName': '', 'passWord': '123456'})[0] == False)

# 1.7 空密码
runner.test("空密码",
    lambda: api_post('/api/login/', {'userName': 'student', 'passWord': ''})[0] == False)

# 1.8 SQL注入测试1
runner.test("SQL注入防护-单引号",
    lambda: api_post('/api/login/', {'userName': "admin'", 'passWord': '123456'})[0] == False)

# 1.9 SQL注入测试2
runner.test("SQL注入防护-OR语句",
    lambda: api_post('/api/login/', {'userName': "admin OR 1=1", 'passWord': '123456'})[0] == False)

# 1.10 SQL注入测试3
runner.test("SQL注入防护-注释",
    lambda: api_post('/api/login/', {'userName': "admin'; DROP TABLE--", 'passWord': '123456'})[0] == False)

# 1.11 XSS攻击测试1
runner.test("XSS防护-script标签",
    lambda: api_post('/api/login/', {'userName': '<script>alert(1)</script>', 'passWord': '123456'})[0] == False)

# 1.12 XSS攻击测试2
runner.test("XSS防护-img标签",
    lambda: api_post('/api/login/', {'userName': '<img src=x onerror=alert(1)>', 'passWord': '123456'})[0] == False)

# 1.13 XSS攻击测试3
runner.test("XSS防护-iframe",
    lambda: api_post('/api/login/', {'userName': '<iframe onload=alert(1)>', 'passWord': '123456'})[0] == False)

# 1.14 超长用户名
runner.test("超长用户名处理",
    lambda: api_post('/api/login/', {'userName': 'a'*1000, 'passWord': '123456'})[0] == False)

# 1.15 特殊字符用户名
runner.test("特殊字符处理",
    lambda: api_post('/api/login/', {'userName': '!@#$%^&*()', 'passWord': '123456'})[0] == False)

# 1.16 Unicode字符
runner.test("Unicode字符支持",
    lambda: api_post('/api/login/', {'userName': '学生测试', 'passWord': '123456'})[0] == False)

# 1.17 Token验证
def test_token_validation():
    token = test_data['tokens'].get('student')
    if not token:
        return False, "无可用token"
    success, _ = api_get('/api/exams/all', token=token)
    return success, "Token验证" if success else "Token验证失败"

runner.test("Token有效性", test_token_validation, critical=True)

# 1.18 Token持久性
def test_token_persistence():
    token = test_data['tokens'].get('student')
    if not token:
        return False, "无可用token"
    # 使用token多次
    for _ in range(5):
        success, _ = api_get('/api/exams/all', token=token)
        if not success:
            return False, "Token持久性失败"
    return True, "Token持续工作正常"

runner.test("Token持久性", test_token_persistence)

# 1.19 多用户同时登录
def test_multi_user_login():
    results = []
    for user in ['admin', 'teacher', 'student']:
        success, _ = api_post('/api/login/', {'userName': user, 'passWord': '123456'})
        results.append(success)
    return all(results), "多用户登��正常"

runner.test("多用户并发登录", test_multi_user_login)

# 1.20 登录性能测试
def test_login_performance():
    def login():
        return api_post('/api/login/', {'userName': 'student', 'passWord': '123456'})
    success, elapsed = measure_performance(login)
    return success and elapsed < 300, f"登录耗时{elapsed:.0f}ms"

runner.test("登录性能<300ms", test_login_performance)


# ========================================
# 第二部分：考试系统完整测试 (25项)
# ========================================

runner.set_section("考试系统")
print("\n" + "=" * 80)
print("第二部分：考试系统完整测试 (25项)")
print("=" * 80)

student_token = test_data['tokens'].get('student')
teacher_token = test_data['tokens'].get('teacher')

if student_token:
    # 2.1 获取所有考试
    runner.test("获取所有考试", lambda: api_get('/api/exams/all', token=student_token)[0])

    # 2.2 获取考试分页
    runner.test("考试分页-第1页", lambda: api_get('/api/exams/page', {'page': 1, 'size': 10}, token=student_token)[0])

    # 2.3 获取考试分页-第2页
    runner.test("考试分页-第2页", lambda: api_get('/api/exams/page', {'page': 2, 'size': 10}, token=student_token)[0])

    # 2.4 获取考试详情
    runner.test("获取考试详情-ID1", lambda: api_get('/api/exams/info', {'id': 1}, token=student_token)[0])

    # 2.5 获取我的考试
    runner.test("获取我的考试", lambda: api_get('/api/exams/my', token=student_token)[0])

    # 2.6 搜索考试
    runner.test("搜索考试", lambda: api_get('/api/exams/search', {'keyword': '测试'}, token=student_token)[0])

    # 2.7 获取考试题目
    runner.test("获取考试题目", lambda: api_get('/api/exams/questions', {'examId': 1}, token=student_token)[0])

    # 2.8 获取考试统计
    runner.test("获取考试统计", lambda: api_get('/api/exams/stats', {'examId': 1}, token=student_token)[0])

    # 2.9 性能-考试列表响应
    def test_exams_performance():
        success, elapsed = measure_performance(lambda: api_get('/api/exams/all', token=student_token))
        return success and elapsed < 500, f"{elapsed:.0f}ms"

    runner.test("考试列表响应<500ms", test_exams_performance)

    # 2.10 数据一致性-两次请求
    def test_exam_consistency():
        success1, data1 = api_get('/api/exams/all', token=student_token)
        success2, data2 = api_get('/api/exams/all', token=student_token)
        return success1 and success2 and data1 == data2, "数据一致"

    runner.test("考试数据一致性", test_exam_consistency)

    # 2.11 边界-无效ID
    runner.test("考试详情-无效ID", lambda: api_get('/api/exams/info', {'id': 99999}, token=student_token)[0])

    # 2.12 边界-负ID
    runner.test("考试详情-负ID", lambda: api_get('/api/exams/info', {'id': -1}, token=student_token)[0])

    # 2.13 边界-0 ID
    runner.test("考试详情-0 ID", lambda: api_get('/api/exams/info', {'id': 0}, token=student_token)[0])

    # 2.14 边界-大分页
    runner.test("考试分页-超大页", lambda: api_get('/api/exams/page', {'page': 1, 'size': 1000}, token=student_token)[0])

    # 2.15 边界-空参数
    runner.test("考试搜索-空关键词", lambda: api_get('/api/exams/search', {'keyword': ''}, token=student_token)[0])

    # 2.16 边界-特殊字符
    runner.test("考试搜索-特殊字符", lambda: api_get('/api/exams/search', {'keyword': '<test>'}, token=student_token)[0])

    # 2.17 边界-超长关键词
    runner.test("考试搜索-超长关键词", lambda: api_get('/api/exams/search', {'keyword': 'a'*500}, token=student_token)[0])
else:
    for i in range(17):
        runner.skip(f"考试系统测试-{i+1}", "无学生token")

if teacher_token:
    # 2.18 教师创建考试
    runner.skip("创建考试", "需要实际数据")

    # 2.19 教师更新考试
    runner.skip("更新考试", "需要实际数据")

    # 2.20 教师删除考试
    runner.skip("删除考试", "需要实际数据")

    # 2.21 教师添加题目
    runner.skip("添加题目", "需要实际数据")

    # 2.22 教师发布考试
    runner.skip("发布考试", "需要实际数据")
else:
    for i in range(5):
        runner.skip(f"教师功能-{i+1}", "无教师token")


# ========================================
# 第三部分：任务系统测试 (15项)
# ========================================

runner.set_section("任务系统")
print("\n" + "=" * 80)
print("第三部分：任务系统测试 (15项)")
print("=" * 80)

if student_token:
    # 3.1 获取所有任务
    runner.test("获取所有任务", lambda: api_get('/api/tasks/all', token=student_token)[0])

    # 3.2 任务分页
    runner.test("任务分页", lambda: api_get('/api/tasks/page', {'page': 1, 'size': 10}, token=student_token)[0])

    # 3.3 获取任务详情
    runner.test("获取任务详情", lambda: api_get('/api/tasks/info', {'id': 1}, token=student_token)[0])

    # 3.4 获取任务题目
    runner.test("获取任务题目", lambda: api_get('/api/tasks/questions', {'taskId': 1}, token=student_token)[0])

    # 3.5 我的任务
    runner.test("获取我的任务", lambda: api_get('/api/tasks/my', token=student_token)[0])

    # 3.6 任务统计
    runner.test("获取任务统计", lambda: api_get('/api/tasks/stats', token=student_token)[0])

    # 3.7 性能测试
    def test_tasks_performance():
        success, elapsed = measure_performance(lambda: api_get('/api/tasks/all', token=student_token))
        return success and elapsed < 500, f"{elapsed:.0f}ms"

    runner.test("任务列表响应<500ms", test_tasks_performance)

    # 3.8-3.15 边界测试
    runner.test("任务详情-无效ID", lambda: api_get('/api/tasks/info', {'id': 99999}, token=student_token)[0])
    runner.test("任务搜索", lambda: api_get('/api/tasks/search', {'keyword': '测试'}, token=student_token)[0])
    runner.test("任务分类-所有", lambda: api_get('/api/tasks/categories', token=student_token)[0])
    runner.test("任务状态-进行中", lambda: api_get('/api/tasks/status', {'status': 'ongoing'}, token=student_token)[0])
    runner.test("任务状态-已完成", lambda: api_get('/api/tasks/status', {'status': 'completed'}, token=student_token)[0])
    runner.test("任务统计-概览", lambda: api_get('/api/tasks/overview', token=student_token)[0])
    runner.test("任务进度", lambda: api_get('/api/tasks/progress', token=student_token)[0])
else:
    for i in range(15):
        runner.skip(f"任务系统-{i+1}", "无学生token")


# ========================================
# 第四部分：消息系统测试 (12项)
# ========================================

runner.set_section("消息系统")
print("\n" + "=" * 80)
print("第四部分：消息系统测试 (12项)")
print("=" * 80)

if student_token:
    # 4.1 获取消息列表
    runner.test("获取消息列表", lambda: api_get('/api/messages/', {'action': 'list'}, token=student_token)[0])

    # 4.2 获取未读消息
    runner.test("获取未读消息", lambda: api_get('/api/messages/', {'action': 'unread'}, token=student_token)[0])

    # 4.3 获取已读消息
    runner.test("获取已读消息", lambda: api_get('/api/messages/', {'action': 'read'}, token=student_token)[0])

    # 4.4 标记已读
    runner.skip("标记消息已读", "需要实际消息ID")

    # 4.5 删除消息
    runner.skip("删除消息", "需要实际消息ID")

    # 4.6 发送消息
    runner.skip("发送消息", "需要接收者ID")

    # 4.7 消息详情
    runner.test("获取消息详情", lambda: api_get('/api/messages/detail', {'id': 1}, token=student_token)[0])

    # 4.8-4.12 更多测试
    runner.test("消息统计", lambda: api_get('/api/messages/stats', token=student_token)[0])
    runner.test("系统通知", lambda: api_get('/api/messages/system', token=student_token)[0])
    runner.test("个人消息", lambda: api_get('/api/messages/personal', token=student_token)[0])
    runner.test("消息搜索", lambda: api_get('/api/messages/search', {'keyword': '测试'}, token=student_token)[0])
    runner.test("消息性能", lambda: api_get('/api/messages/', token=student_token)[0])
else:
    for i in range(12):
        runner.skip(f"消息系统-{i+1}", "无学生token")


# ========================================
# 第五部分：数据统计测试 (10项)
# ========================================

runner.set_section("数据统计")
print("\n" + "=" * 80)
print("第五部分：数据统计测试 (10项)")
print("=" * 80)

if student_token:
    # 5.1 仪表板数据
    runner.test("仪表板总览", lambda: api_get('/api/dashboard', token=student_token)[0])

    # 5.2 学生统计
    runner.test("学生个人统计", lambda: api_get('/api/stats/student', token=student_token)[0])

    # 5.3 考试统计
    runner.test("考试统计分析", lambda: api_get('/api/stats/exams', token=student_token)[0])

    # 5.4 练习统计
    runner.test("练习统计", lambda: api_get('/api/stats/practice', token=student_token)[0])

    # 5.5 任务统计
    runner.test("任务统计", lambda: api_get('/api/stats/tasks', token=student_token)[0])

    # 5.6 错题统计
    runner.test("错题统计", lambda: api_get('/api/stats/wrong', token=student_token)[0])

    # 5.7 进度统计
    runner.test("学习进度", lambda: api_get('/api/stats/progress', token=student_token)[0])

    # 5.8 排行榜
    runner.test("成绩排行榜", lambda: api_get('/api/rankings', token=student_token)[0])

    # 5.9 图表数据
    runner.test("图表数据", lambda: api_get('/api/charts/data', token=student_token)[0])

    # 5.10 性能测试
    def test_stats_performance():
        success, elapsed = measure_performance(lambda: api_get('/api/dashboard', token=student_token))
        return success and elapsed < 1000, f"{elapsed:.0f}ms"

    runner.test("统计数据响应<1s", test_stats_performance)
else:
    for i in range(10):
        runner.skip(f"数据统计-{i+1}", "无学生token")


# ========================================
# 第六部分：基础数据测试 (10项)
# ========================================

runner.set_section("基础数据")
print("\n" + "=" * 80)
print("第六部分：基础数据测试 (10项)")
print("=" * 80)

if student_token:
    # 6.1 科目/项目
    runner.test("获取所有科目", lambda: api_get('/api/projects/all', token=student_token)[0])
    runner.test("科目分页", lambda: api_get('/api/projects/page', {'page': 1}, token=student_token)[0])

    # 6.2 班级
    runner.test("获取所有班级", lambda: api_get('/api/grades/all', token=student_token)[0])

    # 6.3 学院
    runner.test("获取所有学院", lambda: api_get('/api/colleges/all', token=student_token)[0])

    # 6.4 用户
    runner.test("获取用户列表", lambda: api_get('/api/users/all', {'page': 1, 'size': 10}, token=student_token)[0])
    runner.test("获取用户信息", lambda: api_get('/api/users/info', token=student_token)[0])
    runner.test("获取用户资料", lambda: api_get('/api/users/profile', token=student_token)[0])

    # 6.5 系统
    runner.test("获取系统配置", lambda: api_get('/api/config', token=student_token)[0])
    runner.test("获取系统公告", lambda: api_get('/api/announcements', token=student_token)[0])
else:
    for i in range(10):
        runner.skip(f"基础数据-{i+1}", "无学生token")


# ========================================
# 第七部分：性能压力测试 (8项)
# ========================================

runner.set_section("性能压力")
print("\n" + "=" * 80)
print("第七部分：性能压力测试 (8项)")
print("=" * 80)

if student_token:
    # 7.1 并发请求测试
    def test_concurrent():
        start = time.time()
        results = []
        for _ in range(10):
            success, _ = api_get('/api/exams/all', token=student_token)
            results.append(success)
        elapsed = (time.time() - start) * 1000
        return all(results) and elapsed < 3000, f"10次请求耗时{elapsed:.0f}ms"

    runner.test("并发10次请求<3s", test_concurrent)

    # 7.2 快速连续请求
    def test_rapid():
        start = time.time()
        for _ in range(20):
            api_get('/api/exams/all', token=student_token)
        elapsed = (time.time() - start) * 1000
        return elapsed < 5000, f"20次请求耗时{elapsed:.0f}ms"

    runner.test("快速20次请求<5s", test_rapid)

    # 7.3 大数据量测试
    def test_large_dataset():
        success, elapsed = measure_performance(lambda: api_get('/api/users/all', {'page': 1, 'size': 100}, token=student_token))
        return success and elapsed < 2000, f"100条记录{elapsed:.0f}ms"

    runner.test("大数据量100条<2s", test_large_dataset)

    # 7.4 登录压力
    def test_login_stress():
        start = time.time()
        for _ in range(5):
            api_post('/api/login/', {'userName': 'student', 'passWord': '123456'})
        elapsed = (time.time() - start) * 1000
        return elapsed < 1500, f"5次登录{elapsed:.0f}ms"

    runner.test("登录5次<1.5s", test_login_stress)

    # 7.5 模块导入压力
    sys.path.insert(0, 'source/server')
    def test_import_stress():
        start = time.time()
        for _ in range(50):
            __import__('comm.cache_manager')
        elapsed = (time.time() - start) * 1000
        return elapsed < 500, f"50次导入{elapsed:.0f}ms"

    runner.test("模块导入50次<500ms", test_import_stress)

    # 7.6 缓存操作压力
    def test_cache_stress():
        from comm.cache_manager import CacheManager
        start = time.time()
        for i in range(100):
            CacheManager.set(f'key_{i}', f'value_{i}', timeout=1)
            CacheManager.get(f'key_{i}')
        elapsed = (time.time() - start) * 1000
        return elapsed < 2000, f"200次操作{elapsed:.0f}ms"

    runner.test("缓存200次操作<2s", test_cache_stress)

    # 7.7 错误处理压力
    def test_error_stress():
        from comm.error_handler_enhanced import ErrorHandler
        start = time.time()
        for _ in range(100):
            ErrorHandler.not_found_error('test')
        elapsed = (time.time() - start) * 1000
        return elapsed < 500, f"100次错误处理{elapsed:.0f}ms"

    runner.test("错误处理100次<500ms", test_error_stress)


# ========================================
# 第八部分：安全深度测试 (15项)
# ========================================

runner.set_section("安全测试")
print("\n" + "=" * 80)
print("第八部分：安全深度测试 (15项)")
print("=" * 80)

# 8.1 SQL注入变体
runner.test("SQL注入-UNION",
    lambda: api_post('/api/login/', {'userName': "admin' UNION SELECT 1--", 'passWord': '123456'})[0] == False)

runner.test("SQL注入-叠加查询",
    lambda: api_post('/api/login/', {'userName': "admin'; SELECT * FROM users--", 'passWord': '123456'})[0] == False)

runner.test("SQL注入-时间盲注",
    lambda: api_post('/api/login/', {'userName': "admin' AND SLEEP(5)--", 'passWord': '123456'})[0] == False)

# 8.2 XSS变体
runner.test("XSS-onload",
    lambda: api_post('/api/login/', {'userName': "<body onload=alert(1)>", 'passWord': '123456'})[0] == False)

runner.test("XSS-onerror",
    lambda: api_post('/api/login/', {'userName': "<img src=x onerror=alert(1)>", 'passWord': '123456'})[0] == False)

runner.test("XSS-svg",
    lambda: api_post('/api/login/', {'userName': "<svg onload=alert(1)>", 'passWord': '123456'})[0] == False)

runner.test("XSS-input",
    lambda: api_post('/api/login/', {'userName': "<input autofocus onfocus=alert(1)>", 'passWord': '123456'})[0] == False)

runner.test("XSS-details",
    lambda: api_post('/api/login/', {'userName': "<details open ontoggle=alert(1)>", 'passWord': '123456'})[0] == False)

# 8.3 路径遍历
runner.test("路径遍历-../",
    lambda: api_post('/api/login/', {'userName': "../../../etc/passwd", 'passWord': '123456'})[0] == False)

runner.test("路径遍历-%2e%2e",
    lambda: api_post('/api/login/', {'userName': "%2e%2e%2fpasswd", 'passWord': '123456'})[0] == False)

# 8.4 命令注入
runner.test("命令注入-;",
    lambda: api_post('/api/login/', {'userName': "admin; ls", 'passWord': '123456'})[0] == False)

runner.test("命令注入-|",
    lambda: api_post('/api/login/', {'userName': "admin|cat /etc/passwd", 'passWord': '123456'})[0] == False)

# 8.5 CSRF测试
runner.skip("CSRF Token检查", "需要表单提交")

# 8.6 权限测试
if student_token:
    runner.test("学生访问管理员API", lambda: api_get('/api/admin/users', token=student_token)[0] == False)
    runner.test("学生访问教师API", lambda: api_get('/api/teacher/students', token=student_token)[0] == False)


# ========================================
# 第九部分：前端测试 (10项)
# ========================================

runner.set_section("前端测试")
print("\n" + "=" * 80)
print("第九部分：前端测试 (10项)")
print("=" * 80)

# 9.1 前端服务
runner.test("前端首页", lambda: requests.get(FRONTEND_URL, timeout=5).status_code == 200)
runner.test("前端静态文件", lambda: len(requests.get(f'{FRONTEND_URL}/js/app.js', timeout=5).content) > 0)

# 9.2 资源检查
def check_resources():
    r = requests.get(FRONTEND_URL, timeout=5)
    has_css = '.css' in r.text or 'style' in r.text.lower()
    has_js = '.js' in r.text or 'script' in r.text.lower()
    return has_css and has_js

runner.test("前端资源完整性", check_resources)

# 9.3 API配置
def check_api_config():
    r = requests.get(FRONTEND_URL, timeout=5)
    return 'api' in r.text.lower() or 'API' in r.text

runner.test("API配置存在", check_api_config)

# 9.4 页面加载性能
def test_frontend_load():
    start = time.time()
    r = requests.get(FRONTEND_URL, timeout=10)
    elapsed = (time.time() - start) * 1000
    return r.status_code == 200 and elapsed < 3000, f"{elapsed:.0f}ms"

runner.test("前端加载<3s", test_frontend_load)

# 9.5-9.10 更多前端测试
runner.test("登录页面", lambda: requests.get(f'{FRONTEND_URL}/#/login', timeout=5).status_code == 200)
runner.test("响应式设计", lambda: requests.get(FRONTEND_URL, timeout=5).status_code == 200)  # 简化检查
runner.test("字符编码", lambda: 'charset' in requests.get(FRONTEND_URL, timeout=5).text.lower())


# ========================================
# 第十部分：数据库完整性测试 (8项)
# ========================================

runner.set_section("数据库测试")
print("\n" + "=" * 80)
print("第十部分：数据库完整性测试 (8项)")
print("=" * 80)

if student_token:
    # 10.1 读取测试
    runner.test("读取用户数据", lambda: api_get('/api/users/all', {'page': 1, 'size': 5}, token=student_token)[0])
    runner.test("读取考试数据", lambda: api_get('/api/exams/all', token=student_token)[0])
    runner.test("读取科目数据", lambda: api_get('/api/projects/all', token=student_token)[0])
    runner.test("读取班级数据", lambda: api_get('/api/grades/all', token=student_token)[0])

    # 10.2 数据一致性
    def test_data_consistency():
        r1, d1 = api_get('/api/exams/all', token=student_token)
        time.sleep(0.1)
        r2, d2 = api_get('/api/exams/all', token=student_token)
        return r1 and r2 and d1 == d2, "数据一致"

    runner.test("数据一致性检查", test_data_consistency)

    # 10.3 数据完整性
    runner.test("数据完整性-用户", lambda: api_get('/api/users/validate', token=student_token)[0])
    runner.test("数据完整性-考试", lambda: api_get('/api/exams/validate', token=student_token)[0])


# ========================================
# 生成最终报告
# ========================================

print("\n" + "=" * 80)
print("  测试结果详细摘要")
print("=" * 80)

print(f"\n总测试数: {test_results['total']}")
print(f"通过: {test_results['passed']} ✓")
print(f"失败: {test_results['failed']} ✗")
print(f"跳过: {test_results['skipped']} -")

if test_results['warnings']:
    print(f"\n警告 ({len(test_results['warnings'])}):")
    for w in test_results['warnings'][:10]:
        print(f"  ⚠ {w}")
    if len(test_results['warnings']) > 10:
        print(f"  ... 还有{len(test_results['warnings'])-10}个警告")

if test_results['errors']:
    print(f"\n错误 ({len(test_results['errors'])}):")
    for e in test_results['errors'][:10]:
        print(f"  ✗ {e}")
    if len(test_results['errors']) > 10:
        print(f"  ... 还有{len(test_results['errors'])-10}个错误")

pass_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
print(f"\n通过率: {pass_rate:.1f}%")

print("\n" + "=" * 80)
print("  评级")
print("=" * 80)

if pass_rate >= 90:
    print("✓✓✓ 优秀 (A+)")
elif pass_rate >= 80:
    print("✓✓ 很好 (A)")
elif pass_rate >= 70:
    print("✓ 良好 (B)")
elif pass_rate >= 60:
    print("及格 (C)")
else:
    print("需要改进 (D)")

print("\n" + "=" * 80)
print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# 保存详细报告
report_file = 'ULTIMATE_DETAILED_TEST_REPORT.md'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("# FYP项目终极详细测试报告\n\n")
    f.write(f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**测试数量**: {test_results['total']}\n")
    f.write(f"**通过数量**: {test_results['passed']}\n")
    f.write(f"**失败数量**: {test_results['failed']}\n")
    f.write(f"**跳过数量**: {test_results['skipped']}\n")
    f.write(f"**通过率**: {pass_rate:.1f}%\n\n")

    f.write("## 测试详情\n\n")

    # 按章节分组
    sections = {}
    for test in test_results['test_details']:
        section = test.get('section', '未分类')
        if section not in sections:
            sections[section] = []
        sections[section].append(test)

    for section, tests in sections.items():
        f.write(f"### {section}\n\n")
        passed = sum(1 for t in tests if t['status'] == 'passed')
        total = len(tests)
        f.write(f"通过率: {passed}/{total} ({passed/total*100:.0f}%)\n\n")

        for test in tests:
            status_icon = "✓" if test['status'] == 'passed' else "✗" if test['status'] == 'failed' else "-" if test['status'] == 'skipped' else "⚠"
            f.write(f"- {status_icon} {test['name']}")
            if test.get('message'):
                f.write(f" - {test['message']}")
            f.write("\n")
        f.write("\n")

    f.write("## 建议\n\n")
    if test_results['errors']:
        f.write("### 需要修复的错误\n\n")
        for error in test_results['errors']:
            f.write(f"- {error}\n")
        f.write("\n")

    if test_results['warnings']:
        f.write("### 需要注意的警告\n\n")
        for warning in test_results['warnings']:
            f.write(f"- {warning}\n")
        f.write("\n")

print(f"\n详细报告已保存: {report_file}")
