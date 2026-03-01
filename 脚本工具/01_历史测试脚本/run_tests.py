"""
FYP项目自动测试脚本
快速验证所有功能模块
"""
import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'source/server'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

print("=" * 70)
print("  FYP项目自动测试套件")
print("=" * 70)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 测试结果
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'tests': []
}


def test_import(name, module_path):
    """测试模块导入"""
    test_name = f"导入 {name}"
    print(f"测试: {test_name}...", end=' ')

    try:
        __import__(module_path)
        print("✓ 通过")
        test_results['passed'] += 1
        test_results['tests'].append({'name': test_name, 'status': 'passed'})
        return True
    except Exception as e:
        print(f"✗ 失败: {str(e)[:50]}")
        test_results['failed'] += 1
        test_results['tests'].append({'name': test_name, 'status': 'failed', 'error': str(e)})
        return False


def test_function(name, func):
    """测试函数执行"""
    print(f"测试: {name}...", end=' ')

    try:
        result = func()
        if result:
            print("✓ 通过")
            test_results['passed'] += 1
            test_results['tests'].append({'name': test_name, 'status': 'passed'})
            return True
        else:
            print("✗ 失败: 返回值为False")
            test_results['failed'] += 1
            test_results['tests'].append({'name': test_name, 'status': 'failed'})
            return False
    except Exception as e:
        print(f"✗ 失败: {str(e)[:50]}")
        test_results['failed'] += 1
        test_results['tests'].append({'name': test_name, 'status': 'failed', 'error': str(e)})
        return False


print("【第一阶段】模块导入测试")
print("-" * 70)

# 测试基础模块
test_import("CacheManager", "comm.cache_manager")
test_import("QueryOptimizer", "comm.query_optimizer")
test_import("ErrorHandler", "comm.error_handler_enhanced")
test_import("PerformanceMonitor", "comm.performance_monitor")

print()
print("【第二阶段】功能测试")
print("-" * 70)


# 测试缓存管理器
def test_cache_basic():
    """测试基础缓存功能"""
    from comm.cache_manager import CacheManager

    # 测试设置和获取
    CacheManager.set('test_key', 'test_value', timeout=10)
    value = CacheManager.get('test_key')

    # 清理
    CacheManager.delete('test_key')

    return value == 'test_value'


test_function("CacheManager 基础功能", test_cache_basic)


def test_cache_get_or_set():
    """测试缓存获取或设置"""
    from comm.cache_manager import CacheManager

    # 第一次调用应该执行回调
    call_count = [0]

    def callback():
        call_count[0] += 1
        return 'callback_result'

    result1 = CacheManager.get_or_set('test_callback_key', callback, timeout=10)
    if call_count[0] != 1:
        return False

    # 第二次调用应该使用缓存
    result2 = CacheManager.get_or_set('test_callback_key', callback, timeout=10)
    if call_count[0] != 1:  # 没有再次调用
        return False

    # 清理
    CacheManager.delete('test_callback_key')

    return result1 == result2 == 'callback_result'


test_function("CacheManager 智能缓存", test_cache_get_or_set)


# 测试查询优化器
def test_query_optimizer():
    """测试查询优化器"""
    from comm.query_optimizer import QueryOptimizer

    # 验证类存在且方法可调用
    return hasattr(QueryOptimizer, 'get_exam_logs_with_related') and \
           hasattr(QueryOptimizer, 'get_practice_logs_with_related')


test_function("QueryOptimizer 类结构", test_query_optimizer)


# 测试错误处理器
def test_error_handler():
    """测试错误处理器"""
    from comm.error_handler_enhanced import ErrorHandler
    from django.http import JsonResponse

    # 测试错误响应创建
    response = ErrorHandler.not_found_error('测试资源不存在')

    return response.status_code == 404


test_function("ErrorHandler 错误响应", test_error_handler)


# 测试性能监控
def test_performance_monitor():
    """测试性能监控"""
    from comm.performance_monitor import PerformanceMonitorMiddleware

    # 验证中间件类存在
    return hasattr(PerformanceMonitorMiddleware, 'process_request') and \
           hasattr(PerformanceMonitorMiddleware, 'process_response')


test_function("PerformanceMonitor 中间件", test_performance_monitor)


print()
print("【第三阶段】API端点测试")
print("-" * 70)


def test_api_health():
    """测试健康检查API"""
    import requests

    try:
        response = requests.get('http://localhost:8000/api/health/', timeout=5)
        return response.status_code == 200
    except:
        return False


test_function("API 健康检查", test_api_health)


def test_api_login():
    """测试登录API"""
    import requests

    try:
        response = requests.post('http://localhost:8000/api/login/', data={
            'userName': 'student',
            'passWord': '123456'
        }, timeout=5)

        data = response.json()
        return data.get('code') == 0 and 'data' in data
    except Exception as e:
        return False


test_function("API 用户登录", test_api_login)


def test_api_exams():
    """测试考试列表API"""
    import requests

    try:
        # 先登录获取token
        login_response = requests.post('http://localhost:8000/api/login/', data={
            'userName': 'student',
            'passWord': '123456'
        }, timeout=5)

        token = login_response.json().get('data', {}).get('token')

        if not token:
            return False

        # 获取考试列表
        response = requests.get('http://localhost:8000/api/exams/all', params={
            'token': token
        }, timeout=5)

        return response.status_code == 200
    except:
        return False


test_function("API 考试列表", test_api_exams)


def test_swagger_docs():
    """测试Swagger文档"""
    import requests

    try:
        response = requests.get('http://localhost:8000/swagger/', timeout=5)
        return response.status_code == 200
    except:
        return False


test_function("Swagger 文档访问", test_swagger_docs)


def test_redoc_docs():
    """测试ReDoc文档"""
    import requests

    try:
        response = requests.get('http://localhost:8000/redoc/', timeout=5)
        return response.status_code == 200
    except:
        return False


test_function("ReDoc 文档访问", test_redoc_docs)


print()
print("=" * 70)
print("  测试结果摘要")
print("=" * 70)

total = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total * 100) if total > 0 else 0

print(f"总测试数: {total}")
print(f"通过: {test_results['passed']} ✓")
print(f"失败: {test_results['failed']} ✗")
print(f"通过率: {pass_rate:.1f}%")
print()

if pass_rate >= 80:
    print("评价: ✓ 优秀")
elif pass_rate >= 60:
    print("评价: ✓ 良好")
else:
    print("评价: ✗ 需要改进")

print()
print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 失败的测试详情
if test_results['failed'] > 0:
    print("失败的测试:")
    print("-" * 70)
    for test in test_results['tests']:
        if test['status'] == 'failed':
            error = test.get('error', '未知错误')
            print(f"  ✗ {test['name']}: {error}")
    print()

# 生成测试报告
report_file = 'test_report.txt'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("FYP项目测试报告\n")
    f.write("=" * 70 + "\n")
    f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"总测试数: {total}\n")
    f.write(f"通过: {test_results['passed']}\n")
    f.write(f"��败: {test_results['failed']}\n")
    f.write(f"通过率: {pass_rate:.1f}%\n")
    f.write("\n详细结果:\n")
    for test in test_results['tests']:
        status_symbol = "✓" if test['status'] == 'passed' else "✗"
        f.write(f"  {status_symbol} {test['name']}\n")
        if test['status'] == 'failed' and 'error' in test:
            f.write(f"    错误: {test['error']}\n")

print(f"✓ 测试报告已保存: {report_file}")
print()
print("=" * 70)
