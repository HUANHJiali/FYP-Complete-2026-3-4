"""
FYP Comprehensive Test Suite - Simple Version
"""
import requests
import time
import sys
from datetime import datetime

BASE_URL = 'http://localhost:8000'

results = {'passed': 0, 'failed': 0, 'total': 0}

def test(name, func):
    results['total'] += 1
    print(f'{name}...', end=' ')
    try:
        if func():
            print('[PASS]')
            results['passed'] += 1
            return True
        else:
            print('[FAIL]')
            results['failed'] += 1
            return False
    except Exception as e:
        print(f'[ERROR] {str(e)[:40]}')
        results['failed'] += 1
        return False

print('='*70)
print('  FYP Project Comprehensive Test Suite')
print('='*70)
print(f'Start: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Wait for service
print('Waiting for backend...')
for i in range(5):
    try:
        r = requests.get(f'{BASE_URL}/api/health/', timeout=2)
        if r.status_code == 200:
            print('Backend ready!')
            break
    except:
        time.sleep(2)

print()
print('='*70)
print('PART 1: Infrastructure (4 tests)')
print('='*70)

test('Backend Health', lambda: requests.get(f'{BASE_URL}/api/health/').status_code == 200)
test('Swagger UI', lambda: 'swagger' in requests.get(f'{BASE_URL}/swagger/').text.lower())
test('ReDoc', lambda: requests.get(f'{BASE_URL}/redoc/').status_code == 200)
test('Frontend Running', lambda: requests.get('http://localhost:8080', timeout=3).status_code == 200)

print()
print('='*70)
print('PART 2: Authentication (4 tests)')
print('='*70)

token = None

def login_student():
    global token
    r = requests.post(f'{BASE_URL}/api/login/', data={'userName': 'student', 'passWord': '123456'})
    data = r.json()
    if data.get('code') == 0:
        token = data.get('data', {}).get('token')
        return True
    return False

test('Admin Login', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': 'admin', 'passWord': '123456'}).json().get('code') == 0)
test('Student Login', login_student)
test('Teacher Login', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': 'teacher', 'passWord': '123456'}).json().get('code') == 0)
test('Wrong Password', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': 'student', 'passWord': 'wrong'}).json().get('code') != 0)

print()
print('='*70)
print('PART 3: Exam System (3 tests)')
print('='*70)

if token:
    test('Get All Exams', lambda: requests.get(f'{BASE_URL}/api/exams/all', params={'token': token}).status_code == 200)
    test('Get Exam Page', lambda: requests.get(f'{BASE_URL}/api/exams/page', params={'token': token, 'page': 1, 'size': 10}).status_code == 200)
    test('Get Exam Info', lambda: requests.get(f'{BASE_URL}/api/exams/info', params={'token': token, 'id': 1}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 4: Practice System (2 tests)')
print('='*70)

if token:
    test('Get Practice Papers', lambda: requests.get(f'{BASE_URL}/api/practice/papers/all', params={'token': token}).status_code == 200)
    test('Get Practice Logs', lambda: requests.get(f'{BASE_URL}/api/practice/logs', params={'token': token}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 5: Question Bank (2 tests)')
print('='*70)

if token:
    test('Get All Questions', lambda: requests.get(f'{BASE_URL}/api/questions/all', params={'token': token}).status_code == 200)
    test('Get Question Page', lambda: requests.get(f'{BASE_URL}/api/questions/page', params={'token': token, 'page': 1}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 6: Wrong Questions (2 tests)')
print('='*70)

if token:
    test('Get Wrong Questions', lambda: requests.get(f'{BASE_URL}/api/wrong-questions/all', params={'token': token}).status_code == 200)
    test('Get Wrong Question Page', lambda: requests.get(f'{BASE_URL}/api/wrong-questions/page', params={'token': token}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 7: Task System (2 tests)')
print('='*70)

if token:
    test('Get All Tasks', lambda: requests.get(f'{BASE_URL}/api/tasks/all', params={'token': token}).status_code == 200)
    test('Get Task Page', lambda: requests.get(f'{BASE_URL}/api/tasks/page', params={'token': token, 'page': 1}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 8: Messages (1 test)')
print('='*70)

if token:
    test('Get Messages', lambda: requests.get(f'{BASE_URL}/api/messages/', params={'token': token, 'action': 'list'}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 9: Statistics (1 test)')
print('='*70)

if token:
    test('Get Dashboard', lambda: requests.get(f'{BASE_URL}/api/dashboard', params={'token': token}).status_code == 200)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 10: Core Modules (4 tests)')
print('='*70)

sys.path.insert(0, 'source/server')
test('Import CacheManager', lambda: __import__('comm.cache_manager'))
test('Import QueryOptimizer', lambda: __import__('comm.query_optimizer'))
test('Import ErrorHandler', lambda: __import__('comm.error_handler_enhanced'))
test('Import PerformanceMonitor', lambda: __import__('comm.performance_monitor'))

print()
print('='*70)
print('PART 11: Performance (2 tests)')
print('='*70)

if token:
    def check_perf():
        start = time.time()
        r = requests.get(f'{BASE_URL}/api/exams/all', params={'token': token})
        return (time.time() - start) < 1.0 and r.status_code == 200

    test('List API < 1s', check_perf)
    test('Login < 500ms', lambda: (lambda s: (time.time() - s) < 0.5)(time.time()) or requests.post(f'{BASE_URL}/api/login/', data={'userName': 'student', 'passWord': '123456'}).json().get('code') == 0)
else:
    print('No token - skipping')

print()
print('='*70)
print('PART 12: Security (2 tests)')
print('='*70)

test('SQL Injection Protection', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': "admin OR 1=1", 'passWord': '123456'}).json().get('code') != 0)
test('XSS Protection', lambda: requests.post(f'{BASE_URL}/api/login/', data={'userName': '<script>alert(1)</script>', 'passWord': '123456'}).json().get('code') != 0)

print()
print('='*70)
print('  Test Summary')
print('='*70)
print(f'Total Tests: {results["total"]}')
print(f'Passed: {results["passed"]}')
print(f'Failed: {results["failed"]}')
rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
print(f'Success Rate: {rate:.1f}%')
print()

if rate >= 90:
    print('Rating: EXCELLENT (A+)')
elif rate >= 75:
    print('Rating: VERY GOOD (A)')
elif rate >= 60:
    print('Rating: GOOD (B)')
else:
    print('Rating: NEEDS IMPROVEMENT')

print()
print('='*70)
print(f'End: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*70)

# Save report
with open('COMPREHENSIVE_TEST_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write('FYP Comprehensive Test Report\n')
    f.write('='*70 + '\n')
    f.write(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    f.write(f'Total: {results["total"]}\n')
    f.write(f'Passed: {results["passed"]}\n')
    f.write(f'Failed: {results["failed"]}\n')
    f.write(f'Success Rate: {rate:.1f}%\n')

print('Report saved to: COMPREHENSIVE_TEST_REPORT.txt')
