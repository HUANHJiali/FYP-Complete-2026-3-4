"""初始化演示数据（可重复执行）"""
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from app import models


class Command(BaseCommand):
    help = '初始化可演示的完整业务数据（用户/题库/考试/练习/任务/错题/消息）'

    @staticmethod
    def now_str(delta_days=0, delta_minutes=0):
        return (datetime.now() + timedelta(days=delta_days, minutes=delta_minutes)).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def ensure_user(user_id, username, password, name, gender, age, user_type, email=''):
        defaults = {
            'userName': username,
            'passWord': make_password(password),
            'name': name,
            'gender': gender,
            'age': age,
            'type': user_type,
            'email': email,
            'status': 0,
        }
        user, created = models.Users.objects.get_or_create(id=user_id, defaults=defaults)
        if not created:
            changed = False
            for key, value in defaults.items():
                if key == 'passWord':
                    continue
                if getattr(user, key) != value:
                    setattr(user, key, value)
                    changed = True
            if changed:
                user.save()
        return user

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('开始初始化演示数据...'))

        # 1) 基础字典数据
        colleges = [
            {'id': 1, 'name': '软件工程学院'},
            {'id': 2, 'name': '人工智能学院'},
        ]
        grades = [
            {'id': 1, 'name': '一年级一班'},
            {'id': 2, 'name': '一年级二班'},
            {'id': 3, 'name': '二年级一班'},
            {'id': 4, 'name': '二年级二班'},
        ]
        projects = [
            {'id': 1, 'name': 'Python全栈开发'},
            {'id': 2, 'name': '数据库原理'},
            {'id': 3, 'name': '数据结构与算法'},
        ]

        for item in colleges:
            models.Colleges.objects.update_or_create(id=item['id'], defaults={'name': item['name'], 'createTime': self.now_str()})
        for item in grades:
            models.Grades.objects.update_or_create(id=item['id'], defaults={'name': item['name'], 'createTime': self.now_str()})
        for item in projects:
            models.Projects.objects.update_or_create(id=item['id'], defaults={'name': item['name'], 'createTime': self.now_str()})

        college1 = models.Colleges.objects.get(id=1)
        college2 = models.Colleges.objects.get(id=2)
        grade1 = models.Grades.objects.get(id=1)
        grade2 = models.Grades.objects.get(id=2)
        grade3 = models.Grades.objects.get(id=3)
        project_python = models.Projects.objects.get(id=1)
        project_db = models.Projects.objects.get(id=2)
        project_algo = models.Projects.objects.get(id=3)

        # 2) 用户与身份数据
        admin = self.ensure_user('ADMIN001', 'admin', '123456', '系统管理员', '男', 30, 0, 'admin@example.com')
        teacher1 = self.ensure_user('TEACHER001', 'teacher', '123456', '张老师', '女', 35, 1, 'teacher@example.com')
        teacher2 = self.ensure_user('TEACHER002', 'teacher2', '123456', '李老师', '男', 38, 1, 'teacher2@example.com')
        student1 = self.ensure_user('STUDENT001', 'student', '123456', '学生一', '男', 20, 2, 'student@example.com')
        student2 = self.ensure_user('STUDENT002', 'student2', '123456', '学生二', '女', 21, 2, 'student2@example.com')
        student3 = self.ensure_user('STUDENT003', 'student3', '123456', '学生三', '男', 19, 2, 'student3@example.com')
        student4 = self.ensure_user('STUDENT004', 'student4', '123456', '学生四', '女', 22, 2, 'student4@example.com')

        models.Teachers.objects.get_or_create(user=teacher1, defaults={'phone': '13800000001', 'record': '硕士', 'job': '讲师'})
        models.Teachers.objects.get_or_create(user=teacher2, defaults={'phone': '13800000002', 'record': '博士', 'job': '副教授'})

        models.Students.objects.get_or_create(user=student1, defaults={'grade': grade1, 'college': college1})
        models.Students.objects.get_or_create(user=student2, defaults={'grade': grade1, 'college': college1})
        models.Students.objects.get_or_create(user=student3, defaults={'grade': grade2, 'college': college1})
        models.Students.objects.get_or_create(user=student4, defaults={'grade': grade3, 'college': college2})

        # 3) 题库与选项
        practise_specs = [
            ('Python变量命名规则', 0, 'A', '变量名不能以数字开头', project_python, ['A', 'B', 'C', 'D'], 1),
            ('列表和元组的区别', 3, '列表可变，元组不可变', '重点掌握可变性与性能差异', project_python, [], 2),
            ('MySQL主键作用', 1, '唯一标识一条记录', '主键用于唯一性和索引优化', project_db, [], 1),
            ('事务四大特性', 3, 'ACID', '原子性、一致性、隔离性、持久性', project_db, [], 2),
            ('二叉树前序遍历顺序', 0, 'C', '根-左-右', project_algo, ['根左右', '左右根', '根左���', '左根右'], 1),
            ('时间复杂度 O(n log n) 示例', 3, '归并排序', '排序类常见复杂度对比', project_algo, [], 2),
            ('Python布尔表达式结果', 2, 'True', '逻辑表达式真值判断', project_python, [], 1),
            ('数据库索引优缺点', 3, '提升查询速度但增加写入成本', '读多写少场景优先考虑索引', project_db, [], 3),
        ]

        practises = []
        for idx, (name, qtype, answer, analyse, project, choices, difficulty) in enumerate(practise_specs, start=1):
            practise, _ = models.Practises.objects.update_or_create(
                name=name,
                project=project,
                defaults={
                    'answer': answer,
                    'analyse': analyse,
                    'type': qtype,
                    'difficulty': difficulty,
                    'tags': ['演示', project.name],
                    'createTime': self.now_str(delta_days=-idx),
                }
            )
            practises.append(practise)
            if qtype == 0 and choices:
                if models.Options.objects.filter(practise=practise).count() == 0:
                    for opt_name in choices:
                        models.Options.objects.create(practise=practise, name=opt_name)

        # 4) 考试数据
        exam1, _ = models.Exams.objects.update_or_create(
            name='Python阶段测试',
            teacher=teacher1,
            grade=grade1,
            project=project_python,
            defaults={
                'createTime': self.now_str(delta_days=-2),
                'examTime': '90',
                'startTime': self.now_str(delta_days=-1, delta_minutes=-30),
                'endTime': self.now_str(delta_days=3),
            }
        )
        exam2, _ = models.Exams.objects.update_or_create(
            name='数据库章节测验',
            teacher=teacher2,
            grade=grade3,
            project=project_db,
            defaults={
                'createTime': self.now_str(delta_days=-3),
                'examTime': '60',
                'startTime': self.now_str(delta_days=-2),
                'endTime': self.now_str(delta_days=5),
            }
        )

        models.ExamLogs.objects.update_or_create(
            student=student1,
            exam=exam1,
            defaults={'status': 2, 'score': 86, 'createTime': self.now_str(delta_days=-1)}
        )
        models.ExamLogs.objects.update_or_create(
            student=student2,
            exam=exam1,
            defaults={'status': 1, 'score': 72, 'createTime': self.now_str(delta_days=-1)}
        )

        # 5) 答题记录
        exam_practises = practises[:3]
        for no, p in enumerate(exam_practises, start=1):
            models.AnswerLogs.objects.update_or_create(
                student=student1,
                exam=exam1,
                practise=p,
                no=no,
                defaults={'score': 8.0 + no, 'status': 1, 'answer': p.answer or '演示答案'}
            )

        # 6) 练习试卷与练习记录
        paper1, _ = models.PracticePapers.objects.update_or_create(
            title='Python基础练习卷A',
            teacher=teacher1,
            project=project_python,
            defaults={
                'description': '面向入门学生的基础练习',
                'type': 'fixed',
                'difficulty': 'easy',
                'duration': 30,
                'totalScore': 100,
                'createTime': self.now_str(delta_days=-2),
                'isActive': True,
            }
        )
        paper2, _ = models.PracticePapers.objects.update_or_create(
            title='数据库强化练习卷B',
            teacher=teacher2,
            project=project_db,
            defaults={
                'description': '数据库核心概念强化训练',
                'type': 'timed',
                'difficulty': 'medium',
                'duration': 45,
                'totalScore': 100,
                'createTime': self.now_str(delta_days=-1),
                'isActive': True,
            }
        )

        models.PracticePaperQuestions.objects.filter(paper=paper1).delete()
        models.PracticePaperQuestions.objects.filter(paper=paper2).delete()
        for idx, p in enumerate(practises[:4], start=1):
            models.PracticePaperQuestions.objects.create(paper=paper1, practise=p, questionOrder=idx, score=25)
        for idx, p in enumerate(practises[2:6], start=1):
            models.PracticePaperQuestions.objects.create(paper=paper2, practise=p, questionOrder=idx, score=25)

        practice_log, _ = models.StudentPracticeLogs.objects.update_or_create(
            student=student1,
            paper=paper1,
            defaults={
                'startTime': self.now_str(delta_days=-1, delta_minutes=-40),
                'endTime': self.now_str(delta_days=-1, delta_minutes=-10),
                'score': 82,
                'accuracy': 0.75,
                'status': 'completed',
                'usedTime': 30,
            }
        )
        models.StudentPracticeAnswers.objects.update_or_create(
            practiceLog=practice_log,
            practise=practises[0],
            defaults={
                'studentAnswer': 'A',
                'isCorrect': True,
                'score': 25,
                'answerTime': self.now_str(delta_days=-1, delta_minutes=-30),
                'aiConfidence': 0.98,
                'aiFeedback': '回答正确，概念清晰。',
                'aiAnalysis': '能够正确区分变量命名规则。',
                'aiModel': 'glm-4-flash',
            }
        )

        # 7) 任务中心数据
        task1, _ = models.Tasks.objects.update_or_create(
            title='Python作业一',
            teacher=teacher1,
            grade=grade1,
            project=project_python,
            defaults={
                'description': '完成基础语法与数据结构练习',
                'type': 'practice',
                'deadline': self.now_str(delta_days=7),
                'score': 100,
                'createTime': self.now_str(delta_days=-1),
                'isActive': True,
            }
        )
        task2, _ = models.Tasks.objects.update_or_create(
            title='数据库作业一',
            teacher=teacher2,
            grade=grade3,
            project=project_db,
            defaults={
                'description': 'SQL与事务专题练习',
                'type': 'project',
                'deadline': self.now_str(delta_days=10),
                'score': 100,
                'createTime': self.now_str(delta_days=-1),
                'isActive': True,
            }
        )

        models.TaskQuestions.objects.filter(task=task1).delete()
        models.TaskQuestions.objects.filter(task=task2).delete()
        for idx, p in enumerate(practises[:3], start=1):
            models.TaskQuestions.objects.create(task=task1, practise=p, questionOrder=idx, score=33.3)
        for idx, p in enumerate(practises[3:6], start=1):
            models.TaskQuestions.objects.create(task=task2, practise=p, questionOrder=idx, score=33.3)

        task_log, _ = models.StudentTaskLogs.objects.update_or_create(
            student=student2,
            task=task1,
            defaults={
                'startTime': self.now_str(delta_days=-1, delta_minutes=-60),
                'endTime': self.now_str(delta_days=-1, delta_minutes=-15),
                'score': 76,
                'accuracy': 0.66,
                'status': 'completed',
                'usedTime': 45,
            }
        )
        models.StudentTaskAnswers.objects.update_or_create(
            taskLog=task_log,
            practise=practises[1],
            defaults={
                'studentAnswer': '列表可修改，元组不可修改',
                'isCorrect': True,
                'score': 30,
                'answerTime': self.now_str(delta_days=-1, delta_minutes=-30),
                'aiConfidence': 0.95,
                'aiFeedback': '答案正确，表述清晰。',
                'aiAnalysis': '能正确描述核心差异。',
                'aiModel': 'glm-4-flash',
            }
        )

        # 8) 错题与复习
        wrong, _ = models.WrongQuestions.objects.update_or_create(
            student=student1,
            practise=practises[4],
            source='exam',
            sourceId=exam1.id,
            defaults={
                'wrongAnswer': 'B',
                'correctAnswer': practises[4].answer,
                'analysis': practises[4].analyse,
                'isReviewed': True,
                'reviewCount': 2,
                'masteryLevel': 1,
                'lastReviewTime': self.now_str(delta_days=-1),
                'createTime': self.now_str(delta_days=-2),
            }
        )
        models.WrongQuestionReviews.objects.update_or_create(
            wrongQuestion=wrong,
            reviewTime=self.now_str(delta_days=-1, delta_minutes=-20),
            defaults={
                'reviewAnswer': '根-左-右',
                'isCorrect': True,
                'notes': '已掌握先序遍历规则。',
            }
        )

        # 9) 消息与已读
        msg1, _ = models.Messages.objects.get_or_create(
            title='系统演示通知',
            sender=admin,
            defaults={
                'content': '演示环境数据已初始化，可直接体验各模块。',
                'type': 'announcement',
                'priority': 'high',
            }
        )
        msg2, _ = models.Messages.objects.get_or_create(
            title='任务提醒',
            sender=teacher1,
            defaults={
                'content': '请同学们在截止前完成 Python 作业一。',
                'type': 'reminder',
                'priority': 'medium',
            }
        )
        models.MessageReads.objects.get_or_create(message=msg1, user=student1, defaults={'isRead': True})
        models.MessageReads.objects.get_or_create(message=msg2, user=student2, defaults={'isRead': False})

        # 10) 增量历史数据（让图表与列表更丰满）
        exam3, _ = models.Exams.objects.update_or_create(
            name='算法单元测验',
            teacher=teacher1,
            grade=grade2,
            project=project_algo,
            defaults={
                'createTime': self.now_str(delta_days=-5),
                'examTime': '75',
                'startTime': self.now_str(delta_days=-4),
                'endTime': self.now_str(delta_days=2),
            }
        )

        exam_logs_seed = [
            (student3, exam3, 2, 91, -2),
            (student4, exam2, 2, 84, -1),
            (student2, exam2, 1, 68, -1),
        ]
        for st, ex, status, score, day in exam_logs_seed:
            models.ExamLogs.objects.update_or_create(
                student=st,
                exam=ex,
                defaults={'status': status, 'score': score, 'createTime': self.now_str(delta_days=day)}
            )

        answer_seed = [
            (student3, exam3, practises[5], 1, 9.5, '归并排序'),
            (student4, exam2, practises[2], 1, 8.0, '唯一标识一条记录'),
            (student2, exam2, practises[3], 1, 7.0, 'ACID'),
        ]
        for st, ex, p, no, score, ans in answer_seed:
            models.AnswerLogs.objects.update_or_create(
                student=st,
                exam=ex,
                practise=p,
                no=no,
                defaults={'score': score, 'status': 1, 'answer': ans}
            )

        practice_logs_seed = [
            (student2, paper1, 74, 0.62, 28, -2),
            (student3, paper2, 88, 0.81, 33, -1),
            (student4, paper2, 69, 0.58, 40, -1),
        ]
        for st, paper, score, acc, used, day in practice_logs_seed:
            p_log, _ = models.StudentPracticeLogs.objects.update_or_create(
                student=st,
                paper=paper,
                defaults={
                    'startTime': self.now_str(delta_days=day, delta_minutes=-45),
                    'endTime': self.now_str(delta_days=day, delta_minutes=-10),
                    'score': score,
                    'accuracy': acc,
                    'status': 'completed',
                    'usedTime': used,
                }
            )
            models.StudentPracticeAnswers.objects.update_or_create(
                practiceLog=p_log,
                practise=practises[0],
                defaults={
                    'studentAnswer': 'A',
                    'isCorrect': True,
                    'score': 20,
                    'answerTime': self.now_str(delta_days=day, delta_minutes=-25),
                    'aiConfidence': 0.92,
                    'aiFeedback': '思路正确，细节可再优化。',
                    'aiAnalysis': '已掌握基础概念。',
                    'aiModel': 'glm-4-flash',
                }
            )

        task_logs_seed = [
            (student1, task1, 85, 0.78, 36, -2),
            (student3, task1, 90, 0.86, 31, -1),
            (student4, task2, 73, 0.64, 42, -1),
        ]
        for st, task, score, acc, used, day in task_logs_seed:
            t_log, _ = models.StudentTaskLogs.objects.update_or_create(
                student=st,
                task=task,
                defaults={
                    'startTime': self.now_str(delta_days=day, delta_minutes=-60),
                    'endTime': self.now_str(delta_days=day, delta_minutes=-15),
                    'score': score,
                    'accuracy': acc,
                    'status': 'completed',
                    'usedTime': used,
                }
            )
            models.StudentTaskAnswers.objects.update_or_create(
                taskLog=t_log,
                practise=practises[2],
                defaults={
                    'studentAnswer': '唯一标识记录',
                    'isCorrect': True,
                    'score': 30,
                    'answerTime': self.now_str(delta_days=day, delta_minutes=-35),
                    'aiConfidence': 0.9,
                    'aiFeedback': '答案基本准确。',
                    'aiAnalysis': '可补充索引层面的描述。',
                    'aiModel': 'glm-4-flash',
                }
            )

        extra_wrong_specs = [
            (student2, practises[6], 'practice', paper1.id, 'False', practises[6].answer, False, 0, 0, -2),
            (student3, practises[7], 'task', task1.id, '提升写入速度', practises[7].answer, True, 1, 1, -1),
            (student4, practises[3], 'exam', exam2.id, 'ACD', practises[3].answer, True, 2, 1, -1),
        ]
        for st, p, source, source_id, wrong_ans, right_ans, reviewed, review_count, mastery, day in extra_wrong_specs:
            wq, _ = models.WrongQuestions.objects.update_or_create(
                student=st,
                practise=p,
                source=source,
                sourceId=source_id,
                defaults={
                    'wrongAnswer': wrong_ans,
                    'correctAnswer': right_ans,
                    'analysis': p.analyse,
                    'isReviewed': reviewed,
                    'reviewCount': review_count,
                    'masteryLevel': mastery,
                    'lastReviewTime': self.now_str(delta_days=day) if reviewed else None,
                    'createTime': self.now_str(delta_days=day),
                }
            )
            if reviewed:
                models.WrongQuestionReviews.objects.update_or_create(
                    wrongQuestion=wq,
                    reviewTime=self.now_str(delta_days=day, delta_minutes=-20),
                    defaults={
                        'reviewAnswer': right_ans,
                        'isCorrect': True,
                        'notes': '已复习并订正。',
                    }
                )

        msg3, _ = models.Messages.objects.get_or_create(
            title='考试安排更新',
            sender=teacher1,
            defaults={
                'content': 'Python阶段测试已开放，请按时参加。',
                'type': 'notice',
                'priority': 'medium',
            }
        )
        msg4, _ = models.Messages.objects.get_or_create(
            title='错题复习提醒',
            sender=teacher2,
            defaults={
                'content': '请针对近期错题完成一次复习并提交笔记。',
                'type': 'reminder',
                'priority': 'high',
            }
        )
        models.MessageReads.objects.get_or_create(message=msg3, user=student3, defaults={'isRead': True})
        models.MessageReads.objects.get_or_create(message=msg4, user=student4, defaults={'isRead': False})

        # 11) 保底：每个学生至少 2 条练习记录 / 2 条任务记录 / 2 条错题记录
        all_students = [student1, student2, student3, student4]
        all_papers = [paper1, paper2]
        all_tasks = [task1, task2]

        for st_idx, st in enumerate(all_students, start=1):
            # 练习记录（每位学生两条）
            for p_idx, paper in enumerate(all_papers, start=1):
                day_offset = -(st_idx + p_idx)
                p_log, _ = models.StudentPracticeLogs.objects.update_or_create(
                    student=st,
                    paper=paper,
                    defaults={
                        'startTime': self.now_str(delta_days=day_offset, delta_minutes=-50),
                        'endTime': self.now_str(delta_days=day_offset, delta_minutes=-20),
                        'score': 65 + st_idx * 4 + p_idx * 3,
                        'accuracy': min(0.95, 0.55 + st_idx * 0.07 + p_idx * 0.05),
                        'status': 'completed',
                        'usedTime': 25 + st_idx * 3 + p_idx * 2,
                    }
                )
                models.StudentPracticeAnswers.objects.update_or_create(
                    practiceLog=p_log,
                    practise=practises[(st_idx + p_idx) % len(practises)],
                    defaults={
                        'studentAnswer': '演示答案',
                        'isCorrect': True,
                        'score': 18 + st_idx,
                        'answerTime': self.now_str(delta_days=day_offset, delta_minutes=-30),
                        'aiConfidence': 0.88,
                        'aiFeedback': '演示数据：已完成练习。',
                        'aiAnalysis': '知识点掌握情况稳定。',
                        'aiModel': 'glm-4-flash',
                    }
                )

            # 任务记录（每位学生两条）
            for t_idx, task in enumerate(all_tasks, start=1):
                day_offset = -(st_idx + t_idx)
                t_log, _ = models.StudentTaskLogs.objects.update_or_create(
                    student=st,
                    task=task,
                    defaults={
                        'startTime': self.now_str(delta_days=day_offset, delta_minutes=-70),
                        'endTime': self.now_str(delta_days=day_offset, delta_minutes=-25),
                        'score': 60 + st_idx * 5 + t_idx * 4,
                        'accuracy': min(0.93, 0.5 + st_idx * 0.08 + t_idx * 0.06),
                        'status': 'completed',
                        'usedTime': 30 + st_idx * 4 + t_idx * 3,
                    }
                )
                models.StudentTaskAnswers.objects.update_or_create(
                    taskLog=t_log,
                    practise=practises[(st_idx + t_idx + 2) % len(practises)],
                    defaults={
                        'studentAnswer': '演示作答',
                        'isCorrect': True,
                        'score': 22 + st_idx,
                        'answerTime': self.now_str(delta_days=day_offset, delta_minutes=-40),
                        'aiConfidence': 0.86,
                        'aiFeedback': '演示数据：任务完成。',
                        'aiAnalysis': '可进一步优化答题表达。',
                        'aiModel': 'glm-4-flash',
                    }
                )

            # 错题记录（每位学生两条）
            for w_idx in [1, 2]:
                practise = practises[(st_idx + w_idx) % len(practises)]
                source_task = task1 if w_idx == 1 else task2
                wq, _ = models.WrongQuestions.objects.update_or_create(
                    student=st,
                    practise=practise,
                    source='task',
                    sourceId=source_task.id,
                    defaults={
                        'wrongAnswer': '演示错误答案',
                        'correctAnswer': practise.answer,
                        'analysis': practise.analyse,
                        'isReviewed': (w_idx % 2 == 0),
                        'reviewCount': 1 if w_idx % 2 == 0 else 0,
                        'masteryLevel': 1 if w_idx % 2 == 0 else 0,
                        'lastReviewTime': self.now_str(delta_days=-(st_idx + w_idx)) if w_idx % 2 == 0 else None,
                        'createTime': self.now_str(delta_days=-(st_idx + w_idx + 1)),
                    }
                )
                if w_idx % 2 == 0:
                    models.WrongQuestionReviews.objects.update_or_create(
                        wrongQuestion=wq,
                        reviewTime=self.now_str(delta_days=-(st_idx + w_idx), delta_minutes=-10),
                        defaults={
                            'reviewAnswer': practise.answer,
                            'isCorrect': True,
                            'notes': '演示复习记录。',
                        }
                    )

        # 12) 汇总输出
        self.stdout.write(self.style.SUCCESS('演示数据初始化完成！'))
        self.stdout.write(
            self.style.SUCCESS(
                f'用户={models.Users.objects.count()} 题目={models.Practises.objects.count()} '
                f'考试={models.Exams.objects.count()} 练习卷={models.PracticePapers.objects.count()} '
                f'任务={models.Tasks.objects.count()} 错题={models.WrongQuestions.objects.count()} '
                f'错题复习={models.WrongQuestionReviews.objects.count()} 消息={models.Messages.objects.count()}'
            )
        )
