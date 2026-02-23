from django.db import models

# 用户类型枚举
class UserType(models.IntegerChoices):
    """用户类型：0-管理员 1-教师 2-学生"""
    ADMIN = 0, '管理员'
    TEACHER = 1, '教师'
    STUDENT = 2, '学生'

# 题目类型枚举
class QuestionType(models.IntegerChoices):
    """题目类型：0-选择题 1-填空题 2-判断题 3-简答题 4-编程题 5-综合题"""
    CHOICE = 0, '选择题'
    FILL_BLANK = 1, '填空题'
    TRUE_FALSE = 2, '判断题'
    SHORT_ANSWER = 3, '简答题'
    PROGRAMMING = 4, '编程题'
    COMPREHENSIVE = 5, '综合题'

# 消息类型枚举
class MessageType(models.IntegerChoices):
    """消息类型：0-系统通知 1-个人消息 2-考试通知 3-任务通知"""
    SYSTEM = 0, '系统通知'
    PERSONAL = 1, '个人消息'
    EXAM = 2, '考试通知'
    TASK = 3, '任务通知'

# 学院信息
class Colleges(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('学院名称',  max_length=32, null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_colleges'

# 班级信息
class Grades(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('班级名称',  max_length=32, null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_grades'

# 科目信息
class Projects(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('科目名称',  max_length=32, null=False)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_projects'

# 用户信息
class Users(models.Model):
    id = models.CharField('用户编号', max_length=20, null=False, primary_key=True)
    userName = models.CharField('用户账号', db_column='user_name', max_length=32, null=False)
    passWord = models.CharField('用户密码', db_column='pass_word', max_length=128, null=False)  # 修复：增加字段长度以支持Django加密密码
    name = models.CharField('用户姓名', max_length=20, null=False)
    gender = models.CharField('用户性别', max_length=4, null=False)
    age = models.IntegerField('用户年龄', null=False)
    type = models.IntegerField(
        '用户身份 0-管理员 1-教师 2-学生',
        null=False,
        choices=UserType.choices
    )
    # P2优化：添加邮箱字段
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name='邮箱')
    # P2优化：添加账户状态字段
    status = models.SmallIntegerField(
        default=0,
        choices=[(0,'正常'),(1,'禁用'),(2,'锁定')],
        verbose_name='账户状态'
    )
    createTime = models.DateTimeField('创建时间', db_column='create_time', auto_now_add=True, null=True)
    lastLoginTime = models.DateTimeField('最后登录时间', db_column='last_login_time', null=True)
    class Meta:
        db_table = 'fater_users'
        indexes = [
            models.Index(fields=['userName'], name='idx_users_username'),
        ]

# 学生信息
class Students(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column="user_id")
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE, db_column="grade_id")
    college = models.ForeignKey(Colleges, on_delete=models.CASCADE, db_column="college_id")
    class Meta:
        db_table = 'fater_students'
        indexes = [
            models.Index(fields=['user', 'grade']),
            models.Index(fields=['grade'], name='idx_students_grade'),
            models.Index(fields=['college'], name='idx_students_college'),
        ]

# 教师信息
class Teachers(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column="user_id")
    phone = models.CharField('联系电话', max_length=11, null=False)
    record = models.CharField('教师学历 ', max_length=10, null=False)
    job = models.CharField('教师职称', max_length=20, null=False)
    class Meta:
        db_table = 'fater_teachers'

# 习题信息
class Practises(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('题目名称',  max_length=64, null=False)
    answer = models.TextField('参考答案')
    analyse = models.TextField('题目分析')
    type = models.IntegerField(
        '题目类型 0-选择 1-填空 2-判断 3-编程',
        null=False,
        choices=QuestionType.choices
    )
    # P2优化：添加难度等级字段
    difficulty = models.SmallIntegerField(
        choices=[(1,'简单'),(2,'中等'),(3,'困难')],
        default=2,
        verbose_name='难度等级'
    )
    # P2优化：添加知识点标签字段
    tags = models.JSONField(default=list, verbose_name='知识点标签')
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column="project_id")
    class Meta:
        db_table = 'fater_practises'
        indexes = [
            models.Index(fields=['project'], name='idx_practises_project'),
            models.Index(fields=['type'], name='idx_practises_type'),
            models.Index(fields=['createTime'], name='idx_practises_createtime'),
        ]

# 选项记录
class Options(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('题目名称',  max_length=64, null=False)
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    class Meta:
        db_table = 'fater_options'
        indexes = [
            models.Index(fields=['practise'], name='idx_options_practise'),
        ]

# 考试信息
class Exams(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('考试名称',  max_length=64, null=False)
    teacher = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="teacher_id")
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column="project_id")
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE, db_column="grade_id")
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19)
    examTime = models.CharField('考试时间', db_column='exam_time', max_length=19)
    # 新增：考试开始/结束时间（为兼容旧数据，允许为空；若存在则以区间为准）
    startTime = models.CharField('开始时间', db_column='start_time', max_length=19, null=True)
    endTime = models.CharField('结束时间', db_column='end_time', max_length=19, null=True)
    class Meta:
        db_table = 'fater_exams'
        indexes = [
            models.Index(fields=['teacher'], name='idx_exams_teacher'),
            models.Index(fields=['project'], name='idx_exams_project'),
            models.Index(fields=['grade'], name='idx_exams_grade'),
            models.Index(fields=['createTime'], name='idx_exams_createtime'),
        ]

# 参考记录
class ExamLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id")
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, db_column="exam_id")
    status = models.IntegerField('考试状态 0-参考 1-待审 2-结束', null=False)
    score = models.FloatField('考试得分', default=0.0)
    createTime = models.CharField('参考时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'fater_exam_logs'
        indexes = [
            models.Index(fields=['exam', 'status']),
            models.Index(fields=['student'], name='idx_examlogs_student'),
            models.Index(fields=['exam'], name='idx_examlogs_exam'),
            models.Index(fields=['status'], name='idx_examlogs_status'),
            models.Index(fields=['createTime'], name='idx_examlogs_createtime'),
        ]

# 答题记录
class AnswerLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id")
    exam = models.ForeignKey(Exams, on_delete=models.CASCADE, db_column="exam_id")
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practises_id")
    score = models.FloatField('审核分数', default=0.0)
    status = models.IntegerField('审核结果 0-待审 1-结束', null=False)
    answer = models.TextField('答案内容')
    no = models.IntegerField('题号索引', null=False)
    class Meta:
        db_table = 'fater_answer_logs'
        indexes = [
            models.Index(fields=['exam', 'student', 'practise']),
            models.Index(fields=['student'], name='idx_answerlogs_student'),
            models.Index(fields=['exam'], name='idx_answerlogs_exam'),
            models.Index(fields=['practise'], name='idx_answerlogs_practise'),
            models.Index(fields=['status'], name='idx_answerlogs_status'),
        ]

# 练习试卷信息
class PracticePapers(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    title = models.CharField('试卷标题', max_length=128, null=False)
    description = models.TextField('试卷描述', null=True)
    type = models.CharField('试卷类型', max_length=20, null=False)  # fixed-固定试卷, timed-时段试卷
    difficulty = models.CharField('难度等级', max_length=20, null=False)  # easy-简单, medium-中等, hard-困难
    duration = models.IntegerField('练习时长(分钟)', null=False)
    totalScore = models.IntegerField('总分', null=False)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column="project_id")
    teacher = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="teacher_id", to_field='id')
    createTime = models.CharField('创建时间', db_column='create_time', max_length=19)
    isActive = models.BooleanField('是否启用', default=True)
    
    class Meta:
        db_table = 'fater_practice_papers'

