"""
Statistics Service
Provides statistics calculation for exams, students, classes, and subjects
"""
from django.db.models import Count, Avg, Max, Min, Q, Sum
from django.utils import timezone
from datetime import timedelta
from app import models


class StatisticsService:
    """Statistics calculation service"""
    
    @staticmethod
    def get_exam_statistics(exam_id):
        """Get exam statistics"""
        try:
            exam = models.Exams.objects.get(id=exam_id)
        except models.Exams.DoesNotExist:
            return None
        
        exam_logs = models.ExamLogs.objects.filter(exam=exam)
        
        stats = exam_logs.aggregate(
            total_participants=Count('id'),
            avg_score=Avg('score'),
            max_score=Max('score'),
            min_score=Min('score')
        )
        
        distribution = {
            'excellent': exam_logs.filter(score__gte=90).count(),
            'good': exam_logs.filter(score__gte=80, score__lt=90).count(),
            'pass': exam_logs.filter(score__gte=60, score__lt=80).count(),
            'fail': exam_logs.filter(score__lt=60).count()
        }
        
        return {
            'examName': exam.name,
            'totalParticipants': stats['total_participants'] or 0,
            'avgScore': round(stats['avg_score'] or 0, 2),
            'maxScore': round(stats['max_score'] or 0, 2),
            'minScore': round(stats['min_score'] or 0, 2),
            'scoreDistribution': distribution
        }
    
    @staticmethod
    def get_student_learning_trend(student_id, days=30):
        """Get student learning trend"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        exam_logs = models.ExamLogs.objects.filter(
            student_id=student_id,
            createTime__gte=start_date
        ).order_by('createTime')
        
        practice_logs = models.StudentPracticeLogs.objects.filter(
            student_id=student_id,
            createTime__gte=start_date
        ).order_by('createTime')
        
        trend_data = []
        for log in exam_logs:
            trend_data.append({
                'date': str(log.createTime)[:10],
                'type': 'exam',
                'score': float(log.score) if log.score else 0
            })
        
        for log in practice_logs:
            trend_data.append({
                'date': str(log.createTime)[:10],
                'type': 'practice',
                'score': float(log.score) if log.score else 0
            })
        
        trend_data.sort(key=lambda x: x['date'])
        
        return {
            'studentId': student_id,
            'days': days,
            'trendData': trend_data,
            'avgScore': round(sum(d['score'] for d in trend_data) / len(trend_data), 2) if trend_data else 0
        }
    
    @staticmethod
    def get_class_performance_statistics(grade_id):
        """Get class performance statistics"""
        try:
            grade = models.Grades.objects.get(id=grade_id)
        except models.Grades.DoesNotExist:
            return None
        
        student_users = models.Students.objects.filter(grade=grade).values_list('user_id', flat=True)
        student_count = len(student_users)
        
        exam_stats = models.ExamLogs.objects.filter(
            student_id__in=student_users
        ).aggregate(
            total_exams=Count('exam', distinct=True),
            avg_score=Avg('score'),
            pass_count=Count('id', filter=Q(score__gte=60))
        )
        
        practice_stats = models.StudentPracticeLogs.objects.filter(
            student_id__in=student_users
        ).aggregate(
            total_practices=Count('id'),
            avg_score=Avg('score')
        )
        
        wrong_count = models.WrongQuestions.objects.filter(
            student_id__in=student_users
        ).count()
        
        return {
            'gradeName': grade.name,
            'studentCount': student_count,
            'examStats': {
                'totalExams': exam_stats['total_exams'] or 0,
                'avgScore': round(exam_stats['avg_score'] or 0, 2),
                'passRate': round((exam_stats['pass_count'] or 0) / max(exam_stats['total_exams'] or 1, 1) * 100, 2)
            },
            'practiceStats': {
                'totalPractices': practice_stats['total_practices'] or 0,
                'avgScore': round(practice_stats['avg_score'] or 0, 2)
            },
            'wrongQuestions': wrong_count
        }
    
    @staticmethod
    def get_subject_statistics(project_id):
        """Get subject statistics"""
        try:
            project = models.Projects.objects.get(id=project_id)
        except models.Projects.DoesNotExist:
            return None
        
        question_stats = models.Practises.objects.filter(
            project=project
        ).aggregate(
            total=Count('id'),
            choice=Count('id', filter=Q(type=0)),
            fillBlank=Count('id', filter=Q(type=1)),
            trueFalse=Count('id', filter=Q(type=2)),
            programming=Count('id', filter=Q(type=3))
        )
        
        exam_count = models.Exams.objects.filter(project=project).count()
        practice_count = models.PracticePapers.objects.filter(project=project).count()
        
        return {
            'projectName': project.name,
            'questions': question_stats,
            'exams': exam_count,
            'practicePapers': practice_count
        }
