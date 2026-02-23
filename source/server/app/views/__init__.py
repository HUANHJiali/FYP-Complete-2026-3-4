"""
视图模块
按功能模块组织的视图类
优先使用拆分后的视图，如果不存在则从旧views.py导入
"""
# 导入已拆分的视图
from .sys_view import SysView
from .organization_views import CollegesView, GradesView
from .user_views import ProjectsView, TeachersView, StudentsView
from .question_views import PractisesView, OptionsView
from .exam_views import ExamsView, ExamLogsView, AnswerLogsView
from .ai_views import AIView
from .wrong_question_views import WrongQuestionsView
from .task_views import TasksView
from .practice_views import PracticePapersView, StudentPracticeView
from .admin_views import AdminView

# 为了避免循环导入，使用importlib动态导入旧视图模块
# 注意：不能直接 import app.views，因为那会导入这个包本身
import sys
import importlib.util
import os

# 获取旧views.py的路径（相对于当前文件）
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_views_py_path = os.path.join(_parent_dir, 'views.py')

# 动态加载旧视图模块
if os.path.exists(_views_py_path):
    spec = importlib.util.spec_from_file_location("app_views_old", _views_py_path)
    old_views_module = importlib.util.module_from_spec(spec)
    # 使用一个唯一的模块名避免冲突
    sys.modules['app_views_old'] = old_views_module
    spec.loader.exec_module(old_views_module)
    
    # 所有视图都已拆分完成！
    # 保留旧视图模块的动态导入代码作为回退方案（如果需要）
    # CollegesView, GradesView -> organization_views.py
    # ProjectsView, TeachersView, StudentsView -> user_views.py
    # PractisesView, OptionsView -> question_views.py
    # ExamsView, ExamLogsView, AnswerLogsView -> exam_views.py
    # AIView -> ai_views.py
    # WrongQuestionsView -> wrong_question_views.py
    # TasksView -> task_views.py
    # PracticePapersView, StudentPracticeView -> practice_views.py
    # AdminView -> admin_views.py
    AdminView = old_views_module.AdminView  # 回退导入，实际应该已被上面导入
else:
    # 如果views.py不存在，抛出错误
    raise ImportError(f"Cannot find app/views.py file at {_views_py_path}")

__all__ = [
    'SysView',
    'CollegesView',
    'GradesView',
    'ProjectsView',
    'TeachersView',
    'StudentsView',
    'PractisesView',
    'ExamsView',
    'ExamLogsView',
    'PracticePapersView',
    'TasksView',
    'WrongQuestionsView',
    'AdminView',
    'AIView',
    'OptionsView',
    'AnswerLogsView',
    'StudentPracticeView',
]