# 练习试卷题目关联
class PracticePaperQuestions(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    paper = models.ForeignKey(PracticePapers, on_delete=models.CASCADE, db_column="paper_id")
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    questionOrder = models.IntegerField('题目顺序', null=False)
    score = models.FloatField('题目分值', null=False)
    
    class Meta:
        db_table = 'fater_practice_paper_questions'

# 学生练习记录
class StudentPracticeLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id", to_field='id')
    paper = models.ForeignKey(PracticePapers, on_delete=models.CASCADE, db_column="paper_id")
    startTime = models.CharField('开始时间', db_column='start_time', max_length=19)
    endTime = models.CharField('结束时间', db_column='end_time', max_length=19, null=True)
    score = models.FloatField('得分', default=0.0)
    accuracy = models.FloatField('正确率', default=0.0)
    status = models.CharField('状态', max_length=20, default='in_progress')  # in_progress-进行中, completed-已完成
    usedTime = models.IntegerField('用时(分钟)', default=0)
    createTime = models.DateTimeField('创建时间', db_column='create_time', auto_now_add=True, null=True)

    class Meta:
        db_table = 'fater_student_practice_logs'
        indexes = [
            models.Index(fields=['student'], name='idx_practicelogs_student'),
            models.Index(fields=['paper'], name='idx_practicelogs_paper'),
            models.Index(fields=['status'], name='idx_practicelogs_status'),
            models.Index(fields=['startTime'], name='idx_practicelogs_starttime'),
        ]

# 学生练习答题记录
class StudentPracticeAnswers(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    practiceLog = models.ForeignKey(StudentPracticeLogs, on_delete=models.CASCADE, db_column="practice_log_id")
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    studentAnswer = models.TextField('学生答案', null=True)
    isCorrect = models.BooleanField('是否正确', null=True)
    score = models.FloatField('得分', default=0.0)
    answerTime = models.CharField('答题时间', db_column='answer_time', max_length=19)
    # AI 评分扩展
    aiConfidence = models.FloatField('AI置信度', null=True)
    aiFeedback = models.TextField('AI反馈', null=True)
    aiAnalysis = models.TextField('AI分析', null=True)
    aiModel = models.CharField('AI模型', max_length=128, null=True)
    
    class Meta:
        db_table = 'fater_student_practice_answers'
        indexes = [
            models.Index(fields=['practiceLog'], name='idx_practiceanswers_log'),
            models.Index(fields=['practise'], name='idx_practiceanswers_practise'),
        ]

# 任务信息
class Tasks(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    title = models.CharField('任务标题', max_length=128, null=False)
    description = models.TextField('任务描述', null=True)
    type = models.CharField('任务类型', max_length=20, null=False)  # practice-练习任务, exam-考试任务, project-项目任务
    deadline = models.CharField('截止时间', max_length=19, null=False)
    score = models.IntegerField('任务分值', null=False)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, db_column="project_id")
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE, db_column="grade_id")
    teacher = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="teacher_id", to_field='id')
    createTime = models.CharField('创建时间', db_column='create_time', max_length=19)
    isActive = models.BooleanField('是否启用', default=True)
    
    class Meta:
        db_table = 'fater_tasks'
        indexes = [
            models.Index(fields=['project'], name='idx_tasks_project'),
            models.Index(fields=['grade'], name='idx_tasks_grade'),
            models.Index(fields=['teacher'], name='idx_tasks_teacher'),
            models.Index(fields=['isActive'], name='idx_tasks_isactive'),
            models.Index(fields=['createTime'], name='idx_tasks_createtime'),
        ]

