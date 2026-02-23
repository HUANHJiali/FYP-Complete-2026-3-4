#!/usr/bin/env python
"""
API性能测试脚本
用于测试优化后的API响应速度
"""
import os
import sys
import django
import time
import requests
from statistics import mean, median

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.core.cache import cache
from app import models
from django.db import connection
from django.test import Client

class APIPerformanceTester:
    def __init__(self):
        self.client = Client()
        self.results = {}
        
    def test_query_performance(self, query_func, name, iterations=10):
        """测试查询性能"""
        times = []
        query_counts = []
        
        for i in range(iterations):
            # 重置查询计数
            initial_queries = len(connection.queries)
            
            # 执行查询
            start_time = time.time()
            result = query_func()
            end_time = time.time()
            
            # 计算查询次数
            queries_executed = len(connection.queries) - initial_queries
            
            elapsed = (end_time - start_time) * 1000  # 转换为毫秒
            times.append(elapsed)
            query_counts.append(queries_executed)
        
        self.results[name] = {
            'avg_time': mean(times),
            'median_time': median(times),
            'min_time': min(times),
            'max_time': max(times),
            'avg_queries': mean(query_counts),
            'total_queries': sum(query_counts)
        }
        
        return self.results[name]
    
    def test_practises_list(self):
        """测试习题列表查询"""
        def query():
            # 模拟PractisesView.getPageInfos的查询
            data = models.Practises.objects.filter(
                project__id=1
            ).select_related('project').order_by('-createTime')[:10]
            
            result = []
            practise_ids = [item.id for item in data]
            if practise_ids:
                from django.db.models import Count
                option_counts = models.Options.objects.filter(
                    practise_id__in=practise_ids
                ).values('practise_id').annotate(count=Count('id'))
                option_counts_dict = {item['practise_id']: item['count'] for item in option_counts}
            else:
                option_counts_dict = {}
            
            for item in data:
                result.append({
                    'id': item.id,
                    'name': item.name,
                    'projectName': item.project.name,
                    'optionTotal': option_counts_dict.get(item.id, 0)
                })
            return result
        
        return self.test_query_performance(query, '习题列表查询')
    
    def test_student_tasks(self):
        """测试学生任务查询"""
        def query():
            # 模拟TasksView.getStudentTasks的查询
            student = models.Students.objects.first()
            if not student:
                return []
            
            tasks = models.Tasks.objects.filter(
                grade=student.grade,
                isActive=True
            ).select_related('project', 'teacher').order_by('-createTime')
            
            task_ids = [task.id for task in tasks]
            existing_logs = {}
            if task_ids:
                logs = models.StudentTaskLogs.objects.filter(
                    student__id=student.user.id,
                    task_id__in=task_ids
                ).select_related('task')
                for log in logs:
                    existing_logs[log.task_id] = log
            
            result = []
            for task in tasks:
                existingLog = existing_logs.get(task.id)
                result.append({
                    'id': task.id,
                    'title': task.title,
                    'projectName': task.project.name,
                    'teacherName': task.teacher.name,
                    'status': 'not_started' if not existingLog else existingLog.status
                })
            return result
        
        return self.test_query_performance(query, '学生任务查询')
    
    def test_exam_logs(self):
        """测试考试记录查询"""
        def query():
            # 模拟ExamLogsView.getPageStudentLogs的查询
            student = models.Users.objects.filter(type=2).first()
            if not student:
                return []
            
            data = models.ExamLogs.objects.filter(
                student__id=student.id
            ).select_related('exam', 'exam__teacher', 'exam__project').order_by('-createTime')[:10]
            
            result = []
            for item in data:
                result.append({
                    'id': item.id,
                    'examName': item.exam.name,
                    'teacherName': item.exam.teacher.name,
                    'projectName': item.exam.project.name,
                    'score': item.score
                })
            return result
        
        return self.test_query_performance(query, '考试记录查询')
    
    def test_wrong_questions(self):
        """测试错题本查询"""
        def query():
            # 模拟WrongQuestionsView.getPageInfos的查询
            student = models.Users.objects.filter(type=2).first()
            if not student:
                return []
            
            queryset = models.WrongQuestions.objects.filter(
                student_id=student.id
            ).select_related('practise', 'practise__project').order_by('-createTime')[:10]
            
            result = []
            for wq in queryset:
                result.append({
                    'id': wq.id,
                    'title': wq.practise.name,
                    'type': wq.practise.type,
                    'project': wq.practise.project.name,
                    'isReviewed': wq.isReviewed
                })
            return result
        
        return self.test_query_performance(query, '错题本查询')
    
    def print_results(self):
        """打印测试结果"""
        print("\n" + "="*80)
        print("API性能测试结果")
        print("="*80)
        print(f"{'测试项':<20} {'平均时间(ms)':<15} {'查询次数':<15} {'最小(ms)':<12} {'最大(ms)':<12}")
        print("-"*80)
        
        for name, result in self.results.items():
            print(f"{name:<20} {result['avg_time']:<15.2f} {result['avg_queries']:<15.1f} "
                  f"{result['min_time']:<12.2f} {result['max_time']:<12.2f}")
        
        print("="*80)
        print("\n性能评估:")
        for name, result in self.results.items():
            if result['avg_time'] < 50:
                status = "✅ 优秀"
            elif result['avg_time'] < 100:
                status = "✅ 良好"
            elif result['avg_time'] < 200:
                status = "⚠️  一般"
            else:
                status = "❌ 需要优化"
            
            print(f"  {name}: {status} (平均 {result['avg_time']:.2f}ms, {result['avg_queries']:.1f} 次查询)")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始API性能测试...")
        print("测试迭代次数: 10次\n")
        
        self.test_practises_list()
        self.test_student_tasks()
        self.test_exam_logs()
        self.test_wrong_questions()
        
        self.print_results()

if __name__ == '__main__':
    tester = APIPerformanceTester()
    tester.run_all_tests()

