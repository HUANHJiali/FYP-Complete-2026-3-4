"""
数据库查询优化补丁
包含针对常见N+1查询问题的优化方案
"""

# ============================================================
# 优化补丁1: 考试日志查��优化
# ============================================================

# 优化前 (存在N+1问题):
"""
def getPageStudentLogs(request):
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    student_id = request.GET.get('studentId')

    # 这里的查询会触发N+1问题
    exam_logs = models.ExamLogs.objects.filter(studentId_id=student_id)
    for log in exam_logs:
        print(log.examId.title)  # 每次访问都查询数据库
        print(log.studentId.userName)  # 每次访问都查询数据库
"""

# 优化后:
def getPageStudentLogs_optimized(request):
    """优化的学生考试日志查询"""
    from app.models import ExamLogs
    from django.core.paginator import Paginator
    from app.comm.BaseView import BaseView

    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    student_id = request.GET.get('studentId')

    # 使用select_related预加载关联对象
    exam_logs = ExamLogs.objects.select_related(
        'examId',      # 预加载考试信息
        'studentId'    # 预加载学生���息
    ).filter(studentId_id=student_id).order_by('-createTime')

    paginator = Paginator(exam_logs, size)
    page_data = paginator.get_page(page)

    # 构建响应数据
    data = []
    for log in page_data:
        data.append({
            'id': log.id,
            'examTitle': log.examId.title,  # 现在不会触发额外查询
            'studentName': log.studentId.userName,  # 现在不会触发额外查询
            'score': log.score,
            'status': log.status,
            'createTime': log.createTime.strftime('%Y-%m-%d %H:%M:%S') if log.createTime else ''
        })

    return BaseView.successData({
        'list': data,
        'total': paginator.count,
        'page': page,
        'size': size
    })


# ============================================================
# 优化补丁2: 练习记录查询优化
# ============================================================

def getPracticeLogs_optimized(request):
    """优化的练习记录查询"""
    from app.models import StudentPracticeLogs
    from app.comm.BaseView import BaseView

    student_id = request.GET.get('studentId')

    # 使用select_related预加载
    practice_logs = StudentPracticeLogs.objects.select_related(
        'practicePaper',  # 预加载练习试卷
        'studentId'       # 预加载学生信息
    ).filter(studentId_id=student_id).order_by('-createTime')

    data = []
    for log in practice_logs:
        data.append({
            'id': log.id,
            'paperTitle': log.practicePaper.title,  # 预加载，无额外查询
            'studentName': log.studentId.userName,
            'score': log.score,
            'createTime': log.createTime.strftime('%Y-%m-%d %H:%M:%S') if log.createTime else ''
        })

    return BaseView.successData(data)


# ============================================================
# 优化补丁3: 错题查询优化
# ============================================================

def getWrongQuestions_optimized(request):
    """优化的错题查询"""
    from app.models import WrongQuestions
    from app.comm.BaseView import BaseView

    student_id = request.GET.get('studentId')
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 20))

    # 使用select_related预加载多层关联
    wrong_questions = WrongQuestions.objects.select_related(
        'studentId',              # 学生信息
        'questionId',             # 题目信息
        'questionId__project'     # 科目信息（多层预加载）
    ).filter(studentId_id=student_id).order_by('-createTime')

    # 分页
    from django.core.paginator import Paginator
    paginator = Paginator(wrong_questions, size)
    page_data = paginator.get_page(page)

    data = []
    for wq in page_data:
        data.append({
            'id': wq.id,
            'questionContent': wq.questionId.name,  # 预加载
            'subjectName': wq.questionId.project.name,  # 预加载
            'wrongCount': wq.wrongCount,
            'createTime': wq.createTime.strftime('%Y-%m-%d %H:%M:%S') if wq.createTime else ''
        })

    return BaseView.successData({
        'list': data,
        'total': paginator.count
    })


# ============================================================
# 优化补丁4: 消息查询优化
# ============================================================