# 任务题目关联
class TaskQuestions(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, db_column="task_id")
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    questionOrder = models.IntegerField('题目顺序', null=False)
    score = models.FloatField('题目分值', null=False)

    class Meta:
        db_table = 'fater_task_questions'
        indexes = [
            models.Index(fields=['task'], name='idx_taskquestions_task'),
            models.Index(fields=['practise'], name='idx_taskquestions_practise'),
        ]

# 学生任务记录
class StudentTaskLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id", to_field='id')
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, db_column="task_id")
    startTime = models.CharField('开始时间', db_column='start_time', max_length=19)
    endTime = models.CharField('结束时间', db_column='end_time', max_length=19, null=True)
    score = models.FloatField('得分', default=0.0)
    accuracy = models.FloatField('正确率', default=0.0)
    status = models.CharField('状态', max_length=20, default='in_progress')  # in_progress-进行中, completed-已完成
    usedTime = models.IntegerField('用时(分钟)', default=0)
    
    class Meta:
        db_table = 'fater_student_task_logs'
        indexes = [
            models.Index(fields=['student'], name='idx_tasklogs_student'),
            models.Index(fields=['task'], name='idx_tasklogs_task'),
            models.Index(fields=['status'], name='idx_tasklogs_status'),
            models.Index(fields=['startTime'], name='idx_tasklogs_starttime'),
        ]

