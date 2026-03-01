"""
管理员 AI 练习试卷生成相关视图

从 admin 视图中拆分 AI 练习试卷生成功能，降低单文件复杂度。
"""

from app import models
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil


class AdminPracticePaperAIView:
    """管理员 AI 练习试卷生成接口集合"""

    @staticmethod
    def generate_ai_practice_paper(request):
        """AI 生成练习试卷并入库：先生成题目入库，再创建试卷并关联题目。"""
        try:
            from comm.AIUtils import AIUtils
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            question_type = int(request.POST.get('questionType', 0))
            count = int(request.POST.get('count', 10))
            subject_id = request.POST.get('subjectId')
            teacher_id = request.POST.get('teacherId')
            duration = int(request.POST.get('duration', 60))
            total_score = int(request.POST.get('totalScore', 100))
            title = request.POST.get('title')

            if not all([subject, topic, subject_id, teacher_id]):
                return BaseView.error('缺少必要参数：subject/topic/subjectId/teacherId')

            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'
            if question_type not in [0, 1, 2, 3]:
                return BaseView.error('无效的题目类型')
            if count < 1 or count > 50:
                count = 10

            subject_obj = models.Projects.objects.filter(id=subject_id).first()
            teacher_obj = models.Users.objects.filter(id=teacher_id).first()
            if not subject_obj:
                return BaseView.error('科目不存在')
            if not teacher_obj:
                return BaseView.error('教师不存在')

            ai_utils = AIUtils()
            questions = ai_utils.ai_generate_questions(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                count=count
            )
            if not questions:
                return BaseView.error('AI生成题目失败')

            created_practises = []
            for question in questions:
                try:
                    practise = models.Practises.objects.create(
                        name=question['content'],
                        type=question_type,
                        project=subject_obj,
                        answer=question['answer'],
                        analyse=question.get('analysis', ''),
                        createTime=DateUtil.getNowDateTime()
                    )
                    if question_type == 0 and 'options' in question:
                        for option in question['options']:
                            models.Options.objects.create(practise=practise, name=option)
                    created_practises.append(practise)
                except Exception as ie:
                    print(f'保存题目失败: {str(ie)}')
                    continue

            if not created_practises:
                return BaseView.error('题目入库失败')

            paper_title = title or f"{subject}-{topic}-{difficulty}-{DateUtil.getNowDateTime()}"
            paper = models.PracticePapers.objects.create(
                title=paper_title,
                description='AI自动生成练习试卷',
                type='fixed',
                difficulty=difficulty,
                duration=duration,
                totalScore=total_score,
                project=subject_obj,
                teacher=teacher_obj,
                createTime=DateUtil.getNowDateTime(),
                isActive=True
            )

            per_score = round(total_score / len(created_practises), 2)
            for idx, practise in enumerate(created_practises, start=1):
                models.PracticePaperQuestions.objects.create(
                    paper=paper,
                    practise=practise,
                    questionOrder=idx,
                    score=per_score
                )

            return BaseView.successData({
                'paperId': paper.id,
                'title': paper.title,
                'questionCount': len(created_practises)
            })
        except Exception as e:
            return BaseView.error(f'生成练习试卷失败: {str(e)}')

    @staticmethod
    def generate_ai_practice_paper_counts(request):
        """按不同题型数量一次性生成练习试卷。"""
        try:
            from comm.AIUtils import AIUtils
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            subject_id = request.POST.get('subjectId')
            teacher_id = request.POST.get('teacherId')
            title = request.POST.get('title')
            duration = int(request.POST.get('duration', 60))
            counts_raw = request.POST.get('counts', '0:10,1:10,2:10,3:2')

            if not all([subject, topic, subject_id, teacher_id]):
                return BaseView.error('缺少必要参数：subject/topic/subjectId/teacherId')

            subject_obj = models.Projects.objects.filter(id=subject_id).first()
            teacher_obj = models.Users.objects.filter(id=teacher_id).first()
            if not subject_obj:
                return BaseView.error('科目不存在')
            if not models.Teachers.objects.filter(user=teacher_obj).exists():
                return BaseView.error('教师不存在')

            count_map = {0: 10, 1: 10, 2: 10, 3: 2}
            try:
                parts = [p for p in counts_raw.split(',') if ':' in p]
                for p in parts:
                    k, v = p.split(':', 1)
                    k_i = int(k)
                    v_i = int(v)
                    if k_i in [0, 1, 2, 3] and v_i >= 0:
                        count_map[k_i] = v_i
            except Exception:
                pass

            paper = models.PracticePapers.objects.create(
                title=title or f"{subject}-{topic}-{difficulty}-{DateUtil.getNowDateTime()}",
                description='AI自动生成练习试卷（多题型）',
                type='fixed',
                difficulty=difficulty,
                duration=duration,
                totalScore=count_map.get(0, 0) * 2 + count_map.get(1, 0) * 2 +
                count_map.get(2, 0) * 2 + count_map.get(3, 0) * 20,
                project=subject_obj,
                teacher=teacher_obj,
                createTime=DateUtil.getNowDateTime(),
                isActive=True
            )

            ai = AIUtils()
            order = 1
            created = {0: 0, 1: 0, 2: 0, 3: 0}
            for t in [0, 1, 2, 3]:
                c = int(count_map.get(t, 0))
                if c <= 0:
                    continue
                questions = ai.ai_generate_questions(
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    question_type=t,
                    count=c
                ) or []
                for question in questions:
                    practise = models.Practises.objects.create(
                        name=question.get('content', ''),
                        type=t,
                        project=subject_obj,
                        answer=question.get('answer', ''),
                        analyse=question.get('analysis', ''),
                        createTime=DateUtil.getNowDateTime()
                    )
                    if t == 0 and 'options' in question:
                        for option in question['options']:
                            models.Options.objects.create(practise=practise, name=option)
                    score = 2 if t in [0, 1, 2] else 20
                    models.PracticePaperQuestions.objects.create(
                        paper=paper,
                        practise=practise,
                        questionOrder=order,
                        score=score
                    )
                    order += 1
                    created[t] += 1

            return BaseView.successData({
                'paperId': paper.id,
                'title': paper.title,
                'createdByType': created,
                'totalScore': paper.totalScore
            })
        except Exception as e:
            return BaseView.error(f'生成失败: {str(e)}')
