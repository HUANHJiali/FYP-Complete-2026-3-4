"""
管理员看板相关视图

从 admin 视图中拆分 dashboard/cards/trends 逻辑，降低单文件复杂度。
"""

from datetime import timedelta
import itertools
import os

from django.db.models import Q
from django.utils import timezone

from app import models
from comm.BaseView import BaseView


class AdminDashboardView:
    """管理员看板接口集合"""

    @staticmethod
    def get_dashboard(request):
        try:
            total_users = models.Users.objects.count()
            total_students = models.Users.objects.filter(type=2).count()
            total_teachers = models.Users.objects.filter(type=1).count()
            total_admins = models.Users.objects.filter(type=0).count()
            total_exams = models.Exams.objects.count()
            total_questions = models.Practises.objects.count()
            total_tasks = models.Tasks.objects.count()

            now = timezone.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            monthly_exams = models.Exams.objects.filter(
                createTime__gte=month_start
            ).count()
            monthly_questions = models.Practises.objects.filter(
                createTime__gte=month_start
            ).count()
            monthly_users = models.Users.objects.filter(
                createTime__gte=month_start
            ).count()

            week_ago = now - timedelta(days=7)
            active_practice = models.StudentPracticeLogs.objects.filter(
                startTime__gte=week_ago
            ).values_list('student_id', flat=True)
            active_task = models.StudentTaskLogs.objects.filter(
                startTime__gte=week_ago
            ).values_list('student_id', flat=True)
            active_exam = models.ExamLogs.objects.filter(
                createTime__gte=week_ago
            ).values_list('student_id', flat=True)
            active_users = len(set(list(active_practice) + list(active_task) + list(active_exam)))

            ai_scoring_count = models.StudentPracticeAnswers.objects.filter(
                aiConfidence__isnull=False
            ).count()
            ai_scoring_count += models.StudentTaskAnswers.objects.filter(
                aiConfidence__isnull=False
            ).count()

            today_ai_scoring = models.StudentPracticeAnswers.objects.filter(
                aiConfidence__isnull=False,
                answerTime__gte=day_start
            ).count()
            today_ai_scoring += models.StudentTaskAnswers.objects.filter(
                aiConfidence__isnull=False,
                answerTime__gte=day_start
            ).count()

            wrong_question_practices = models.WrongQuestions.objects.count()

            today_practices = models.StudentPracticeLogs.objects.filter(startTime__gte=day_start).count()
            today_tasks = models.StudentTaskLogs.objects.filter(startTime__gte=day_start).count()
            today_completed_practices = models.StudentPracticeLogs.objects.filter(
                status='completed', endTime__gte=day_start
            ).count()
            today_completed_tasks = models.StudentTaskLogs.objects.filter(
                status='completed', endTime__gte=day_start
            ).count()

            exams_7d = models.ExamLogs.objects.filter(status=2, createTime__gte=week_ago)
            practices_7d = models.StudentPracticeLogs.objects.filter(status='completed', startTime__gte=week_ago)
            exam_scores = [entry['score'] for entry in exams_7d.values('score')]
            practice_scores = [entry['score'] for entry in practices_7d.values('score')]
            all_scores = list(itertools.chain(exam_scores, practice_scores))
            total_completed = len(all_scores)
            passed = len([score for score in all_scores if (score or 0) >= 60])
            pass_rate = round(passed / total_completed * 100, 2) if total_completed > 0 else 0

            trends_7d = {
                'days': [],
                'practices': [],
                'tasks': []
            }
            for i in range(7):
                day = now - timedelta(days=6 - i)
                day_start_obj = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end_obj = day_start_obj + timedelta(days=1)
                trends_7d['days'].append(day.strftime('%m-%d'))
                trends_7d['practices'].append(
                    models.StudentPracticeLogs.objects.filter(
                        status='completed', endTime__gte=day_start_obj, endTime__lt=day_end_obj
                    ).count()
                )
                trends_7d['tasks'].append(
                    models.StudentTaskLogs.objects.filter(
                        status='completed', endTime__gte=day_start_obj, endTime__lt=day_end_obj
                    ).count()
                )

            return BaseView.successData({
                'overview': {
                    'total_users': total_users,
                    'total_students': total_students,
                    'total_teachers': total_teachers,
                    'total_admins': total_admins,
                    'total_exams': total_exams,
                    'total_questions': total_questions,
                    'total_tasks': total_tasks,
                    'ai_scoring_count': ai_scoring_count,
                    'wrong_question_practices': wrong_question_practices,
                    'pass_rate': pass_rate
                },
                'monthly': {
                    'new_exams': monthly_exams,
                    'new_questions': monthly_questions,
                    'new_users': monthly_users
                },
                'activity': {
                    'active_users': active_users
                },
                'today': {
                    'practices': today_practices,
                    'tasks': today_tasks,
                    'completed_practices': today_completed_practices,
                    'completed_tasks': today_completed_tasks,
                    'ai_scoring': today_ai_scoring
                },
                'trends_7d': trends_7d
            })
        except Exception as e:
            return BaseView.error(f'获取仪表板数据失败: {str(e)}')

    @staticmethod
    def get_dashboard_cards(request):
        """系统首页卡片统计。"""
        try:
            now = timezone.now()
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = now - timedelta(days=7)

            today_questions = models.Practises.objects.filter(createTime__gte=day_start).count()
            today_practices = models.StudentPracticeLogs.objects.filter(startTime__gte=day_start).count()
            today_exams = models.Exams.objects.filter(createTime__gte=day_start).count()

            active_practice = models.StudentPracticeLogs.objects.filter(
                startTime__gte=week_ago
            ).values_list('student_id', flat=True)
            active_task = models.StudentTaskLogs.objects.filter(
                startTime__gte=week_ago
            ).values_list('student_id', flat=True)
            active_exam = models.ExamLogs.objects.filter(
                createTime__gte=week_ago
            ).values_list('student_id', flat=True)
            active_users = len(set(list(active_practice) + list(active_task) + list(active_exam)))

            exams_7d = models.ExamLogs.objects.filter(status=2, createTime__gte=week_ago)
            practices_7d = models.StudentPracticeLogs.objects.filter(status='completed', startTime__gte=week_ago)
            exam_scores = [entry['score'] for entry in exams_7d.values('score')]
            practice_scores = [entry['score'] for entry in practices_7d.values('score')]
            all_scores = list(itertools.chain(exam_scores, practice_scores))
            total_completed = len(all_scores)
            passed = len([score for score in all_scores if (score or 0) >= 60])
            avg_score = round(sum(all_scores) / total_completed, 2) if total_completed > 0 else 0
            pass_rate = round(passed / total_completed * 100, 2) if total_completed > 0 else 0

            threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.6'))
            pending_practice = models.StudentPracticeAnswers.objects.filter(
                Q(aiConfidence__lt=threshold) | Q(aiConfidence__isnull=True)
            ).count()
            pending_task = models.StudentTaskAnswers.objects.filter(
                Q(aiConfidence__lt=threshold) | Q(aiConfidence__isnull=True)
            ).count()
            pending_exam = models.AnswerLogs.objects.filter(status=0, practise__type__in=[1, 3]).count()
            pending_reviews = pending_practice + pending_task + pending_exam

            return BaseView.successData({
                'todayNewQuestions': today_questions,
                'todayNewPractices': today_practices,
                'todayNewExams': today_exams,
                'activeUsers7d': active_users,
                'passRate7d': pass_rate,
                'avgScore7d': avg_score,
                'pendingReviews': pending_reviews
            })
        except Exception as e:
            return BaseView.error(f'获取首页卡片失败: {str(e)}')

    @staticmethod
    def get_trends(request):
        """首页趋势数据：题目月度新增、活跃用户趋势、练习/任务完成趋势（近30天）。"""
        try:
            now = timezone.now()
            start_30d = now - timedelta(days=29)

            months = [f"{m:02d}" for m in range(1, 13)]
            questions_by_month = []
            for month in months:
                month_start = now.replace(month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
                if int(month) == 12:
                    month_end = month_start.replace(year=now.year + 1, month=1)
                else:
                    month_end = month_start.replace(month=int(month) + 1)
                cnt = models.Practises.objects.filter(
                    createTime__gte=month_start,
                    createTime__lt=month_end
                ).count()
                questions_by_month.append(cnt)

            active_daily = []
            days = []
            for i in range(30):
                day = start_30d + timedelta(days=i)
                day_start_obj = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end_obj = day_start_obj + timedelta(days=1)
                ap = models.StudentPracticeLogs.objects.filter(startTime__gte=day_start_obj, startTime__lt=day_end_obj).values_list('student_id', flat=True)
                at = models.StudentTaskLogs.objects.filter(startTime__gte=day_start_obj, startTime__lt=day_end_obj).values_list('student_id', flat=True)
                ae = models.ExamLogs.objects.filter(createTime__gte=day_start_obj, createTime__lt=day_end_obj).values_list('student_id', flat=True)
                active_daily.append(len(set(list(ap) + list(at) + list(ae))))
                days.append(day.strftime('%m-%d'))

            practice_done_daily = []
            task_done_daily = []
            for i in range(30):
                day = start_30d + timedelta(days=i)
                day_start_obj = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end_obj = day_start_obj + timedelta(days=1)
                pd = models.StudentPracticeLogs.objects.filter(status='completed', endTime__gte=day_start_obj, endTime__lt=day_end_obj).count()
                td = models.StudentTaskLogs.objects.filter(status='completed', endTime__gte=day_start_obj, endTime__lt=day_end_obj).count()
                practice_done_daily.append(pd)
                task_done_daily.append(td)

            return BaseView.successData({
                'months': months,
                'questionsByMonth': questions_by_month,
                'days': days,
                'activeUsersDaily': active_daily,
                'practiceDoneDaily': practice_done_daily,
                'taskDoneDaily': task_done_daily
            })
        except Exception as e:
            return BaseView.error(f'获取趋势数据失败: {str(e)}')