# 学生任务答题记录
class StudentTaskAnswers(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    taskLog = models.ForeignKey(StudentTaskLogs, on_delete=models.CASCADE, db_column="task_log_id")
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    studentAnswer = models.TextField('学生答案', null=True)
    isCorrect = models.BooleanField('是否正确', null=True)
    score = models.FloatField('得分', default=0.0)
    answerTime = models.CharField('答题时间', db_column='answer_time', max_length=19)
    # AI 评分扩展
    aiConfidence = models.FloatField('AI置信度', null=True)
    aiFeedback = models.TextField('AI反馈', null=True)
    aiAnalysis = models.TextField('AI分析', null=True)
    aiModel = models.CharField('AI模型', max_length=128, null=True)

    class Meta:
        db_table = 'fater_student_task_answers'
        indexes = [
            models.Index(fields=['taskLog'], name='idx_taskanswers_tasklog'),
            models.Index(fields=['practise'], name='idx_taskanswers_practise'),
            models.Index(fields=['answerTime'], name='idx_taskanswers_answertime'),
        ]

# 错题本记录
class WrongQuestions(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    student = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="student_id", to_field='id')
    practise = models.ForeignKey(Practises, on_delete=models.CASCADE, db_column="practise_id")
    source = models.CharField('错题来源', max_length=20, null=False)  # task-任务, exam-考试, practice-练习
    sourceId = models.IntegerField('来源ID', null=False)  # 对应的任务/考试/练习ID
    wrongAnswer = models.TextField('错误答案', null=True)
    correctAnswer = models.TextField('正确答案', null=True)
    analysis = models.TextField('错题分析', null=True)
    isReviewed = models.BooleanField('是否已复习', default=False)
    reviewCount = models.IntegerField('复习次数', default=0)
    # P2优化：添加掌握程度字段
    masteryLevel = models.SmallIntegerField(
        default=0,
        choices=[(0,'未复习'),(1,'复习中'),(2,'已掌握')],
        verbose_name='掌握程度'
    )
    lastReviewTime = models.CharField('最后复习时间', db_column='last_review_time', max_length=19, null=True)
    createTime = models.CharField('添加时间', db_column='create_time', max_length=19, null=True)

    class Meta:
        db_table = 'fater_wrong_questions'
        indexes = [
            models.Index(fields=['student', 'isReviewed']),
            models.Index(fields=['student'], name='idx_wrongquestions_student'),
            models.Index(fields=['practise'], name='idx_wrongquestions_practise'),
            models.Index(fields=['isReviewed'], name='idx_wrongquestions_isreviewed'),
            models.Index(fields=['createTime'], name='idx_wrongquestions_createtime'),
        ]

# 错题复习记录
class WrongQuestionReviews(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    wrongQuestion = models.ForeignKey(WrongQuestions, on_delete=models.CASCADE, db_column="wrong_question_id")
    reviewAnswer = models.TextField('复习答案', null=True)
    isCorrect = models.BooleanField('是否正确', null=True)
    reviewTime = models.CharField('复习时间', db_column='review_time', max_length=19, null=True)
    notes = models.TextField('复习笔记', null=True)

    class Meta:
        db_table = 'fater_wrong_question_reviews'
        indexes = [
            models.Index(fields=['wrongQuestion'], name='idx_wrongreviews_wrongquestion'),
        ]



# 消息读取记录
class MessageReads(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    message = models.ForeignKey('Messages', on_delete=models.CASCADE, db_column="message_id")
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="user_id", to_field='id')
    isRead = models.BooleanField('是否已读', default=False)
    readTime = models.DateTimeField('阅读时间', auto_now_add=True)

    class Meta:
        db_table = 'fater_message_reads'
        indexes = [
            models.Index(fields=['message'], name='idx_messagereads_message'),
            models.Index(fields=['user'], name='idx_messagereads_user'),
            models.Index(fields=['isRead'], name='idx_messagereads_isread'),
        ]

# 消息信息
class Messages(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    title = models.CharField('消息标题', max_length=128, null=False)
    content = models.TextField('消息内容', null=False)
    type = models.CharField('消息类型', max_length=20, default='notice')  # notice-通知, announcement-公告, reminder-提醒
    priority = models.CharField('优先级', max_length=20, default='medium')  # low-低, medium-中, high-高
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, db_column="sender_id", to_field='id')
    createTime = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'fater_messages'
        indexes = [
            models.Index(fields=['sender'], name='idx_messages_sender'),
            models.Index(fields=['type'], name='idx_messages_type'),
            models.Index(fields=['priority'], name='idx_messages_priority'),
            models.Index(fields=['createTime'], name='idx_messages_createtime'),
        ]

# 操作日志
class OperationLog(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='日志ID')
    user_id = models.CharField(max_length=50, verbose_name='用户ID', db_index=True)
    user_name = models.CharField(max_length=100, verbose_name='用户姓名')
    user_type = models.IntegerField(verbose_name='用户类型')
    operation_type = models.CharField(max_length=50, verbose_name='操作类型', db_index=True)
    module_name = models.CharField(max_length=50, verbose_name='模块名称', db_index=True)
    resource_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='资源ID')
    resource_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='资源名称')
    operation_detail = models.TextField(null=True, blank=True, verbose_name='操作详情')
    status = models.IntegerField(verbose_name='状态：1成功0失败')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    ip_address = models.CharField(max_length=50, null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(null=True, blank=True, verbose_name='用户代理')
    device_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='设备类型')
    browser_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='浏览器类型')
    os_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='操作系统')
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='地理位置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', db_index=True)

    class Meta:
        db_table = 'fater_operation_logs'
        verbose_name = '用户操作日志'
        verbose_name_plural = '用户操作日志'
        ordering = ['-created_at']


