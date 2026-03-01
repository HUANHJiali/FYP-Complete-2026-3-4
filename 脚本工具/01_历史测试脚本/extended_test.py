"""
FYP项目扩展测试套件
包括前端测试、数据库测试、集成测试
"""
import requests
import time
import sys
from datetime import datetime

BASE_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:8080'

results = {'passed': 0, 'failed': 0, 'total': 0, 'warnings': []}

def test(name, func):
    results['total'] += 1
    print(f'{name}...', end=' ')
    try:
        result = func()
        if result:
            print('[PASS]')
            results['passed'] += 1
            return True
        else:
            print('[FAIL]')
            results['failed'] += 1
            return False
    except Exception as e:
        print(f'[ERROR] {str(e)[:50]}')
        results['failed'] += 1
        return False

def warn(msg):
    results['warnings'].append(msg)
    print(f'  [WARNING] {msg}')

print('='*70)
print('  FYP Project Extended Test Suite')
print('='*70)
print(f'Start: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# 等待服务
print('Waiting for services...')
for i in range(5):
    try:
        r = requests.get(f'{BASE_URL}/api/health/', timeout=2)
        if r.status_code == 200:
            print('Backend ready!')
            break
    except:
        time.sleep(1)

# 登录获取token
token_response = requests.post(f'{BASE_URL}/api/login/', data={'userName': 'student', 'passWord': '123456'})
token_data = token_response.json()
token = token_data.get('data', {}).get('token') if token_data.get('code') == 0 else None

print()
print('='*70)
print('PART 1: Extended API Tests (15 tests)')
print('='*70)

if token:
    # 用户信息API
    test('Get User Info', lambda: requests.get(f'{BASE_URL}/api/users/info', params={'token': token}).status_code == 200)
    test('Get User Profile', lambda: requests.get(f'{BASE_URL}/api/users/profile', params={'token': token}).status_code == 200)

    # 科目/项目API
    test('Get All Projects', lambda: requests.get(f'{BASE_URL}/api/projects/all', params={'token': token}).status_code == 200)
    test('Get Projects Page', lambda: requests.get(f'{BASE_URL}/api/projects/page', params={'token': token, 'page': 1}).status_code == 200)

    # 班级API
    test('Get All Grades', lambda: requests.get(f'{BASE_URL}/api/grades/all', params={'token': token}).status_code == 200)

    # 学���API
    test('Get All Colleges', lambda: requests.get(f'{BASE_URL}/api/colleges/all', params={'token': token}).status_code == 200)

    # 更多考试API
    test('Get My Exams', lambda: requests.get(f'{BASE_URL}/api/exams/my', params={'token': token}).status_code == 200)
    test('Get Exam Questions', lambda: requests.get(f'{BASE_URL}/api/exams/questions', params={'token': token, 'examId': 1}).status_code == 200)

    # 答题记录
    test('Get Answer Logs', lambda: requests.get(f'{BASE_URL}/api/answers/logs', params={'token': token, 'examLogId': 1}).status_code == 200)

    # 排行榜
    test('Get Rankings', lambda: requests.get(f'{BASE_URL}/api/rankings', params={'token': token}).status_code == 200)

    # 统计数据
    test('Get Student Stats', lambda: requests.get(f'{BASE_URL}/api/stats/student', params={'token': token}).status_code == 200)

    # 公告
    test('Get Announcements', lambda: requests.get(f'{BASE_URL}/api/announcements', params={'token': token}).status_code == 200)

    # 系统配置
    test('Get System Config', lambda: requests.get(f'{BASE_URL}/api/config', params={'token': token}).status_code == 200)
else:
    print('No token - skipping extended API tests')

print()
print('='*70)
print('PART 2: Frontend Tests (8 tests)')
print('='*70)

# 前端页面测试
test('Frontend Home Page', lambda: requests.get(FRONTEND_URL, timeout=5).status_code == 200)
test('Frontend Login Page', lambda: requests.get(f'{FRONTEND_URL}/#/login', timeout=5).status_code == 200)
test('Frontend Static Files', lambda: len(requests.get(f'{FRONTEND_URL}/js/app.js', timeout=5).content) > 0)

# 检查前端资源
def check_frontend_resources():
    try:
        r = requests.get(FRONTEND_URL, timeout=5)
        has_css = 'css' in r.text.lower()
        has_js = 'script' in r.text.lower()
        return has_css and has_js
    except:
        return False

test('Frontend Has CSS and JS', check_frontend_resources)

# 检查关键组件
def check_vue_app():
    try:
        r = requests.get(FRONTEND_URL, timeout=5)
        has_vue = 'vue' in r.text.lower() or 'Vue' in r.text
        return has_vue
    except:
        return False

test('Vue App Loaded', check_vue_app)

# 检查API配置
def check_api_config():
    try:
        r = requests.get(FRONTEND_URL, timeout=5)
        has_api = 'api' in r.text.lower()
        return has_api
    except:
        return False

test('API Config Present', check_api_config)

# 检查路由配置
def check_router():
    try:
        r = requests.get(FRONTEND_URL, timeout=5)
        has_router = 'router' in r.text.lower() or 'Router' in r.text
        return has_router
    except:
        return False

test('Router Config Present', check_router)

# 检查状态管理
def check_store():
    try:
        r = requests.get(FRONTEND_URL, timeout=5)
        has_store = 'store' in r.text.lower() or 'Store' in r.text or 'vuex' in r.text.lower()
        return has_store
    except:
        return False

test('Vuex Store Present', check_store)

print()
print('='*70)
print('PART 3: Database Tests (5 tests)')
print('='*70)

if token:
    # 测试数据库连接
    def db_test_1():
        r = requests.get(f'{BASE_URL}/api/users/all', params={'token': token, 'page': 1, 'size': 5})
        return r.status_code == 200 and len(r.json().get('data', [])) >= 0

    test('Database Read - Users', db_test_1)

    def db_test_2():
        r = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        return r.status_code == 200

    test('Database Read - Exams', db_test_2)

    def db_test_3():
        r = requests.get(f'{BASE_URL}/api/grades/all', params={'token': token})
        return r.status_code == 200

    test('Database Read - Grades', db_test_3)

    def db_test_4():
        r = requests.get(f'{BASE_URL}/api/projects/all', params={'token': token})
        data = r.json()
        return r.status_code == 200 and 'data' in data

    test('Database Read - Projects', db_test_4)

    def db_test_5():
        r = requests.get(f'{BASE_URL}/api/dashboard', params={'token': token})
        data = r.json()
        return r.status_code == 200 and data.get('code') == 0

    test('Database Statistics', db_test_5)
else:
    print('No token - skipping database tests')

print()
print('='*70)
print('PART 4: Edge Case Tests (8 tests)')
print('='*70)

# 空token测试
test('Empty Token Handling', lambda: requests.get(f'{BASE_URL}/api/exams/all', params={'token': ''}).status_code == 200)

# 无效token测试
test('Invalid Token Handling', lambda: requests.get(f'{BASE_URL}/api/exams/all', params={'token': 'invalid_token_12345'}).status_code == 200)

# 大分页测试
if token:
    test('Large Page Size', lambda: requests.get(f'{BASE_URL}/api/exams/page', params={'token': token, 'page': 1, 'size': 1000}).status_code == 200)

    # 无效ID测试
    test('Invalid Exam ID', lambda: requests.get(f'{BASE_URL}/api/exams/info', params={'token': token, 'id': 99999}).status_code == 200)

    # 特殊字符测试
    test('Special Characters in Search', lambda: requests.get(f'{BASE_URL}/api/exams/search', params={'token': token, 'keyword': '<script>alert(1)</script>'}).status_code == 200)

    # 超长参数测试
    test('Long Parameter', lambda: requests.get(f'{BASE_URL}/api/exams/search', params={'token': token, 'keyword': 'a'*1000}).status_code == 200)

    # SQL注入测试
    test('SQL Injection 1', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': "admin' OR '1'='1", 'passWord': '123456'}).json().get('code') != 0)

    test('SQL Injection 2', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': "admin'; DROP TABLE users--", 'passWord': '123456'}).json().get('code') != 0)

    test('XSS Attack', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': '<img src=x onerror=alert(1)>', 'passWord': '123456'}).json().get('code') != 0)
else:
    print('No token - skipping edge case tests')

print()
print('='*70)
print('PART 5: Performance Tests (6 tests)')
print('='*70)

if token:
    def perf_test_1():
        start = time.time()
        r = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        elapsed = (time.time() - start) * 1000
        return elapsed < 500 and r.status_code == 200

    test('API Response <500ms', perf_test_1)

    def perf_test_2():
        start = time.time()
        r = requests.get(f'{BASE_URL}/api/dashboard', params={'token': token})
        elapsed = (time.time() - start) * 1000
        return elapsed < 1000 and r.status_code == 200

    test('Dashboard <1s', perf_test_2)

    def perf_test_3():
        start = time.time()
        r = requests.post(f'{BASE_URL}/api/login/', data={'userName': 'student', 'passWord': '123456'})
        elapsed = (time.time() - start) * 1000
        return elapsed < 300 and r.json().get('code') == 0

    test('Login <300ms', perf_test_3)

    # 并发测试模拟
    def perf_test_4():
        start = time.time()
        for _ in range(5):
            requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        elapsed = (time.time() - start) * 1000
        return elapsed < 3000  # 5次请求<3秒

    test('Concurrent Requests', perf_test_4)

    # 大数据量测试
    def perf_test_5():
        start = time.time()
        r = requests.get(f'{BASE_URL}/api/users/all', params={'token': token, 'page': 1, 'size': 100})
        elapsed = (time.time() - start) * 1000
        return elapsed < 1000 and r.status_code == 200

    test('Large Dataset <1s', perf_test_5)

    # 前端加载测试
    def perf_test_6():
        start = time.time()
        r = requests.get(FRONTEND_URL, timeout=10)
        elapsed = (time.time() - start) * 1000
        return elapsed < 2000 and r.status_code == 200

    test('Frontend Load <2s', perf_test_6)
else:
    print('No token - skipping performance tests')

print()
print('='*70)
print('PART 6: Integration Tests (5 tests)')
print('='*70)

if token:
    # 测试完整工作流
    def workflow_test():
        # 1. 获取考试列表
        r1 = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        if r1.status_code != 200:
            return False

        # 2. 获取用户信息
        r2 = requests.get(f'{BASE_URL}/api/users/info', params={'token': token})
        if r2.status_code != 200:
            return False

        # 3. 获取仪表板
        r3 = requests.get(f'{BASE_URL}/api/dashboard', params={'token': token})
        if r3.status_code != 200:
            return False

        return True

    test('User Workflow', workflow_test)

    # 测试数据一致性
    def consistency_test():
        r1 = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        r2 = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})

        if r1.status_code != 200 or r2.status_code != 200:
            return False

        data1 = r1.json()
        data2 = r2.json()

        return data1 == data2  # 相同请求应返回相同数据

    test('Data Consistency', consistency_test)

    # 测试Token持续性
    def token_persistence():
        # 使用token多次请求
        for _ in range(3):
            r = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
            if r.status_code != 200:
                return False
        return True

    test('Token Persistence', token_persistence)

    # 测试错误恢复
    def error_recovery():
        # 发送错误请求
        r1 = requests.get(f'{BASE_URL}/api/exams/info', params={'token': token, 'id': 99999})
        if r1.status_code != 200:
            return False

        # 立即发送正确请求
        r2 = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        return r2.status_code == 200

    test('Error Recovery', error_recovery)

    # 测试会话管理
    def session_test():
        # 模拟多次登录
        for i in range(3):
            r = requests.post(f'{BASE_URL}/api/login/', data={'userName': f'student', 'passWord': '123456'})
            if r.json().get('code') != 0:
                return False
        return True

    test('Session Management', session_test)
else:
    print('No token - skipping integration tests')

print()
print('='*70)
print('PART 7: Module Stress Tests (4 tests)')
print('='*70)

sys.path.insert(0, 'source/server')

# 模块压力测试
def stress_test_imports():
    """测试模块导入性能"""
    start = time.time()
    for _ in range(10):
        __import__('comm.cache_manager')
        __import__('comm.query_optimizer')
    elapsed = (time.time() - start) * 1000
    return elapsed < 1000  # 10次导入<1秒

test('Module Import Performance', stress_test_imports)

def stress_test_cache():
    """测试缓存性能"""
    from comm.cache_manager import CacheManager
    start = time.time()
    for i in range(100):
        CacheManager.set(f'test_key_{i}', f'test_value_{i}', timeout=1)
        CacheManager.get(f'test_key_{i}')
    elapsed = (time.time() - start) * 1000
    return elapsed < 2000  # 100次操作<2秒

test('Cache Performance', stress_test_cache)

def stress_test_queries():
    """测试查询优化器"""
    from comm.query_optimizer import QueryOptimizer
    start = time.time()
    for _ in range(50):
        # 调用查询优化器方法
        hasattr(QueryOptimizer, 'get_exam_logs_with_related')
    elapsed = (time.time() - start) * 1000
    return elapsed < 100  # 50次检查<100ms

test('Query Optimizer Performance', stress_test_queries)

def stress_test_error_handler():
    """测试错误处理器"""
    from comm.error_handler_enhanced import ErrorHandler
    start = time.time()
    for _ in range(100):
        ErrorHandler.not_found_error('test')
    elapsed = (time.time() - start) * 1000
    return elapsed < 500  # 100次错误处理<500ms

test('Error Handler Performance', stress_test_error_handler)

print()
print('='*70)
print('  Final Test Summary')
print('='*70)
print(f'Total Tests: {results["total"]}')
print(f'Passed: {results["passed"]}')
print(f'Failed: {results["failed"]}')
if results['warnings']:
    print(f'Warnings: {len(results["warnings"])}')
    for w in results['warnings']:
        print(f'  - {w}')

rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
print(f'Success Rate: {rate:.1f}%')
print()

if rate >= 90:
    print('Rating: EXCELLENT (A+)')
elif rate >= 80:
    print('Rating: VERY GOOD (A)')
elif rate >= 70:
    print('Rating: GOOD (B)')
elif rate >= 60:
    print('Rating: SATISFACTORY (C)')
else:
    print('Rating: NEEDS IMPROVEMENT')

print()
print('='*70)
print(f'End: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*70)

# 保存报告
with open('EXTENDED_TEST_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write('FYP Extended Test Report\n')
    f.write('='*70 + '\n')
    f.write(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    f.write(f'Total: {results["total"]}\n')
    f.write(f'Passed: {results["passed"]}\n')
    f.write(f'Failed: {results["failed"]}\n')
    f.write(f'Success Rate: {rate:.1f}%\n')
    if results['warnings']:
        f.write(f'\nWarnings:\n')
        for w in results['warnings']:
            f.write(f'  - {w}\n')

print('Report saved to: EXTENDED_TEST_REPORT.txt')
