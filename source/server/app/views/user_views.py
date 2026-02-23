"""
用户管理视图
处理教师、学生等用户管理
"""
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.hashers import make_password

from app import models
from app.services.crud_service import CRUDService
from app.permissions import get_user_from_request
from comm.BaseView import BaseView
from comm.CommUtils import SysUtil
from utils.OperationLogger import OperationLogger


def _log_user_operation(request, operation_type, module, resource_id, resource_name, status=1):
    """记录用户操作日志"""
    try:
        user = get_user_from_request(request)
        if user:
            OperationLogger.log(
                user_id=user.id,
                user_name=user.name,
                user_type=user.type,
                operation_type=operation_type,
                module_name=module,
                resource_id=str(resource_id),
                resource_name=resource_name,
                status=status,
                request=request
            )
    except Exception:
        pass


class ProjectsView(BaseView):
    """科目/项目管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return self.get_all(request)
        elif module == 'page':
            return self.get_page_infos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'del':
            return self.del_info(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_all(request):
        """获取所有科目信息"""
        projects = models.Projects.objects.all()
        return BaseView.successData(list(projects.values()))

    @staticmethod
    def get_page_infos(request):
        """分页获取科目信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        query = Q()

        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)

        data = models.Projects.objects.filter(query).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    def add_info(request):
        """添加科目信息（使用服务层）"""
        return CRUDService.add_info(
            model_class=models.Projects,
            request=request,
            fields_mapping={'name': 'name'}
        )

    @staticmethod
    def upd_info(request):
        """修改科目信息（使用服务层）"""
        return CRUDService.upd_info(
            model_class=models.Projects,
            request=request,
            fields_mapping={'name': 'name'}
        )

    @staticmethod
    def del_info(request):
        """删除科目信息（使用服务层）"""
        return CRUDService.del_info(
            model_class=models.Projects,
            request=request,
            check_relations=[
                {
                    'model': models.Exams,
                    'field': 'project__id',
                    'message': '存在关联考试无法移除'
                },
                {
                    'model': models.Practises,
                    'field': 'project__id',
                    'message': '存在关联题目无法移除'
                },
                {
                    'model': models.PracticePapers,
                    'field': 'project__id',
                    'message': '存在关联练习试卷无法移除'
                },
                {
                    'model': models.Tasks,
                    'field': 'project__id',
                    'message': '存在关联任务无法移除'
                }
            ]
        )