# 任务附件模型
class TaskAttachments(models.Model):
    """任务附件"""
    id = models.AutoField('记录编号', primary_key=True)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, db_column="task_id", verbose_name='关联任务')
    fileName = models.CharField('文件名称', max_length=255, null=False)
    filePath = models.CharField('文件路径', max_length=500, null=False)
    fileSize = models.IntegerField('文件大小(字节)', null=False)
    fileType = models.CharField('文件类型', max_length=20, null=False)
    uploadedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, db_column="uploaded_by", null=True, blank=True, verbose_name='上传者')
    uploadTime = models.DateTimeField('上传时间', auto_now_add=True)
    downloadCount = models.IntegerField('下载次数', default=0)
    
    class Meta:
        db_table = 'fater_task_attachments'
        verbose_name = '任务附件'
        verbose_name_plural = '任务附件'
        ordering = ['-uploadTime']
        indexes = [
            models.Index(fields=['task'], name='idx_taskattachments_task'),
            models.Index(fields=['uploadTime'], name='idx_taskattachments_uploadtime'),
        ]
    
    def __str__(self):
        return self.fileName


# 用户主题设置模型
class UserThemeSettings(models.Model):
    """用户主题设置"""
    id = models.AutoField('记录编号', primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE, db_column="user_id", verbose_name='用户')
    theme = models.CharField('主题名称', max_length=50, default='light', help_text='light/dark')
    primaryColor = models.CharField('主题色', max_length=20, default='#2d8cf0')
    fontSize = models.CharField('字体大小', max_length=10, default='medium', help_text='small/medium/large')
    sidebarCollapsed = models.BooleanField('侧边栏折叠', default=False)
    showAnimations = models.BooleanField('显示动画', default=True)
    compactMode = models.BooleanField('紧凑模式', default=False)
    updateTime = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'fater_user_theme_settings'
        verbose_name = '用户主题设置'
        verbose_name_plural = '用户主题设置'
    
    def __str__(self):
        return f'{self.user.name} - {self.theme}'

# Audit Log Model - Added 2026-02-21
from django.db import models


class AuditLog(models.Model):
    """审计日志模型 - 记录用户操作"""
    
    # 操作类型选择
    OPERATION_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('export', '导出'),
        ('import', '导入'),
        ('submit', '提交'),
        ('review', '审核'),
        ('other', '其他'),
    ]
    
    # 基础信息
    user_id = models.IntegerField(null=True, blank=True, verbose_name="用户ID")
    username = models.CharField(max_length=100, null=True, blank=True, verbose_name="用户名")
    user_type = models.IntegerField(null=True, blank=True, verbose_name="用户类型")
    
    # 操作信息
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES, verbose_name="操作类型")
    operation_desc = models.CharField(max_length=255, verbose_name="操作描述")
    module = models.CharField(max_length=50, verbose_name="模块名称")
    
    # 操作对象
    target_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="对象类型")
    target_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="对象ID")
    target_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="对象名称")
    
    # 请求信息
    ip_address = models.CharField(max_length=50, null=True, blank=True, verbose_name="IP地址")
    user_agent = models.CharField(max_length=255, null=True, blank=True, verbose_name="用户代理")
    request_method = models.CharField(max_length=10, null=True, blank=True, verbose_name="请求方法")
    request_path = models.CharField(max_length=255, null=True, blank=True, verbose_name="请求路径")
    
    # 结果信息
    status = models.CharField(max_length=20, default="success", verbose_name="操作状态")
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")
    
    # 变更详情 (JSON格式)
    old_value = models.TextField(null=True, blank=True, verbose_name="变更前值")
    new_value = models.TextField(null=True, blank=True, verbose_name="变更后值")
    
    # 时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        db_table = "fater_audit_logs"
        verbose_name = "审计日志"
        verbose_name_plural = "审计日志"
        ordering = ["-create_time"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["operation_type"]),
            models.Index(fields=["module"]),
            models.Index(fields=["create_time"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.operation_desc}"
