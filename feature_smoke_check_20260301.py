import requests
from datetime import datetime

BASE = 'http://localhost:8000/api'

results = []

def record(name, ok, detail=''):
    results.append((name, ok, detail))
    print(f"{'[PASS]' if ok else '[FAIL]'} {name} {detail}")


def get_json(url, method='get', **kwargs):
    try:
        if method == 'post':
            r = requests.post(url, timeout=20, **kwargs)
        else:
            r = requests.get(url, timeout=20, **kwargs)
        data = {}
        try:
            data = r.json()
        except Exception:
            pass
        return r.status_code, data
    except Exception as exc:
        return None, {'msg': str(exc)}


def login(user, pwd):
    status, data = get_json(f'{BASE}/login/', method='post', data={'userName': user, 'passWord': pwd})
    if status == 200 and data.get('code') == 0:
        return data.get('data', {}).get('token'), data.get('msg', '')
    return None, data.get('msg', '') if isinstance(data, dict) else '登录响应异常'


def login_with_fallback(candidates, pwd):
    last_msg = ''
    for username in candidates:
        token, msg = login(username, pwd)
        if token:
            return token, msg, username
        last_msg = msg
    return None, last_msg, candidates[0] if candidates else ''


def expect_api(name, path, role_token=None, method='get', params=None, data=None, expect_code=0, allow_non_standard_success=False):
    params = params or {}
    data = data or {}
    if role_token and 'token' not in params and method == 'get':
        params['token'] = role_token
    if role_token and 'token' not in data and method == 'post':
        data['token'] = role_token

    status, payload = get_json(f'{BASE}{path}', method=method, params=params if method=='get' else None, data=data if method=='post' else None)
    if allow_non_standard_success:
        ok = (status == 200)
    else:
        ok = (status == 200 and payload.get('code') == expect_code)
    msg = payload.get('msg', '') if isinstance(payload, dict) else ''
    record(name, ok, f"status={status}, code={payload.get('code') if isinstance(payload, dict) else None}, msg={msg}")
    return ok, payload


if __name__ == '__main__':
    print('=' * 80)
    print('FYP FEATURE SMOKE CHECK 2026-03-01')
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('=' * 80)

    # Infra
    expect_api('健康检查', '/health/', allow_non_standard_success=True)
    expect_api('健康检查简版', '/health/simple/', allow_non_standard_success=True)
    expect_api('验证码接口', '/captcha/')

    # Login
    admin_token, admin_msg = login('admin', '123456')
    teacher_token, teacher_msg = login('teacher', '123456')
    student_token, student_msg, student_user = login_with_fallback(['student', 'student001', 'STUDENT001'], '123456')
    record('管理员登录', bool(admin_token), admin_msg)
    record('教师登录', bool(teacher_token), teacher_msg)
    record('学生登录', bool(student_token), f"账号={student_user} {student_msg}")

    # Sys/user
    if student_token:
        expect_api('获取当前用户信息', '/info/', role_token=student_token)

    # Base data
    grade_ids_for_compare = []
    if admin_token:
        expect_api('学院列表', '/colleges/all/', role_token=admin_token)
        ok_grades, grade_payload = expect_api('班级列表', '/grades/all/', role_token=admin_token)
        if ok_grades:
            grade_list = (grade_payload or {}).get('data') or []
            grade_ids_for_compare = [str(item.get('id')) for item in grade_list if isinstance(item, dict) and item.get('id') is not None]
        expect_api('学科列表', '/projects/all/', role_token=admin_token)

    # Users
    if admin_token:
        expect_api('学生分页', '/students/page/', role_token=admin_token, params={'pageIndex': 1, 'pageSize': 5})
        expect_api('教师分页', '/teachers/page/', role_token=admin_token, params={'pageIndex': 1, 'pageSize': 5})

    # Question bank
    if admin_token:
        ok, p = expect_api('题库分页', '/practises/page/', role_token=admin_token, params={'pageIndex': 1, 'pageSize': 10})

    # Exams
    if student_token:
        expect_api('考试分页(学生视角)', '/exams/page/', role_token=student_token, params={'pageIndex': 1, 'pageSize': 10})
        expect_api('学生考试记录分页', '/examlogs/pagestu/', role_token=student_token, params={'pageIndex': 1, 'pageSize': 10})
    if teacher_token:
        expect_api('教师考试记录分页', '/examlogs/pagetea/', role_token=teacher_token, params={'pageIndex': 1, 'pageSize': 10})

    # Practice
    if student_token:
        expect_api('学生练习试卷', '/practicepapers/student/', role_token=student_token)
        expect_api('学生练习记录', '/studentpractice/logs/', role_token=student_token)

    # Tasks
    if teacher_token:
        expect_api('任务分页', '/tasks/page/', role_token=teacher_token, params={'pageIndex': 1, 'pageSize': 10})
    if student_token:
        expect_api('学生任务列表', '/tasks/student/', role_token=student_token)

    # Wrong questions
    if student_token:
        expect_api('错题分页', '/wrongquestions/getPageInfos/', role_token=student_token, params={'page': 1, 'limit': 10})

    # AI
    if teacher_token:
        expect_api(
            'AI评分', '/ai/score_answer/', role_token=teacher_token, method='post',
            data={
                'questionContent': '判断题：1+1=2',
                'correctAnswer': '正确',
                'studentAnswer': '正确',
                'questionType': 2,
                'maxScore': 2
            }
        )
        expect_api(
            'AI出题', '/ai/generate_questions/', role_token=teacher_token, method='post',
            data={
                'subject': '数学',
                'topic': '四则运算',
                'difficulty': 'easy',
                'questionType': 0,
                'count': 1
            }
        )

    # Admin dashboard and statistics
    if admin_token:
        expect_api('管理员仪表盘', '/admin/dashboard/', role_token=admin_token)
        if len(grade_ids_for_compare) >= 2:
            expect_api('班级对比统计', '/statistics/compare_classes/', role_token=admin_token, params={'gradeIds': ','.join(grade_ids_for_compare[:2])})
        elif len(grade_ids_for_compare) == 1:
            # 测试环境可能只有1个班级：使用重复ID验证接口可用性
            gid = grade_ids_for_compare[0]
            expect_api('班级对比统计', '/statistics/compare_classes/', role_token=admin_token, params={'gradeIds': f'{gid},{gid}'})
        else:
            record('班级对比统计', False, '可用班级数量不足，至少需要2个班级')

    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = total - passed
    print('\n' + '=' * 80)
    print(f'总计: {total}, 通过: {passed}, 失败: {failed}, 通过率: {(passed/total*100 if total else 0):.1f}%')
    print('=' * 80)

    with open('FEATURE_SMOKE_REPORT_20260301.md', 'w', encoding='utf-8') as f:
        f.write('# Feature Smoke Report 2026-03-01\n\n')
        f.write(f'- 总计: {total}\n- 通过: {passed}\n- 失败: {failed}\n- 通过率: {(passed/total*100 if total else 0):.1f}%\n\n')
        f.write('## 明细\n')
        for name, ok, detail in results:
            f.write(f"- {'✅' if ok else '❌'} {name}: {detail}\n")

    print('报告已生成: FEATURE_SMOKE_REPORT_20260301.md')
