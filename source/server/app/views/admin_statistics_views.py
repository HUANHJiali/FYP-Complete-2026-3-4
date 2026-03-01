"""
管理员统计分析相关视图

从 admin_views.py 拆分出的统计/推荐接口，降低单文件复杂度。
"""
from collections import Counter

from django.db.models import Avg, Count, Max, Min

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView


class AdminStatisticsView:
    """管理员统计分析与推荐接口集合"""

    @staticmethod
    def _require_admin(request):
        user = get_user_from_request(request)
        if not user:
            return None, BaseView.error('用户未登录')
        if user.type != 0:
            return None, BaseView.error('权限不足')
        return user, None

    @staticmethod
    def get_exam_statistics(request):
        """获取考试统计信息（兼容旧 Admin 路径）。"""
        try:
            exam_id = request.GET.get('examId')
            if not exam_id:
                return BaseView.error('请提供考试ID')

            from app.services.statistics_service import StatisticsService
            statistics = StatisticsService.get_exam_statistics(int(exam_id))

            if 'error' in statistics:
                return BaseView.error(statistics['error'])

            return BaseView.successData(statistics)
        except Exception as e:
            return BaseView.error(f'获取统计失败: {str(e)}')

    @staticmethod
    def get_student_statistics(request):
        """获取学生学习趋势（兼容旧 Admin 路径）。"""
        try:
            student_id = request.GET.get('studentId')
            days = int(request.GET.get('days', 30))

            if not student_id:
                return BaseView.error('请提供学生ID')

            if days <= 0:
                days = 30

            from app.services.statistics_service import StatisticsService
            statistics = StatisticsService.get_student_learning_trend(student_id, days)

            if 'error' in statistics:
                return BaseView.error(statistics['error'])

            return BaseView.successData(statistics)
        except Exception as e:
            return BaseView.error(f'获取统计失败: {str(e)}')

    @staticmethod
    def get_class_statistics(request):
        """获取班级成绩统计（兼容旧 Admin 路径）。"""
        try:
            grade_id = request.GET.get('gradeId')
            if not grade_id:
                return BaseView.error('请提供班级ID')

            from app.services.statistics_service import StatisticsService
            statistics = StatisticsService.get_class_performance_statistics(int(grade_id))

            if 'error' in statistics:
                return BaseView.error(statistics['error'])

            return BaseView.successData(statistics)
        except Exception as e:
            return BaseView.error(f'获取统计失败: {str(e)}')

    @staticmethod
    def get_subject_statistics(request):
        """获取科目统计信息（兼容旧 Admin 路径）。"""
        try:
            project_id = request.GET.get('projectId')
            if not project_id:
                return BaseView.error('请提供科目ID')

            from app.services.statistics_service import StatisticsService
            statistics = StatisticsService.get_subject_statistics(int(project_id))

            if 'error' in statistics:
                return BaseView.error(statistics['error'])

            return BaseView.successData(statistics)
        except Exception as e:
            return BaseView.error(f'获取统计失败: {str(e)}')

    @staticmethod
    def compare_class_grades(request):
        """班级成绩对比分析"""
        _, err = AdminStatisticsView._require_admin(request)
        if err:
            return err

        grade_ids_str = request.GET.get('gradeIds', '')
        exam_id = request.GET.get('examId')

        if not grade_ids_str:
            return BaseView.warn('请选择要对比的班级')

        try:
            grade_ids = [int(gid.strip()) for gid in grade_ids_str.split(',') if gid.strip()]
        except ValueError:
            return BaseView.error('班级ID格式错误')

        if len(grade_ids) < 2:
            return BaseView.warn('请至少选择两个班级进行对比')

        if len(grade_ids) > 10:
            return BaseView.warn('最多同时对比10个班级')

        comparison_data = []

        for grade_id in grade_ids:
            try:
                grade = models.Grades.objects.get(id=grade_id)
            except models.Grades.DoesNotExist:
                continue

            student_count = models.Students.objects.filter(grade=grade).count()

            if exam_id:
                exam_logs = models.ExamLogs.objects.filter(
                    exam_id=exam_id,
                    student__students__grade_id=grade_id,
                    status=2
                )
            else:
                exam_logs = models.ExamLogs.objects.filter(
                    student__students__grade_id=grade_id,
                    status=2
                )

            exam_stats = exam_logs.aggregate(
                avg_score=Avg('score'),
                max_score=Max('score'),
                min_score=Min('score'),
                total_count=Count('id')
            )

            pass_count = exam_logs.filter(score__gte=60).count()
            total_count = exam_stats['total_count'] or 0
            pass_rate = round(pass_count / total_count * 100, 2) if total_count > 0 else 0

            excellent_count = exam_logs.filter(score__gte=80).count()
            excellent_rate = round(excellent_count / total_count * 100, 2) if total_count > 0 else 0

            practice_logs = models.StudentPracticeLogs.objects.filter(
                student__students__grade_id=grade_id,
                status=2
            )
            practice_stats = practice_logs.aggregate(
                avg_score=Avg('score'),
                total_count=Count('id')
            )

            wrong_count = models.WrongQuestions.objects.filter(
                student__students__grade_id=grade_id
            ).count()

            avg_wrong = round(wrong_count / student_count, 2) if student_count > 0 else 0

            comparison_data.append({
                'gradeId': grade_id,
                'gradeName': grade.name,
                'studentCount': student_count,
                'examStats': {
                    'avgScore': round(exam_stats['avg_score'] or 0, 2),
                    'maxScore': round(exam_stats['max_score'] or 0, 2),
                    'minScore': round(exam_stats['min_score'] or 0, 2),
                    'totalParticipants': total_count,
                    'passRate': pass_rate,
                    'excellentRate': excellent_rate
                },
                'practiceStats': {
                    'avgScore': round(practice_stats['avg_score'] or 0, 2),
                    'totalPractices': practice_stats['total_count'] or 0
                },
                'wrongQuestionStats': {
                    'total': wrong_count,
                    'avgPerStudent': avg_wrong
                }
            })

        comparison_data.sort(key=lambda x: x['examStats']['avgScore'], reverse=True)

        for index, data in enumerate(comparison_data):
            data['rank'] = index + 1

        return BaseView.successData({
            'comparisonData': comparison_data,
            'examId': exam_id,
            'totalGrades': len(comparison_data)
        })

    @staticmethod
    def compare_student_progress(request):
        """学生个人进步对比"""
        _, err = AdminStatisticsView._require_admin(request)
        if err:
            return err

        student_id = request.GET.get('studentId')
        time_range = request.GET.get('timeRange', 'semester')

        if not student_id:
            return BaseView.warn('缺少学生ID')

        try:
            student = models.Students.objects.get(user_id=student_id)
        except models.Students.DoesNotExist:
            return BaseView.warn('学生不存在')

        exam_logs = models.ExamLogs.objects.filter(
            student_id=student_id,
            status=2
        ).select_related('exam', 'exam__project').order_by('exam__examTime')

        practice_logs = models.StudentPracticeLogs.objects.filter(
            student_id=student_id,
            status='completed'
        ).select_related('paper', 'paper__project').order_by('createTime')

        exam_progress = []
        for log in exam_logs:
            exam_progress.append({
                'type': 'exam',
                'name': log.exam.name if log.exam else '',
                'subject': log.exam.project.name if log.exam and log.exam.project else '',
                'score': float(log.score) if log.score else 0,
                'time': log.exam.examTime if log.exam else '',
                'date': log.exam.examTime[:10] if log.exam and log.exam.examTime else ''
            })

        practice_progress = []
        for log in practice_logs:
            practice_progress.append({
                'type': 'practice',
                'name': log.paper.title if log.paper else '',
                'subject': log.paper.project.name if log.paper and log.paper.project else '',
                'score': float(log.score) if log.score else 0,
                'time': str(log.createTime) if log.createTime else '',
                'date': str(log.createTime)[:10] if log.createTime else ''
            })

        all_progress = exam_progress + practice_progress
        all_progress.sort(key=lambda x: x['time'])

        if len(all_progress) >= 2:
            first_score = all_progress[0]['score']
            last_score = all_progress[-1]['score']
            improvement = last_score - first_score
            improvement_rate = round((improvement / first_score) * 100, 2) if first_score > 0 else 0
        else:
            improvement = 0
            improvement_rate = 0

        avg_score = round(sum(p['score'] for p in all_progress) / len(all_progress), 2) if all_progress else 0

        subject_stats = {}
        for progress in all_progress:
            subject = progress['subject']
            if subject not in subject_stats:
                subject_stats[subject] = []
            subject_stats[subject].append(progress['score'])

        subject_averages = {
            subject: round(sum(scores) / len(scores), 2)
            for subject, scores in subject_stats.items()
        }

        return BaseView.successData({
            'studentId': student_id,
            'studentName': student.user.name if student.user else '',
            'timeRange': time_range,
            'progressData': all_progress[-20:] if len(all_progress) > 20 else all_progress,
            'summary': {
                'totalRecords': len(all_progress),
                'avgScore': avg_score,
                'improvement': round(improvement, 2),
                'improvementRate': improvement_rate,
                'subjectAverages': subject_averages
            }
        })

    @staticmethod
    def recommend_practice(request):
        """AI练习推荐"""
        _, err = AdminStatisticsView._require_admin(request)
        if err:
            return err

        student_id = request.GET.get('studentId')
        count = int(request.GET.get('count', 10))

        if not student_id:
            return BaseView.warn('缺少学生ID')

        try:
            models.Students.objects.get(user_id=student_id)
        except models.Students.DoesNotExist:
            return BaseView.warn('学生不存在')

        wrong_questions = models.WrongQuestions.objects.filter(
            student_id=student_id
        ).select_related('practise', 'practise__project')

        wrong_subjects = Counter()
        wrong_types = Counter()

        for wq in wrong_questions:
            if wq.practise:
                if wq.practise.project:
                    wrong_subjects[wq.practise.project.name] += 1
                wrong_types[wq.practise.type] += 1

        weak_subjects = [s[0] for s in wrong_subjects.most_common(3)]

        recommended_papers = []

        if weak_subjects:
            papers = models.PracticePapers.objects.filter(
                project__name__in=weak_subjects,
                status=1
            ).exclude(
                id__in=models.StudentPracticeLogs.objects.filter(
                    student_id=student_id
                ).values_list('practicePaper_id', flat=True)
            ).annotate(
                question_count=Count('practicepaperquestions')
            ).filter(question_count__gt=0)[:count // 2]

            for paper in papers:
                recommended_papers.append({
                    'id': paper.id,
                    'name': paper.title,
                    'subject': paper.project.name if paper.project else '',
                    'reason': f'针对薄弱科目"{paper.project.name if paper.project else ""}"强化练习',
                    'priority': 1,
                    'questionCount': paper.question_count
                })

        if len(recommended_papers) < count:
            additional_papers = models.PracticePapers.objects.filter(
                isActive=True
            ).exclude(
                id__in=[p['id'] for p in recommended_papers]
            ).exclude(
                id__in=models.StudentPracticeLogs.objects.filter(
                    student_id=student_id,
                    status='completed'
                ).values_list('paper_id', flat=True)
            ).annotate(
                question_count=Count('practicepaperquestions')
            ).filter(question_count__gt=0)[:count - len(recommended_papers)]

            for paper in additional_papers:
                recommended_papers.append({
                    'id': paper.id,
                    'name': paper.title,
                    'subject': paper.project.name if paper.project else '',
                    'reason': '推荐练习',
                    'priority': 2,
                    'questionCount': paper.question_count
                })

        return BaseView.successData({
            'studentId': student_id,
            'recommendedPapers': recommended_papers,
            'analysis': {
                'weakSubjects': weak_subjects,
                'weakTypes': dict(wrong_types.most_common(3)),
                'totalWrongQuestions': wrong_questions.count()
            }
        })

    @staticmethod
    def recommend_wrong_questions(request):
        """智能错题推荐"""
        _, err = AdminStatisticsView._require_admin(request)
        if err:
            return err

        student_id = request.GET.get('studentId')
        count = int(request.GET.get('count', 5))

        if not student_id:
            return BaseView.warn('缺少学生ID')

        wrong_questions = models.WrongQuestions.objects.filter(
            student_id=student_id
        ).select_related('practise', 'practise__project').order_by('-reviewCount')

        if not wrong_questions.exists():
            return BaseView.successData({
                'studentId': student_id,
                'recommendedQuestions': [],
                'message': '暂无错题，继续加油！'
            })

        wrong_project_ids = set()
        wrong_types = set()

        for wq in wrong_questions[:10]:
            if wq.practise:
                if wq.practise.project:
                    wrong_project_ids.add(wq.practise.project_id)
                wrong_types.add(wq.practise.type)

        recommended_questions = []

        for project_id in wrong_project_ids:
            questions = models.Practises.objects.filter(
                project_id=project_id,
                type__in=wrong_types
            ).exclude(
                id__in=models.WrongQuestions.objects.filter(
                    student_id=student_id
                ).values_list('practise_id', flat=True)
            ).exclude(
                id__in=models.StudentPracticeAnswers.objects.filter(
                    practiceLog__student_id=student_id
                ).values_list('question_id', flat=True)
            )[:count]

            for question in questions:
                recommended_questions.append({
                    'id': question.id,
                    'name': question.name[:50] + '...' if len(question.name) > 50 else question.name,
                    'type': question.type,
                    'typeName': {0: '选择题', 1: '填空题', 2: '判断题', 3: '简答题', 4: '编程题', 5: '综合题'}.get(question.type, '未知'),
                    'subject': question.project.name if question.project else '',
                    'difficulty': question.difficulty,
                    'reason': f'巩固"{question.project.name if question.project else ""}"科目薄弱知识点'
                })

                if len(recommended_questions) >= count:
                    break

            if len(recommended_questions) >= count:
                break

        return BaseView.successData({
            'studentId': student_id,
            'recommendedQuestions': recommended_questions,
            'wrongQuestionCount': wrong_questions.count()
        })