class TeachersView(BaseView):
    """教师管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return self.get_page_infos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'del':
            return self.del_info(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_page_infos(request):
        """分页查询教师信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        record = request.GET.get('record')
        job = request.GET.get('job')

        query = Q()
        if SysUtil.isExit(name):
            query = query & Q(user__name__contains=name)
        if SysUtil.isExit(record):
            query = query & Q(record=record)
        if SysUtil.isExit(job):
            query = query & Q(job=job)

        data = models.Teachers.objects.filter(query)

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.user.id,
                'userName': item.user.userName,
                'name': item.user.name,
                'gender': item.user.gender,
                'age': item.user.age,
                'type': item.user.type,
                'phone': item.phone,
                'record': item.record,
                'job': item.job
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    @transaction.atomic
    def add_info(request):
        """添加教师信息"""
        # 参数校验
        required_fields = ['id', 'userName', 'name', 'gender', 'age', 'phone', 'record', 'job']
        for field in required_fields:
            if not SysUtil.isExit(request.POST.get(field)):
                return BaseView.warn(f'{field} 不能为空')

        # 年龄格式校验
        try:
            age_val = int(request.POST.get('age'))
        except Exception:
            return BaseView.warn('年龄必须为数字')

        if models.Users.objects.filter(userName=request.POST.get('userName')).exists():
            return BaseView.warn('账号已存在，请重新输入')
        elif models.Users.objects.filter(id=request.POST.get('id')).exists():
            return BaseView.warn('工号已存在，请重新输入')
        else:
            # 允许未显式提供密码时使用默认密码（默认与账号相同）
            default_password = request.POST.get('passWord') or request.POST.get('userName') or '123456'
            # 使用加密密码存储
            user = models.Users.objects.create(
                id=request.POST.get('id'),
                userName=request.POST.get('userName'),
                passWord=make_password(default_password),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                age=age_val,
                type=1,
            )
            models.Teachers.objects.create(
                user=user,
                phone=request.POST.get('phone'),
                record=request.POST.get('record'),
                job=request.POST.get('job')
            )
            _log_user_operation(request, 'create', 'teacher', user.id, user.name)
            return BaseView.success()

    @staticmethod
    def upd_info(request):
        """修改教师信息"""
        teacher_id = request.POST.get('id')
        teacher = models.Teachers.objects.filter(user__id=teacher_id).first()
        teacher_name = teacher.user.name if teacher else teacher_id
        
        models.Teachers.objects.filter(user__id=teacher_id).update(
            phone=request.POST.get('phone'),
            record=request.POST.get('record'),
            job=request.POST.get('job')
        )
        _log_user_operation(request, 'update', 'teacher', teacher_id, teacher_name)
        return BaseView.success()

    @staticmethod
    @transaction.atomic
    def del_info(request):
        """删除教师信息"""
        id = request.POST.get('id')
        teacher = models.Teachers.objects.filter(user__id=id).first()
        teacher_name = teacher.user.name if teacher else id
        
        # 检查所有关联表，防止孤立数据
        if models.Exams.objects.filter(teacher__id=id).exists():
            return BaseView.warn('存在关联考试无法移除')
        
        if models.PracticePapers.objects.filter(teacher__id=id).exists():
            return BaseView.warn('存在关联练习试卷无法移除')
        
        if models.Tasks.objects.filter(teacher__id=id).exists():
            return BaseView.warn('存在关联任务无法移除')
        
        models.Users.objects.filter(id=id).delete()
        _log_user_operation(request, 'delete', 'teacher', id, teacher_name)
        return BaseView.success()


