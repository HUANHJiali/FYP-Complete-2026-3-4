# 从新的模块化视图导入（包括已拆分和未拆分的）
from app.views import (
    SysView, CollegesView, GradesView, ProjectsView,
    TeachersView, StudentsView, PractisesView, ExamsView,
    ExamLogsView, PracticePapersView, TasksView, WrongQuestionsView,
    AdminView, AIView, OptionsView, AnswerLogsView, StudentPracticeView
)
from app.views.log_views import LogViews
from app.views.health_view import health_check, health_check_simple
from app.views.import_export_views import import_students, export_students_template
from app.views.admin_views import AdminView as AdminViews
from app.views.backup_views import BackupViews
from app.views.attachment_views import TaskAttachmentViews
from app.views.theme_views import ThemeViews
from app.views.exam_monitor_views import ExamMonitorView
from app.views.captcha_views import get_captcha, check_login_status
from comm.metrics import metrics_view

from django.urls import path

urlpatterns = [
    # 监控指标（Prometheus）
    path('metrics/', metrics_view),

    # 健康检查（优先级最高）
    path('health/', health_check),
    path('health/simple/', health_check_simple),

    # 验证码API
    path('captcha/', get_captcha, name='get_captcha'),
    path('login/status/', check_login_status, name='check_login_status'),

    # 考试监控API
    path('exam-monitor/exams/', ExamMonitorView.get_active_exams, name='exam_monitor_exams'),
    path('exam-monitor/status/', ExamMonitorView.get_exam_status, name='exam_monitor_status'),
    path('exam-monitor/students/', ExamMonitorView.get_student_status, name='exam_monitor_students'),
    path('exam-monitor/questions/', ExamMonitorView.get_question_stats, name='exam_monitor_questions'),
    path('exam-monitor/realtime/', ExamMonitorView.get_realtime_data, name='exam_monitor_realtime'),

    # 系统相关（优先级最高，放在最前面）
    path('logs/', LogViews.as_view()),
    path('admin/<str:module>/', AdminView.as_view()),
    
    # 新增：统计分析API
    path('statistics/compare_classes/', AdminViews.compare_class_grades, name='compare_classes'),
    path('statistics/student_progress/', AdminViews.compare_student_progress, name='student_progress'),
    path('statistics/recommend_practice/', AdminViews.recommend_practice, name='recommend_practice'),
    path('statistics/recommend_wrong/', AdminViews.recommend_wrong_questions, name='recommend_wrong'),
    
    # 新增：备份和导出API
    path('backup/export/', BackupViews.export_system_data, name='backup_export'),
    path('report/student/', BackupViews.generate_student_report, name='student_report'),
    path('teachers/export/', BackupViews.export_teachers, name='export_teachers'),
    
    # 新增：任务附件API
    path('attachments/upload/', TaskAttachmentViews.upload_attachment, name='attachment_upload'),
    path('attachments/list/', TaskAttachmentViews.get_attachments, name='attachment_list'),
    path('attachments/download/', TaskAttachmentViews.download_attachment, name='attachment_download'),
    path('attachments/delete/', TaskAttachmentViews.delete_attachment, name='attachment_delete'),
    
    # 新增：主题设置API
    path('theme/get/', ThemeViews.get_theme, name='theme_get'),
    path('theme/save/', ThemeViews.save_theme, name='theme_save'),
    path('theme/reset/', ThemeViews.reset_theme, name='theme_reset'),

    # 基础数据管理
    path('colleges/<str:module>/', CollegesView.as_view()),
    path('grades/<str:module>/', GradesView.as_view()),
    path('projects/<str:module>/', ProjectsView.as_view()),

    # 用户管理
    path('students/<str:module>/', StudentsView.as_view()),
    path('students/import/', import_students, name='import_students'),
    path('students/export/template/', export_students_template, name='export_template'),
    path('teachers/<str:module>/', TeachersView.as_view()),

    # 题库管理
    path('practises/<str:module>/', PractisesView.as_view()),
    path('options/<str:module>/', OptionsView.as_view()),

    # 考试管理
    path('exams/<str:module>/', ExamsView.as_view()),
    path('examlogs/<str:module>/', ExamLogsView.as_view()),
    path('answerlogs/<str:module>/', AnswerLogsView.as_view()),

    # 练习管理
    path('practicepapers/<str:module>/', PracticePapersView.as_view()),
    path('studentpractice/<str:module>/', StudentPracticeView.as_view()),

    # 任务与错题
    path('tasks/<str:module>/', TasksView.as_view()),
    path('wrongquestions/<str:module>/', WrongQuestionsView.as_view()),

    # AI功能
    path('ai/<str:module>/', AIView.as_view()),

    # 通用系统路由（支持二级路径如 sys/login）
    path('<str:module>/<str:action>/', SysView.as_view()),
    path('<str:module>/', SysView.as_view()),
]
