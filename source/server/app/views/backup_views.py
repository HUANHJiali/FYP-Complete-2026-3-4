"""
数据备份和导出功能视图
支持系统数据备份、学习报告生成等功能
"""
import os
import json
import csv
import io
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models import Q, Count, Avg, Max, Min
from django.core import serializers
from django.conf import settings

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView
from utils.OperationLogger import OperationLogger


def _log_export_operation(request, operation_type, detail, status=1):
    """记录导出操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name='backup',
                resource_name=detail,
                status=status,
                request=request
            )
    except Exception:
        pass


class BackupViews:
    """数据备份和导出功能"""
    
    @staticmethod
    def export_system_data(request):
        """
        导出系统数据备份
        
        参数:
            dataType: 数据类型 (all/students/teachers/exams/questions/logs)
            format: 导出格式 (json/csv)
        
        返回:
            备份文件下载
        """
        data_type = request.GET.get('dataType', 'all')
        export_format = request.GET.get('format', 'json')
        
        # 根据数据类型获取数据
        data = {}
        
        if data_type in ['all', 'colleges']:
            data['colleges'] = list(models.Colleges.objects.all().values(
                'id', 'name', 'createTime'
            ))
        
        if data_type in ['all', 'grades']:
            data['grades'] = list(models.Grades.objects.all().values(
                'id', 'name', 'createTime'
            ))
        
        if data_type in ['all', 'projects']:
            data['projects'] = list(models.Projects.objects.all().values(
                'id', 'name', 'createTime'
            ))
        
        if data_type in ['all', 'students']:
            students = models.Students.objects.all().select_related('user', 'grade', 'college')
            data['students'] = [{
                'id': s.user.id if s.user else '',
                'userName': s.user.userName if s.user else '',
                'name': s.user.name if s.user else '',
                'gender': s.user.gender if s.user else '',
                'age': s.user.age if s.user else 0,
                'gradeName': s.grade.name if s.grade else '',
                'collegeName': s.college.name if s.college else ''
            } for s in students]
        
        if data_type in ['all', 'teachers']:
            teachers = models.Teachers.objects.all().select_related('user')
            data['teachers'] = [{
                'id': t.user.id if t.user else '',
                'userName': t.user.userName if t.user else '',
                'name': t.user.name if t.user else '',
                'phone': t.phone or '',
                'record': t.record or '',
                'job': t.job or ''
            } for t in teachers]
        
        if data_type in ['all', 'questions']:
            questions = models.Practises.objects.all().select_related('project')
            data['questions'] = [{
                'id': q.id,
                'name': q.name,
                'type': q.type,
                'answer': q.answer,
                'analyse': q.analyse,
                'projectName': q.project.name if q.project else '',
                'difficulty': q.difficulty,
                'createTime': q.createTime
            } for q in questions]
        
        if data_type in ['all', 'exams']:
            exams = models.Exams.objects.all().select_related('teacher', 'project', 'grade')
            data['exams'] = [{
                'id': e.id,
                'name': e.name,
                'teacherName': e.teacher.name if e.teacher else '',
                'projectName': e.project.name if e.project else '',
                'gradeName': e.grade.name if e.grade else '',
                'examTime': e.examTime,
                'createTime': e.createTime
            } for e in exams]
        
        # 生成文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'system_backup_{data_type}_{timestamp}'
        
        if export_format == 'json':
            response = HttpResponse(
                json.dumps(data, ensure_ascii=False, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        else:  # CSV格式（仅支持单表导出）
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入数据
            if data_type == 'students' and 'students' in data:
                writer.writerow(['学号', '账号', '姓名', '性别', '年龄', '班级', '学院'])
                for s in data['students']:
                    writer.writerow([
                        s['id'], s['userName'], s['name'], s['gender'],
                        s['age'], s['gradeName'], s['collegeName']
                    ])
            elif data_type == 'questions' and 'questions' in data:
                writer.writerow(['ID', '题目内容', '题型', '答案', '学科', '难度', '创建时间'])
                for q in data['questions']:
                    writer.writerow([
                        q['id'], q['name'], q['type'], q['answer'],
                        q['projectName'], q['difficulty'], q['createTime']
                    ])
            else:
                writer.writerow(['数据类型不支持CSV导出，请使用JSON格式'])
            
            output.seek(0)
            response = HttpResponse(
                output.getvalue(),
                content_type='text/csv; charset=utf-8-sig'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        _log_export_operation(request, 'export', f'导出{data_type}数据-{export_format}格式')
        return response
    
    @staticmethod
    def generate_student_report(request):
        """
        生成学生学习报告
        
        参数:
            studentId: 学生ID
            timeRange: 时间范围 (month/semester/year)
        
        返回:
            学习报告PDF/HTML
        """
        student_id = request.GET.get('studentId')
        time_range = request.GET.get('timeRange', 'semester')
        
        if not student_id:
            return BaseView.warn('缺少学生ID')
        
        try:
            student = models.Students.objects.get(user_id=student_id)
        except models.Students.DoesNotExist:
            return BaseView.warn('学生不存在')
        
        # 计算时间范围
        now = datetime.now()
        if time_range == 'month':
            start_date = now - timedelta(days=30)
        elif time_range == 'semester':
            start_date = now - timedelta(days=180)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # 获取考试数据
        exam_logs = models.ExamLogs.objects.filter(
            student_id=student_id,
            status=2
        ).select_related('exam', 'exam__project')
        
        exam_stats = exam_logs.aggregate(
            total=Count('id'),
            avg_score=Avg('score'),
            max_score=Max('score'),
            min_score=Min('score')
        )
        
        # 获取练习数据
        practice_logs = models.StudentPracticeLogs.objects.filter(
            student_id=student_id,
            status=2
        ).select_related('practicePaper')
        
        practice_stats = practice_logs.aggregate(
            total=Count('id'),
            avg_score=Avg('score')
        )
        
        # 获取错题数据
        wrong_questions = models.WrongQuestions.objects.filter(
            student_id=student_id
        ).select_related('practise', 'practise__project')
        
        wrong_stats = {
            'total': wrong_questions.count(),
            'by_subject': {}
        }
        
        for wq in wrong_questions:
            if wq.practise and wq.practise.project:
                subject = wq.practise.project.name
                if subject not in wrong_stats['by_subject']:
                    wrong_stats['by_subject'][subject] = 0
                wrong_stats['by_subject'][subject] += 1
        
        # 获取任务完成数据
        task_logs = models.StudentTaskLogs.objects.filter(
            student_id=student_id,
            status='completed'
        )
        
        task_stats = {
            'total': task_logs.count(),
            'avg_score': task_logs.aggregate(avg=Avg('score'))['avg'] or 0
        }
        
        # 生成报告HTML
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>学生学习报告 - {student.user.name if student.user else ''}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #2d8cf0; border-bottom: 2px solid #2d8cf0; padding-bottom: 10px; }}
                h2 {{ color: #515a6e; margin-top: 30px; }}
                .stat-box {{ background: #f8f8f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .stat-item {{ display: inline-block; width: 45%; margin: 10px 0; }}
                .stat-label {{ color: #808695; font-size: 14px; }}
                .stat-value {{ font-size: 24px; font-weight: 600; color: #2d8cf0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e8eaec; }}
                th {{ background: #f8f8f9; font-weight: 600; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e8eaec; color: #808695; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>学生学习报告</h1>
            
            <div class="stat-box">
                <h2>学生信息</h2>
                <p><strong>姓名：</strong>{student.user.name if student.user else ''}</p>
                <p><strong>学号：</strong>{student.user.id if student.user else ''}</p>
                <p><strong>班级：</strong>{student.grade.name if student.grade else ''}</p>
                <p><strong>学院：</strong>{student.college.name if student.college else ''}</p>
                <p><strong>报告周期：</strong>{time_range} ({start_date.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')})</p>
            </div>
            
            <h2>考试表现</h2>
            <div class="stat-box">
                <div class="stat-item">
                    <div class="stat-label">参加考试</div>
                    <div class="stat-value">{exam_stats['total'] or 0} 场</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">平均分</div>
                    <div class="stat-value">{round(exam_stats['avg_score'] or 0, 1)} 分</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">最高分</div>
                    <div class="stat-value">{round(exam_stats['max_score'] or 0, 1)} 分</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">最低分</div>
                    <div class="stat-value">{round(exam_stats['min_score'] or 0, 1)} 分</div>
                </div>
            </div>
            
            <h2>练习情况</h2>
            <div class="stat-box">
                <div class="stat-item">
                    <div class="stat-label">完成练习</div>
                    <div class="stat-value">{practice_stats['total'] or 0} 次</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">练习平均分</div>
                    <div class="stat-value">{round(practice_stats['avg_score'] or 0, 1)} 分</div>
                </div>
            </div>
            
            <h2>任务完成</h2>
            <div class="stat-box">
                <div class="stat-item">
                    <div class="stat-label">完成任务</div>
                    <div class="stat-value">{task_stats['total']} 个</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">任务平均分</div>
                    <div class="stat-value">{round(task_stats['avg_score'], 1)} 分</div>
                </div>
            </div>
            
            <h2>错题统计</h2>
            <div class="stat-box">
                <p><strong>总错题数：</strong>{wrong_stats['total']} 道</p>
                {''.join([f'<p><strong>{subject}：</strong>{count} 道</p>' for subject, count in wrong_stats['by_subject'].items()])}
            </div>
            
            <div class="footer">
                <p>报告生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>本报告由在线考试系统自动生成</p>
            </div>
        </body>
        </html>
        """
        
        response = HttpResponse(report_html, content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = f'inline; filename="student_report_{student_id}.html"'
        
        _log_export_operation(request, 'export', f'学生报告-{student_id}-{time_range}')
        return response
    
    @staticmethod
    def export_teachers(request):
        """导出教师列表"""
        teachers = models.Teachers.objects.all().select_related('user')
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['工号', '账号', '姓名', '性别', '年龄', '电话', '学历', '职位'])
        
        # 写入数据
        for t in teachers:
            writer.writerow([
                t.user.id if t.user else '',
                t.user.userName if t.user else '',
                t.user.name if t.user else '',
                t.user.gender if t.user else '',
                t.user.age if t.user else '',
                t.phone or '',
                t.record or '',
                t.job or ''
            ])
        
        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='text/csv; charset=utf-8-sig'
        )
        response['Content-Disposition'] = 'attachment; filename="teachers_export.csv"'
        
        _log_export_operation(request, 'export', f'导出教师列表-{teachers.count()}条')
        return response
