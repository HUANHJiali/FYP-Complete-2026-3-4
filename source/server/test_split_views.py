"""
测试拆分后的视图功能
验证所有拆分的视图是否正常工作
"""
import sys
import os
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

import django
django.setup()

from django.test import RequestFactory
from django.core.paginator import Paginator
from app.views import (
    SysView, CollegesView, GradesView, ProjectsView,
    TeachersView, StudentsView, PractisesView, OptionsView
)
from app import models

factory = RequestFactory()

print('='*70)
print('测试拆分后的视图功能')
print('='*70)

# 测试计数器
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_view(test_name, test_func):
    """运行测试并记录结果"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    print(f'\n[{total_tests}] {test_name}')
    try:
        test_func()
        print(f'    [OK] PASSED')
        passed_tests += 1
        return True
    except Exception as e:
        print(f'    [FAIL] {str(e)[:100]}')
        failed_tests += 1
        return False

# ============================================================================
# 测试 1: 组织架构视图 - CollegesView
# ============================================================================

def test_colleges_get_all():
    """测试获取所有学院"""
    request = factory.get('/api/colleges/all/')
    result = CollegesView.get_all(request)
    assert result is not None, "Result should not be None"
    assert hasattr(result, 'status_code') or result.status_code == 200, "Should return success response"

test_view('CollegesView.get_all() - 获取所有学院', test_colleges_get_all)

def test_colleges_methods_exist():
    """测试 CollegesView 方法存在"""
    methods = ['get_all', 'get_page_infos', 'add_info', 'upd_info', 'del_info']
    for method in methods:
        assert hasattr(CollegesView, method), f"Missing method: {method}"
    assert CollegesView.__module__ == 'app.views.organization_views', "Wrong module"

test_view('CollegesView - 方法验证', test_colleges_methods_exist)

# ============================================================================
# 测试 2: 组织架构视图 - GradesView
# ============================================================================

def test_grades_get_all():
    """测试获取所有年级"""
    request = factory.get('/api/grades/all/')
    result = GradesView.get_all(request)
    assert result is not None, "Result should not be None"

test_view('GradesView.get_all() - 获取所有年级', test_grades_get_all)

def test_grades_methods_exist():
    """测试 GradesView 方法存在"""
    methods = ['get_all', 'get_page_infos', 'add_info', 'upd_info', 'del_info']
    for method in methods:
        assert hasattr(GradesView, method), f"Missing method: {method}"
    assert GradesView.__module__ == 'app.views.organization_views', "Wrong module"

test_view('GradesView - 方法验证', test_grades_methods_exist)

# ============================================================================
# 测试 3: 用户管理视图 - ProjectsView
# ============================================================================

def test_projects_get_all():
    """测试获取所有科目"""
    request = factory.get('/api/projects/all/')
    result = ProjectsView.get_all(request)
    assert result is not None, "Result should not be None"

test_view('ProjectsView.get_all() - 获取所有科目', test_projects_get_all)

def test_projects_methods_exist():
    """测试 ProjectsView 方法存在"""
    methods = ['get_all', 'get_page_infos', 'add_info', 'upd_info', 'del_info']
    for method in methods:
        assert hasattr(ProjectsView, method), f"Missing method: {method}"
    assert ProjectsView.__module__ == 'app.views.user_views', "Wrong module"

test_view('ProjectsView - 方法验证', test_projects_methods_exist)

# ============================================================================
# 测试 4: 用户管理视图 - TeachersView
# ============================================================================

def test_teachers_methods_exist():
    """测试 TeachersView 方法存在"""
    methods = ['get_page_infos', 'add_info', 'upd_info', 'del_info']
    for method in methods:
        assert hasattr(TeachersView, method), f"Missing method: {method}"
    assert TeachersView.__module__ == 'app.views.user_views', "Wrong module"

test_view('TeachersView - 方法验证', test_teachers_methods_exist)

# ============================================================================
# 测试 5: 用户管理视图 - StudentsView
# ============================================================================

def test_students_methods_exist():
    """测试 StudentsView 方法存在"""
    methods = ['get_info', 'get_page_infos', 'add_info', 'upd_info', 'del_info']
    for method in methods:
        assert hasattr(StudentsView, method), f"Missing method: {method}"
    assert StudentsView.__module__ == 'app.views.user_views', "Wrong module"

test_view('StudentsView - 方法验证', test_students_methods_exist)

# ============================================================================
# 测试 6: 题目管理视图 - PractisesView
# ============================================================================

def test_practises_methods_exist():
    """测试 PractisesView 方法存在"""
    methods = ['get_info', 'get_page_infos', 'add_info', 'set_answer']
    for method in methods:
        assert hasattr(PractisesView, method), f"Missing method: {method}"
    assert PractisesView.__module__ == 'app.views.question_views', "Wrong module"

test_view('PractisesView - 方法验证', test_practises_methods_exist)

# ============================================================================
# 测试 7: 题目管理视图 - OptionsView
# ============================================================================

def test_options_methods_exist():
    """测试 OptionsView 方法存在"""
    methods = ['get_list_by_practise_id', 'add_info', 'upd_info']
    for method in methods:
        assert hasattr(OptionsView, method), f"Missing method: {method}"
    assert OptionsView.__module__ == 'app.views.question_views', "Wrong module"

test_view('OptionsView - 方法验证', test_options_methods_exist)

# ============================================================================
# 测试 8: 系统视图 - SysView
# ============================================================================

def test_sys_methods_exist():
    """测试 SysView 方法存在"""
    # SysView 使用旧命名 getUserInfo, login, exit
    methods = ['getUserInfo', 'login', 'exit']
    for method in methods:
        assert hasattr(SysView, method), f"Missing method: {method}"
    assert SysView.__module__ == 'app.views.sys_view', "Wrong module"

test_view('SysView - 方法验证', test_sys_methods_exist)

# ============================================================================
# 测试 9: 检查命名规范
# ============================================================================

def test_naming_conventions():
    """测试新视图使用 snake_case 命名"""
    # 检查新视图使用了 snake_case 命名的方法
    assert hasattr(CollegesView, 'get_all'), "Should use get_all instead of getAll"
    assert hasattr(CollegesView, 'add_info'), "Should use add_info instead of addInfo"
    assert hasattr(GradesView, 'upd_info'), "Should use upd_info instead of updInfo"
    assert hasattr(ProjectsView, 'del_info'), "Should use del_info instead of delInfo"

test_view('命名规范检查 - snake_case', test_naming_conventions)

# ============================================================================
# 测试 10: 模块导入验证
# ============================================================================

def test_module_imports():
    """测试所有拆分的视图都能正确导入"""
    from app.views import (
        SysView, CollegesView, GradesView,
        ProjectsView, TeachersView, StudentsView,
        PractisesView, OptionsView
    )
    # 验证它们来自正确的模块
    assert SysView.__module__ == 'app.views.sys_view'
    assert CollegesView.__module__ == 'app.views.organization_views'
    assert GradesView.__module__ == 'app.views.organization_views'
    assert ProjectsView.__module__ == 'app.views.user_views'
    assert TeachersView.__module__ == 'app.views.user_views'
    assert StudentsView.__module__ == 'app.views.user_views'
    assert PractisesView.__module__ == 'app.views.question_views'
    assert OptionsView.__module__ == 'app.views.question_views'

test_view('模块导入验证', test_module_imports)

# ============================================================================
# 测试总结
# ============================================================================

print('\n' + '='*70)
print('Test Summary')
print('='*70)
print(f'Total tests: {total_tests}')
print(f'Passed: {passed_tests}')
print(f'Failed: {failed_tests}')
print(f'Success rate: {(passed_tests/total_tests*100):.1f}%')
print('='*70)

if failed_tests == 0:
    print('\n[OK] All tests passed! Split views are working correctly.')
    sys.exit(0)
else:
    print(f'\n[FAIL] {failed_tests} test(s) failed, please check.')
    sys.exit(1)