def getMessages_optimized(request):
    """优化的消息查询"""
    from app.models import Messages
    from app.comm.BaseView import BaseView

    receiver_id = request.GET.get('receiverId')

    # 使用select_related和prefetch_related
    messages = Messages.objects.select_related(
        'sender'  # 预加载发送者信息
    ).prefetch_related(
        'messagereads_set'  # 预加载已读状态
    ).filter(receiver=receiver_id).order_by('-createTime')

    data = []
    for msg in messages:
        # 检查当前用户是否已读
        is_read = False
        if msg.messagereads_set.exists():
            is_read = True

        data.append({
            'id': msg.id,
            'title': msg.title,
            'content': msg.content,
            'senderName': msg.sender.userName,  # 预加载
            'isRead': is_read,
            'createTime': msg.createTime.strftime('%Y-%m-%d %H:%M:%S') if msg.createTime else ''
        })

    return BaseView.successData(data)


# ============================================================
# 优化补丁5: 答案记录查询优化
# ============================================================

def getAnswerLogs_optimized(request):
    """优化的答案记录查询"""
    from app.models import AnswerLogs
    from app.comm.BaseView import BaseView

    exam_log_id = request.GET.get('examLogId')

    # 使用select_related预加载多层关联
    answer_logs = AnswerLogs.objects.select_related(
        'examLog',                # 考试记录
        'examLog__examId',        # 考试信息
        'examLog__studentId',     # 学生信息
        'questionId'              # 题目信息
    ).filter(examLog_id=exam_log_id)

    data = []
    for answer in answer_logs:
        data.append({
            'id': answer.id,
            'questionContent': answer.questionId.name,  # 预加载
            'studentAnswer': answer.studentAnswer,
            'isCorrect': answer.isCorrect,
            'score': answer.score,
            'examTitle': answer.examLog.examId.title  # 预加载
        })

    return BaseView.successData(data)


# ============================================================
# 优化补丁6: 带统计的考试列表
# ============================================================

def getExamsWithStats_optimized(request):
    """优化的考试列表（带统计）"""
    from app.models import Exams
    from django.db.models import Count, Q
    from app.comm.BaseView import BaseView

    teacher_id = request.GET.get('teacherId')

    # 使用注解添加统计信息
    exams = Exams.objects.select_related(
        'projectId'  # 预加载科目信息
    ).annotate(
        participant_count=Count('examlogs', distinct=True),  # 参与人数
        completed_count=Count(
            'examlogs',
            filter=Q(examlogs__status='completed'),
            distinct=True
        )  # 完成人数
    ).filter(creatorId_id=teacher_id)

    data = []
    for exam in exams:
        data.append({
            'id': exam.id,
            'title': exam.title,
            'subjectName': exam.projectId.name,  # 预加载
            'examTime': exam.examTime,
            'participantCount': exam.participant_count,  # 注解字段
            'completedCount': exam.completed_count,  # 注解字段
            'completionRate': round(exam.completed_count / exam.participant_count * 100, 2) if exam.participant_count > 0 else 0
        })

    return BaseView.successData(data)


# ============================================================
# 使用说明
# ============================================================

"""
应用这些优化补丁的步骤：

1. 在views.py文件开头导入QueryOptimizer：
   from app.comm.query_optimizer import QueryOptimizer

2. 替换原有的查询代码：

   # 原代码
   exam_logs = models.ExamLogs.objects.filter(studentId_id=1)

   # 优化后
   exam_logs = QueryOptimizer.get_exam_logs_with_related(student_id=1)

3. 或者直接使用本文件中的优化函数替换原有函数

4. 验证优化效果：
   from django.db import connection
   from django.test.utils import override_settings

   with override_settings(DEBUG=True):
       # 执行查询
       results = some_query_function()
       print(f"查询次数: {len(connection.queries)}")

预期效果：
- 查询次数减少 50-80%
- 响应时间减少 30-50%
- 数据库CPU使用率降低
"""
