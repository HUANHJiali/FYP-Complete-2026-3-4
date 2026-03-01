"""
错题本管理视图
处理错题收集、复习、分析等功能
"""
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
import csv

from app import models
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil


class WrongQuestionsView(BaseView):
    """错题本管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return self.get_info(request)
        elif module == 'getPageInfos':
            return self.get_page_infos(request)
        elif module == 'getStudentWrongQuestions':
            return self.get_student_wrong_questions(request)
        elif module == 'getWrongQuestionDetail':
            return self.get_wrong_question_detail(request)
        elif module == 'getReviewHistory':
            return self.get_review_history(request)
        elif module == 'export':
            return self.export_wrong_questions(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'addWrongQuestion':
            return self.add_wrong_question(request)
        elif module == 'markAsReviewed':
            return self.mark_as_reviewed(request)
        elif module == 'addReview':
            return self.add_review(request)
        elif module == 'deleteWrongQuestion':
            return self.delete_wrong_question(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取错题信息"""
        try:
            wrong_question_id = request.GET.get('id')
            if not wrong_question_id:
                return BaseView.error('错题ID不能为空')

            wrong_question = models.WrongQuestions.objects.filter(id=wrong_question_id).first()
            if not wrong_question:
                return BaseView.error('错题不存在')

            # 获取题目详细信息
            practise = wrong_question.practise
            options = models.Options.objects.filter(practise=practise)

            data = {
                'id': wrong_question.id,
                'title': practise.name,
                'type': practise.type,
                'wrongAnswer': wrong_question.wrongAnswer,
                'correctAnswer': wrong_question.correctAnswer,
                'analysis': wrong_question.analysis,
                'isReviewed': wrong_question.isReviewed,
                'reviewCount': wrong_question.reviewCount,
                'lastReviewTime': wrong_question.lastReviewTime,
                'createTime': wrong_question.createTime,
                'options': [{'id': opt.id, 'name': opt.name} for opt in options],
                'project': practise.project.name
            }

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取错题信息失败: {str(e)}')

    @staticmethod
    def get_page_infos(request):
        """分页获取错题列表"""
        try:
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            student_id = request.GET.get('studentId')
            # 允许使用 token 自动识别学生ID
            if not student_id:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                if token:
                    from django.core.cache import cache as _cache
                    student_id = _cache.get(token)

            if not student_id:
                return BaseView.error('学生ID不能为空')

            queryset = models.WrongQuestions.objects.filter(student_id=student_id)

            # 搜索关键字（题目/学科）
            search = request.GET.get('search', '')
            if search:
                queryset = queryset.filter(
                    Q(practise__name__icontains=search) |
                    Q(practise__project__name__icontains=search)
                )

            # 学科筛选
            project_id = request.GET.get('projectId')
            if project_id:
                queryset = queryset.filter(practise__project_id=project_id)

            # 题型筛选
            qtype = request.GET.get('type')
            if qtype not in [None, '']:
                try:
                    qtype_int = int(qtype)
                    if qtype_int in [0, 1, 2, 3]:
                        queryset = queryset.filter(practise__type=qtype_int)
                except Exception:
                    pass

            # 复习状态筛选
            review_status = request.GET.get('reviewStatus')
            if review_status == 'reviewed':
                queryset = queryset.filter(isReviewed=True)
            elif review_status == 'unreviewed':
                queryset = queryset.filter(isReviewed=False)

            # 时间范围筛选
            start_date = request.GET.get('startDate')
            end_date = request.GET.get('endDate')
            if start_date:
                queryset = queryset.filter(createTime__gte=start_date)
            if end_date:
                queryset = queryset.filter(createTime__lte=end_date)

            # 排序
            queryset = queryset.order_by('-createTime')

            paginator = Paginator(queryset, limit)
            wrong_questions = paginator.get_page(page)

            data = []
            for wq in wrong_questions:
                data.append({
                    'id': wq.id,
                    'title': wq.practise.name,
                    'type': wq.practise.type,
                    'project': wq.practise.project.name,
                    'isReviewed': wq.isReviewed,
                    'reviewCount': wq.reviewCount,
                    'createTime': wq.createTime
                })

            return BaseView.successData({
                'list': data,
                'total': paginator.count,
                'page': page,
                'limit': limit
            })
        except Exception as e:
            return BaseView.error(f'获取错题列表失败: {str(e)}')

    @staticmethod
    def get_student_wrong_questions(request):
        """获取学生的错题列表"""
        try:
            student_id = request.GET.get('studentId')
            if not student_id:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                if token:
                    from django.core.cache import cache as _cache
                    student_id = _cache.get(token)
            if not student_id:
                return BaseView.error('学生ID不能为空')

            wrong_questions = models.WrongQuestions.objects.filter(
                student_id=student_id
            ).select_related('practise', 'practise__project').order_by('-createTime')

            data = []
            for wq in wrong_questions:
                data.append({
                    'id': wq.id,
                    'title': wq.practise.name,
                    'type': wq.practise.type,
                    'project': wq.practise.project.name,
                    'isReviewed': wq.isReviewed,
                    'reviewCount': wq.reviewCount,
                    'createTime': wq.createTime
                })

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取学生错题失败: {str(e)}')

    @staticmethod
    def get_wrong_question_detail(request):
        """获取错题详细信息"""
        try:
            wrong_question_id = request.GET.get('id')
            if not wrong_question_id:
                return BaseView.error('错题ID不能为空')

            wrong_question = models.WrongQuestions.objects.filter(id=wrong_question_id).first()
            if not wrong_question:
                return BaseView.error('错题不存在')

            practise = wrong_question.practise
            options = models.Options.objects.filter(practise=practise)

            data = {
                'id': wrong_question.id,
                'title': practise.name,
                'type': practise.type,
                'wrongAnswer': wrong_question.wrongAnswer,
                'correctAnswer': wrong_question.correctAnswer,
                'analysis': wrong_question.analysis,
                'isReviewed': wrong_question.isReviewed,
                'reviewCount': wrong_question.reviewCount,
                'lastReviewTime': wrong_question.lastReviewTime,
                'createTime': wrong_question.createTime,
                'options': [{'id': opt.id, 'name': opt.name} for opt in options],
                'project': practise.project.name
            }

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取错题详情失败: {str(e)}')

    @staticmethod
    def get_review_history(request):
        """获取复习历史"""
        try:
            wrong_question_id = request.GET.get('id')
            if not wrong_question_id:
                return BaseView.error('错题ID不能为空')

            reviews = models.WrongQuestionReviews.objects.filter(
                wrongQuestion_id=wrong_question_id
            ).order_by('-reviewTime')

            data = []
            for review in reviews:
                data.append({
                    'id': review.id,
                    'reviewAnswer': review.reviewAnswer,
                    'isCorrect': review.isCorrect,
                    'reviewTime': review.reviewTime,
                    'notes': review.notes
                })

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取复习历史失败: {str(e)}')

    @staticmethod
    def add_wrong_question(request):
        """添加错题"""
        try:
            student_id = request.POST.get('studentId')
            practise_id = request.POST.get('practiseId')
            source = request.POST.get('source')
            source_id = request.POST.get('sourceId')
            wrong_answer = request.POST.get('wrongAnswer')
            correct_answer = request.POST.get('correctAnswer')
            analysis = request.POST.get('analysis')

            if not all([student_id, practise_id, source, source_id]):
                return BaseView.error('必要参数不能为空')

            try:
                source_id_int = int(source_id)
            except (TypeError, ValueError):
                return BaseView.error('sourceId必须为数字')

            if source_id_int < 0 or source_id_int > 2147483647:
                return BaseView.error('sourceId超出有效范围')

            # 检查是否已存在相同错题
            existing = models.WrongQuestions.objects.filter(
                student_id=student_id,
                practise_id=practise_id,
                source=source,
                sourceId=source_id_int
            ).first()

            if existing:
                return BaseView.error('该错题已存在')

            # 创建错题记录
            wrong_question = models.WrongQuestions.objects.create(
                student_id=student_id,
                practise_id=practise_id,
                source=source,
                sourceId=source_id_int,
                wrongAnswer=wrong_answer,
                correctAnswer=correct_answer,
                analysis=analysis,
                createTime=DateUtil.getNowTime()
            )

            return BaseView.successData({'id': wrong_question.id})
        except Exception as e:
            return BaseView.error(f'添加错题失败: {str(e)}')

    @staticmethod
    def mark_as_reviewed(request):
        """标记为已复习"""
        try:
            wrong_question_id = request.POST.get('id')
            if not wrong_question_id:
                return BaseView.error('错题ID不能为空')

            wrong_question = models.WrongQuestions.objects.filter(id=wrong_question_id).first()
            if not wrong_question:
                return BaseView.error('错题不存在')

            wrong_question.isReviewed = True
            wrong_question.lastReviewTime = DateUtil.getNowTime()
            wrong_question.save()

            return BaseView.successData({'message': '标记成功'})
        except Exception as e:
            return BaseView.error(f'标记失败: {str(e)}')

    @staticmethod
    def add_review(request):
        """添加复习记录"""
        try:
            wrong_question_id = request.POST.get('wrongQuestionId')
            review_answer = request.POST.get('reviewAnswer')
            is_correct = request.POST.get('isCorrect') == 'true'
            notes = request.POST.get('notes', '')

            if not wrong_question_id:
                return BaseView.error('错题ID不能为空')

            wrong_question = models.WrongQuestions.objects.filter(id=wrong_question_id).first()
            if not wrong_question:
                return BaseView.error('错题不存在')

            # 创建复习记录
            review = models.WrongQuestionReviews.objects.create(
                wrongQuestion_id=wrong_question_id,
                reviewAnswer=review_answer,
                isCorrect=is_correct,
                reviewTime=DateUtil.getNowTime(),
                notes=notes
            )

            # 更新错题统计
            wrong_question.reviewCount += 1
            wrong_question.lastReviewTime = DateUtil.getNowTime()
            wrong_question.save()

            return BaseView.successData({'id': review.id})
        except Exception as e:
            return BaseView.error(f'添加复习记录失败: {str(e)}')

    @staticmethod
    def delete_wrong_question(request):
        """删除错题"""
        try:
            wrong_question_id = request.POST.get('id')
            if not wrong_question_id:
                return BaseView.error('错题ID不能为空')

            wrong_question = models.WrongQuestions.objects.filter(id=wrong_question_id).first()
            if not wrong_question:
                return BaseView.error('错题不存在')

            # 删除相关的复习记录
            models.WrongQuestionReviews.objects.filter(wrongQuestion_id=wrong_question_id).delete()

            # 删除错题
            wrong_question.delete()

            return BaseView.successData({'message': '删除成功'})
        except Exception as e:
            return BaseView.error(f'删除失败: {str(e)}')

    @staticmethod
    def export_wrong_questions(request):
        """导出错题为CSV格式"""
        try:
            student_id = request.GET.get('studentId')
            if not student_id:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                if token:
                    from django.core.cache import cache as _cache
                    student_id = _cache.get(token)

            if not student_id:
                return BaseView.error('学生ID不能为空')

            # 获取筛选条件
            search = request.GET.get('search', '')
            project_id = request.GET.get('projectId')
            qtype = request.GET.get('type')
            review_status = request.GET.get('reviewStatus')
            start_date = request.GET.get('startDate')
            end_date = request.GET.get('endDate')

            # 构建查询
            queryset = models.WrongQuestions.objects.filter(student_id=student_id)

            if search:
                queryset = queryset.filter(
                    Q(practise__name__icontains=search) |
                    Q(practise__project__name__icontains=search)
                )

            if project_id:
                queryset = queryset.filter(practise__project_id=project_id)

            if qtype not in [None, '']:
                try:
                    qtype_int = int(qtype)
                    if qtype_int in [0, 1, 2, 3]:
                        queryset = queryset.filter(practise__type=qtype_int)
                except Exception:
                    pass

            if review_status == 'reviewed':
                queryset = queryset.filter(isReviewed=True)
            elif review_status == 'unreviewed':
                queryset = queryset.filter(isReviewed=False)

            if start_date:
                queryset = queryset.filter(createTime__gte=start_date)
            if end_date:
                queryset = queryset.filter(createTime__lte=end_date)

            queryset = queryset.select_related('practise', 'practise__project').order_by('-createTime')

            # 创建CSV响应
            response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
            filename = f'wrong_questions_{DateUtil.getNowTime()}.csv'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            writer = csv.writer(response)
            # 写入表头
            writer.writerow([
                '题目', '题型', '学科', '错误答案', '正确答案',
                '题目分析', '复习状态', '复习次数', '最后复习时间', '创建时间', '来源'
            ])

            # 题型映射
            type_map = {0: '选择题', 1: '填空题', 2: '判断题', 3: '编程题'}

            # 写入数据
            for wq in queryset:
                writer.writerow([
                    wq.practise.name or '',
                    type_map.get(wq.practise.type, '未知'),
                    wq.practise.project.name,
                    wq.wrongAnswer or '',
                    wq.correctAnswer or '',
                    wq.analysis or '',
                    '已复习' if wq.isReviewed else '待复习',
                    wq.reviewCount or 0,
                    wq.lastReviewTime or '',
                    wq.createTime,
                    wq.source or ''
                ])

            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')