class StudentsView(BaseView):
    """学生管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module in ['page', 'getPageInfos']:
            return self.get_page_infos(request)
        elif module == 'info':
            return self.get_info(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.add_info(request)
        elif module == 'upd':
            return self.upd_info(request)
        elif module == 'del':
            return self.del_info(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def get_info(request):
        """获取指定学生信息"""
        student = models.Students.objects.filter(user__id=request.GET.get('id')).first()

        if not student:
            return BaseView.warn('学生不存在')

        return BaseView.successData({
            'id': student.user.id,
            'userName': student.user.userName,
            'name': student.user.name,
            'gender': student.user.gender,
            'gradeId': student.grade.id,
            'gradeName': student.grade.name,
            'collegeId': student.college.id,
            'collegeName': student.college.name,
        })

    @staticmethod
    def get_page_infos(request):
        """分页查询学生信息"""
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        collegeId = request.GET.get('collegeId')
        gradeId = request.GET.get('gradeId')

        query = Q()
        if SysUtil.isExit(name):
            query = query & Q(user__name__contains=name)
        if SysUtil.isExit(collegeId):
            query = query & Q(college__id=int(collegeId))
        if SysUtil.isExit(gradeId):
            query = query & Q(grade__id=int(gradeId))

        data = models.Students.objects.filter(query)

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.user.id,
                'userName': item.user.userName,
                'name': item.user.name,
                'gender': item.user.gender,
                'age': item.user.age,
                'type': item.user.type,
                'gradeId': item.grade.id,
                'gradeName': item.grade.name,
                'collegeId': item.college.id,
                'collegeName': item.college.name
            })

        pageData = BaseView.parasePage(
            int(pageIndex), int(pageSize),
            paginator.page(pageIndex).paginator.num_pages,
            paginator.count, resl
        )

        return BaseView.successData(pageData)

    @staticmethod
    @transaction.atomic
    def add_info(request):
        """添加学生信息"""
        # 参数校验
        required_fields = ['id', 'userName', 'name', 'gender', 'age', 'gradeId', 'collegeId']
        for field in required_fields:
            if not SysUtil.isExit(request.POST.get(field)):
                return BaseView.warn(f'{field} 不能为空')

        # 年龄格式校验
        try:
            age_val = int(request.POST.get('age'))
        except Exception:
            return BaseView.warn('年龄必须为数字')

        # 关联对象检查
        if not models.Grades.objects.filter(id=request.POST.get('gradeId')).exists():
            return BaseView.warn('指定的班级不存在')
        if not models.Colleges.objects.filter(id=request.POST.get('collegeId')).exists():
            return BaseView.warn('指定的学院不存在')

        if models.Users.objects.filter(userName=request.POST.get('userName')).exists():
            return BaseView.warn('账号已存在，请重新输入')
        elif models.Users.objects.filter(id=request.POST.get('id')).exists():
            return BaseView.warn('学号已存在，请重新输入')
        else:
            # 允许未显式提供密码时使用默认密码（与教师保持一致：默认使用账号作为初始密码）
            default_password = request.POST.get('passWord') or request.POST.get('userName') or '123456'
            # 使用加密密码存储
            user = models.Users.objects.create(
                id=request.POST.get('id'),
                userName=request.POST.get('userName'),
                passWord=make_password(default_password),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                age=age_val,
                type=2,
            )
            models.Students.objects.create(
                user=user,
                grade=models.Grades.objects.get(id=request.POST.get('gradeId')),
                college=models.Colleges.objects.get(id=request.POST.get('collegeId'))
            )
            _log_user_operation(request, 'create', 'student', user.id, user.name)
            return BaseView.success()

    @staticmethod
    def upd_info(request):
        """修改学生信息"""
        id = request.POST.get('id')
        grade_id = request.POST.get('gradeId')
        college_id = request.POST.get('collegeId')

        # 验证必填参数
        if not all([id, grade_id, college_id]):
            return BaseView.error('缺少必填参数')

        # 安全地获取关联对象，避免DoesNotExist异常
        try:
            grade = models.Grades.objects.get(id=grade_id)
        except models.Grades.DoesNotExist:
            return BaseView.warn('指定的班级不存在')

        try:
            college = models.Colleges.objects.get(id=college_id)
        except models.Colleges.DoesNotExist:
            return BaseView.warn('指定的学院不存在')

        student = models.Students.objects.filter(user__id=id).first()
        student_name = student.user.name if student else id
        
        # 执行更新
        models.Students.objects.filter(user__id=id).update(
            grade=grade,
            college=college
        )
        _log_user_operation(request, 'update', 'student', id, student_name)
        return BaseView.success()

    @staticmethod
    @transaction.atomic
    def del_info(request):
        """删除学生信息"""
        id = request.POST.get('id')
        student = models.Students.objects.filter(user__id=id).first()
        student_name = student.user.name if student else id

        # 检查所有关联表，防止孤立数据
        if models.ExamLogs.objects.filter(student__user__id=id).exists():
            return BaseView.warn('该学生有考试记录，无法删除')

        if models.AnswerLogs.objects.filter(student__user__id=id).exists():
            return BaseView.warn('该学生有答题记录，无法删除')

        if models.StudentPracticeLogs.objects.filter(student__user__id=id).exists():
            return BaseView.warn('该学生有练习记录，无法删除')

        if models.StudentTaskLogs.objects.filter(student__user__id=id).exists():
            return BaseView.warn('该学生有任务记录，无法删除')

        if models.WrongQuestions.objects.filter(student__user__id=id).exists():
            return BaseView.warn('该学生有错题记录，无法删除')

        # 所有检查通过，执行删除
        models.Users.objects.filter(id=id).delete()
        _log_user_operation(request, 'delete', 'student', id, student_name)
        return BaseView.success()
