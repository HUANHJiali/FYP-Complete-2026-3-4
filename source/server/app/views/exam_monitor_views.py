"""
考试监控视图
实时监控考试状态、学生答题进度等
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg, Max, Min
from django.core.paginator import Paginator
from datetime import datetime
import json

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView


class ExamMonitorView:
    """考试监控视图"""
    
    @staticmethod
    @require_http_methods(['GET'])
    def get_active_exams(request):
        """获取进行中的考试列表"""
        try:
            user = get_user_from_request(request)
            if not user or user.type not in [0, 1]:
                return BaseView.error('权限不足')
            
            now = datetime.now()
            current_time = now.strftime('%Y-%m-%d %H:%M:%S')
            
            query = Q()
            if user.type == 1:
                query = Q(teacher__id=user.id)
            
            exams = models.Exams.objects.filter(query).order_by('-createTime')[:20]
            
            exam_list = []
            for exam in exams:
                student_count = models.Students.objects.filter(grade=exam.grade).count()
                submitted_count = models.ExamLogs.objects.filter(
                    exam=exam, 
                    status__in=[1, 2]
                ).count()
                in_progress_count = models.ExamLogs.objects.filter(
                    exam=exam, 
                    status=0
                ).count()
                
                exam_list.append({
                    'id': exam.id,
                    'name': exam.name,
                    'examTime': exam.examTime,
                    'startTime': exam.startTime,
                    'endTime': exam.endTime,
                    'gradeName': exam.grade.name if exam.grade else '',
                    'projectName': exam.project.name if exam.project else '',
                    'teacherName': exam.teacher.name if exam.teacher else '',
                    'totalStudents': student_count,
                    'submittedCount': submitted_count,
                    'inProgressCount': in_progress_count,
                    'notStartedCount': student_count - submitted_count - in_progress_count,
                    'submitRate': round(submitted_count / student_count * 100, 1) if student_count > 0 else 0
                })
            
            return BaseView.successData(exam_list)
        except Exception as e:
            return BaseView.error(f'获取考试列表失败: {str(e)}')
    
    @staticmethod
    @require_http_methods(['GET'])
    def get_exam_status(request):
        """获取考试实时状态统计"""
        try:
            user = get_user_from_request(request)
            if not user or user.type not in [0, 1]:
                return BaseView.error('权限不足')
            
            exam_id = request.GET.get('examId')
            if not exam_id:
                return BaseView.error('缺少考试ID')
            
            exam = models.Exams.objects.filter(id=exam_id).first()
            if not exam:
                return BaseView.error('考试不存在')
            
            student_count = models.Students.objects.filter(grade=exam.grade).count()
            
            submitted = models.ExamLogs.objects.filter(exam=exam, status__in=[1, 2])
            submitted_count = submitted.count()
            
            in_progress = models.ExamLogs.objects.filter(exam=exam, status=0)
            in_progress_count = in_progress.count()
            
            avg_score = submitted.aggregate(avg=Avg('score'))['avg'] or 0
            max_score = submitted.aggregate(max=Max('score'))['max'] or 0
            min_score = submitted.aggregate(min=Min('score'))['min'] or 0
            
            answer_stats = models.AnswerLogs.objects.filter(exam=exam).aggregate(
                total=Count('id'),
                correct=Count('id', filter=Q(status=1))
            )
            
            return BaseView.successData({
                'examId': exam.id,
                'examName': exam.name,
                'examTime': exam.examTime,
                'totalStudents': student_count,
                'submittedCount': submitted_count,
                'inProgressCount': in_progress_count,
                'notStartedCount': student_count - submitted_count - in_progress_count,
                'submitRate': round(submitted_count / student_count * 100, 1) if student_count > 0 else 0,
                'avgScore': round(avg_score, 1),
                'maxScore': round(max_score, 1),
                'minScore': round(min_score, 1),
                'totalAnswers': answer_stats['total'] or 0,
                'correctAnswers': answer_stats['correct'] or 0,
                'correctRate': round((answer_stats['correct'] or 0) / (answer_stats['total'] or 1) * 100, 1)
            })
        except Exception as e:
            return BaseView.error(f'获取考试状态失败: {str(e)}')
    
    @staticmethod
    @require_http_methods(['GET'])
    def get_student_status(request):
        """获取考试中学生状态列表"""
        try:
            user = get_user_from_request(request)
            if not user or user.type not in [0, 1]:
                return BaseView.error('权限不足')
            
            exam_id = request.GET.get('examId')
            page_index = int(request.GET.get('pageIndex', 1))
            page_size = int(request.GET.get('pageSize', 20))
            status_filter = request.GET.get('status', '')
            
            if not exam_id:
                return BaseView.error('缺少考试ID')
            
            exam = models.Exams.objects.filter(id=exam_id).first()
            if not exam:
                return BaseView.error('考试不存在')
            
            students = models.Students.objects.filter(grade=exam.grade).select_related('user')
            
            student_list = []
            for student in students:
                if not student.user:
                    continue
                    
                exam_log = models.ExamLogs.objects.filter(
                    exam=exam, 
                    student=student.user
                ).first()
                
                answer_count = models.AnswerLogs.objects.filter(
                    exam=exam, 
                    student=student.user
                ).count()
                
                correct_count = models.AnswerLogs.objects.filter(
                    exam=exam, 
                    student=student.user, 
                    status=1
                ).count()
                
                status = 'not_started'
                score = None
                submit_time = None
                
                if exam_log:
                    if exam_log.status == 0:
                        status = 'in_progress'
                    elif exam_log.status in [1, 2]:
                        status = 'submitted'
                        score = exam_log.score
                        submit_time = exam_log.createTime
                
                student_status = {
                    'studentId': student.user.id if student.user else '',
                    'studentName': student.user.name if student.user else '',
                    'studentNo': student.user.userName if student.user else '',
                    'status': status,
                    'statusText': {'not_started': '未开始', 'in_progress': '答题中', 'submitted': '已提交'}.get(status, '未知'),
                    'score': score,
                    'answerCount': answer_count,
                    'correctCount': correct_count,
                    'submitTime': submit_time
                }
                
                if status_filter:
                    if status_filter == status:
                        student_list.append(student_status)
                else:
                    student_list.append(student_status)
            
            paginator = Paginator(student_list, page_size)
            page = paginator.get_page(page_index)
            
            return BaseView.successData({
                'list': list(page),
                'total': paginator.count,
                'pageIndex': page_index,
                'pageSize': page_size
            })
        except Exception as e:
            return BaseView.error(f'获取学生状态失败: {str(e)}')
    
    @staticmethod
    @require_http_methods(['GET'])
    def get_question_stats(request):
        """获取考试题目统计"""
        try:
            user = get_user_from_request(request)
            if not user or user.type not in [0, 1]:
                return BaseView.error('权限不足')
            
            exam_id = request.GET.get('examId')
            if not exam_id:
                return BaseView.error('缺少考试ID')
            
            exam = models.Exams.objects.filter(id=exam_id).first()
            if not exam:
                return BaseView.error('考试不存在')
            
            from app.models import Practises
            questions = Practises.objects.filter(project=exam.project)
            
            question_stats = []
            for q in questions:
                total = models.AnswerLogs.objects.filter(exam=exam, practise=q).count()
                correct = models.AnswerLogs.objects.filter(exam=exam, practise=q, status=1).count()
                
                question_stats.append({
                    'questionId': q.id,
                    'questionName': q.name[:50] + '...' if len(q.name) > 50 else q.name,
                    'questionType': q.type,
                    'questionTypeText': {0: '选择题', 1: '填空题', 2: '判断题', 3: '简答题'}.get(q.type, '其他'),
                    'totalAnswers': total,
                    'correctAnswers': correct,
                    'correctRate': round(correct / total * 100, 1) if total > 0 else 0
                })
            
            return BaseView.successData(question_stats[:20])
        except Exception as e:
            return BaseView.error(f'获取题目统计失败: {str(e)}')
    
    @staticmethod
    @require_http_methods(['GET'])
    def get_realtime_data(request):
        """获取实时监控数据（用于定时刷新）"""
        try:
            user = get_user_from_request(request)
            if not user or user.type not in [0, 1]:
                return BaseView.error('权限不足')
            
            exam_id = request.GET.get('examId')
            if not exam_id:
                return BaseView.error('缺少考试ID')
            
            exam = models.Exams.objects.filter(id=exam_id).first()
            if not exam:
                return BaseView.error('考试不存在')
            
            student_count = models.Students.objects.filter(grade=exam.grade).count()
            submitted_count = models.ExamLogs.objects.filter(exam=exam, status__in=[1, 2]).count()
            in_progress_count = models.ExamLogs.objects.filter(exam=exam, status=0).count()
            
            recent_submits = models.ExamLogs.objects.filter(
                exam=exam, 
                status__in=[1, 2]
            ).order_by('-createTime')[:5]
            
            recent_list = []
            for log in recent_submits:
                recent_list.append({
                    'studentName': log.student.name if log.student else '',
                    'score': log.score,
                    'submitTime': log.createTime
                })
            
            return BaseView.successData({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'totalStudents': student_count,
                'submittedCount': submitted_count,
                'inProgressCount': in_progress_count,
                'recentSubmits': recent_list
            })
        except Exception as e:
            return BaseView.error(f'获取实时数据失败: {str(e)}')
