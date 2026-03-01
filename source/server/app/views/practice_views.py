"""
练习系统视图
处理练习试卷管理、学生练习等功能
"""
from django.core.paginator import Paginator
from django.db.models import Q

from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil
from comm.lifecycle_status import resolve_practice_lifecycle, status_text
from comm.cache_decorator import cache_api_response
from django.core.cache import cache
from utils.OperationLogger import OperationLogger


def _log_practice_operation(request, operation_type, resource_id, resource_name, status=1):
    """记录练习试卷操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name='practice',
                resource_id=str(resource_id),
                resource_name=resource_name,
                status=status,
                request=request
            )
    except Exception:
        pass


class PracticePapersView(BaseView):
    """练习试卷管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return self.get_page_infos(request)
        elif module == 'info':
            return self.get_info(request)
        elif module == 'questions':
            return self.get_paper_questions(request)
        elif module == 'student':
            return self.get_student_papers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'del':
            return self.del_info(request)
        elif module == 'generate_wrong':
            return self.generate_wrong_practice_paper(request)
        elif module == 'generate_ai':
            return self.generate_ai_practice_paper(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取指定ID的练习试卷信息"""
        paper = models.PracticePapers.objects.filter(id=request.GET.get('id')).first()
        if not paper:
            return BaseView.error('练习试卷不存在')

        # 获取题目分布
        questions = models.PracticePaperQuestions.objects.filter(paper=paper).order_by('questionOrder')
        questionDistribution = {}
        for q in questions:
            questionType = q.practise.type
            if questionType not in questionDistribution:
                questionDistribution[questionType] = 0
            questionDistribution[questionType] += 1

        return BaseView.successData({
            'id': paper.id,
            'title': paper.title,
            'description': paper.description,
            'type': paper.type,
            'difficulty': paper.difficulty,
            'duration': paper.duration,
            'totalScore': paper.totalScore,
            'projectId': paper.project.id,
            'projectName': paper.project.name,
            'teacherId': paper.teacher.id,
            'teacherName': paper.teacher.name,
            'createTime': paper.createTime,
            'isActive': paper.isActive,
            'questionCount': questions.count(),
            'questionDistribution': questionDistribution
        })

    @staticmethod
    @cache_api_response(timeout=60, key_prefix='practice_papers_page')
    def get_page_infos(request):
        """分页查询练习试卷信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        title = request.GET.get('title')
        type = request.GET.get('type')
        difficulty = request.GET.get('difficulty')
        projectId = request.GET.get('projectId')

        query = Q(isActive=True)
        if title:
            query = query & Q(title__contains=title)
        if type:
            query = query & Q(type=type)
        if difficulty:
            query = query & Q(difficulty=difficulty)
        if projectId:
            query = query & Q(project__id=int(projectId))

        data = models.PracticePapers.objects.filter(query).order_by('-createTime')
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            # 获取题目数量
            questionCount = models.PracticePaperQuestions.objects.filter(paper=item).count()
            lifecycle_status = resolve_practice_lifecycle(log_status=None, is_active=item.isActive)

            resl.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'type': item.type,
                'difficulty': item.difficulty,
                'duration': item.duration,
                'totalScore': item.totalScore,
                'projectId': item.project.id,
                'projectName': item.project.name,
                'createTime': item.createTime,
                'questionCount': questionCount,
                'lifecycleStatus': lifecycle_status,
                'lifecycleStatusText': status_text(lifecycle_status)
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def get_student_papers(request):
        """获取学生可用的练习试卷"""
        studentId = cache.get(request.GET.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        student = models.Users.objects.filter(id=studentId).first()
        if not student or student.type != 2:
            return BaseView.error('用户身份错误')

        # 获取学生信息
        studentInfo = models.Students.objects.filter(user=student).first()
        if not studentInfo:
            return BaseView.error('学生信息不存在')

        # 获取学生所在年级的练习试卷
        papers = models.PracticePapers.objects.filter(
            isActive=True,
            project__id__in=models.Practises.objects.filter(
                project__id__in=models.Projects.objects.all()
            ).values_list('project__id', flat=True).distinct()
        ).order_by('-createTime')

        resl = []
        for paper in papers:
            # 获取题目数量
            questionCount = models.PracticePaperQuestions.objects.filter(paper=paper).count()

            # 检查学生是否已完成该试卷
            practiceLog = models.StudentPracticeLogs.objects.filter(
                student=student,
                paper=paper,
                status='completed'
            ).first()

            # 检查是否有进行中的练习
            inProgressLog = models.StudentPracticeLogs.objects.filter(
                student=student,
                paper=paper,
                status='in_progress'
            ).first()

            if practiceLog:
                status = 'completed'
                score = practiceLog.score
                usedTime = practiceLog.usedTime
                accuracy = practiceLog.accuracy
            elif inProgressLog:
                status = 'in_progress'
                score = 0
                usedTime = 0
                accuracy = 0
            else:
                status = 'not_started'
                score = 0
                usedTime = 0
                accuracy = 0

            lifecycle_status = resolve_practice_lifecycle(log_status=status, is_active=paper.isActive)

            resl.append({
                'id': paper.id,
                'title': paper.title,
                'description': paper.description,
                'type': paper.type,
                'difficulty': paper.difficulty,
                'duration': paper.duration,
                'totalScore': paper.totalScore,
                'projectId': paper.project.id,
                'projectName': paper.project.name,
                'createTime': paper.createTime,
                'questionCount': questionCount,
                'status': status,
                'score': score,
                'usedTime': usedTime,
                'accuracy': accuracy,
                'lifecycleStatus': lifecycle_status,
                'lifecycleStatusText': status_text(lifecycle_status)
            })

        return BaseView.successData(resl)

    @staticmethod
    def get_paper_questions(request):
        """获取试卷题目"""
        paperId = request.GET.get('paperId')
        if not paperId:
            return BaseView.error('试卷ID不能为空')

        # 获取token以查询学生答案（如果有）
        token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        logId = request.GET.get('logId')

        questions = models.PracticePaperQuestions.objects.filter(
            paper__id=paperId
        ).order_by('questionOrder')

        # 如果有logId，获取已保存的答案
        saved_answers = {}
        if logId:
            answers = models.StudentPracticeAnswers.objects.filter(
                practiceLog__id=logId
            )
            for ans in answers:
                saved_answers[ans.practise_id] = ans.studentAnswer

        resl = []
        for q in questions:
            practise = q.practise
            questionData = {
                'practiseId': practise.id,  # 修改字段名以匹配前端
                'practiseType': practise.type,  # 修改字段名以匹配前端
                'questionOrder': q.questionOrder,
                'score': q.score,
                'type': practise.type,  # 保留type字段以兼容
                'content': practise.name,
                'analyse': practise.analyse,
                'studentAnswer': saved_answers.get(practise.id, None)  # 添加学生答案
            }

            # 如果是选择题，获取选项
            if practise.type == 0:
                options = models.Options.objects.filter(practise=practise)
                questionData['options'] = [opt.name for opt in options]

            resl.append(questionData)

        return BaseView.successData(resl)

    @staticmethod
    def add_info(request):
        """添加练习试卷"""
        paper = models.PracticePapers.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            type=request.POST.get('type'),
            difficulty=request.POST.get('difficulty'),
            duration=request.POST.get('duration'),
            totalScore=request.POST.get('totalScore'),
            project=models.Projects.objects.get(id=request.POST.get('projectId')),
            teacher=models.Users.objects.get(id=request.POST.get('teacherId')),
            createTime=DateUtil.getNowDateTime()
        )
        _log_practice_operation(request, 'create', paper.id, paper.title)
        return BaseView.success()

    @staticmethod
    def upd_info(request):
        """修改练习试卷"""
        paper_id = request.POST.get('id')
        paper = models.PracticePapers.objects.filter(id=paper_id).first()
        paper_title = paper.title if paper else paper_id
        
        models.PracticePapers.objects.filter(
            id=request.POST.get('id')
        ).update(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            type=request.POST.get('type'),
            difficulty=request.POST.get('difficulty'),
            duration=request.POST.get('duration'),
            totalScore=request.POST.get('totalScore'),
            project=models.Projects.objects.get(id=request.POST.get('projectId')),
            isActive=request.POST.get('isActive')
        )
        _log_practice_operation(request, 'update', paper_id, paper_title)
        return BaseView.success()

    @staticmethod
    def del_info(request):
        """删除练习试卷（软删除）"""
        paper_id = request.POST.get('id')
        paper = models.PracticePapers.objects.filter(id=paper_id).first()
        paper_title = paper.title if paper else paper_id
        
        models.PracticePapers.objects.filter(
            id=request.POST.get('id')
        ).update(isActive=False)
        _log_practice_operation(request, 'delete', paper_id, paper_title)
        return BaseView.success()

    @staticmethod
    def generate_wrong_practice_paper(request):
        """基于学生错题自动生成专项练习试卷"""
        try:
            studentId = cache.get(request.POST.get('token'))
            if not studentId:
                return BaseView.error('用户未登录')

            limit = int(request.POST.get('limit', 10))
            projectId = request.POST.get('projectId')

            wrong_query = models.WrongQuestions.objects.filter(student__id=studentId)
            if projectId:
                wrong_query = wrong_query.filter(practise__project__id=projectId)

            wrong_query = wrong_query.order_by('-createTime')
            wrong_list = list(wrong_query[:limit])
            if len(wrong_list) == 0:
                return BaseView.error('没有可用的错题')

            # 选择第一道错题的学科作为试卷学科
            first_practise = wrong_list[0].practise
            project = first_practise.project

            # 创建专项试卷
            title = f"错题专项-{DateUtil.getNowDateTime()}"
            paper = models.PracticePapers.objects.create(
                title=title,
                description='系统基于错题自动生成的专项练习',
                type='fixed',
                difficulty='medium',
                duration=30,
                totalScore=len(wrong_list),
                project=project,
                teacher=models.Users.objects.get(id=studentId),
                createTime=DateUtil.getNowDateTime(),
                isActive=True
            )

            # 生成题目关联
            for idx, wq in enumerate(wrong_list, start=1):
                models.PracticePaperQuestions.objects.create(
                    paper=paper,
                    practise=wq.practise,
                    questionOrder=idx,
                    score=1.0
                )

            return BaseView.successData({'paperId': paper.id, 'title': paper.title})
        except Exception as e:
            return BaseView.error(f'生成错题专项失败: {str(e)}')

    @staticmethod
    def generate_ai_practice_paper(request):
        """AI智能组卷"""
        try:
            teacherId = cache.get(request.POST.get('token'))
            if not teacherId:
                return BaseView.error('用户未登录')

            title = request.POST.get('title')
            projectId = request.POST.get('projectId')
            difficulty = request.POST.get('difficulty', 'medium')
            duration = int(request.POST.get('duration', 30))
            questionCounts = request.POST.get('questionCounts', '{}')

            import json
            try:
                questionCounts = json.loads(questionCounts)
            except:
                questionCounts = {'0': 5, '1': 3, '2': 2}  # 默认：5选择、3填空、2判断

            if not all([title, projectId]):
                return BaseView.error('标题和学科不能为空')

            project = models.Projects.objects.filter(id=projectId).first()
            if not project:
                return BaseView.error('学科不存在')

            teacher = models.Users.objects.filter(id=teacherId).first()
            if not teacher:
                return BaseView.error('教师不存在')

            # 调用AI生成题目
            from comm.AIUtils import AIUtils
            ai_utils = AIUtils()

            questions_data = []

            # 按题型生成题目
            question_type_names = {0: '选择题', 1: '填空题', 2: '判断题', 3: '编程题'}
            total_score = 0
            question_order = 0

            for qtype, count in questionCounts.items():
                try:
                    count = int(count)
                    if count <= 0:
                        continue
                except:
                    continue

                # AI生成题目
                try:
                    generated_questions = ai_utils.ai_generate_questions(
                        subject=project.name,
                        topic='综合练习',
                        difficulty=difficulty,
                        question_type=int(qtype),
                        count=count
                    )

                    for q_data in generated_questions:
                        # 创建题目
                        practise = models.Practises.objects.create(
                            name=q_data.get('content', ''),
                            answer=q_data.get('answer', ''),
                            analyse=q_data.get('analysis', ''),
                            project=project,
                            type=int(qtype),
                            createTime=DateUtil.getNowDateTime()
                        )

                        # 如果是选择题，创建选项
                        if int(qtype) == 0:
                            options = q_data.get('options', [])
                            for i, opt_text in enumerate(options):
                                models.Options.objects.create(
                                    practise=practise,
                                    name=opt_text
                                )

                        questions_data.append({
                            'practise': practise,
                            'score': 2.0 if int(qtype) != 3 else 10.0,  # 编程题10分，其他2分
                            'order': question_order + 1
                        })
                        total_score += questions_data[-1]['score']
                        question_order += 1

                except Exception as e:
                    # AI生成失败，尝试从题库随机抽取
                    existing_questions = models.Practises.objects.filter(
                        project=project,
                        type=int(qtype)
                    ).exclude(
                        id__in=[q['practise'].id for q in questions_data]
                    )[:count]

                    for q in existing_questions:
                        questions_data.append({
                            'practise': q,
                            'score': 2.0 if int(qtype) != 3 else 10.0,
                            'order': question_order + 1
                        })
                        total_score += questions_data[-1]['score']
                        question_order += 1

            if len(questions_data) == 0:
                return BaseView.error('生成题目失败，请检查AI配置或题库')

            # 创建练习试卷
            paper = models.PracticePapers.objects.create(
                title=title,
                description=f'AI智能生成的{difficulty}难度练习卷',
                type='fixed',
                difficulty=difficulty,
                duration=duration,
                totalScore=total_score,
                project=project,
                teacher=teacher,
                createTime=DateUtil.getNowDateTime(),
                isActive=True
            )

            # 关联题目到试卷
            for q_data in questions_data:
                models.PracticePaperQuestions.objects.create(
                    paper=paper,
                    practise=q_data['practise'],
                    questionOrder=q_data['order'],
                    score=q_data['score']
                )

            return BaseView.successData({
                'paperId': paper.id,
                'title': paper.title,
                'questionCount': len(questions_data),
                'totalScore': total_score
            })
        except Exception as e:
            return BaseView.error(f'AI组卷失败: {str(e)}')


class StudentPracticeView(BaseView):
    """学生练习记录视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'logs':
            return self.get_practice_logs(request)
        elif module == 'answers':
            return self.get_practice_answers(request)
        elif module == 'export':
            return self.export_practice_logs(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'start':
            return self.start_practice(request)
        elif module == 'save':
            return self.save_practice(request)
        elif module == 'submit':
            return self.submit_practice(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_practice_logs(request):
        """获取学生练习记录"""
        try:
            studentId = request.GET.get('studentId')
            if not studentId:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                studentId = cache.get(token) if token else None

            if not studentId:
                return BaseView.error('学生ID不能为空')

            logs = models.StudentPracticeLogs.objects.filter(
                student__id=studentId
            ).select_related('paper', 'paper__project').order_by('-createTime')

            data = []
            for log in logs:
                data.append({
                    'id': log.id,
                    'paperId': log.paper.id,
                    'paperTitle': log.paper.title,
                    'projectName': log.paper.project.name,
                    'status': log.status,
                    'score': log.score,
                    'accuracy': log.accuracy,
                    'usedTime': log.usedTime,
                    'startTime': log.startTime if log.startTime else '',
                    'endTime': log.endTime if log.endTime else '',
                    'createTime': log.createTime.strftime('%Y-%m-%d %H:%M:%S') if log.createTime else ''
                })

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取练习记录失败: {str(e)}')

    @staticmethod
    def get_practice_answers(request):
        """获取练习答题记录"""
        try:
            logId = request.GET.get('logId')
            if not logId:
                return BaseView.error('练习记录ID不能为空')

            answers = models.StudentPracticeAnswers.objects.filter(
                practiceLog__id=logId
            ).select_related('practise', 'practise__project').order_by('answerTime')

            data = []
            for answer in answers:
                data.append({
                    'id': answer.id,
                    'practiseId': answer.practise.id,
                    'questionContent': answer.practise.name,
                    'questionType': answer.practise.type,
                    'studentAnswer': answer.studentAnswer,
                    'isCorrect': answer.isCorrect,
                    'answerTime': answer.answerTime if answer.answerTime else ''
                })

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取答题记录失败: {str(e)}')

    @staticmethod
    def start_practice(request):
        """开始练习"""
        try:
            studentId = cache.get(request.POST.get('token'))
            if not studentId:
                return BaseView.error('用户未登录')

            paperId = request.POST.get('paperId')
            if not paperId:
                return BaseView.error('试卷ID不能为空')

            paper = models.PracticePapers.objects.filter(id=paperId).first()
            if not paper:
                return BaseView.error('练习试卷不存在')

            # 检查是否有进行中的练习
            existingLog = models.StudentPracticeLogs.objects.filter(
                student__id=studentId,
                paper=paper,
                status='in_progress'
            ).first()

            if existingLog:
                return BaseView.successData({
                    'logId': existingLog.id,
                    'message': '继续现有练习'
                })

            # 创建新的练习记录
            practiceLog = models.StudentPracticeLogs.objects.create(
                student_id=studentId,
                paper=paper,
                status='in_progress',
                startTime=DateUtil.getNowDateTime()
            )

            return BaseView.successData({
                'logId': practiceLog.id,
                'message': '练习开始成功'
            })
        except Exception as e:
            return BaseView.error(f'开始练习失败: {str(e)}')

    @staticmethod
    def submit_practice(request):
        """提交练习"""
        try:
            logId = request.POST.get('logId')
            if not logId:
                return BaseView.error('练习记录ID不能为空')

            practiceLog = models.StudentPracticeLogs.objects.filter(id=logId).first()
            if not practiceLog:
                return BaseView.error('练习记录不存在')

            # 解析答案数据
            import json
            try:
                answersData = json.loads(request.POST.get('answers'))
            except:
                answersData = []

            # 获取AI工具实例
            from comm.AIUtils import AIUtils
            ai_utils = AIUtils()

            # 保存答案并自动评分
            correct_count = 0
            total_count = 0

            for answerData in answersData:
                practiseId = answerData.get('practiseId')
                studentAnswer = answerData.get('studentAnswer')

                practise = models.Practises.objects.filter(id=practiseId).first()
                if not practise:
                    continue

                total_count += 1

                # 评分逻辑：支持AI评分
                is_correct = False
                ai_feedback = ''
                ai_analysis = ''
                ai_confidence = None
                question_score = 2.0  # 默认每题2分

                if practise.type in [0, 2]:  # 选择题和判断题
                    # 传统评分：直接对比答案
                    if str(studentAnswer).strip().lower() == str(practise.answer).strip().lower():
                        is_correct = True
                        correct_count += 1
                        question_score = 2.0
                    else:
                        question_score = 0.0

                elif practise.type in [1, 3]:  # 填空题和编程题
                    # AI评分
                    try:
                        max_score = 20.0 if practise.type == 3 else 2.0
                        ai_result = ai_utils.ai_score_answer(
                            question_content=practise.name,
                            correct_answer=practise.answer or '',
                            student_answer=studentAnswer or '',
                            question_type=practise.type,
                            max_score=max_score
                        )

                        question_score = float(ai_result.get('score', 0))
                        ai_confidence = ai_result.get('confidence')
                        ai_feedback = ai_result.get('feedback', '')
                        ai_analysis = ai_result.get('analysis', '')

                        # 如果得分超过60%，认为正确
                        if question_score >= max_score * 0.6:
                            is_correct = True
                            correct_count += 1
                    except Exception as e:
                        # AI评分失败，降级为0分
                        question_score = 0.0
                        is_correct = False

                # 保存答案
                models.StudentPracticeAnswers.objects.create(
                    practiceLog=practiceLog,
                    practise=practise,
                    studentAnswer=studentAnswer,
                    isCorrect=is_correct,
                    score=question_score,
                    answerTime=DateUtil.getNowDateTime(),
                    aiConfidence=ai_confidence,
                    aiFeedback=ai_feedback,
                    aiAnalysis=ai_analysis
                )

                # 错题自动收集：如果答错，加入错题本
                if not is_correct:
                    try:
                        models.WrongQuestions.objects.get_or_create(
                            student=practiceLog.student,
                            practise=practise,
                            source='practice',
                            sourceId=str(logId),
                            defaults={
                                'wrongAnswer': studentAnswer,
                                'correctAnswer': practise.answer,
                                'analysis': ai_analysis,
                                'createTime': DateUtil.getNowDateTime()
                            }
                        )
                    except Exception:
                        # 错题收集失败不影响主流程
                        pass

            # 计算正确率和得分
            accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
            score = practiceLog.paper.totalScore * (accuracy / 100)

            # 更新练习记录
            practiceLog.status = 'completed'
            practiceLog.endTime = DateUtil.getNowDateTime()
            practiceLog.score = score
            practiceLog.accuracy = accuracy
            practiceLog.save()

            return BaseView.successData({
                'score': score,
                'accuracy': accuracy
            })
        except Exception as e:
            return BaseView.error(f'提交练习失败: {str(e)}')

    @staticmethod
    def save_practice(request):
        """保存单题练习进度"""
        try:
            logId = request.POST.get('logId')
            practiseId = request.POST.get('practiseId') or request.POST.get('id')
            studentAnswer = request.POST.get('studentAnswer', '')

            if not logId:
                return BaseView.error('练习记录ID不能为空')
            if not practiseId:
                return BaseView.error('题目ID不能为空')

            practiceLog = models.StudentPracticeLogs.objects.filter(id=logId).first()
            if not practiceLog:
                return BaseView.error('练习记录不存在')

            practise = models.Practises.objects.filter(id=practiseId).first()
            if not practise:
                return BaseView.error('题目不存在')

            answer = models.StudentPracticeAnswers.objects.filter(
                practiceLog=practiceLog,
                practise=practise
            ).first()

            if answer:
                answer.studentAnswer = studentAnswer
                answer.answerTime = DateUtil.getNowDateTime()
                answer.save()
            else:
                models.StudentPracticeAnswers.objects.create(
                    practiceLog=practiceLog,
                    practise=practise,
                    studentAnswer=studentAnswer,
                    answerTime=DateUtil.getNowDateTime()
                )

            return BaseView.successData({'message': '保存成功'})
        except Exception as e:
            return BaseView.error(f'保存练习进度失败: {str(e)}')

    @staticmethod
    def export_practice_logs(request):
        """导出练习记录"""
        try:
            studentId = request.GET.get('studentId')
            if not studentId:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                studentId = cache.get(token) if token else None

            if not studentId:
                return BaseView.error('学生ID不能为空')

            # 获取练习记录
            logs = models.StudentPracticeLogs.objects.filter(
                student__id=studentId,
                status='completed'
            ).select_related('paper', 'paper__project')

            # 生成Excel文件（需要pandas）
            import pandas as pd
            from django.http import HttpResponse

            data = []
            for log in logs:
                data.append({
                    '试卷名称': log.paper.title,
                    '学科': log.paper.project.name,
                    '得分': log.score,
                    '正确率': f"{log.accuracy}%",
                    '用时（分钟）': log.usedTime,
                    '开始时间': log.startTime,
                    '结束时间': log.endTime
                })

            df = pd.DataFrame(data)

            # 生成Excel文件
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="practice_logs_{DateUtil.getNowDateTime()}.xlsx"'
            df.to_excel(excel_writer=response, index=False)

            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')
