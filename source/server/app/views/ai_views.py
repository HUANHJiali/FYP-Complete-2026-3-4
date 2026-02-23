"""
AI 功能视图
处理 AI 智能评分、自动出题、错题分析等功能
"""
import logging
from comm.BaseView import BaseView
from app.permissions import get_user_from_request
from utils.OperationLogger import OperationLogger

logger = logging.getLogger(__name__)


def _log_ai_operation(request, operation_type, detail, status=1):
    """记录AI操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name='ai',
                resource_name=detail,
                status=status,
                request=request
            )
    except Exception:
        pass


class AIView(BaseView):
    """AI功能视图类"""

    def get(self, request, module, *args, **kwargs):
        if module == 'generate_questions':
            return self.generate_questions(request)
        elif module == 'analyze_wrong_answer':
            return self.analyze_wrong_answer(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'score_answer':
            return self.score_answer(request)
        elif module == 'generate_questions':
            return self.generate_questions(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def score_answer(request):
        """AI评分功能"""
        try:
            from comm.AIUtils import AIUtils

            question_content = request.POST.get('questionContent')
            correct_answer = request.POST.get('correctAnswer')
            student_answer = request.POST.get('studentAnswer')
            question_type = int(request.POST.get('questionType', 0))
            max_score = float(request.POST.get('maxScore', 10.0))

            if not all([question_content, correct_answer, student_answer]):
                return BaseView.error('缺少必要参数')

            ai_utils = AIUtils()

            result = ai_utils.ai_score_answer(
                question_content=question_content,
                correct_answer=correct_answer,
                student_answer=student_answer,
                question_type=question_type,
                max_score=max_score
            )

            _log_ai_operation(request, 'other', f'AI评分-得分{result.get("score", 0)}')
            return BaseView.successData(result)

        except Exception as e:
            logger.error(f"AI评分失败: {str(e)}", exc_info=True)
            _log_ai_operation(request, 'other', f'AI评分失败-{str(e)}', status=0)
            return BaseView.error(f'AI评分失败: {str(e)}')

    @staticmethod
    def generate_questions(request):
        """AI自动创建题目功能"""
        try:
            from comm.AIUtils import AIUtils

            subject = request.POST.get('subject') or request.GET.get('subject')
            topic = request.POST.get('topic') or request.GET.get('topic')
            difficulty = request.POST.get('difficulty') or request.GET.get('difficulty', 'medium')
            question_type = int(request.POST.get('questionType') or request.GET.get('questionType', 0))
            count = int(request.POST.get('count') or request.GET.get('count', 5))

            if not all([subject, topic]):
                return BaseView.error('缺少必要参数：科目和主题')

            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'

            if question_type not in [0, 1, 2, 3]:
                return BaseView.error('无效的题目类型')

            if count < 1 or count > 20:
                count = 5

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

            _log_ai_operation(request, 'create', f'AI生成题目-{subject}-{topic}-{len(questions)}道')
            return BaseView.successData({
                'questions': questions,
                'count': len(questions),
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty,
                'question_type': question_type
            })

        except Exception as e:
            logger.error(f"AI生成题目失败: {str(e)}", exc_info=True)
            _log_ai_operation(request, 'create', f'AI生成题目失败-{str(e)}', status=0)
            return BaseView.error(f'AI生成题目失败: {str(e)}')

    @staticmethod
    def analyze_wrong_answer(request):
        """AI分析错误答案"""
        try:
            from comm.AIUtils import AIUtils

            question_content = request.GET.get('questionContent')
            correct_answer = request.GET.get('correctAnswer')
            student_answer = request.GET.get('studentAnswer')
            question_type = int(request.GET.get('questionType', 0))

            if not all([question_content, correct_answer, student_answer]):
                return BaseView.error('缺少必要参数')

            ai_utils = AIUtils()

            result = ai_utils.ai_analyze_wrong_answer(
                question_content=question_content,
                correct_answer=correct_answer,
                student_answer=student_answer,
                question_type=question_type
            )

            _log_ai_operation(request, 'other', 'AI分析错题')
            return BaseView.successData(result)

        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}", exc_info=True)
            _log_ai_operation(request, 'other', f'AI分析失败-{str(e)}', status=0)
            return BaseView.error(f'AI分析失败: {str(e)}')
