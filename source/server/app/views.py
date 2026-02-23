"""
⚠️  DEPRECATED WARNING ⚠️
此文件已被模块化拆分，但保留用于向后兼容。
请优先使用 app.views/ 目录下的独立模块：

- sys_view.py -> SysView
- organization_views.py -> CollegesView, GradesView
- user_views.py -> ProjectsView, TeachersView, StudentsView
- question_views.py -> PractisesView, OptionsView
- exam_views.py -> ExamsView, ExamLogsView, AnswerLogsView
- practice_views.py -> PracticePapersView, StudentPracticeView
- task_views.py -> TasksView
- wrong_question_views.py -> WrongQuestionsView
- admin_views.py -> AdminView
- ai_views.py -> AIView
- log_views.py -> LogViews

此文件将在未来版本中移除。
"""

from utils.OperationLogger import OperationLogger
from comm.CommUtils import DateUtil
from comm.CommUtils import SysUtil
from comm.BaseView import BaseView
from comm import ExamUtils
from comm.auth_utils import generate_token, revoke_token  # JWT认证
from app.services.crud_service import CRUDService
from app.services.pagination_service import PaginationService
from app.services.user_service import UserService
import uuid
import os
from datetime import time
import csv
import io
import logging

from django.core.cache import cache
from django.db import DatabaseError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password

from app import models
from app.validators import InputValidator

# 配置日志记录器
logger = logging.getLogger(__name__)

# 导入错误处理（如果可用）
try:
    from comm.error_handler import handle_exceptions, validate_required_fields, validate_user_token
except ImportError:
    # 如果导入失败，定义空装饰器
    def handle_exceptions(func):
        return func

    def validate_required_fields(request, fields, method='POST'):
        return True, None

    def validate_user_token(request):
        return False, None

'''
系统处理
'''


class SysView(BaseView):

    def get(self, request, module, action=None, *args, **kwargs):
        # Handle both patterns: /api/info/ and /api/sys/info/
        actual_action = action if action else module
        if actual_action == 'info':
            return SysView.getUserInfo(request)
        elif actual_action == 'messages':
            return SysView.getUserMessages(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, *args, **kwargs):
        # Handle both patterns: /api/login/ and /api/sys/login/
        module = kwargs.get('module')
        action = kwargs.get('action')
        actual_action = action if action else module
        if actual_action == 'login':
            return SysView.login(request)
        elif actual_action == 'exit':
            return SysView.exit(request)
        elif actual_action == 'info':
            return SysView.updUserInfo(request)
        elif actual_action == 'pwd':
            return SysView.updUserPwd(request)
        elif actual_action == 'messages':
            return SysView.manageUserMessages(request)
        else:
            return BaseView.error(f'请求地址不存在: module={module}, action={action}')




    # 获取指定用户信息
    def getUserInfo(request):
        """获取当前登录用户信息（使用服务层）"""
        token = request.GET.get('token')
        user = UserService.get_user_by_token(token)

        if not user:
            return BaseView.error('用户未登录')

        user_info = UserService.build_user_info(user)
        return BaseView.successData(user_info)

    @staticmethod
    def getUserMessages(request):
        """获取当前登录用户的消息列表"""
        try:
            token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            user_id = cache.get(token)
            if not user_id:
                return BaseView.error('用户未登录')

            # 关联读取记录与消息本体，并预加载附件以避免N+1查询
            reads_qs = models.MessageReads.objects.filter(user_id=user_id).select_related(
                'message', 'message__sender'
            ).prefetch_related('message__attachments')
            # 支持按类型过滤
            msg_type = request.GET.get('type') or ''
            if msg_type:
                reads_qs = reads_qs.filter(message__type=msg_type)

            reads_qs = reads_qs.order_by('-message__createTime')

            data = []
            for mr in reads_qs:
                msg = mr.message
                # 附件列表（使用预加载的数据，避免N+1查询）
                attachments_data = []
                if hasattr(msg, 'attachments'):
                    for att in msg.attachments.all():
                        attachments_data.append({
                            'id': att.id,
                            'name': att.name,
                            'size': att.size or 0,
                            'url': att.file.url if att.file else ''
                        })

                data.append({
                    'id': msg.id,
                    'title': msg.title,
                    'content': msg.content,
                    'type': msg.type,
                    'priority': msg.priority,
                    'senderId': msg.sender.id if msg.sender else None,
                    'senderName': msg.sender.name if msg.sender else '',
                    'createTime': msg.createTime.strftime('%Y-%m-%d %H:%M:%S') if msg.createTime else '',
                    'isRead': mr.isRead,
                    'readTime': mr.readTime.strftime('%Y-%m-%d %H:%M:%S') if mr.readTime else '',
                    'attachments': attachments_data
                })

            return BaseView.successData(data)
        except Exception as e:
            return BaseView.error(f'获取用户消息失败: {str(e)}')

    @staticmethod
    def manageUserMessages(request):
        """当前登录用户对自己消息的操作：标记已读 / 全部已读 / 删除"""
        try:
            token = request.POST.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            user_id = cache.get(token)
            if not user_id:
                return BaseView.error('用户未登录')

            action = request.POST.get('action')
            if action == 'mark_read':
                msg_id = request.POST.get('id')
                if not msg_id:
                    return BaseView.error('消息ID不能为空')
                mr = models.MessageReads.objects.filter(user_id=user_id, message_id=msg_id).first()
                if not mr:
                    return BaseView.error('消息记录不存在')
                mr.isRead = True
                from django.utils import timezone
                mr.readTime = timezone.now()
                mr.save(update_fields=['isRead', 'readTime'])
                return BaseView.success('标记已读成功')
            elif action == 'mark_all_read':
                from django.utils import timezone
                now = timezone.now()
                models.MessageReads.objects.filter(user_id=user_id, isRead=False).update(isRead=True, readTime=now)
                return BaseView.success('全部标记为已读成功')
            elif action == 'delete':
                msg_id = request.POST.get('id')
                if not msg_id:
                    return BaseView.error('消息ID不能为空')
                # 学生删除仅删除自己的读取记录，不删除消息本身
                models.MessageReads.objects.filter(user_id=user_id, message_id=msg_id).delete()
                return BaseView.success('删除成功')
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'消息操作失败: {str(e)}')

    # 登陆处理

    @handle_exceptions
    def login(request):
        """登录方法（使用JWT，保持向后兼容）"""
        userName = request.POST.get('userName')
        passWord = request.POST.get('passWord')

        # 参数验证
        if not userName:
            return BaseView.warn('用户名不能为空')
        if not passWord:
            return BaseView.warn('密码不能为空')

        # 查询用户
        user = models.Users.objects.filter(userName=userName).first()
        if not user:
            OperationLogger.log_login(userName, userName, 0, 0, request, '用户名不存在')
            return BaseView.warn('用户名输入错误')

        # 验证密码
        password_valid = False
        if len(user.passWord) < 50:
            # 旧明文密码格式，直接比较（向后兼容）
            if user.passWord == passWord:
                password_valid = True
                # 登录成功后自动迁移为加密密码
                try:
                    user.passWord = make_password(passWord)
                    user.save()
                    logger.info(f"用户 {userName} 密码已自动迁移到加密格式")
                except Exception as e:
                    logger.error(f"密码迁移失败: {str(e)}")
            else:
                OperationLogger.log_login(userName, userName, 0, 0, request, '密码错误')
                return BaseView.warn('用户密码输入错误')
        else:
            # 新加密密码格式，使用check_password验证
            if check_password(passWord, user.passWord):
                password_valid = True
            else:
                OperationLogger.log_login(userName, userName, 0, 0, request, '密码错误')
                return BaseView.warn('用户密码输入错误')

        if password_valid:
            try:
                # 生成JWT token
                token = generate_token(user_id=user.id, user_type=user.type)

                # 为了向后兼容，同时将token存入缓存
                cache.set(token, user.id, 60 * 60 * 24)

                # 更新最后登录时间
                try:
                    user.lastLoginTime = user.lastLoginTime or None
                    user.save(update_fields=['lastLoginTime'])
                except Exception as e:
                    logger.warning(f"更新最后登录时间失败: {str(e)}")

                logger.info(f"用户 {userName} (ID: {user.id}, Type: {user.type}) 登录成功")
                
                # 记录登录日志
                OperationLogger.log_login(user.id, user.name, user.type, 1, request)

                return SysView.successData({'token': token})

            except Exception as e:
                logger.error(f"生成token失败: {str(e)}")
                return BaseView.error('登录失败，请稍后重试')

        return BaseView.warn('登录失败')

    # 退出系统
    def exit(request):
        """退出方法（支持JWT和旧token）"""
        # 获取当前用户信息用于记录登出日志
        token = (
            request.POST.get('token') or
            request.GET.get('token') or
            request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        )
        user_id = cache.get(token) if token else None
        if user_id:
            user = models.Users.objects.filter(id=user_id).first()
            if user:
                OperationLogger.log_logout(user.id, user.name, user.type, request)
        
        # 尝试从多个位置获取token
        token = (
            request.POST.get('token') or
            request.GET.get('token') or
            request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        )

        if token:
            try:
                # 尝试作为JWT token撤销
                if revoke_token(token):
                    logger.info(f"JWT token已撤销")
                else:
                    # 如果不是JWT token，从缓存中删除（向后兼容）
                    cache.delete(token)
                    logger.info(f"旧token已从缓存中删除")
            except Exception as e:
                # 退出操作失败不影响用户体验，记录日志即可
                logger.warning(f'退出登录时删除token失败: {str(e)}')

        return BaseView.success()

    # 修改用户信息
    def updUserInfo(request):

        user = models.Users.objects.filter(id=cache.get(request.POST.get('token')))
        if (request.POST.get('userName') != user.first().userName) & \
                (models.Users.objects.filter(userName=request.POST.get('userName')).exists()):
            return BaseView.warn('用户账号已存在')
        else:
            user.update(
                userName=request.POST.get('userName'),
                name=request.POST.get('name'),
                gender=request.POST.get('gender'),
                age=request.POST.get('age'),
            )
            return BaseView.success()

    # 修改用户密码
    def updUserPwd(request):
        user = models.Users.objects.filter(id=cache.get(request.POST.get('token'))).first()
        if not user:
            return BaseView.error('用户未登录')

        newPwd = request.POST.get('newPwd')
        rePwd = request.POST.get('rePwd')
        oldPwd = request.POST.get('oldPwd')

        if newPwd != rePwd:
            return BaseView.warn('两次输入的密码不一致')

        # 验证旧密码（支持明文和加密两种格式）
        if len(user.passWord) < 50:
            # 旧明文密码格式
            if oldPwd != user.passWord:
                return BaseView.warn('原始密码输入错误')
        else:
            # 新加密密码格式
            if not check_password(oldPwd, user.passWord):
                return BaseView.warn('原始密码输入错误')

        # 使用加密密码存储新密码
        user.passWord = make_password(newPwd)
        user.save()
        return BaseView.success()


'''
学院信息处理
'''


class CollegesView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return CollegesView.getAll(request)
        elif module == 'page':
            return CollegesView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return CollegesView.addInfo(request)
        elif module == 'upd':
            return CollegesView.updInfo(request)
        elif module == 'del':
            return CollegesView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取全部的学院信息
    def getAll(request):

        # 使用缓存减少数据库查询
        cache_key = 'colleges:all'
        colleges_data = cache.get(cache_key)
        if colleges_data is None:
            colleges = models.Colleges.objects.all()
            colleges_data = list(colleges.values())
            cache.set(cache_key, colleges_data, 3600)  # 缓存1小时

        return BaseView.successData(colleges_data)

    # 分页获取学院信息
    def getPageInfos(request):
        """分页获取学院信息（使用服务层）"""
        def serializer(item):
            return {
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            }

        return CRUDService.get_page_infos(
            model_class=models.Colleges,
            request=request,
            search_fields=['name'],
            serializer_func=serializer
        )

    # 添加学院信息
    def addInfo(request):
        """添加学院信息（使用服务层）"""
        return CRUDService.add_info(
            model_class=models.Colleges,
            request=request,
            fields_mapping={'name': 'name'}
        )

    # 修改学院信息
    def updInfo(request):
        """修改学院信息（使用服务层）"""
        return CRUDService.upd_info(
            model_class=models.Colleges,
            request=request,
            fields_mapping={'name': 'name'}
        )

    # 删除学院信息
    def delInfo(request):
        """删除学院信息（使用服务层）"""
        return CRUDService.del_info(
            model_class=models.Colleges,
            request=request,
            check_relations=[
                {
                    'model': models.Students,
                    'field': 'college__id',
                    'message': '存在关联记录无法移除'
                }
            ]
        )


'''
班级信息处理
'''


class GradesView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return GradesView.getAll(request)
        elif module == 'page':
            return GradesView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return GradesView.addInfo(request)
        elif module == 'upd':
            return GradesView.updInfo(request)
        elif module == 'del':
            return GradesView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取全部的班级信息
    def getAll(request):

        # 使用缓存减少数据库查询
        cache_key = 'grades:all'
        grades_data = cache.get(cache_key)
        if grades_data is None:
            grades = models.Grades.objects.all()
            grades_data = list(grades.values())
            cache.set(cache_key, grades_data, 3600)  # 缓存1小时

        return BaseView.successData(grades_data)

    # 分页获取班级信息
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        query = Q()

        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)

        data = models.Grades.objects.filter(query).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加班级信息
    def addInfo(request):

        models.Grades.objects.create(
            name=request.POST.get('name'),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改班级信息
    def updInfo(request):

        models.Grades.objects. \
            filter(id=request.POST.get('id')).update(
                name=request.POST.get('name')
            )
        return BaseView.success()

    # 删除班级信息
    def delInfo(request):

        if models.Students.objects.filter(grade__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联学生无法移除')
        elif models.Exams.objects.filter(grade__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联考试无法移除')
        else:
            models.Grades.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
科目信息处理
'''


class ProjectsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'all':
            return ProjectsView.getAll(request)
        elif module == 'page':
            return ProjectsView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return ProjectsView.addInfo(request)
        elif module == 'upd':
            return ProjectsView.updInfo(request)
        elif module == 'del':
            return ProjectsView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取全部的科目信息
    def getAll(request):

        # 使用缓存减少数据库查询
        cache_key = 'projects:all'
        projects_data = cache.get(cache_key)
        if projects_data is None:
            projects = models.Projects.objects.all()
            projects_data = list(projects.values())
            cache.set(cache_key, projects_data, 3600)  # 缓存1小时

        return BaseView.successData(projects_data)

    # 分页获取科目信息
    def getPageInfos(request):

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

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加科目信息
    def addInfo(request):
        """添加科目信息（使用服务层）"""
        return CRUDService.add_info(
            model_class=models.Projects,
            request=request,
            fields_mapping={'name': 'name'}
        )

    # 修改科目信息
    def updInfo(request):
        """修改科目信息（使用服务层）"""
        return CRUDService.upd_info(
            model_class=models.Projects,
            request=request,
            fields_mapping={'name': 'name'}
        )

    # 删除科目信息
    def delInfo(request):
        """删除科目信息（使用服务层）"""
        return CRUDService.del_info(
            model_class=models.Projects,
            request=request,
            check_relations=[
                {
                    'model': models.Exams,
                    'field': 'project__id',
                    'message': '存在关联记录无法移除'
                },
                {
                    'model': models.Practises,
                    'field': 'project__id',
                    'message': '存在关联记录无法移除'
                }
            ]
        )


'''
教师信息处理
'''


class TeachersView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return TeachersView.getPageInfos(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return TeachersView.addInfo(request)
        elif module == 'upd':
            return TeachersView.updInfo(request)
        elif module == 'del':
            return TeachersView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 分页查询教师信息
    def getPageInfos(request):

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

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加教师信息
    @transaction.atomic
    def addInfo(request):
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
            return BaseView.success()

    # 修改教师信息
    def updInfo(request):

        models.Teachers.objects. \
            filter(user__id=request.POST.get('id')).update(
                phone=request.POST.get('phone'),
                record=request.POST.get('record'),
                job=request.POST.get('job')
            )
        return BaseView.success()

    # 删除教师信息
    @transaction.atomic
    def delInfo(request):

        if models.Exams.objects.filter(teacher__id=request.POST.get('id')).exists():
            return BaseView.warn('存在关联记录无法移除')
        else:
            models.Users.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
学生信息处理
'''


class StudentsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module in ['page', 'getPageInfos']:
            return StudentsView.getPageInfos(request)
        elif module == 'info':
            return StudentsView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return StudentsView.addInfo(request)
        elif module == 'upd':
            return StudentsView.updInfo(request)
        elif module == 'del':
            return StudentsView.delInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定学生信息
    def getInfo(request):

        student = models.Students.objects.filter(
            user__id=request.GET.get('id')).select_related(
            'user', 'grade', 'college').first()

        if not student:
            return BaseView.error('学生信息不存在')

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

    # 分页查询学生信息

    def getPageInfos(request):
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

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加学生信息
    @transaction.atomic
    def addInfo(request):
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
            return BaseView.success()

    # 修改学生信息
    def updInfo(request):

        models.Students.objects. \
            filter(user__id=request.POST.get('id')).update(
                grade=models.Grades.objects.get(id=request.POST.get('gradeId')),
                college=models.Colleges.objects.get(id=request.POST.get('collegeId'))
            )
        return BaseView.success()

    # 删除学生信息
    @transaction.atomic
    def delInfo(request):

        if (models.ExamLogs.objects.filter(student__id=request.POST.get('id')).exists() |
                models.AnswerLogs.objects.filter(student__id=request.POST.get('id')).exists()):
            return BaseView.warn('存在关联记录无法移除')
        else:
            models.Users.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
习题信息处理
'''


class PractisesView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return PractisesView.getPageInfos(request)
        elif module == 'info':
            return PractisesView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return PractisesView.addInfo(request)
        elif module == 'setanswer':
            return PractisesView.setAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定 ID 的习题信息
    def getInfo(request):

        practise = models.Practises.objects.filter(id=request.GET.get('id')).select_related('project').first()

        if not practise:
            return BaseView.error('题目不存在')

        if practise.type == 0:
            return BaseView.successData({
                'id': practise.id,
                'name': practise.name,
                'answer': practise.answer,
                'analyse': practise.analyse,
                'type': practise.type,
                'createTime': practise.createTime,
                'projectId': practise.project.id,
                'projectName': practise.project.name,
                'options': list(models.Options.objects.filter(practise__id=practise.id).values())
            })
        else:
            return BaseView.successData({
                'id': practise.id,
                'name': practise.name,
                'answer': practise.answer,
                'analyse': practise.analyse,
                'type': practise.type,
                'createTime': practise.createTime,
                'projectId': practise.project.id,
                'projectName': practise.project.name,
            })

    # 分页查询习题信息

    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        type = request.GET.get('type')
        projectId = request.GET.get('projectId')

        query = Q()
        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)
        if SysUtil.isExit(type):
            query = query & Q(type=int(type))
        if SysUtil.isExit(projectId):
            query = query & Q(project__id=int(projectId))

        # 使用select_related优化外键查询，避免N+1问题
        data = models.Practises.objects.filter(query).select_related('project').order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        # 获取当前页数据
        page_data = list(paginator.page(pageIndex))

        # 批量获取选项数量，避免循环中查询
        practise_ids = [item.id for item in page_data]
        option_counts = {}
        if practise_ids:
            from django.db.models import Count
            option_counts_query = models.Options.objects.filter(
                practise_id__in=practise_ids).values('practise_id').annotate(
                count=Count('id'))
            option_counts = {item['practise_id']: item['count'] for item in option_counts_query}

        for item in page_data:

            if item.type == 0:
                resl.append({
                    'id': item.id,
                    'name': item.name,
                    'answer': int(item.answer) if SysUtil.isExit(item.answer) else '',
                    'analyse': item.analyse,
                    'type': item.type,
                    'projectId': item.project.id,
                    'projectName': item.project.name,
                    'createTime': item.createTime,
                    'optionTotal': option_counts.get(item.id, 0)
                })
            else:
                resl.append({
                    'id': item.id,
                    'name': item.name,
                    'answer': item.answer,
                    'analyse': item.analyse,
                    'type': item.type,
                    'projectId': item.project.id,
                    'projectName': item.project.name,
                    'createTime': item.createTime,
                    'optionTotal': 0
                })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加习题信息
    def addInfo(request):
        models.Practises.objects.create(
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            project=models.Projects.objects.get(id=request.POST.get('projectId')),
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改习题信息
    def setAnswer(request):
        models.Practises.objects. \
            filter(id=request.POST.get('id')).update(
                answer=request.POST.get('answer'),
                analyse=request.POST.get('analyse')
            )
        return BaseView.success()


'''
选项信息处理
'''


class OptionsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'list':
            return OptionsView.getListByPractiseId(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return OptionsView.addInfo(request)
        elif module == 'upd':
            return OptionsView.updInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    # 依据习题编号获取选项信息
    def getListByPractiseId(request):

        options = models.Options.objects.filter(practise__id=request.GET.get('practiseId'))

        return BaseView.successData(list(options.values()))

    # 添加选项信息
    def addInfo(request):
        models.Options.objects.create(
            name=request.POST.get('name'),
            practise=models.Practises.objects.get(id=request.POST.get('practiseId'))
        )
        return BaseView.success()

    # 修改选项信息
    def updInfo(request):
        models.Options.objects. \
            filter(id=request.POST.get('id')).update(
                name=request.POST.get('name')
            )
        return BaseView.success()


'''
考试信息处理
'''


class ExamsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return ExamsView.getPageInfos(request)
        elif module == 'info':
            return ExamsView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return ExamsView.addInfo(request)
        elif module == 'make':
            return ExamsView.createExamPaper(request)
        elif module == 'create_from_practice_paper':
            return ExamsView.createFromPracticePaper(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取��试信息
    def getInfo(request):

        exam = models.Exams.objects.filter(
            id=request.GET.get('id')).select_related(
            'teacher', 'project', 'grade').first()

        if not exam:
            return BaseView.error('考试信息不存在')

        return BaseView.successData({
            'id': exam.id,
            'name': exam.name,
            'createTime': exam.createTime,
            'examTime': exam.examTime,
            'startTime': getattr(exam, 'startTime', None),
            'endTime': getattr(exam, 'endTime', None),
            'teacherId': exam.teacher.id,
            'teacherName': exam.teacher.name,
            'projectId': exam.project.id,
            'projectName': exam.project.name,
            'gradeId': exam.grade.id,
            'gradeName': exam.grade.name,
        })

    # 分页查询考试信息
    """
    API分页获取考试列表

    ---
    tags:
      - 考试管理
    summary:
      分页查询考试信息
    description:
      支持按名称、年级、科目、教师等条件筛选考试列表
    parameters:
      - name: pageIndex
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
      - name: pageSize
        in: query
        type: integer
        required: false
        default: 10
        description: 每页数量
      - name: name
        in: query
        type: string
        required: false
        description: 考试名称（模糊搜索）
      - name: gradeId
        in: query
        type: integer
        required: false
        description: 年级ID
      - name: projectId
        in: query
        type: integer
        required: false
        description: 科目ID
      - name: teacherId
        in: query
        type: integer
        required: false
        description: 教师ID
    responses:
      200:
        description: 成功返回考试列表
        schema:
          type: object
          properties:
            code:
              type: integer
              description: 状态码（0表示成功）
            msg:
              type: string
              description: 消息
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: 考试ID
                  name:
                    type: string
                    description: 考试名称
                  examTime:
                    type: string
                    description: 考试时间
                  teacherId:
                    type: integer
                    description: 教师ID
                  teacherName:
                    type: string
                    description: 教师姓名
                  projectId:
                    type: integer
                    description: 科目ID
                  projectName:
                    type: string
                    description: 科目名称
      400:
        description: 参数错误
    """
    def getPageInfos(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        gradeId = request.GET.get('gradeId')
        projectId = request.GET.get('projectId')
        teacherId = request.GET.get('teacherId')

        query = Q()
        if SysUtil.isExit(teacherId):
            query = query & Q(teacher__id=teacherId)
        if SysUtil.isExit(name):
            query = query & Q(name__contains=name)
        if SysUtil.isExit(gradeId):
            query = query & Q(grade__id=gradeId)
        if SysUtil.isExit(projectId):
            query = query & Q(project__id=projectId)

        # 优化：使用select_related预加载外键对象，避免N+1查询
        data = models.Exams.objects.filter(query).select_related(
            'teacher', 'project', 'grade'
        ).order_by('-createTime')

        paginator = Paginator(data, pageSize)

        # 只查询一次页面数据，避免重复查询
        page = paginator.page(pageIndex)
        exam_list = list(page)

        # 优化：预先批量查询当前学生的考试记录
        from django.core.cache import cache
        token = request.GET.get('token')
        student_id = cache.get(token) if token else None

        # 批量查询该学生在这些考试中的记录
        exam_logs = {}
        if student_id and exam_list:
            exam_ids = [exam.id for exam in exam_list]
            logs = models.ExamLogs.objects.filter(
                student__id=student_id,
                exam__id__in=exam_ids
            ).select_related('exam').order_by('-id')

            # 为每个考试记录保存最新状态
            for log in logs:
                if log.exam_id not in exam_logs:  # 只保留每个考试的最新记录
                    exam_logs[log.exam_id] = log.status

        resl = []

        for item in exam_list:
            # 查询当前年级下每个学生的个人考试状态（如果需要，可限制为当前登录学生）
            # 这里提供 studentStatus 字段：0-进行中/未开始；2-已结束
            student_status = exam_logs.get(item.id)

            resl.append({
                'id': item.id,
                'name': item.name,
                'examTime': item.examTime,
                'startTime': getattr(item, 'startTime', None),
                'endTime': getattr(item, 'endTime', None),
                'createTime': item.createTime,
                'projectId': item.project.id,
                'projectName': item.project.name,
                'teacherId': item.teacher.id,
                'teacherName': item.teacher.name,
                'gradeId': item.grade.id,
                'gradeName': item.grade.name,
                'studentStatus': student_status
            })

        # 复用已有的page对象，避免重复查询
        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       page.paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加考试信息
    def addInfo(request):

        if ExamUtils.CheckPractiseTotal.check(request.POST.get('projectId')):

            # 验证考试时间
            start_time = request.POST.get('startTime')
            end_time = request.POST.get('endTime')
            if start_time and end_time:
                if start_time >= end_time:
                    return BaseView.warn('结束时间必须晚于开始时间')

            if models.Teachers.objects.filter(user__id=request.POST.get('teacherId')).exists():
                models.Exams.objects.create(
                    name=request.POST.get('name'),
                    examTime=request.POST.get('examTime'),
                    startTime=start_time or None,
                    endTime=end_time or None,
                    project=models.Projects.objects.get(id=request.POST.get('projectId')),
                    teacher=models.Users.objects.get(id=request.POST.get('teacherId')),
                    grade=models.Grades.objects.get(id=request.POST.get('gradeId')),
                    createTime=DateUtil.getNowDateTime()
                )
                return BaseView.success()
            else:
                return BaseView.warn('指定工号的教师不存在')
        else:
            return BaseView.warn('相关题目数量不足，无法准备考试')

    # 生成考试试卷
    def createExamPaper(request):

        projectId = request.POST.get('projectId')
        paper = ExamUtils.MakeExam.make(projectId)

        return BaseView.successData(paper)

    @staticmethod
    def createFromPracticePaper(request):
        """从练习试卷一键创建考试（仅创建 Exams 记录，题目由系统按学科抽取）"""
        try:
            paper_id = request.POST.get('paperId')
            name = request.POST.get('name')
            teacher_id = request.POST.get('teacherId')
            grade_id = request.POST.get('gradeId')
            exam_time = request.POST.get('examTime')  # 'YYYY-MM-DD HH:MM:SS'

            if not all([paper_id, teacher_id, grade_id]):
                return BaseView.error('缺少必要参数：paperId/teacherId/gradeId')

            paper = models.PracticePapers.objects.filter(id=paper_id, isActive=True).first()
            if not paper:
                return BaseView.error('练习试卷不存在或未启用')

            # 检查教师存在
            if not models.Teachers.objects.filter(user__id=teacher_id).exists():
                return BaseView.warn('指定工号的教师不存在')
            teacher_user = models.Users.objects.filter(id=teacher_id).first()
            if not teacher_user:
                return BaseView.warn('教师用户不存在')

            # 检查年级存在
            grade_obj = models.Grades.objects.filter(id=grade_id).first()
            if not grade_obj:
                return BaseView.warn('指定的年级不存在')

            exam = models.Exams.objects.create(
                name=name or f"{paper.title}-考试",
                examTime=exam_time or DateUtil.getNowDateTime(),
                startTime=request.POST.get('startTime') or None,
                endTime=request.POST.get('endTime') or None,
                project=paper.project,
                teacher=teacher_user,
                grade=grade_obj,
                createTime=DateUtil.getNowDateTime()
            )

            return BaseView.successData({'examId': exam.id, 'name': exam.name})
        except Exception as e:
            return BaseView.error(f'创建考试失败: {str(e)}')


'''
考试记录处理
'''


class ExamLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'pagestu':
            return ExamLogsView.getPageStudentLogs(request)
        elif module == 'pagetea':
            return ExamLogsView.getPageTeacherLogs(request)
        elif module == 'info':
            return ExamLogsView.getInfo(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return ExamLogsView.addInfo(request)
        elif module == 'upd':
            return ExamLogsView.updInfo(request)
        elif module == 'put':
            return ExamLogsView.putExamLog(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定考试记录
    def getInfo(request):

        # 使用select_related优化查询
        examLogs = models.ExamLogs.objects.filter(
            id=request.GET.get('id')).select_related(
            'exam', 'exam__project', 'exam__teacher', 'exam__grade').first()

        answers = []
        query = Q()
        query = query & Q(student__id=request.GET.get('studentId'))
        query = query & Q(exam__id=examLogs.exam.id)
        # 使用select_related和prefetch_related优化查询
        temps = models.AnswerLogs.objects.filter(query).select_related(
            'practise', 'practise__project').prefetch_related('practise__options').order_by('no')

        # 批量获取选项，避免循环中查询
        practise_ids = [item.practise.id for item in temps]
        options_dict = {}
        if practise_ids:
            all_options = models.Options.objects.filter(practise_id__in=practise_ids)
            for option in all_options:
                if option.practise_id not in options_dict:
                    options_dict[option.practise_id] = []
                options_dict[option.practise_id].append({
                    'id': option.id,
                    'name': option.name,
                    'practise_id': option.practise_id
                })

        for item in temps:
            answers.append({
                'id': item.id,
                'score': item.score,
                'status': item.status,
                'answer': item.answer,
                'no': item.no,
                'practiseId': item.practise.id,
                'practiseName': item.practise.name,
                'practiseAnswer': item.practise.answer,
                'practiseAnalyse': item.practise.analyse,
                'options': options_dict.get(item.practise.id, []),
            })

        return BaseView.successData({
            'id': examLogs.id,
            'status': examLogs.status,
            'score': examLogs.score,
            'createTime': examLogs.createTime,
            'examId': examLogs.exam.id,
            'examName': examLogs.exam.name,
            'projectId': examLogs.exam.project.id,
            'projectName': examLogs.exam.project.name,
            'teacherId': examLogs.exam.teacher.id,
            'teacherName': examLogs.exam.teacher.name,
            'gradeId': examLogs.exam.grade.id,
            'gradeName': examLogs.exam.grade.name,
            'answers': answers
        })

    # 分页获取学生考试记录
    def getPageStudentLogs(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        examName = request.GET.get('examName')
        studentId = request.GET.get('studentId')
        projectId = request.GET.get('projectId')

        query = Q(student__id=studentId)
        if SysUtil.isExit(examName):
            query = query & Q(exam__name__contains=examName)
        if SysUtil.isExit(projectId):
            query = query & Q(exam__project__id=projectId)

        # 使用select_related优化外键查询，避免N+1问题
        data = models.ExamLogs.objects.filter(query).select_related(
            'exam', 'exam__teacher', 'exam__project').order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'status': item.status,
                'createTime': item.createTime,
                'score': item.score,
                'examId': item.exam.id,
                'examName': item.exam.name,
                'teacherId': item.exam.teacher.id,
                'teacherName': item.exam.teacher.name,
                'projectId': item.exam.project.id,
                'projectName': item.exam.project.name,
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 分页获取教师审核记录
    def getPageTeacherLogs(request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        examName = request.GET.get('examName')
        token = request.GET.get('token')
        gradeId = request.GET.get('gradeId')
        projectId = request.GET.get('projectId')

        query = Q(exam__teacher__id=cache.get(token))
        if SysUtil.isExit(examName):
            query = query & Q(exam__name__contains=examName)
        if SysUtil.isExit(gradeId):
            query = query & Q(exam__grade__id=gradeId)
        if SysUtil.isExit(projectId):
            query = query & Q(exam__project__id=projectId)

        # 使用select_related优化外键查询，避免N+1问题
        data = models.ExamLogs.objects.filter(query).select_related(
            'exam', 'exam__project', 'exam__grade', 'student').order_by('-createTime')

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            resl.append({
                'id': item.id,
                'status': item.status,
                'createTime': item.createTime,
                'score': item.score,
                'examId': item.exam.id,
                'examName': item.exam.name,
                'studentId': item.student.id,
                'studentName': item.student.name,
                'projectId': item.exam.project.id,
                'projectName': item.exam.project.name,
                'gradeId': item.exam.grade.id,
                'gradeName': item.exam.grade.name,
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 添加考试记录
    def addInfo(request):

        token = request.POST.get('token')
        if not token:
            return BaseView.error('未登录，请先登录')

        student_id = cache.get(token)
        if not student_id:
            return BaseView.error('登录已过期，请重��登录')

        exam_id = request.POST.get('examId')
        if not exam_id:
            return BaseView.error('考试ID不能为空')

        # 验证学生是否存在
        try:
            student = models.Users.objects.get(id=student_id)
        except models.Users.DoesNotExist:
            return BaseView.error('学生用户不存在')

        # 验证考试是否存在且有效
        try:
            exam = models.Exams.objects.get(id=exam_id)
        except models.Exams.DoesNotExist:
            return BaseView.error('考试不存在')

        # 验证学生是否有权限参加该考试（检查年级匹配）
        try:
            student_info = models.Students.objects.get(user__id=student_id)
            if student_info.grade.id != exam.grade.id:
                return BaseView.error('您没有权限参加该考试')
        except models.Students.DoesNotExist:
            return BaseView.error('学生信息不存在')

        # 检查是否已经参加过该考试
        if models.ExamLogs.objects.filter(student__id=student_id, exam__id=exam_id).exists():
            return BaseView.warn('您已参加过该考试，请勿重复参加')

        # 创建考试记录
        models.ExamLogs.objects.create(
            student=student,
            exam=exam,
            status=0,
            score=0,
            createTime=DateUtil.getNowDateTime()
        )
        return BaseView.success()

    # 修改考试记录
    def updInfo(request):

        models.ExamLogs.objects. \
            filter(id=request.POST.get('id')).update(
                status=request.POST.get('status')
            )
        return BaseView.success()

    # 公布学生考核成绩
    def putExamLog(request):
        studentId = request.POST.get('studentId')
        examId = request.POST.get('examId')

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)

        total = 0.0
        # 使用select_related预加载practise外键，避免N+1查询
        answers = models.AnswerLogs.objects.filter(query).select_related('practise')
        for item in answers:

            if item.practise.type == 0:
                temp = 2 if item.practise.answer == item.answer else 0
                total = total + temp
                models.AnswerLogs.objects. \
                    filter(id=item.id).update(
                        status=1,
                        score=temp
                    )
            elif item.practise.type == 1:
                total = total + item.score
            elif item.practise.type == 2:
                temp = 2 if item.practise.answer == item.answer else 0
                total = total + temp
                models.AnswerLogs.objects. \
                    filter(id=item.id).update(
                        status=1,
                        score=temp
                    )
            elif item.practise.type == 3:
                total = total + item.score

        models.ExamLogs.objects. \
            filter(query).update(
                status=2,
                score=total
            )
        return BaseView.success()


'''
答题记录处理
'''


class AnswerLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return AnswerLogsView.getInfo(request)
        elif module == 'answers':
            return AnswerLogsView.getAnswers(request)
        elif module == 'check':
            return AnswerLogsView.checkAnswers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return AnswerLogsView.addInfo(request)
        elif module == 'audit':
            return AnswerLogsView.aduitAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定答题记录
    def getInfo(request):
        pass

    # 获取指定的答案列表
    def getAnswers(request):

        studentId = request.GET.get('studentId')
        type = request.GET.get('type')
        examId = request.GET.get('examId')

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)

        resl = []
        data = models.AnswerLogs.objects.filter(query).select_related('practise').order_by('no')
        for item in data:
            resl.append({
                'id': item.id,
                'practiseId': item.practise.id,
                'practiseName': item.practise.name,
                'practiseAnswer': item.practise.answer,
                'answer': item.answer,
                'score': item.score,
                'status': item.status,
                'no': item.no,
                'type': item.practise.type
            })

        # 若请求了具体类型，过滤返回
        if type in ('1', '3'):
            t = int(type)
            resl = [x for x in resl if x['type'] == t]

        return BaseView.successData(resl)

    # 按照类型检查答题
    def checkAnswerType(studentId, examId, type):

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)
        query = query & Q(status=0)
        query = query & Q(practise__type=type)

        return models.AnswerLogs.objects.filter(query).exists()

    # 检查手动审核题目
    def checkAnswers(request):

        studentId = request.GET.get('studentId')
        examId = request.GET.get('examId')

        query = Q(student__id=studentId)
        query = query & Q(exam__id=examId)
        query = query & Q(status=0)
        query = query & Q(practise__type=1)
        query = query | Q(practise__type=3)

        if AnswerLogsView.checkAnswerType(studentId, examId, 1):

            return BaseView.successData({'flag': True, 'msg': '填空题还有未审核的内容'})
        elif AnswerLogsView.checkAnswerType(studentId, examId, 3):

            return BaseView.successData({'flag': True, 'msg': '编程题还有未审核的内容'})
        else:

            return BaseView.successData({'flag': False, 'msg': '手动审核部分已完成'})

    # 添加答题记录
    @transaction.atomic
    def addInfo(request):
        # 兼容 JSON 与 form-data 两种提交方式
        import json as _json
        try:
            body = request.body.decode('utf-8') if request.body else ''
            data = _json.loads(body) if body else {}
        except Exception:
            data = {}

        answers = data.get('answers') if isinstance(data, dict) else None
        nos = data.get('nos') if isinstance(data, dict) else None
        practiseIds = data.get('practiseIds') if isinstance(data, dict) else None
        examId = data.get('examId') if isinstance(data, dict) else None
        token = data.get('token') if isinstance(data, dict) else None

        # 若 JSON 为空，回退到表单
        if not answers:
            answers = request.POST.getlist('answers')
        if not nos:
            nos = request.POST.getlist('nos')
        if not practiseIds:
            practiseIds = request.POST.getlist('practiseIds')
        if not examId:
            examId = request.POST.get('examId')
        if not token:
            token = request.POST.get('token')

        if answers is None or nos is None or practiseIds is None or not examId or not token:
            return BaseView.error('参数不完整，无法提交答卷')

        student_id = cache.get(token)
        if not student_id:
            return BaseView.error('登录状态失效，请重新登录后再试')

        # 验证考试时间，防止逾期提交
        try:
            exam = models.Exams.objects.filter(id=examId).first()
            if not exam:
                return BaseView.error('考试不存在')

            # 检查考试是否已结束
            current_time = DateUtil.getNowDateTime()
            if exam.endTime:
                if current_time > exam.endTime:
                    return BaseView.error('考试已结束，无法提交答案')
            # 如果设置了startTime，检查是否未开始
            if exam.startTime:
                if current_time < exam.startTime:
                    return BaseView.error('考试尚未开始')
        except Exception as e:
            return BaseView.error(f'验证考试时间失败: {str(e)}')

        # 统一将 nos/ids/answers 全部转为列表（防止是逗号分隔字符串导致长度对不上）
        if isinstance(nos, str):
            nos = [x for x in nos.split(',') if x != '']
        if isinstance(practiseIds, str):
            practiseIds = [x for x in practiseIds.split(',') if x != '']
        if isinstance(answers, str):
            try:
                # 尝试 JSON 字符串
                import json as _json
                tmp = _json.loads(answers)
                if isinstance(tmp, list):
                    answers = tmp
            except Exception:
                answers = [answers]

        # 写入答案
        for no in nos:
            idx = int(no) - 1
            if idx < 0 or idx >= len(practiseIds) or idx >= len(answers):
                continue
            models.AnswerLogs.objects.create(
                student=models.Users.objects.get(id=student_id),
                exam=models.Exams.objects.get(id=examId),
                practise=models.Practises.objects.get(id=practiseIds[idx]),
                status=0,
                answer=answers[idx] if answers[idx] is not None else '',
                no=no
            )

        # 自动评分并直接出分（取消老师审核）
        from comm.AIUtils import AIUtils as _AI
        ai_utils = _AI()
        query = Q(exam__id=examId) & Q(student__id=student_id)
        answers_qs = models.AnswerLogs.objects.filter(query).select_related('practise')
        total = 0.0
        for item in answers_qs:
            practise = item.practise
            ai_res = {}
            if practise.type in [0, 2]:
                # 选择/判断：对比正确答案
                score = 2 if str(practise.answer).strip().lower() == str(item.answer).strip().lower() else 0
                item.score = score
                item.status = 1
                item.save(update_fields=['score', 'status'])
                total += score
                # 错题入库：选择/判断答错
                if score < 2:
                    try:
                        analysis_text = practise.analyse or ''
                        if not analysis_text:
                            # 使用AI做错误解析
                            try:
                                ai_explain = ai_utils.ai_analyze_wrong_answer(
                                    practise.name, practise.answer or '', item.answer or '', practise.type)
                                analysis_text = ai_explain.get('analysis') or ''
                            except Exception:
                                analysis_text = ''
                        wrong, created = models.WrongQuestions.objects.get_or_create(
                            student=models.Users.objects.get(id=student_id),
                            practise=practise,
                            source='exam',
                            sourceId=examId,
                            defaults={
                                'wrongAnswer': item.answer or '',
                                'correctAnswer': practise.answer or '',
                                'analysis': analysis_text,
                                'createTime': DateUtil.getNowDateTime()
                            }
                        )
                        if not created:
                            wrong.wrongAnswer = item.answer or ''
                            wrong.correctAnswer = practise.answer or ''
                            if analysis_text and not wrong.analysis:
                                wrong.analysis = analysis_text
                            wrong.save()
                    except Exception:
                        pass
            elif practise.type in [1, 3]:
                # 填空/编程：AI评分（失败则回退为0分）
                try:
                    ai_res = ai_utils.ai_score_answer(
                        question_content=practise.name,
                        correct_answer=practise.answer or '',
                        student_answer=item.answer or '',
                        question_type=practise.type,
                        max_score=2.0 if practise.type == 1 else 20.0
                    )
                    score = float(ai_res.get('score', 0))
                except Exception:
                    score = 0.0
                item.score = score
                item.status = 1
                item.save(update_fields=['score', 'status'])
                total += score
                # 错题入库：分数未满则视为错题（支持复习/讲解）
                max_score = 2.0 if practise.type == 1 else 20.0
                if score < max_score:
                    try:
                        analysis_text = (
                            ai_res.get('analysis') if isinstance(
                                ai_res, dict) else '') or practise.analyse or ''
                        wrong, created = models.WrongQuestions.objects.get_or_create(
                            student=models.Users.objects.get(id=student_id),
                            practise=practise,
                            source='exam',
                            sourceId=examId,
                            defaults={
                                'wrongAnswer': item.answer or '',
                                'correctAnswer': practise.answer or '',
                                'analysis': analysis_text,
                                'createTime': DateUtil.getNowDateTime()
                            }
                        )
                        if not created:
                            wrong.wrongAnswer = item.answer or ''
                            wrong.correctAnswer = practise.answer or ''
                            if analysis_text and not wrong.analysis:
                                wrong.analysis = analysis_text
                            wrong.save()
                    except Exception:
                        pass

        # 写入考试日志为结束状态并记录总分
        models.ExamLogs.objects.filter(query).update(status=2, score=total)
        return BaseView.successData({'score': total})

    # 审核答题
    def aduitAnswer(request):

        if int(request.POST.get('type')) == 1:

            models.AnswerLogs.objects. \
                filter(id=request.POST.get('id')).update(
                    status=1,
                    score=2 if int(request.POST.get('flag')) == 0 else 0,
                )
        else:
            models.AnswerLogs.objects. \
                filter(id=request.POST.get('id')).update(
                    status=1,
                    score=20 if int(request.POST.get('flag')) == 0 else 0,
                )

        return BaseView.success()


'''
练习试卷信息处理
'''


class PracticePapersView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'page':
            return PracticePapersView.getPageInfos(request)
        elif module == 'info':
            return PracticePapersView.getInfo(request)
        elif module == 'questions':
            return PracticePapersView.getPaperQuestions(request)
        elif module == 'student':
            return PracticePapersView.getStudentPapers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return PracticePapersView.addInfo(request)
        elif module == 'upd':
            return PracticePapersView.updInfo(request)
        elif module == 'del':
            return PracticePapersView.delInfo(request)
        elif module == 'generate_wrong':
            return PracticePapersView.generateWrongPracticePaper(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取指定ID的练习试卷信息
    def getInfo(request):
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

    # 分页查询练习试卷信息
    def getPageInfos(request):
        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        title = request.GET.get('title')
        type = request.GET.get('type')
        difficulty = request.GET.get('difficulty')
        projectId = request.GET.get('projectId')

        query = Q(isActive=True)
        if SysUtil.isExit(title):
            query = query & Q(title__contains=title)
        if SysUtil.isExit(type):
            query = query & Q(type=type)
        if SysUtil.isExit(difficulty):
            query = query & Q(difficulty=difficulty)
        if SysUtil.isExit(projectId):
            query = query & Q(project__id=int(projectId))

        data = models.PracticePapers.objects.filter(query).order_by('-createTime')
        paginator = Paginator(data, pageSize)

        resl = []
        for item in list(paginator.page(pageIndex)):
            # 获取题目数量
            questionCount = models.PracticePaperQuestions.objects.filter(paper=item).count()

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
                'questionCount': questionCount
            })

        pageData = BaseView.parasePage(int(pageIndex), int(pageSize),
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    # 获取学生可用的练习试卷
    def getStudentPapers(request):
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
        # 使用缓存获取项目列表
        cache_key = 'projects:all_ids'
        project_ids = cache.get(cache_key)
        if project_ids is None:
            project_ids = list(models.Projects.objects.all().values_list('id', flat=True))
            cache.set(cache_key, project_ids, 3600)  # 缓存1小时

        papers = models.PracticePapers.objects.filter(
            isActive=True,
            project__id__in=models.Practises.objects.filter(
                project__id__in=project_ids
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
                'accuracy': accuracy
            })

        return BaseView.successData(resl)

    # 获取试卷题目
    def getPaperQuestions(request):
        paperId = request.GET.get('paperId')
        if not paperId:
            return BaseView.error('试卷ID不能为空')

        questions = models.PracticePaperQuestions.objects.filter(
            paper__id=paperId
        ).order_by('questionOrder')

        resl = []
        for q in questions:
            practise = q.practise
            questionData = {
                'id': practise.id,
                'questionOrder': q.questionOrder,
                'score': q.score,
                'type': practise.type,
                'content': practise.name,
                'analyse': practise.analyse
            }

            # 如果是选择题，获取选项
            if practise.type == 0:
                options = models.Options.objects.filter(practise=practise)
                questionData['options'] = [opt.name for opt in options]

            resl.append(questionData)

        return BaseView.successData(resl)

    # 添加练习试卷
    def addInfo(request):
        models.PracticePapers.objects.create(
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
        return BaseView.success()

    # 修改练习试卷
    def updInfo(request):
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
        return BaseView.success()

    # 删除练习试卷
    def delInfo(request):
        models.PracticePapers.objects.filter(
            id=request.POST.get('id')
        ).update(isActive=False)
        return BaseView.success()

    # 基于学生错题自动生成专项练习试卷
    def generateWrongPracticePaper(request):
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
            from comm.CommUtils import DateUtil
            title = f"错题专项-{DateUtil.getNowDateTime()}"
            paper = models.PracticePapers.objects.create(
                title=title,
                description='系统基于错题自动生成的专项练习',
                type='fixed',
                difficulty='medium',
                duration=30,
                totalScore=len(wrong_list),
                project=project,
                teacher=models.Users.objects.get(id=studentId),  # 使用当前用户占位
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


'''
学生练习记录处理
'''


class StudentPracticeView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'logs':
            return StudentPracticeView.getPracticeLogs(request)
        elif module == 'answers':
            return StudentPracticeView.getPracticeAnswers(request)
        elif module == 'export':
            return StudentPracticeView.exportPracticeLogs(request)
        elif module == 'export_answers':
            return StudentPracticeView.exportPracticeAnswers(request)
        elif module == 'pending':
            return StudentPracticeView.getPendingAnswers(request)
        elif module == 'logs_admin':
            return StudentPracticeView.getPracticeLogsAdmin(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'start':
            return StudentPracticeView.startPractice(request)
        elif module == 'submit':
            return StudentPracticeView.submitPractice(request)
        elif module == 'save':
            return StudentPracticeView.saveProgress(request)
        elif module == 'review':
            return StudentPracticeView.reviewAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    # 开始练习
    def startPractice(request):
        studentId = cache.get(request.POST.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        paperId = request.POST.get('paperId')
        if not paperId:
            return BaseView.error('试卷ID不能为空')

        # 检查是否已有进行中的练习
        existingLog = models.StudentPracticeLogs.objects.filter(
            student__id=studentId,
            paper__id=paperId,
            status='in_progress'
        ).first()

        if existingLog:
            return BaseView.successData({
                'logId': existingLog.id,
                'message': '继续现有练习'
            })

        # 验证试卷是否存在且启用
        try:
            paper = models.PracticePapers.objects.get(id=paperId)
            if not paper.isActive:
                return BaseView.error('该练习试卷已禁用，无法开始')
        except models.PracticePapers.DoesNotExist:
            return BaseView.error('练习试卷不存在')

        # 创建新的练习��录
        practiceLog = models.StudentPracticeLogs.objects.create(
            student=models.Users.objects.get(id=studentId),
            paper=models.PracticePapers.objects.get(id=paperId),
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        return BaseView.successData({
            'logId': practiceLog.id,
            'message': '开始新练习'
        })

    # 保存练习进度
    def saveProgress(request):
        logId = request.POST.get('logId')
        practiseId = request.POST.get('practiseId')
        studentAnswer = request.POST.get('studentAnswer')

        if not logId or not practiseId:
            return BaseView.error('参数不完整')

        # 检查是否已有答题记录
        existingAnswer = models.StudentPracticeAnswers.objects.filter(
            practiceLog__id=logId,
            practise__id=practiseId
        ).first()

        if existingAnswer:
            # 更新现有记录
            existingAnswer.studentAnswer = studentAnswer
            existingAnswer.answerTime = DateUtil.getNowDateTime()
            existingAnswer.save()
        else:
            # 创建新记录
            models.StudentPracticeAnswers.objects.create(
                practiceLog=models.StudentPracticeLogs.objects.get(id=logId),
                practise=models.Practises.objects.get(id=practiseId),
                studentAnswer=studentAnswer,
                answerTime=DateUtil.getNowDateTime()
            )

        return BaseView.success()

    # 提交练习
    def submitPractice(request):
        logId = request.POST.get('logId')
        if not logId:
            return BaseView.error('练习记录ID不能为空')

        practiceLog = models.StudentPracticeLogs.objects.filter(id=logId).first()
        if not practiceLog:
            return BaseView.error('练习记录不存在')

        # 获取所有答题记录
        answers = models.StudentPracticeAnswers.objects.filter(practiceLog=practiceLog).select_related('practise')

        # 计算得分和正确率
        totalScore = 0
        correctCount = 0

        # 初始化AI工具
        try:
            from comm.AIUtils import AIUtils
            ai_utils = AIUtils()
            use_ai_scoring = True
        except Exception as e:
            print(f"AI工具初始化失败，使用传统评分: {str(e)}")
            use_ai_scoring = False

        for answer in answers:
            practise = answer.practise
            studentAnswer = answer.studentAnswer
            correctAnswer = practise.answer

            # 使用AI评分或传统评分
            if use_ai_scoring and practise.type in [1, 3]:  # 填空题和编程题使用AI评分
                try:
                    # 获取题目分值
                    max_score = practise.score if hasattr(practise, 'score') else 1.0

                    # AI评分
                    ai_result = ai_utils.ai_score_answer(
                        question_content=practise.name,
                        correct_answer=correctAnswer,
                        student_answer=studentAnswer,
                        question_type=practise.type,
                        max_score=max_score
                    )

                    answer.isCorrect = ai_result['is_correct']
                    answer.score = ai_result['score']
                    # 保存AI细节
                    answer.aiConfidence = ai_result.get('confidence')
                    answer.aiFeedback = ai_result.get('feedback')
                    answer.aiAnalysis = ai_result.get('analysis')
                    answer.aiModel = ai_result.get('model')
                    # 保存AI细节
                    answer.aiConfidence = ai_result.get('confidence')
                    answer.aiFeedback = ai_result.get('feedback')
                    answer.aiAnalysis = ai_result.get('analysis')
                    answer.aiModel = ai_result.get('model')

                    # 保存AI分析结果到题目分析字段
                    if not practise.analyse or practise.analyse.strip() == '':
                        practise.analyse = f"AI评分反馈: {ai_result['feedback']}\nAI分析: {ai_result['analysis']}"
                        practise.save()

                except Exception as e:
                    print(f"AI评分失败，使用传统评分: {str(e)}")
                    # 如果AI评分失败，使用传统评分
                    if practise.type == 0:  # 选择题
                        isCorrect = str(studentAnswer) == str(correctAnswer)
                    else:  # 其他题型，简单字符串比较
                        isCorrect = str(studentAnswer).strip().lower() == str(correctAnswer).strip().lower()

                    answer.isCorrect = isCorrect
                    if isCorrect:
                        answer.score = practise.score if hasattr(practise, 'score') else 1.0
                    else:
                        answer.score = 0
            else:
                # 传统评分方法
                if practise.type == 0:  # 选择题
                    isCorrect = str(studentAnswer) == str(correctAnswer)
                else:  # 其他题型，简单字符串比较
                    isCorrect = str(studentAnswer).strip().lower() == str(correctAnswer).strip().lower()

                answer.isCorrect = isCorrect
                if isCorrect:
                    answer.score = practise.score if hasattr(practise, 'score') else 1.0
                else:
                    answer.score = 0

            answer.save()

            if answer.isCorrect:
                correctCount += 1
            totalScore += answer.score

        # 计算正确率
        accuracy = (correctCount / answers.count() * 100) if answers.count() > 0 else 0

        # 计算用时
        startTime = DateUtil.parseDateTime(practiceLog.startTime)
        endTime = DateUtil.getNowDateTime()
        usedTime = int((endTime - startTime).total_seconds() / 60)

        # 更新练习记录
        practiceLog.endTime = DateUtil.getNowDateTime()
        practiceLog.score = totalScore
        practiceLog.accuracy = accuracy
        practiceLog.usedTime = usedTime
        practiceLog.status = 'completed'
        practiceLog.save()

        return BaseView.successData({
            'score': totalScore,
            'accuracy': accuracy,
            'usedTime': usedTime,
            'correctCount': correctCount,
            'totalCount': answers.count()
        })

    # 获取练习记录
    def getPracticeLogs(request):
        studentId = cache.get(request.GET.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        # 优化查询：使用select_related避免N+1问题
        logs = models.StudentPracticeLogs.objects.filter(
            student__id=studentId
        ).select_related(
            'paper',
            'paper__project'
        ).order_by('-startTime')

        resl = []
        for log in logs:
            resl.append({
                'id': log.id,
                'paperId': log.paper.id if log.paper else None,
                'paperTitle': log.paper.title,
                'projectName': log.paper.project.name,
                'startTime': log.startTime,
                'endTime': log.endTime,
                'score': log.score,
                'accuracy': log.accuracy,
                'usedTime': log.usedTime,
                'status': log.status
            })

        return BaseView.successData(resl)

    # 管理端/教师端：按学生ID获取练习记录
    def getPracticeLogsAdmin(request):
        studentId = request.GET.get('studentId')
        if not studentId:
            return BaseView.error('学生ID不能为空')
        # 优化查询：使用select_related避免N+1问题
        logs = models.StudentPracticeLogs.objects.filter(
            student__id=studentId
        ).select_related(
            'paper',
            'paper__project'
        ).order_by('-startTime')
        resl = []
        for log in logs:
            resl.append({
                'id': log.id,
                'paperId': log.paper.id if log.paper else None,
                'paperTitle': log.paper.title if log.paper else '',
                'projectName': log.paper.project.name if (log.paper and log.paper.project) else '',
                'startTime': log.startTime,
                'endTime': log.endTime,
                'score': log.score,
                'accuracy': log.accuracy,
                'usedTime': log.usedTime,
                'status': log.status
            })
        return BaseView.successData(resl)

    # 导出当前学生的练习记录 CSV
    def exportPracticeLogs(request):
        try:
            studentId = cache.get(request.GET.get('token'))
            if not studentId:
                return BaseView.error('用户未登录')

            logs = models.StudentPracticeLogs.objects.filter(
                student__id=studentId).select_related(
                'paper', 'paper__project').order_by('-startTime')
            from django.http import HttpResponse
            import csv
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['paperTitle', 'projectName', 'startTime', 'endTime',
                            'score', 'accuracy', 'usedTime', 'status'])
            for log in logs:
                writer.writerow([
                    log.paper.title if log.paper else '',
                    log.paper.project.name if log.paper and log.paper.project else '',
                    log.startTime, log.endTime, log.score, log.accuracy, log.usedTime, log.status
                ])
            resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename=practice_logs.csv'
            return resp
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    # 导出指定练习的答题明细 CSV
    def exportPracticeAnswers(request):
        try:
            logId = request.GET.get('logId')
            if not logId:
                return BaseView.error('练习记录ID不能为空')
            answers = models.StudentPracticeAnswers.objects.filter(practiceLog__id=logId).order_by('practise__id')
            from django.http import HttpResponse
            import csv
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['questionId', 'questionContent', 'questionType', 'studentAnswer',
                            'correctAnswer', 'isCorrect', 'score', 'answerTime'])
            for a in answers:
                writer.writerow([
                    a.practise.id if a.practise else '',
                    a.practise.name if a.practise else '',
                    a.practise.type if a.practise else '',
                    a.studentAnswer, a.practise.answer if a.practise else '', a.isCorrect, a.score, a.answerTime
                ])
            resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename=practice_answers.csv'
            return resp
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    # 获取练习答题记录
    def getPracticeAnswers(request):
        logId = request.GET.get('logId')
        if not logId:
            return BaseView.error('练习记录ID不能为空')

        answers = models.StudentPracticeAnswers.objects.filter(
            practiceLog__id=logId
        ).order_by('practise__id')

        threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.6'))
        resl = []
        for answer in answers:
            practise = answer.practise
            needsReview = False
            if practise.type in [1, 3]:
                c = getattr(answer, 'aiConfidence', None)
                needsReview = (c is None) or (c < threshold)
            answerData = {
                'id': answer.id,
                'questionContent': practise.name,
                'questionType': practise.type,
                'studentAnswer': answer.studentAnswer,
                'correctAnswer': practise.answer,
                'isCorrect': answer.isCorrect,
                'score': answer.score,
                'analyse': practise.analyse,
                'answerTime': answer.answerTime,
                'aiConfidence': getattr(answer, 'aiConfidence', None),
                'aiFeedback': getattr(answer, 'aiFeedback', None),
                'aiAnalysis': getattr(answer, 'aiAnalysis', None),
                'aiModel': getattr(answer, 'aiModel', None),
                'needsReview': needsReview
            }

            # 如果是选择题，获取选项
            if practise.type == 0:
                options = models.Options.objects.filter(practise=practise)
                answerData['options'] = [opt.name for opt in options]

            resl.append(answerData)

        return BaseView.successData(resl)

    # 获取需要人工覆核的练习答题
    def getPendingAnswers(request):
        logId = request.GET.get('logId')
        if not logId:
            return BaseView.error('练习记录ID不能为空')
        threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.6'))
        answers = models.StudentPracticeAnswers.objects.filter(
            practiceLog__id=logId,
            practise__type__in=[1, 3]
        ).select_related('practise')
        resl = []
        for a in answers:
            c = getattr(a, 'aiConfidence', None)
            if (c is None) or (c < threshold):
                resl.append({
                    'id': a.id,
                    'questionContent': a.practise.name,
                    'questionType': a.practise.type,
                    'studentAnswer': a.studentAnswer,
                    'correctAnswer': a.practise.answer,
                    'aiConfidence': c,
                    'aiFeedback': getattr(a, 'aiFeedback', None),
                    'aiAnalysis': getattr(a, 'aiAnalysis', None),
                    'aiModel': getattr(a, 'aiModel', None)
                })
        return BaseView.successData(resl)

    # 教师人工覆核（练习）
    def reviewAnswer(request):
        try:
            ans_id = request.POST.get('id')
            score = request.POST.get('score')
            is_correct = request.POST.get('isCorrect')
            feedback = request.POST.get('feedback')
            analysis = request.POST.get('analysis')
            if not ans_id:
                return BaseView.error('答案ID不能为空')
            answer = models.StudentPracticeAnswers.objects.filter(id=ans_id).first()
            if not answer:
                return BaseView.error('答案记录不存在')
            if score is not None:
                try:
                    answer.score = float(score)
                except Exception:
                    return BaseView.error('分数格式错误')
            if is_correct is not None:
                answer.isCorrect = str(is_correct).lower() in ['true', '1', 'yes']
            if feedback is not None:
                setattr(answer, 'aiFeedback', feedback)
            if analysis is not None:
                setattr(answer, 'aiAnalysis', analysis)
            answer.save()
            return BaseView.success()
        except Exception as e:
            return BaseView.error(f'覆核失败: {str(e)}')


class TasksView(BaseView):
    """任务管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return TasksView.getInfo(request)
        elif module in ['getPageInfos', 'page']:
            return TasksView.getPageInfos(request)
        elif module == 'student':
            return TasksView.getStudentTasks(request)
        elif module in ['getTaskQuestions', 'questions']:
            return TasksView.getTaskQuestions(request)
        elif module in ['getTaskLogs', 'logs']:
            return TasksView.getTaskLogs(request)
        elif module == 'loginfo':
            return TasksView.getTaskLogInfo(request)
        elif module == 'answers':
            return TasksView.getTaskAnswers(request)
        elif module == 'pending':
            return TasksView.getPendingAnswers(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module in ['addInfo', 'add']:
            return TasksView.addInfo(request)
        elif module in ['updInfo', 'upd']:
            return TasksView.updInfo(request)
        elif module in ['delInfo', 'del']:
            return TasksView.delInfo(request)
        elif module in ['startTask', 'start']:
            return TasksView.startTask(request)
        elif module in ['saveTaskProgress', 'save']:
            return TasksView.saveTaskProgress(request)
        elif module in ['submitTask', 'submit']:
            return TasksView.submitTask(request)
        elif module == 'review':
            return TasksView.reviewAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取任务信息
    def getInfo(request):
        taskId = request.GET.get('id')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        task = models.Tasks.objects.filter(id=taskId).first()
        if not task:
            return BaseView.error('任务不存在')

        resl = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'type': task.type,
            'deadline': task.deadline,
            'score': task.score,
            'projectId': task.project.id,
            'projectName': task.project.name,
            'gradeId': task.grade.id,
            'gradeName': task.grade.name,
            'teacherId': task.teacher.id,
            'teacherName': task.teacher.name,
            'createTime': task.createTime,
            'isActive': task.isActive
        }

        return BaseView.successData(resl)

    # 分页获取任务列表
    def getPageInfos(request):
        pageIndex = int(request.GET.get('pageIndex', 1))
        pageSize = min(int(request.GET.get('pageSize', 10)), 100)  # 限制最大每页100条
        title = request.GET.get('title', '')
        type = request.GET.get('type', '')
        projectId = request.GET.get('projectId', '')
        gradeId = request.GET.get('gradeId', '')

        query = models.Tasks.objects.all()

        if title:
            query = query.filter(title__icontains=title)
        if type:
            query = query.filter(type=type)
        if projectId:
            query = query.filter(project__id=projectId)
        if gradeId:
            query = query.filter(grade__id=gradeId)

        query = query.order_by('-createTime')

        paginator = Paginator(query, pageSize)
        page = paginator.get_page(pageIndex)

        resl = []
        for task in page:
            resl.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'type': task.type,
                'deadline': task.deadline,
                'score': task.score,
                'projectName': task.project.name,
                'gradeName': task.grade.name,
                'teacherName': task.teacher.name,
                'createTime': task.createTime,
                'isActive': task.isActive
            })

        return BaseView.successData({
            'list': resl,
            'total': paginator.count,
            'pageIndex': pageIndex,
            'pageSize': pageSize,
            'totalPages': paginator.num_pages
        })

    # 获取学生可做的任务
    def getStudentTasks(request):
        studentId = cache.get(request.GET.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        # 获取学生信息
        student = models.Students.objects.filter(user__id=studentId).select_related('user', 'grade', 'college').first()
        if not student:
            return BaseView.error('学生信息不存在')

        # 使用select_related优化外键查询，避免N+1问题
        tasks = models.Tasks.objects.filter(
            grade=student.grade,
            isActive=True
        ).select_related('project', 'teacher').order_by('-createTime')

        # 批量获取任务日志，避免循环中查询
        task_ids = [task.id for task in tasks]
        existing_logs = {}
        if task_ids:
            logs = models.StudentTaskLogs.objects.filter(
                student__id=studentId,
                task_id__in=task_ids
            ).select_related('task')
            for log in logs:
                existing_logs[log.task_id] = log

        resl = []
        for task in tasks:
            existingLog = existing_logs.get(task.id)

            taskData = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'type': task.type,
                'deadline': task.deadline,
                'score': task.score,
                'projectName': task.project.name,
                'teacherName': task.teacher.name,
                'createTime': task.createTime,
                'status': 'not_started' if not existingLog else existingLog.status,
                'logId': existingLog.id if existingLog else None,
                'startTime': existingLog.startTime if existingLog else None,
                'endTime': existingLog.endTime if existingLog else None,
                'score': existingLog.score if existingLog else None,
                'accuracy': existingLog.accuracy if existingLog else None
            }

            resl.append(taskData)

        return BaseView.successData(resl)

    # 获取任务题目
    def getTaskQuestions(request):
        taskId = request.GET.get('taskId')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        taskQuestions = models.TaskQuestions.objects.filter(
            task__id=taskId
        ).order_by('questionOrder')

        resl = []
        for tq in taskQuestions:
            practise = tq.practise
            questionData = {
                'id': practise.id,
                'name': practise.name,
                'type': practise.type,
                'score': tq.score,
                'questionOrder': tq.questionOrder
            }

            # 如果是选择题，获取选项
            if practise.type == 0:
                options = models.Options.objects.filter(practise=practise)
                questionData['options'] = [opt.name for opt in options]

            resl.append(questionData)

        return BaseView.successData(resl)

    # 开始任务
    def startTask(request):
        studentId = cache.get(request.POST.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        taskId = request.POST.get('taskId')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        # 检查任务是否存在
        task = models.Tasks.objects.filter(id=taskId).first()
        if not task:
            return BaseView.error('任务不存在')

        # 检查任务是否启用
        if not task.isActive:
            return BaseView.error('该任务尚未发布或已禁用')

        # 检查任务是否已过期
        current_time = DateUtil.getNowDateTime()
        if task.deadline and current_time > task.deadline:
            return BaseView.error('任务已截止，无法开始')

        # 检查学生是否已经做过这个任务
        existingLog = models.StudentTaskLogs.objects.filter(
            student__id=studentId,
            task=task
        ).first()

        if existingLog:
            if existingLog.status == 'completed':
                return BaseView.error('该任务已完成，不能重复开始')
            # 如果进行中，返回现有记录
            return BaseView.successData({
                'logId': existingLog.id,
                'message': '继续现有任务'
            })

        # 创建新的任务记录
        taskLog = models.StudentTaskLogs.objects.create(
            student_id=studentId,
            task=task,
            startTime=DateUtil.getNowDateTime(),
            status='in_progress'
        )

        return BaseView.successData({
            'logId': taskLog.id,
            'message': '任务开始成功'
        })

    # 保存任务进度
    def saveTaskProgress(request):
        logId = request.POST.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')

        # 获取任务记录
        taskLog = models.StudentTaskLogs.objects.filter(id=logId).first()
        if not taskLog:
            return BaseView.error('任务记录不存在')

        # 保存答案
        answers = request.POST.getlist('answers[]') or request.POST.getlist('answers')
        practiseIds = request.POST.getlist('practiseIds[]') or request.POST.getlist('practiseIds')

        if len(answers) != len(practiseIds):
            return BaseView.error('答案和题目数量不匹配')

        for i in range(len(answers)):
            practiseId = practiseIds[i]
            answer = answers[i]

            # 检查是否已有答案记录
            answerRecord = models.StudentTaskAnswers.objects.filter(
                taskLog=taskLog,
                practise_id=practiseId
            ).first()

            if answerRecord:
                # 更新现有答案
                answerRecord.studentAnswer = answer
                answerRecord.answerTime = DateUtil.getNowDateTime()
                answerRecord.save()
            else:
                # 创建新的答案记录
                models.StudentTaskAnswers.objects.create(
                    taskLog=taskLog,
                    practise_id=practiseId,
                    studentAnswer=answer,
                    answerTime=DateUtil.getNowDateTime()
                )

        return BaseView.successData('进度保存成功')

    # 提交任务
    def submitTask(request):
        logId = request.POST.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')

        # 获取任务记录
        taskLog = models.StudentTaskLogs.objects.filter(id=logId).first()
        if not taskLog:
            return BaseView.error('任务记录不存在')

        # 检查任务是否已截止
        task = taskLog.task
        current_time = DateUtil.getNowDateTime()
        if task.deadline and current_time > task.deadline:
            return BaseView.error('任务已截止，无法提交')

        if taskLog.status == 'completed':
            return BaseView.error('任务已完成，不能重复提交')

        # 获取所有答案记录
        answers = models.StudentTaskAnswers.objects.filter(taskLog=taskLog)

        if not answers.exists():
            return BaseView.error('没有答题记录')

        # 计算得分和正确率
        totalScore = 0
        correctCount = 0

        # 初始化AI工具
        try:
            from comm.AIUtils import AIUtils
            ai_utils = AIUtils()
            use_ai_scoring = True
        except Exception as e:
            print(f"AI工具初始化失败，使用传统评分: {str(e)}")
            use_ai_scoring = False

        for answer in answers:
            practise = answer.practise

            # 使用AI评分或传统评分
            if use_ai_scoring and practise.type in [1, 3]:  # 填空题和编程题使用AI评分
                try:
                    # 获取该题目在任务中的分值
                    taskQuestion = models.TaskQuestions.objects.filter(
                        task=taskLog.task,
                        practise=practise
                    ).first()
                    max_score = taskQuestion.score if taskQuestion else 1.0

                    # AI评分
                    ai_result = ai_utils.ai_score_answer(
                        question_content=practise.name,
                        correct_answer=practise.answer,
                        student_answer=answer.studentAnswer,
                        question_type=practise.type,
                        max_score=max_score
                    )

                    answer.isCorrect = ai_result['is_correct']
                    answer.score = ai_result['score']

                    # 保存AI分析结果到题目分析字段
                    if not practise.analyse or practise.analyse.strip() == '':
                        practise.analyse = f"AI评分反馈: {ai_result['feedback']}\nAI分析: {ai_result['analysis']}"
                        practise.save()

                except Exception as e:
                    print(f"AI评分失败，使用传统评分: {str(e)}")
                    # 如果AI评分失败，使用传统评分
                    if practise.type == 0:  # 选择题
                        isCorrect = str(answer.studentAnswer) == str(practise.answer)
                    else:  # 其他题型，简单字符串比较
                        isCorrect = str(answer.studentAnswer).strip().lower() == str(practise.answer).strip().lower()

                    answer.isCorrect = isCorrect
                    if isCorrect:
                        taskQuestion = models.TaskQuestions.objects.filter(
                            task=taskLog.task,
                            practise=practise
                        ).first()
                        answer.score = taskQuestion.score if taskQuestion else 1.0
                    else:
                        answer.score = 0
            else:
                # 传统评分方法
                if practise.type == 0:  # 选择题
                    isCorrect = str(answer.studentAnswer) == str(practise.answer)
                else:  # 其他题型，简单字符串比较
                    isCorrect = str(answer.studentAnswer).strip().lower() == str(practise.answer).strip().lower()

                answer.isCorrect = isCorrect
                if isCorrect:
                    # 获取该题目在任务中的分值
                    taskQuestion = models.TaskQuestions.objects.filter(
                        task=taskLog.task,
                        practise=practise
                    ).first()
                    answer.score = taskQuestion.score if taskQuestion else 1.0
                else:
                    answer.score = 0

            answer.save()

            if answer.isCorrect:
                correctCount += 1
            totalScore += answer.score

        # 计算正确率
        accuracy = (correctCount / answers.count() * 100) if answers.count() > 0 else 0

        # 计算用时
        startTime = DateUtil.parseDateTime(taskLog.startTime)
        endTime = DateUtil.getNowDateTime()
        usedTime = int((endTime - startTime).total_seconds() / 60)

        # 更新任务记录
        taskLog.endTime = DateUtil.getNowDateTime()
        taskLog.score = totalScore
        taskLog.accuracy = accuracy
        taskLog.usedTime = usedTime
        taskLog.status = 'completed'
        taskLog.save()

        return BaseView.successData({
            'score': totalScore,
            'accuracy': accuracy,
            'usedTime': usedTime,
            'correctCount': correctCount,
            'totalCount': answers.count()
        })

    # 获取任务记录
    """
    API获取学生的任务记录列表

    ---
    tags:
      - 任务管理
    summary:
      获取任务记录列表
    description:
      获取当前登录学生的所有任务记录，包括任务状态、分数、准确���等信息
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: 用户认证令牌
    responses:
      200:
        description: 成功返回任务记录列表
        schema:
          type: object
          properties:
            code:
              type: integer
              example: 0
            msg:
              type: string
              example: "处理成功"
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: 任务记录ID
                  taskTitle:
                    type: string
                    description: 任务标题
                  projectName:
                    type: string
                    description: 科目名称
                  startTime:
                    type: string
                    description: 开始时间
                  endTime:
                    type: string
                    description: 结束时间
                  score:
                    type: number
                    description: 得分
                  accuracy:
                    type: number
                    description: 准确率
                  usedTime:
                    type: integer
                    description: 用时（秒）
                  status:
                    type: integer
                    description: 状态（0-进行中，2-已完成）
      401:
        description: 用户未登录
    """
    def getTaskLogs(request):
        studentId = cache.get(request.GET.get('token'))
        if not studentId:
            return BaseView.error('用户未登录')

        logs = models.StudentTaskLogs.objects.filter(
            student__id=studentId
        ).select_related('task', 'task__project').order_by('-startTime')

        resl = []
        for log in logs:
            resl.append({
                'id': log.id,
                'taskTitle': log.task.title,
                'projectName': log.task.project.name,
                'startTime': log.startTime,
                'endTime': log.endTime,
                'score': log.score,
                'accuracy': log.accuracy,
                'usedTime': log.usedTime,
                'status': log.status
            })

        return BaseView.successData(resl)

    # 获取任务日志详细信息
    def getTaskLogInfo(request):
        logId = request.GET.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')

        taskLog = models.StudentTaskLogs.objects.filter(id=logId).first()
        if not taskLog:
            return BaseView.error('任务记录不存在')

        resl = {
            'id': taskLog.id,
            'taskId': taskLog.task.id,
            'taskTitle': taskLog.task.title,
            'startTime': taskLog.startTime,
            'endTime': taskLog.endTime,
            'score': taskLog.score,
            'accuracy': taskLog.accuracy,
            'usedTime': taskLog.usedTime,
            'status': taskLog.status,
            'correctCount': 0,  # 将在getTaskAnswers中计算
            'totalCount': 0      # 将在getTaskAnswers中计算
        }

        # 计算正确题目数和总题目数
        answers = models.StudentTaskAnswers.objects.filter(taskLog=taskLog)
        resl['correctCount'] = answers.filter(isCorrect=True).count()
        resl['totalCount'] = answers.count()

        return BaseView.successData(resl)

    # 获取任务答题记录
    def getTaskAnswers(request):
        logId = request.GET.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')

        answers = models.StudentTaskAnswers.objects.filter(
            taskLog__id=logId
        ).order_by('practise__id')

        threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.6'))
        resl = []
        for answer in answers:
            practise = answer.practise
            needsReview = False
            if practise.type in [1, 3]:
                c = getattr(answer, 'aiConfidence', None)
                needsReview = (c is None) or (c < threshold)
            answerData = {
                'id': answer.id,
                'questionContent': practise.name,
                'questionType': practise.type,
                'studentAnswer': answer.studentAnswer,
                'correctAnswer': practise.answer,
                'isCorrect': answer.isCorrect,
                'score': answer.score,
                'analyse': practise.analyse,
                'answerTime': answer.answerTime,
                'aiConfidence': getattr(answer, 'aiConfidence', None),
                'aiFeedback': getattr(answer, 'aiFeedback', None),
                'aiAnalysis': getattr(answer, 'aiAnalysis', None),
                'aiModel': getattr(answer, 'aiModel', None),
                'needsReview': needsReview
            }

            # 如果是选择题，获取选项
            if practise.type == 0:
                options = models.Options.objects.filter(practise=practise)
                answerData['options'] = [opt.name for opt in options]

            resl.append(answerData)

        return BaseView.successData(resl)

    # 获取需要人工覆核的任务答题
    def getPendingAnswers(request):
        logId = request.GET.get('logId')
        if not logId:
            return BaseView.error('任务记录ID不能为空')
        threshold = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.6'))
        answers = models.StudentTaskAnswers.objects.filter(
            taskLog__id=logId,
            practise__type__in=[1, 3]
        ).select_related('practise')
        resl = []
        for a in answers:
            c = getattr(a, 'aiConfidence', None)
            if (c is None) or (c < threshold):
                resl.append({
                    'id': a.id,
                    'questionContent': a.practise.name,
                    'questionType': a.practise.type,
                    'studentAnswer': a.studentAnswer,
                    'correctAnswer': a.practise.answer,
                    'aiConfidence': c,
                    'aiFeedback': getattr(a, 'aiFeedback', None),
                    'aiAnalysis': getattr(a, 'aiAnalysis', None),
                    'aiModel': getattr(a, 'aiModel', None)
                })
        return BaseView.successData(resl)

    # 教师人工覆核（任务）
    def reviewAnswer(request):
        try:
            ans_id = request.POST.get('id')
            score = request.POST.get('score')
            is_correct = request.POST.get('isCorrect')
            feedback = request.POST.get('feedback')
            analysis = request.POST.get('analysis')
            if not ans_id:
                return BaseView.error('答案ID不能为空')
            answer = models.StudentTaskAnswers.objects.filter(id=ans_id).first()
            if not answer:
                return BaseView.error('答案记录不存在')
            if score is not None:
                try:
                    answer.score = float(score)
                except Exception:
                    return BaseView.error('分数格式错误')
            if is_correct is not None:
                answer.isCorrect = str(is_correct).lower() in ['true', '1', 'yes']
            if feedback is not None:
                setattr(answer, 'aiFeedback', feedback)
            if analysis is not None:
                setattr(answer, 'aiAnalysis', analysis)
            answer.save()
            return BaseView.success()
        except Exception as e:
            return BaseView.error(f'覆核失败: {str(e)}')

    # 添加任务
    def addInfo(request):
        title = request.POST.get('title')
        description = request.POST.get('description')
        type = request.POST.get('type')
        deadline = request.POST.get('deadline')
        score = request.POST.get('score')
        projectId = request.POST.get('projectId')
        gradeId = request.POST.get('gradeId')
        teacherId = request.POST.get('teacherId')

        if not all([title, type, deadline, score, projectId, gradeId, teacherId]):
            return BaseView.error('请填写完整信息')

        try:
            task = models.Tasks.objects.create(
                title=title,
                description=description or '',
                type=type,
                deadline=deadline,
                score=int(score),
                project_id=projectId,
                grade_id=gradeId,
                teacher_id=teacherId,
                createTime=DateUtil.getNowDateTime(),
                isActive=True
            )

            return BaseView.successData({
                'id': task.id,
                'message': '任务创建成功'
            })
        except Exception as e:
            return BaseView.error(f'创建失败: {str(e)}')

    # 更新任务
    def updInfo(request):
        taskId = request.POST.get('id')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        task = models.Tasks.objects.filter(id=taskId).first()
        if not task:
            return BaseView.error('任务不存在')

        # 更新字段
        if 'title' in request.POST:
            task.title = request.POST.get('title')
        if 'description' in request.POST:
            task.description = request.POST.get('description')
        if 'type' in request.POST:
            task.type = request.POST.get('type')
        if 'deadline' in request.POST:
            task.deadline = request.POST.get('deadline')
        if 'score' in request.POST:
            task.score = int(request.POST.get('score'))
        if 'projectId' in request.POST:
            task.project_id = request.POST.get('projectId')
        if 'gradeId' in request.POST:
            task.grade_id = request.POST.get('gradeId')
        if 'isActive' in request.POST:
            task.isActive = request.POST.get('isActive') == 'true'

        task.save()

        return BaseView.successData('更新成功')

    # 删除任务
    def delInfo(request):
        taskId = request.POST.get('id')
        if not taskId:
            return BaseView.error('任务ID不能为空')

        # 检查是否有学生正在做这个任务
        activeLogs = models.StudentTaskLogs.objects.filter(
            task__id=taskId,
            status='in_progress'
        )

        if activeLogs.exists():
            return BaseView.error('有学生正在做此任务，无法删除')

        # 删除任务
        task = models.Tasks.objects.filter(id=taskId).first()
        if task:
            task.delete()

        return BaseView.successData('删除成功')


class WrongQuestionsView(BaseView):
    """错题本管理视图"""

    def get(self, request, module, *args, **kwargs):
        if module == 'info':
            return WrongQuestionsView.getInfo(request)
        elif module == 'getPageInfos':
            return WrongQuestionsView.getPageInfos(request)
        elif module == 'getStudentWrongQuestions':
            return WrongQuestionsView.getStudentWrongQuestions(request)
        elif module == 'getWrongQuestionDetail':
            return WrongQuestionsView.getWrongQuestionDetail(request)
        elif module == 'getReviewHistory':
            return WrongQuestionsView.getReviewHistory(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'addWrongQuestion':
            return WrongQuestionsView.addWrongQuestion(request)
        elif module == 'markAsReviewed':
            return WrongQuestionsView.markAsReviewed(request)
        elif module == 'addReview':
            return WrongQuestionsView.addReview(request)
        elif module == 'deleteWrongQuestion':
            return WrongQuestionsView.deleteWrongQuestion(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def getInfo(request):
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
    def getPageInfos(request):
        """分页获取错题列表"""
        try:
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            student_id = request.GET.get('studentId')
            # 允许使用 token 自动识别学生ID，便于前端无需显式传 studentId
            if not student_id:
                token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
                if token:
                    from django.core.cache import cache as _cache
                    student_id = _cache.get(token)

            if not student_id:
                return BaseView.error('学生ID不能为空')

            # 优化查询：使用select_related避免N+1问题
            queryset = models.WrongQuestions.objects.filter(student_id=student_id).select_related(
                'practise',
                'practise__project'
            )

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

            # 复习状态筛选：reviewed / unreviewed
            review_status = request.GET.get('reviewStatus')
            if review_status == 'reviewed':
                queryset = queryset.filter(isReviewed=True)
            elif review_status == 'unreviewed':
                queryset = queryset.filter(isReviewed=False)

            # 时间范围筛选（基于字符串时间，格式为 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）
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
    def getStudentWrongQuestions(request):
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
    def getWrongQuestionDetail(request):
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
    def getReviewHistory(request):
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
    def addWrongQuestion(request):
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

            # 检查是否已存在相同错题
            existing = models.WrongQuestions.objects.filter(
                student_id=student_id,
                practise_id=practise_id,
                source=source,
                sourceId=source_id
            ).first()

            if existing:
                return BaseView.error('该错题已存在')

            # 创建错题记录
            wrong_question = models.WrongQuestions.objects.create(
                student_id=student_id,
                practise_id=practise_id,
                source=source,
                sourceId=source_id,
                wrongAnswer=wrong_answer,
                correctAnswer=correct_answer,
                analysis=analysis,
                createTime=DateUtil.getNowTime()
            )

            return BaseView.successData({'id': wrong_question.id})
        except Exception as e:
            return BaseView.error(f'添加错题失败: {str(e)}')

    @staticmethod
    def markAsReviewed(request):
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
    def addReview(request):
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
    def deleteWrongQuestion(request):
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


'''
管理员功能视图
'''


class AdminView(BaseView):

    def get(self, request, module, *args, **kwargs):
        if module == 'dashboard':
            return AdminView.getDashboard(request)
        elif module == 'dashboard_cards':
            return AdminView.getDashboardCards(request)
        elif module == 'users':
            return AdminView.getUsers(request)
        elif module == 'trends':
            return AdminView.getTrends(request)
        elif module == 'subjects':
            return AdminView.getSubjects(request)
        elif module == 'exams':
            return AdminView.getExams(request)
        elif module == 'questions':
            return AdminView.getQuestions(request)
        elif module == 'tasks':
            return AdminView.getTasks(request)
        elif module == 'messages':
            return AdminView.getMessages(request)
        elif module == 'message_readers':
            return AdminView.getMessageReaders(request)
        elif module == 'message_attachment':
            return AdminView.downloadMessageAttachment(request)
        elif module == 'logs':
            return AdminView.getLogs(request)
        elif module == 'statistics_exam':
            return AdminView.getExamStatistics(request)
        elif module == 'statistics_student':
            return AdminView.getStudentStatistics(request)
        elif module == 'statistics_class':
            return AdminView.getClassStatistics(request)
        elif module == 'statistics_subject':
            return AdminView.getSubjectStatistics(request)
        elif module == 'export_students':
            return AdminView.exportStudents(request)
        elif module == 'export_teachers':
            return AdminView.exportTeachers(request)
        elif module == 'export_exam_results':
            return AdminView.exportExamResults(request)
        elif module == 'export_practice_results':
            return AdminView.exportPracticeResults(request)
        elif module == 'students_template':
            return AdminView.downloadStudentsTemplate(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'users':
            return AdminView.manageUsers(request)
        elif module == 'subjects':
            return AdminView.manageSubjects(request)
        elif module == 'exams':
            return AdminView.manageExams(request)
        elif module == 'questions':
            return AdminView.manageQuestions(request)
        elif module == 'questions_import':
            return AdminView.importQuestions(request)
        elif module == 'questions_export':
            return AdminView.exportQuestions(request)
        elif module == 'generateAIQuestions':
            return AdminView.generateAIQuestions(request)
        elif module == 'generateAIQuestionsBatch':
            return AdminView.generateAIQuestionsBatch(request)
        elif module == 'generate_ai_practice_paper':
            return AdminView.generateAIPracticePaper(request)
        elif module == 'generate_ai_practice_paper_counts':
            return AdminView.generateAIPracticePaperCounts(request)
        elif module == 'fill_all_subjects':
            return AdminView.fillAllSubjectsMinimum(request)
        elif module == 'tasks':
            return AdminView.manageTasks(request)
        elif module == 'messages':
            return AdminView.manageMessages(request)
        elif module == 'questions_template':
            return AdminView.questionsTemplate(request)
        elif module == 'students_import':
            return AdminView.importStudents(request)
        else:
            return BaseView.error('请求地址不存在')

    # 获取管理员仪表板数据
    @staticmethod
    def fillAllSubjectsMinimum(request):
        """为所有学科补齐基础题量：选择10、填空10、判断10、编程2。
        仅对缺口进行补齐，已满足的不再生成。
        可选参数：
        - topic: 生成主题，默认 "基础知识与核心概念"
        - difficulty: 难度，默认 medium
        - counts: 自定义各类型数量，例如 '0:10,1:10,2:10,3:2'
        """
        try:
            from comm.AIUtils import AIUtils
            # 解析数量映射
            counts_str = request.POST.get('counts', '0:10,1:10,2:10,3:2')
            default_counts = {0: 10, 1: 10, 2: 10, 3: 2}
            counts_map = dict(default_counts)
            try:
                pairs = [p for p in counts_str.split(',') if ':' in p]
                for p in pairs:
                    k, v = p.split(':', 1)
                    k_i, v_i = int(k), int(v)
                    if k_i in [0, 1, 2, 3] and v_i >= 0:
                        counts_map[k_i] = v_i
            except Exception:
                counts_map = default_counts
            topic = request.POST.get('topic', '基础知识与核心概念')
            difficulty = request.POST.get('difficulty', 'medium')
            ai = AIUtils()
            results = []
            total_created = 0

            # 批量统计所有学科的题目数量，避免N+1查询
            from django.db.models import Count, Q

            # 使用缓存获取项目列表
            cache_key = 'projects:all_ids'
            subject_ids = cache.get(cache_key)
            if subject_ids is None:
                subject_ids = list(models.Projects.objects.all().values_list('id', flat=True))
                cache.set(cache_key, subject_ids, 3600)  # 缓存1小时

            # 批量统计各类型题目数量
            type_counts = models.Practises.objects.filter(project_id__in=subject_ids).values(
                'project_id', 'type'
            ).annotate(count=Count('id'))

            # 构建学科题目数量映射 {project_id: {type: count}}
            subject_question_counts = {sid: {0: 0, 1: 0, 2: 0, 3: 0} for sid in subject_ids}
            for tc in type_counts:
                subject_question_counts[tc['project_id']][tc['type']] = tc['count']

            # 批量统计选择题（type=0）中选项数=4的题目数量
            valid_choice_counts = models.Options.objects.filter(
                practise__type=0, practise__project_id__in=subject_ids
            ).values('practise_id').annotate(c=Count('id')).filter(c=4)

            # 统计每个学科的有效选择题数量
            valid_choice_map = {sid: 0 for sid in subject_ids}
            for vc in valid_choice_counts:
                practise = models.Practises.objects.filter(id=vc['practise_id']).first()
                if practise:
                    valid_choice_map[practise.project_id] += 1

            # 遍历所有学科
            for subject in all_subjects:
                created_by_type = {0: 0, 1: 0, 2: 0, 3: 0}

                # 使用预计算的统计数据
                counts = subject_question_counts.get(subject.id, {0: 0, 1: 0, 2: 0, 3: 0})
                valid_choice = valid_choice_map.get(subject.id, 0)

                need_0 = max(0, int(counts_map.get(0, 10)) - valid_choice)
                need_1 = max(0, int(counts_map.get(1, 10)) - counts[1])
                need_2 = max(0, int(counts_map.get(2, 10)) - counts[2])
                need_3 = max(0, int(counts_map.get(3, 2)) - counts[3])
                need_map = {0: need_0, 1: need_1, 2: need_2, 3: need_3}

                # 逐类补齐
                for t, need in need_map.items():
                    if need <= 0:
                        continue
                    qs = ai.ai_generate_questions(subject=subject.name, topic=topic, difficulty=difficulty,
                                                  question_type=int(t), count=int(need)) or []
                    for q in qs:
                        try:
                            pr = models.Practises.objects.create(
                                name=q.get('content', ''),
                                type=int(t),
                                project=subject,
                                answer=q.get('answer', ''),
                                analyse=q.get('analysis', ''),
                                createTime=DateUtil.getNowDateTime()
                            )
                            if int(t) == 0 and q.get('options'):
                                for opt in q['options']:
                                    models.Options.objects.create(practise=pr, name=opt)
                            created_by_type[int(t)] += 1
                            total_created += 1
                        except Exception as ie:
                            print(f'学科{subject.id}生成失败(type={t}): {str(ie)}')
                # 汇总
                results.append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                    'createdByType': created_by_type
                })

            return BaseView.successData({
                'createdTotal': total_created,
                'list': results
            })
        except Exception as e:
            return BaseView.error(f'补齐失败: {str(e)}')

    def getDashboard(request):
        try:
            # 获取统计数据
            total_users = models.Users.objects.count()
            total_students = models.Users.objects.filter(type=2).count()
            total_teachers = models.Users.objects.filter(type=1).count()
            total_admins = models.Users.objects.filter(type=0).count()
            total_exams = models.Exams.objects.count()
            total_questions = models.Practises.objects.count()
            total_tasks = models.Tasks.objects.count()

            # 获取本月新增数据
            from datetime import datetime, timedelta
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            monthly_exams = models.Exams.objects.filter(
                createTime__gte=month_start.strftime('%Y-%m-%d %H:%M:%S')).count()
            monthly_questions = models.Practises.objects.filter(
                createTime__gte=month_start.strftime('%Y-%m-%d %H:%M:%S')).count()
            monthly_users = models.Users.objects.filter(
                createTime__gte=month_start.strftime('%Y-%m-%d %H:%M:%S')).count()

            # 用户活跃度：最近7天有练习/任务/考试记录的用户数
            week_ago = now - timedelta(days=7)
            # 按行为近似：有练习/任务/考试记录的去重人数
            active_practice = models.StudentPracticeLogs.objects.filter(
                startTime__gte=week_ago.strftime('%Y-%m-%d %H:%M:%S')).values_list('student_id', flat=True)
            active_task = models.StudentTaskLogs.objects.filter(
                startTime__gte=week_ago.strftime('%Y-%m-%d %H:%M:%S')).values_list('student_id', flat=True)
            active_exam = models.ExamLogs.objects.filter(createTime__gte=week_ago.strftime(
                '%Y-%m-%d %H:%M:%S')).values_list('student_id', flat=True)
            active_set = set(list(active_practice) + list(active_task) + list(active_exam))
            active_users = len(active_set)

            # AI相关统计
            # AI评分次数（有aiConfidence的记录）
            from django.db.models import Q
            ai_scoring_count = models.StudentPracticeAnswers.objects.filter(
                aiConfidence__isnull=False
            ).count()
            ai_scoring_count += models.StudentTaskAnswers.objects.filter(
                aiConfidence__isnull=False
            ).count()

            # 今日AI评分次数
            day_start_str = day_start.strftime('%Y-%m-%d %H:%M:%S')
            today_ai_scoring = models.StudentPracticeAnswers.objects.filter(
                aiConfidence__isnull=False,
                answerTime__gte=day_start_str
            ).count()
            today_ai_scoring += models.StudentTaskAnswers.objects.filter(
                aiConfidence__isnull=False,
                answerTime__gte=day_start_str
            ).count()

            # 基于错题生成练习次数（通过错题本相关功能）
            # 这里统计错题本中的记录数作为参考
            wrong_question_practices = models.WrongQuestions.objects.count()

            # 今日学习行为速览
            today_practices = models.StudentPracticeLogs.objects.filter(startTime__gte=day_start_str).count()
            today_tasks = models.StudentTaskLogs.objects.filter(startTime__gte=day_start_str).count()
            today_completed_practices = models.StudentPracticeLogs.objects.filter(
                status='completed', endTime__gte=day_start_str
            ).count()
            today_completed_tasks = models.StudentTaskLogs.objects.filter(
                status='completed', endTime__gte=day_start_str
            ).count()

            # 通过率（近7天）
            week_ago_str = week_ago.strftime('%Y-%m-%d %H:%M:%S')
            exams_7d = models.ExamLogs.objects.filter(status=2, createTime__gte=week_ago_str)
            practices_7d = models.StudentPracticeLogs.objects.filter(status='completed', startTime__gte=week_ago_str)
            import itertools
            exam_scores = [e['score'] for e in exams_7d.values('score')]
            practice_scores = [p['score'] for p in practices_7d.values('score')]
            all_scores = list(itertools.chain(exam_scores, practice_scores))
            total_completed = len(all_scores)
            passed = len([s for s in all_scores if (s or 0) >= 60])
            pass_rate = round(passed / total_completed * 100, 2) if total_completed > 0 else 0

            # 近7天趋势数据
            trends_7d = {
                'days': [],
                'practices': [],
                'tasks': []
            }
            for i in range(7):
                d = now - timedelta(days=6 - i)
                d0 = d.replace(hour=0, minute=0, second=0, microsecond=0)
                d1 = d0 + timedelta(days=1)
                d0s, d1s = d0.strftime('%Y-%m-%d %H:%M:%S'), d1.strftime('%Y-%m-%d %H:%M:%S')
                trends_7d['days'].append(d.strftime('%m-%d'))
                trends_7d['practices'].append(
                    models.StudentPracticeLogs.objects.filter(
                        status='completed', endTime__gte=d0s, endTime__lt=d1s).count()
                )
                trends_7d['tasks'].append(
                    models.StudentTaskLogs.objects.filter(status='completed', endTime__gte=d0s, endTime__lt=d1s).count()
                )

            return BaseView.successData({
                'overview': {
                    'total_users': total_users,
                    'total_students': total_students,
                    'total_teachers': total_teachers,
                    'total_admins': total_admins,
                    'total_exams': total_exams,
                    'total_questions': total_questions,
                    'total_tasks': total_tasks,
                    'ai_scoring_count': ai_scoring_count,
                    'wrong_question_practices': wrong_question_practices,
                    'pass_rate': pass_rate
                },
                'monthly': {
                    'new_exams': monthly_exams,
                    'new_questions': monthly_questions,
                    'new_users': monthly_users
                },
                'activity': {
                    'active_users': active_users
                },
                'today': {
                    'practices': today_practices,
                    'tasks': today_tasks,
                    'completed_practices': today_completed_practices,
                    'completed_tasks': today_completed_tasks,
                    'ai_scoring': today_ai_scoring
                },
                'trends_7d': trends_7d
            })
        except Exception as e:
            return BaseView.error(f'获取仪表板数据失败: {str(e)}')

    @staticmethod
    def getDashboardCards(request):
        """用于系统首页卡片：试卷总数、题目总数、用户活跃度、题目月数量"""
        try:
            from datetime import datetime
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta
            week_ago = now - timedelta(days=7)

            # 今日新增
            day_start_str = day_start.strftime('%Y-%m-%d %H:%M:%S')
            today_questions = models.Practises.objects.filter(createTime__gte=day_start_str).count()
            today_practices = models.StudentPracticeLogs.objects.filter(startTime__gte=day_start_str).count()
            today_exams = models.Exams.objects.filter(createTime__gte=day_start_str).count()

            # 近7天活跃用户（练习/任务/考试任一有记录）
            week_ago_str = week_ago.strftime('%Y-%m-%d %H:%M:%S')
            active_practice = models.StudentPracticeLogs.objects.filter(
                startTime__gte=week_ago_str).values_list('student_id', flat=True)
            active_task = models.StudentTaskLogs.objects.filter(
                startTime__gte=week_ago_str).values_list(
                'student_id', flat=True)
            active_exam = models.ExamLogs.objects.filter(
                createTime__gte=week_ago_str).values_list(
                'student_id', flat=True)
            active_users = len(set(list(active_practice) + list(active_task) + list(active_exam)))

            # 通过率与平均分（近7天，练习完成 + 考试结束）
            exams_7d = models.ExamLogs.objects.filter(status=2, createTime__gte=week_ago_str)
            practices_7d = models.StudentPracticeLogs.objects.filter(
                status='completed').filter(startTime__gte=week_ago_str)
            import itertools
            exam_scores = [e['score'] for e in exams_7d.values('score')]
            practice_scores = [p['score'] for p in practices_7d.values('score')]
            all_scores = list(itertools.chain(exam_scores, practice_scores))
            total_completed = len(all_scores)
            passed = len([s for s in all_scores if (s or 0) >= 60])
            avg_score = round(sum(all_scores) / total_completed, 2) if total_completed > 0 else 0
            pass_rate = round(passed / total_completed * 100, 2) if total_completed > 0 else 0

            # 待人工覆核数（AI低置信/无置信 + 考试人工审核未完成）
            import os as _os
            threshold = float(_os.getenv('AI_CONFIDENCE_THRESHOLD', '0.6'))
            from django.db.models import Q
            pending_practice = models.StudentPracticeAnswers.objects.filter(
                Q(aiConfidence__lt=threshold) | Q(aiConfidence__isnull=True)).count()
            pending_task = models.StudentTaskAnswers.objects.filter(
                Q(aiConfidence__lt=threshold) | Q(aiConfidence__isnull=True)).count()
            pending_exam = models.AnswerLogs.objects.filter(status=0, practise__type__in=[1, 3]).count()
            pending_reviews = pending_practice + pending_task + pending_exam

            return BaseView.successData({
                'todayNewQuestions': today_questions,
                'todayNewPractices': today_practices,
                'todayNewExams': today_exams,
                'activeUsers7d': active_users,
                'passRate7d': pass_rate,
                'avgScore7d': avg_score,
                'pendingReviews': pending_reviews
            })
        except Exception as e:
            return BaseView.error(f'获取首页卡片失败: {str(e)}')

    @staticmethod
    def getTrends(request):
        """首页趋势数据：题目月度新增、活跃用户趋势、练习/任务完成趋势（近30天）"""
        try:
            from datetime import datetime, timedelta
            now = datetime.now()
            start_30d = now - timedelta(days=29)
            start_30d_str = start_30d.strftime('%Y-%m-%d %H:%M:%S')
            # 题目月度新增（本年12个月）
            months = [f"{m:02d}" for m in range(1, 13)]
            questionsByMonth = []
            for m in months:
                month_start = datetime(now.year, int(m), 1)
                if int(m) == 12:
                    month_end = datetime(now.year + 1, 1, 1)
                else:
                    month_end = datetime(now.year, int(m) + 1, 1)
                cnt = models.Practises.objects.filter(
                    createTime__gte=month_start.strftime('%Y-%m-%d %H:%M:%S'),
                    createTime__lt=month_end.strftime('%Y-%m-%d %H:%M:%S')).count()
                questionsByMonth.append(cnt)
            # 近30天活跃用户：练习/任务/考试任一有记录的去重数
            activeDaily = []
            days = []
            for i in range(30):
                d = start_30d + timedelta(days=i)
                d0 = d.replace(hour=0, minute=0, second=0, microsecond=0)
                d1 = d0 + timedelta(days=1)
                d0s, d1s = d0.strftime('%Y-%m-%d %H:%M:%S'), d1.strftime('%Y-%m-%d %H:%M:%S')
                ap = models.StudentPracticeLogs.objects.filter(
                    startTime__gte=d0s, startTime__lt=d1s).values_list(
                    'student_id', flat=True)
                at = models.StudentTaskLogs.objects.filter(
                    startTime__gte=d0s, startTime__lt=d1s).values_list(
                    'student_id', flat=True)
                ae = models.ExamLogs.objects.filter(
                    createTime__gte=d0s, createTime__lt=d1s).values_list(
                    'student_id', flat=True)
                activeDaily.append(len(set(list(ap) + list(at) + list(ae))))
                days.append(d.strftime('%m-%d'))
            # 近30天练习/任务完成趋势
            practiceDoneDaily = []
            taskDoneDaily = []
            for i in range(30):
                d = start_30d + timedelta(days=i)
                d0 = d.replace(hour=0, minute=0, second=0, microsecond=0)
                d1 = d0 + timedelta(days=1)
                d0s, d1s = d0.strftime('%Y-%m-%d %H:%M:%S'), d1.strftime('%Y-%m-%d %H:%M:%S')
                pd = models.StudentPracticeLogs.objects.filter(
                    status='completed', endTime__gte=d0s, endTime__lt=d1s).count()
                td = models.StudentTaskLogs.objects.filter(
                    status='completed', endTime__gte=d0s, endTime__lt=d1s).count()
                practiceDoneDaily.append(pd)
                taskDoneDaily.append(td)
            return BaseView.successData({
                'months': months,
                'questionsByMonth': questionsByMonth,
                'days': days,
                'activeUsersDaily': activeDaily,
                'practiceDoneDaily': practiceDoneDaily,
                'taskDoneDaily': taskDoneDaily
            })
        except Exception as e:
            return BaseView.error(f'获取趋势数据失败: {str(e)}')

    # 用户管理
    @staticmethod
    def getUsers(request):
        try:
            user_type = request.GET.get('type', '')  # 0:管理员, 1:教师, 2:学生
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')

            users_query = models.Users.objects.all()

            if user_type:
                users_query = users_query.filter(type=int(user_type))

            if search:
                users_query = users_query.filter(
                    Q(userName__icontains=search) |
                    Q(name__icontains=search)
                )

            total = users_query.count()
            paginator = Paginator(users_query, size)
            users_page = paginator.get_page(page)

            users_data = []
            for user in users_page:
                user_data = {
                    'id': user.id,
                    'userName': user.userName,
                    'name': user.name,
                    'gender': user.gender,
                    'age': user.age,
                    'type': user.type,
                    'createTime': user.createTime.strftime('%Y-%m-%d %H:%M:%S') if user.createTime else '',
                    'lastLoginTime': user.lastLoginTime.strftime('%Y-%m-%d %H:%M:%S') if user.lastLoginTime else ''
                }

                # 根据用户类型添加额外信息
                if user.type == 1:  # 教师
                    teacher = models.Teachers.objects.filter(user=user).first()
                    if teacher:
                        user_data.update({
                            'phone': teacher.phone,
                            'record': teacher.record,
                            'job': teacher.job
                        })
                elif user.type == 2:  # 学生
                    student = models.Students.objects.filter(user=user).select_related('grade', 'college').first()
                    if student:
                        user_data.update({
                            'gradeId': student.grade.id if student.grade else None,
                            'gradeName': student.grade.name if student.grade else '',
                            'collegeId': student.college.id if student.college else None,
                            'collegeName': student.college.name if student.college else ''
                        })

                users_data.append(user_data)

            return BaseView.successData({
                'list': users_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取用户列表失败: {str(e)}')

    @staticmethod
    def manageUsers(request):
        try:
            action = request.POST.get('action')  # add, update, delete, disable

            if action == 'add':
                return AdminView.addUser(request)
            elif action == 'update':
                return AdminView.updateUser(request)
            elif action == 'delete':
                return AdminView.deleteUser(request)
            elif action == 'disable':
                return AdminView.disableUser(request)
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'用户操作失败: {str(e)}')

    @staticmethod
    def addUser(request):
        try:
            user_type = int(request.POST.get('type'))
            user_name = request.POST.get('userName')
            password = request.POST.get('passWord') or '123456'  # 默认密码
            name = request.POST.get('name')
            gender = request.POST.get('gender', '男')
            age = int(request.POST.get('age', 18))

            # 检查用户名是否已存在
            if models.Users.objects.filter(userName=user_name).exists():
                return BaseView.error('用户名已存在')

            # 创建用户（使用加密密码）
            user = models.Users.objects.create(
                userName=user_name,
                passWord=make_password(password),
                name=name,
                gender=gender,
                age=age,
                type=user_type
            )

            # 根据用户类型创建对应信息
            if user_type == 1:  # 教师
                phone = request.POST.get('phone', '')
                record = request.POST.get('record', '')
                job = request.POST.get('job', '')
                models.Teachers.objects.create(
                    user=user,
                    phone=phone,
                    record=record,
                    job=job
                )
            elif user_type == 2:  # 学生
                grade_id = request.POST.get('gradeId')
                college_id = request.POST.get('collegeId')
                grade = models.Grades.objects.filter(id=grade_id).first() if grade_id else None
                college = models.Colleges.objects.filter(id=college_id).first() if college_id else None
                models.Students.objects.create(
                    user=user,
                    grade=grade,
                    college=college
                )

            return BaseView.success('用户创建成功')
        except Exception as e:
            return BaseView.error(f'创建用户失败: {str(e)}')

    @staticmethod
    def updateUser(request):
        try:
            user_id = request.POST.get('id')
            user = models.Users.objects.filter(id=user_id).first()
            if not user:
                return BaseView.error('用户不存在')

            # 更新基本信息
            user.name = request.POST.get('name', user.name)
            user.gender = request.POST.get('gender', user.gender)
            user.age = int(request.POST.get('age', user.age))
            user.save()

            # 根据用户类型更新额外信息
            if user.type == 1:  # 教师
                teacher = models.Teachers.objects.filter(user=user).first()
                if teacher:
                    teacher.phone = request.POST.get('phone', teacher.phone)
                    teacher.record = request.POST.get('record', teacher.record)
                    teacher.job = request.POST.get('job', teacher.job)
                    teacher.save()
            elif user.type == 2:  # 学生
                student = models.Students.objects.filter(user=user).select_related('grade', 'college').first()
                if student:
                    grade_id = request.POST.get('gradeId')
                    college_id = request.POST.get('collegeId')
                    if grade_id:
                        grade = models.Grades.objects.filter(id=grade_id).first()
                        if grade:
                            student.grade = grade
                    if college_id:
                        college = models.Colleges.objects.filter(id=college_id).first()
                        if college:
                            student.college = college
                    student.save()

            return BaseView.success('用户信息更新成功')
        except Exception as e:
            return BaseView.error(f'更新用户信息失败: {str(e)}')

    @staticmethod
    def deleteUser(request):
        try:
            user_id = request.POST.get('id')
            user = models.Users.objects.filter(id=user_id).first()
            if not user:
                return BaseView.error('用户不存在')

            # 删除关联数据
            if user.type == 1:  # 教师
                models.Teachers.objects.filter(user=user).delete()
            elif user.type == 2:  # 学生
                models.Students.objects.filter(user=user).delete()

            # 删除用户
            user.delete()
            return BaseView.success('用户删除成功')
        except Exception as e:
            return BaseView.error(f'删除用户失败: {str(e)}')

    @staticmethod
    def disableUser(request):
        try:
            user_id = request.POST.get('id')
            user = models.Users.objects.filter(id=user_id).first()
            if not user:
                return BaseView.error('用户不存在')

            # 这里可以添加禁用逻辑，比如设置状态字段
            # 目前模型中没有状态字段，可以后续添加
            return BaseView.success('用户状态更新成功')
        except Exception as e:
            return BaseView.error(f'更新用户状态失败: {str(e)}')

    # 学科管理
    @staticmethod
    def getSubjects(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')

            subjects_query = models.Projects.objects.all()

            if search:
                subjects_query = subjects_query.filter(name__icontains=search)

            total = subjects_query.count()
            paginator = Paginator(subjects_query, size)
            subjects_page = paginator.get_page(page)

            subjects_data = []
            for subject in subjects_page:
                subjects_data.append({
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description,
                    'createTime': subject.createTime.strftime('%Y-%m-%d %H:%M:%S') if subject.createTime else ''
                })

            return BaseView.successData({
                'list': subjects_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取学科列表失败: {str(e)}')

    @staticmethod
    def manageSubjects(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name')
                description = request.POST.get('description', '')

                if models.Projects.objects.filter(name=name).exists():
                    return BaseView.error('学科名称已存在')

                models.Projects.objects.create(name=name, description=description)
                return BaseView.success('学科创建成功')

            elif action == 'update':
                subject_id = request.POST.get('id')
                subject = models.Projects.objects.filter(id=subject_id).first()
                if not subject:
                    return BaseView.error('学科不存在')

                subject.name = request.POST.get('name', subject.name)
                subject.description = request.POST.get('description', subject.description)
                subject.save()
                return BaseView.success('学科更新成功')

            elif action == 'delete':
                subject_id = request.POST.get('id')
                subject = models.Projects.objects.filter(id=subject_id).first()
                if not subject:
                    return BaseView.error('学科不存在')

                # 检查是否有关联的试卷或题目
                if models.Exams.objects.filter(project=subject).exists():
                    return BaseView.error('该学科下存在试卷，无法删除')
                if models.Practises.objects.filter(project=subject).exists():
                    return BaseView.error('该学科下存在题目，无法删除')

                subject.delete()
                return BaseView.success('学科删除成功')
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'学科操作失败: {str(e)}')

    # 试卷管理
    @staticmethod
    def getExams(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')
            subject_id = request.GET.get('subjectId', '')

            exams_query = models.Exams.objects.all()

            if search:
                exams_query = exams_query.filter(name__icontains=search)
            if subject_id:
                exams_query = exams_query.filter(project_id=subject_id)

            total = exams_query.count()
            paginator = Paginator(exams_query, size)
            exams_page = paginator.get_page(page)

            exams_data = []
            for exam in exams_page:
                exams_data.append({
                    'id': exam.id,
                    'name': exam.name,
                    'subjectId': exam.project.id if exam.project else None,
                    'subjectName': exam.project.name if exam.project else '',
                    'createTime': exam.createTime.strftime('%Y-%m-%d %H:%M:%S') if hasattr(exam, 'createTime') and exam.createTime else ''
                })

            return BaseView.successData({
                'list': exams_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取试卷列表失败: {str(e)}')

    @staticmethod
    def manageExams(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name')
                exam_type = request.POST.get('type')
                subject_id = request.POST.get('subjectId')
                duration = int(request.POST.get('duration', 120))
                total_score = int(request.POST.get('totalScore', 100))

                subject = models.Projects.objects.filter(id=subject_id).first() if subject_id else None

                exam = models.Exams.objects.create(
                    name=name,
                    type=exam_type,
                    project=subject,
                    duration=duration,
                    totalScore=total_score,
                    status='draft'
                )
                return BaseView.successData({'id': exam.id, 'message': '试卷创建成功'})

            elif action == 'update':
                exam_id = request.POST.get('id')
                exam = models.Exams.objects.filter(id=exam_id).first()
                if not exam:
                    return BaseView.error('试卷不存在')

                exam.name = request.POST.get('name', exam.name)
                exam.duration = int(request.POST.get('duration', exam.duration))
                exam.totalScore = int(request.POST.get('totalScore', exam.totalScore))
                exam.status = request.POST.get('status', exam.status)
                exam.save()
                return BaseView.success('试卷更新成功')

            elif action == 'delete':
                exam_id = request.POST.get('id')
                exam = models.Exams.objects.filter(id=exam_id).first()
                if not exam:
                    return BaseView.error('试卷不存在')

                # 检查是否有关联的考试记录
                if models.ExamLogs.objects.filter(exam=exam).exists():
                    return BaseView.error('该试卷存在考试记录，无法删除')

                exam.delete()
                return BaseView.success('试卷删除成功')
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'试卷操作失败: {str(e)}')

    # 题目管理
    @staticmethod
    def getQuestions(request):
        try:
            # 兼容多种参数名（前端可能传 keyword/type/project）
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search') or request.GET.get('keyword', '')
            subject_id = request.GET.get('subjectId') or request.GET.get('project', '')
            question_type = request.GET.get('questionType') or request.GET.get('type', '')

            questions_query = models.Practises.objects.all().order_by('-createTime', '-id')

            if search:
                questions_query = questions_query.filter(name__icontains=search)
            if subject_id:
                questions_query = questions_query.filter(project_id=subject_id)
            if question_type not in [None, '']:
                questions_query = questions_query.filter(type=question_type)

            total = questions_query.count()
            paginator = Paginator(questions_query, size)
            questions_page = paginator.get_page(page)

            questions_data = []
            for question in questions_page:
                # 获取选项信息
                options = models.Options.objects.filter(practise=question)
                options_data = []
                for option in options:
                    options_data.append({
                        'id': option.id,
                        'content': option.name
                    })

                questions_data.append({
                    'id': question.id,
                    'name': question.name,
                    'type': question.type,
                    'subjectId': question.project.id if question.project else None,
                    'subjectName': question.project.name if question.project else '',
                    'options': options_data,
                    'answer': question.answer,
                    'analyse': question.analyse,
                    'createTime': getattr(question, 'createTime', '')
                })

            return BaseView.successData({
                'list': questions_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取题目列表失败: {str(e)}')

    @staticmethod
    def manageQuestions(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name')
                question_type = request.POST.get('type')
                subject_id = request.POST.get('subjectId')
                answer = request.POST.get('answer', '')
                analyse = request.POST.get('analyse', '')
                options = request.POST.getlist('options[]')
                correct_options = request.POST.getlist('correctOptions[]')

                # 校验必填
                if not all([name, question_type is not None, subject_id]):
                    return BaseView.error('缺少必要参数')

                subject = models.Projects.objects.filter(id=subject_id).first() if subject_id else None

                question = models.Practises.objects.create(
                    name=name,
                    type=question_type,
                    project=subject,
                    answer=answer,
                    analyse=analyse
                )

                # 创建选项
                for i, option_content in enumerate(options):
                    # 题目正确答案仍以 Practises.answer 保存
                    models.Options.objects.create(
                        practise=question,
                        name=option_content
                    )

                return BaseView.successData({'id': question.id, 'message': '题目创建成功'})

            elif action == 'update':
                question_id = request.POST.get('id')
                question = models.Practises.objects.filter(id=question_id).first()
                if not question:
                    return BaseView.error('题目不存在')

                question.name = request.POST.get('name', question.name)
                question.answer = request.POST.get('answer', question.answer)
                question.analyse = request.POST.get('analyse', question.analyse)
                question.save()

                # 更新选项
                options = request.POST.getlist('options[]')
                correct_options = request.POST.getlist('correctOptions[]')

                # 删除旧选项
                models.Options.objects.filter(practise=question).delete()

                # 创建新选项
                for i, option_content in enumerate(options):
                    models.Options.objects.create(
                        practise=question,
                        name=option_content
                    )

                return BaseView.success('题目更新成功')

            elif action == 'delete':
                question_id = request.POST.get('id')
                question = models.Practises.objects.filter(id=question_id).first()
                if not question:
                    return BaseView.error('题目不存在')

                # 删除选项
                models.Options.objects.filter(practise=question).delete()

                # 删除题目
                question.delete()
                return BaseView.success('题目删除成功')
            elif action == 'generate_ai':
                return AdminView.generateAIQuestions(request)
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'题目操作失败: {str(e)}')

    # 批量导入题目（CSV）
    @staticmethod
    def importQuestions(request):
        try:
            file = request.FILES.get('file')
            subject_id = request.POST.get('subjectId')
            if not file:
                return BaseView.error('未上传文件')

            # 验证文件大小（限制10MB）
            if file.size > 10 * 1024 * 1024:
                return BaseView.error('文件大小不能超过10MB')

            # 验证文件类型
            if not file.name.endswith('.csv'):
                return BaseView.error('只支持CSV格式文件')

            subject = models.Projects.objects.filter(id=subject_id).first() if subject_id else None
            if not subject:
                return BaseView.error('指定的科目不存在')

            decoded = file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))

            created, failed = 0, []
            for idx, row in enumerate(reader, start=2):  # 从第2行（跳过表头）
                try:
                    name = row.get('name') or row.get('题目')
                    type_str = (row.get('type') or row.get('题型') or '0').strip()
                    type_map = {
                        'single': 0, '选择': 0, '选择题': 0, '0': 0,
                        'fill': 1, '填空': 1, '填空题': 1, '1': 1,
                        'judge': 2, '判断': 2, '判断题': 2, '2': 2,
                        'essay': 3, '编程': 3, '简答': 3, '编程题': 3, '3': 3,
                    }
                    qtype = type_map.get(type_str.lower(), 0)

                    # 验证题目类型
                    if qtype not in [0, 1, 2, 3]:
                        failed.append({'line': idx, 'reason': f'无效的题目类型: {type_str}'})
                        continue

                    answer = row.get('answer') or row.get('答案') or ''
                    analyse = row.get('analyse') or row.get('解析') or ''

                    # 验证题目内容
                    if not name or not name.strip():
                        failed.append({'line': idx, 'reason': '题目内容为空'})
                        continue

                    # 验证答案
                    if not answer or not answer.strip():
                        failed.append({'line': idx, 'reason': '答案不能为空'})
                        continue

                    # 选择题必须验证选项
                    options = []
                    if qtype == 0:
                        for k in ['optionA', 'optionB', 'optionC', 'optionD',
                                  'A', 'B', 'C', 'D', '选项A', '选项B', '选项C', '选项D']:
                            if row.get(k):
                                options.append(row.get(k))

                        if len(options) < 2:
                            failed.append({'line': idx, 'reason': '选择题至少需要2个选项'})
                            continue

                        # 选择题答案可能提供为 A/B/C/D 或 0/1/2/3
                        if answer:
                            ans_norm = answer.strip().upper()
                            letter_to_index = {'A': '0', 'B': '1', 'C': '2', 'D': '3'}
                            answer = '|'.join([letter_to_index.get(ch, ch)
                                              for ch in ans_norm.replace(',', '|').split('|')])

                    # 行内subjectId优先
                    row_subject_id = row.get('subjectId') or row.get('学科ID')
                    row_subject = models.Projects.objects.filter(
                        id=row_subject_id).first() if row_subject_id else subject

                    if not row_subject:
                        failed.append({'line': idx, 'reason': '科目不存在'})
                        continue

                    question = models.Practises.objects.create(
                        name=name.strip(),
                        type=qtype,
                        project=row_subject,
                        answer=answer,
                        analyse=analyse
                    )
                    if qtype == 0 and options:
                        for opt in options:
                            models.Options.objects.create(practise=question, name=opt)
                    created += 1
                except Exception as ie:
                    failed.append({'line': idx, 'reason': str(ie)})

            return BaseView.successData({'created': created, 'failed': failed})
        except Exception as e:
            return BaseView.error(f'导入失败: {str(e)}')

    # 批量导出题目（CSV）
    @staticmethod
    def exportQuestions(request):
        try:
            subject_id = request.POST.get('subjectId')
            search = request.POST.get('search', '')
            question_type = request.POST.get('questionType')
            query = models.Practises.objects.all()
            if subject_id:
                query = query.filter(project_id=subject_id)
            if search:
                query = query.filter(name__icontains=search)
            if question_type not in [None, '']:
                query = query.filter(type=question_type)

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['id', 'name', 'type', 'subjectId', 'answer', 'analyse', 'options'])
            for q in query:
                options = models.Options.objects.filter(practise=q).values_list('name', flat=True)
                writer.writerow([
                    q.id, q.name, q.type, q.project.id if q.project else '', q.answer, q.analyse, '|'.join(options)
                ])

            from django.http import HttpResponse
            resp = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename=questions_export.csv'
            return resp
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    # 下载题目导入模板
    @staticmethod
    def questionsTemplate(request):
        try:
            sample = (
                'name,type,answer,analyse,optionA,optionB,optionC,optionD,subjectId\n'
                '以下哪个是 Python 的整数类型标识?,0,0,整数类型多为 int,整型,int,float,str,1\n'
                'Python 定义函数使用的关键字是?,1,def,函数定义关键字,,, , ,1\n'
                'Python 是解释型语言?,2,true,判断正误题,,, , ,1\n'
                '实现函数 add(a,b) 返回和,3,def add(a,b): return a+b,示例答案,,, , ,1\n'
            )
            from django.http import HttpResponse
            resp = HttpResponse(sample, content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename=questions_template.csv'
            return resp
        except Exception as e:
            return BaseView.error(f'生成模板失败: {str(e)}')

    @staticmethod
    def generateAIQuestionsBatch(request):
        """AI 批量生成多类型题目并入库。
        支持参数：
          - subject, topic, difficulty, subjectId
          - questionTypes: '0,1,2,3' 或 JSON 数组
          - counts: 可选，JSON 对象或 '0:5,1:5,2:5,3:2'，若缺省则均分 total count
          - count: 可选，总数，用于均分
        """
        try:
            from comm.AIUtils import AIUtils
            import json as _json

            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            subject_id = request.POST.get('subjectId')
            question_types_raw = request.POST.get('questionTypes', '')
            counts_raw = request.POST.get('counts', '')
            total_count = int(request.POST.get('count', '0') or '0')

            # 限制单次生成的最大数量，防止系统过载
            MAX_BATCH_SIZE = 50
            if total_count > MAX_BATCH_SIZE:
                return BaseView.error(f'单次生成题目数量不能超过{MAX_BATCH_SIZE}道')

            if not all([subject, topic, subject_id, question_types_raw]):
                return BaseView.error('缺少必要参数：subject/topic/subjectId/questionTypes')

            # 解析类型列表
            types_list = []
            try:
                if question_types_raw.strip().startswith('['):
                    types_list = [_ for _ in _json.loads(question_types_raw)]
                else:
                    types_list = [int(x) for x in str(question_types_raw).split(',') if str(x).strip() != '']
            except Exception:
                return BaseView.error('参数 questionTypes 格式错误')
            types_list = [int(t) for t in types_list if int(t) in [0, 1, 2, 3]]
            if not types_list:
                return BaseView.error('请选择至少一种题目类型')

            # 解析每类数量
            count_by_type = {}
            if counts_raw:
                try:
                    if counts_raw.strip().startswith('{'):
                        tmp = _json.loads(counts_raw)
                        for k, v in tmp.items():
                            count_by_type[int(k)] = int(v)
                    else:
                        # '0:5,1:5'
                        pairs = [p for p in counts_raw.split(',') if ':' in p]
                        for p in pairs:
                            k, v = p.split(':', 1)
                            count_by_type[int(k)] = int(v)
                except Exception:
                    count_by_type = {}
            # 均分逻辑
            if not count_by_type:
                even = max(1, (total_count or 0) // len(types_list)) if (total_count or 0) > 0 else 5
                for t in types_list:
                    count_by_type[int(t)] = even

            subject_obj = models.Projects.objects.filter(id=subject_id).first()
            if not subject_obj:
                return BaseView.error('科目不存在')

            ai_utils = AIUtils()
            created_total = 0
            created_by_type = {0: 0, 1: 0, 2: 0, 3: 0}

            for t in types_list:
                c = int(count_by_type.get(int(t), 0))
                if c <= 0:
                    continue
                qs = ai_utils.ai_generate_questions(
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    question_type=int(t),
                    count=c
                )
                for q in qs or []:
                    try:
                        question = models.Practises.objects.create(
                            name=q['content'],
                            type=int(t),
                            project=subject_obj,
                            answer=q.get('answer', ''),
                            analyse=q.get('analysis', ''),
                            createTime=DateUtil.getNowDateTime()
                        )
                        if int(t) == 0 and 'options' in q:
                            for opt in q['options']:
                                models.Options.objects.create(practise=question, name=opt)
                        created_total += 1
                        created_by_type[int(t)] += 1
                    except Exception as ie:
                        print(f'保存题目失败(type={t}): {str(ie)}')
                        continue

            return BaseView.successData({
                'created': created_total,
                'createdByType': created_by_type
            })
        except Exception as e:
            return BaseView.error(f'批量生成失败: {str(e)}')

    @staticmethod
    def generateAIPracticePaper(request):
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

            # 入库题目
            created_practises = []
            for q in questions:
                try:
                    practise = models.Practises.objects.create(
                        name=q['content'],
                        type=question_type,
                        project=subject_obj,
                        answer=q['answer'],
                        analyse=q.get('analysis', ''),
                        createTime=DateUtil.getNowDateTime()
                    )
                    if question_type == 0 and 'options' in q:
                        for opt in q['options']:
                            models.Options.objects.create(practise=practise, name=opt)
                    created_practises.append(practise)
                except Exception as ie:
                    print(f'保存题目失败: {str(ie)}')
                    continue

            if not created_practises:
                return BaseView.error('题目入库失败')

            # 创建试卷并关联题目
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

            # 均分分值
            per_score = round(total_score / len(created_practises), 2)
            for idx, p in enumerate(created_practises, start=1):
                models.PracticePaperQuestions.objects.create(
                    paper=paper,
                    practise=p,
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
    def generateAIPracticePaperCounts(request):
        """按不同题型数量一次性生成练习试卷（默认 0:10,1:10,2:10,3:2）。
        参数：subject, topic, difficulty, subjectId, teacherId, title, duration(默认60), totalScore(可留空自动按规则计算)
        可选 counts: '0:10,1:10,2:10,3:2'
        计分规则：0/1/2 每题2分，3 每题20分。
        """
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

            # 解析 counts
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

            # 创建试卷
            from comm.CommUtils import DateUtil
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
                qs = ai.ai_generate_questions(
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    question_type=t,
                    count=c) or []
                for q in qs:
                    # 入库题目
                    practise = models.Practises.objects.create(
                        name=q.get('content', ''),
                        type=t,
                        project=subject_obj,
                        answer=q.get('answer', ''),
                        analyse=q.get('analysis', ''),
                        createTime=DateUtil.getNowDateTime()
                    )
                    if t == 0 and 'options' in q:
                        for opt in q['options']:
                            models.Options.objects.create(practise=practise, name=opt)
                    # 关联到试卷
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

    @staticmethod
    def generateAIQuestions(request):
        """AI自动生成题目"""
        try:
            from comm.AIUtils import AIUtils

            # 获取参数
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
            question_type = int(request.POST.get('questionType', 0))
            count = int(request.POST.get('count', 5))
            subject_id = request.POST.get('subjectId')

            # 参数验证
            if not all([subject, topic, subject_id]):
                return BaseView.error('缺少必要参数：科目、主题和科目ID')

            # 验证难度等级
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'

            # 验证题目类型
            if question_type not in [0, 1, 2, 3]:
                return BaseView.error('无效的题目类型')

            # 验证数量
            if count < 1 or count > 20:
                count = 5

            # 获取科目信息
            subject_obj = models.Projects.objects.filter(id=subject_id).first()
            if not subject_obj:
                return BaseView.error('科目不存在')

            # 初始化AI工具
            ai_utils = AIUtils()

            # 生成题目
            questions = ai_utils.ai_generate_questions(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                count=count
            )

            if not questions:
                # 将关键配置带回，便于排查（不包含密钥）
                return BaseView.error(f"AI生成题目失败（model={ai_utils.model}, base_url={ai_utils.base_url}）")

            # 保存生成的题目到database
            created_questions = []
            for question_data in questions:
                try:
                    # 创建题目
                    question = models.Practises.objects.create(
                        name=question_data['content'],
                        type=question_type,
                        project=subject_obj,
                        answer=question_data['answer'],
                        analyse=question_data.get('analysis', ''),
                        createTime=DateUtil.getNowDateTime()
                    )

                    # 如果是选择题，创建选项
                    if question_type == 0 and 'options' in question_data:
                        options = question_data['options']
                        for i, option in enumerate(options):
                            models.Options.objects.create(
                                practise=question,
                                name=option
                            )

                    created_questions.append({
                        'id': question.id,
                        'content': question.name,
                        'answer': question.answer,
                        'analysis': question.analyse
                    })

                except Exception as e:
                    print(f"保存题目失败: {str(e)}")
                    continue

            return BaseView.successData({
                'message': f'成功生成{len(created_questions)}道题目',
                'questions': created_questions,
                'total_generated': len(created_questions),
                'requested_count': count
            })

        except Exception as e:
            print(f"AI生成题目失败: {str(e)}")
            return BaseView.error(f'AI生成题目失败: {str(e)}')

    # 任务管理
    @staticmethod
    def getTasks(request):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.GET.get('search', '')
            subject_id = request.GET.get('subjectId', '')

            tasks_query = models.Tasks.objects.all()

            if search:
                tasks_query = tasks_query.filter(name__icontains=search)
            if subject_id:
                tasks_query = tasks_query.filter(project_id=subject_id)

            total = tasks_query.count()
            paginator = Paginator(tasks_query, size)
            tasks_page = paginator.get_page(page)

            tasks_data = []
            for task in tasks_page:
                tasks_data.append({
                    'id': task.id,
                    'name': task.name,
                    'subjectId': task.project.id if task.project else None,
                    'subjectName': task.project.name if task.project else '',
                    'gradeId': task.grade.id if task.grade else None,
                    'gradeName': task.grade.name if task.grade else '',
                    'duration': task.duration,
                    'totalScore': task.totalScore,
                    'status': task.status,
                    'createTime': task.createTime.strftime('%Y-%m-%d %H:%M:%S') if task.createTime else ''
                })

            return BaseView.successData({
                'list': tasks_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取任务列表失败: {str(e)}')

    @staticmethod
    def manageTasks(request):
        try:
            action = request.POST.get('action')

            if action == 'add':
                name = request.POST.get('name')
                subject_id = request.POST.get('subjectId')
                grade_id = request.POST.get('gradeId')
                duration = int(request.POST.get('duration', 120))
                total_score = int(request.POST.get('totalScore', 100))

                subject = models.Projects.objects.filter(id=subject_id).first() if subject_id else None
                grade = models.Grades.objects.filter(id=grade_id).first() if grade_id else None

                task = models.Tasks.objects.create(
                    name=name,
                    project=subject,
                    grade=grade,
                    duration=duration,
                    totalScore=total_score,
                    status='draft'
                )
                return BaseView.successData({'id': task.id, 'message': '任务创建成功'})

            elif action == 'update':
                task_id = request.POST.get('id')
                task = models.Tasks.objects.filter(id=task_id).first()
                if not task:
                    return BaseView.error('任务不存在')

                task.name = request.POST.get('name', task.name)
                task.duration = int(request.POST.get('duration', task.duration))
                task.totalScore = int(request.POST.get('totalScore', task.totalScore))
                task.status = request.POST.get('status', task.status)
                task.save()
                return BaseView.success('任务更新成功')

            elif action == 'delete':
                task_id = request.POST.get('id')
                task = models.Tasks.objects.filter(id=task_id).first()
                if not task:
                    return BaseView.error('任务不存在')

                # 检查是否有关联的任务记录
                if models.TaskLogs.objects.filter(task=task).exists():
                    return BaseView.error('该任务存在执行记录，无法删除')

                task.delete()
                return BaseView.success('任务删除成功')
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'任务操作失败: {str(e)}')

    # 消息管理
    @staticmethod
    def getMessages(request):
        """
        API获取消息列表

        ---
        tags:
          - 消息管理
        summary:
          获取消息列表
        description:
          分页获取系统消息列表，支持搜索和筛选
        parameters:
          - name: page
            in: query
            type: integer
            required: false
            default: 1
            description: 页码
          - name: size
            in: query
            type: integer
            required: false
            default: 10
            description: 每页数量
          - name: search
            in: formData
            type: string
            required: false
            description: 搜索关键字（消息标题）
        responses:
          200:
            description: 成功返回消息列表
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 0
                msg:
                  type: string
                  example: "处理成功"
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: 消息ID
                      title:
                        type: string
                        description: 消息标题
                      content:
                        type: string
                        description: 消息内容
                      type:
                        type: integer
                        description: 消息类型
                      priority:
                        type: integer
                        description: 优先级
                      senderName:
                        type: string
                        description: 发送者姓名
                      createTime:
                        type: string
                        description: 创建时间
                      totalRecipients:
                        type: integer
                        description: 总接收人数
                      readCount:
                        type: integer
                        description: 已读人数
        """
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            search = request.POST.get('search', '')

            # 优化查询：使用select_related和prefetch_related
            messages_query = models.Messages.objects.select_related(
                'sender'
            ).prefetch_related(
                'messagereads_set'
            ).all()

            if search:
                messages_query = messages_query.filter(title__icontains=search)

            total = messages_query.count()
            paginator = Paginator(messages_query, size)
            messages_page = paginator.get_page(page)

            messages_data = []
            for message in messages_page:
                # 优化：使用预加载的数据统计接收/已读人数
                total_recipients = message.messagereads_set.count()
                read_count = message.messagereads_set.filter(isRead=True).count()
                # 附件列表
                attachments_data = []
                if hasattr(message, 'attachments'):
                    for att in message.attachments.all():
                        attachments_data.append({
                            'id': att.id,
                            'name': att.name,
                            'size': att.size or 0,
                            # 前端若需要可直接打开URL；下载接口也支持按ID下载
                            'url': att.file.url if att.file else ''
                        })

                messages_data.append({
                    'id': message.id,
                    'title': message.title,
                    'content': message.content,
                    'type': message.type,
                    'priority': message.priority,
                    'senderId': message.sender.id if message.sender else None,
                    'senderName': message.sender.name if message.sender else '',
                    'createTime': message.createTime.strftime('%Y-%m-%d %H:%M:%S') if message.createTime else '',
                    'readCount': read_count,
                    'totalRecipients': total_recipients,
                    'attachments': attachments_data
                })

            return BaseView.successData({
                'list': messages_data,
                'total': total,
                'page': page,
                'size': size
            })
        except Exception as e:
            return BaseView.error(f'获取消息列表失败: {str(e)}')

    @staticmethod
    def getMessageReaders(request):
        """获取某条消息的已读/未读详情列表"""
        try:
            message_id = request.GET.get('messageId')
            if not message_id:
                return BaseView.error('消息ID不能为空')

            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('pageSize', 10))

            from django.core.paginator import Paginator
            qs = models.MessageReads.objects.filter(message_id=message_id).select_related('user')
            paginator = Paginator(qs.order_by('-readTime'), size)
            page_obj = paginator.get_page(page)

            readers = []
            for mr in page_obj:
                u = mr.user
                readers.append({
                    'id': mr.id,
                    'userId': u.id if u else None,
                    'userName': u.userName if u else '',
                    'realName': u.name if u else '',
                    'userType': u.type if u else None,
                    'isRead': mr.isRead,
                    'readTime': mr.readTime.strftime('%Y-%m-%d %H:%M:%S') if mr.readTime else ''
                })

            total_count = qs.count()
            read_count = qs.filter(isRead=True).count()
            unread_count = total_count - read_count
            read_rate = round(read_count / total_count * 100) if total_count > 0 else 0

            return BaseView.successData({
                'totalCount': total_count,
                'readCount': read_count,
                'unreadCount': unread_count,
                'readRate': read_rate,
                'readers': readers,
                'page': page,
                'pageSize': size,
                'total': total_count
            })
        except Exception as e:
            return BaseView.error(f'获取已读情况失败: {str(e)}')

    @staticmethod
    def manageMessages(request):
        try:
            action = request.POST.get('action')

            if action == 'send':
                title = request.POST.get('title')
                content = request.POST.get('content')
                message_type = request.POST.get('type', 'notice')
                priority = request.POST.get('priority', 'medium')
                user_type = request.POST.get('userType', 'all')
                recipient_ids = request.POST.getlist('recipientIds[]')

                # 获取发送者信息
                sender_id = cache.get(request.POST.get('token'))
                sender = models.Users.objects.filter(id=sender_id).first()
                if not sender:
                    return BaseView.error('发送者不存在或未登录，请重新登录后再试')

                # 创建消息
                message = models.Messages.objects.create(
                    title=title,
                    content=content,
                    type=message_type,
                    priority=priority,
                    sender=sender
                )

                # 处理附件上传（可选）
                files = request.FILES.getlist('attachments') or request.FILES.getlist('attachmentFiles')
                for f in files:
                    models.MessageAttachments.objects.create(
                        message=message,
                        file=f,
                        name=getattr(f, 'name', ''),
                        size=getattr(f, 'size', None)
                    )

                # 若非自定义选择，则在后端按用户类型选择接收者
                if user_type != 'custom':
                    qs = models.Users.objects.all()
                    if user_type == 'admin':
                        qs = qs.filter(type=0)
                    elif user_type == 'teacher':
                        qs = qs.filter(type=1)
                    elif user_type == 'student':
                        qs = qs.filter(type=2)
                    recipient_ids = [u.id for u in qs]

                # 添加接收者
                for recipient_id in recipient_ids:
                    recipient = models.Users.objects.filter(id=recipient_id).first()
                    if recipient:
                        models.MessageReads.objects.create(
                            message=message,
                            user=recipient,
                            isRead=False
                        )

                return BaseView.success('消息发送成功')

            elif action == 'forward':
                # 消息转发功能
                message_id = request.POST.get('messageId')
                recipient_ids = request.POST.getlist('recipientIds[]')

                if not message_id or not recipient_ids:
                    return BaseView.error('请选择要转发的消息和接收者')

                # 获取原始消息
                original_message = models.Messages.objects.filter(id=message_id).first()
                if not original_message:
                    return BaseView.error('消息不存在')

                # 获取转发者信息
                forwarder_id = cache.get(request.POST.get('token'))
                forwarder = models.Users.objects.filter(id=forwarder_id).first()
                if not forwarder:
                    return BaseView.error('用户未登录')

                # 创建转发消息（标题添加"转发："前缀）
                forwarded_title = f"转发：{original_message.title}"
                sender_name = original_message.sender.name if original_message.sender else '系统'
                forwarded_content = f"【转发自 {sender_name}】\n\n{original_message.content}"

                # 创建新消息
                forwarded_message = models.Messages.objects.create(
                    title=forwarded_title,
                    content=forwarded_content,
                    type=original_message.type,
                    priority=original_message.priority,
                    sender=forwarder
                )

                # 复制原消息的附件（如有）
                if hasattr(original_message, 'attachments'):
                    for att in original_message.attachments.all():
                        models.MessageAttachments.objects.create(
                            message=forwarded_message,
                            file=att.file,
                            name=att.name,
                            size=att.size
                        )

                # 添加接收者
                for recipient_id in recipient_ids:
                    recipient = models.Users.objects.filter(id=recipient_id).first()
                    if recipient:
                        models.MessageReads.objects.create(
                            message=forwarded_message,
                            user=recipient,
                            isRead=False
                        )

                return BaseView.success('消息转发成功')

            elif action == 'delete':
                message_id = request.POST.get('id')
                message = models.Messages.objects.filter(id=message_id).first()
                if not message:
                    return BaseView.error('消息不存在')

                # 删除消息附件与读取记录
                models.MessageAttachments.objects.filter(message=message).delete()
                models.MessageReads.objects.filter(message=message).delete()

                # 删除消息
                message.delete()
                return BaseView.success('消息删除成功')
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'消息操作失败: {str(e)}')

    @staticmethod
    def downloadMessageAttachment(request):
        """按附件ID下载消息附件"""
        try:
            attachment_id = request.GET.get('id')
            if not attachment_id:
                return BaseView.error('缺少附件ID')

            attachment = models.MessageAttachments.objects.filter(id=attachment_id).first()
            if not attachment or not attachment.file:
                return BaseView.error('附件不存在')

            filename = attachment.name or os.path.basename(attachment.file.name)
            response = FileResponse(attachment.file.open('rb'), as_attachment=True, filename=filename)
            return response
        except Exception as e:
            return BaseView.error(f'下载附件失败: {str(e)}')

    # 批量导入学生
    @staticmethod
    def importStudents(request):
        """批量导入学生"""
        try:
            file = request.FILES.get('file')
            if not file:
                return BaseView.error('请选择文件')

            # 保存临时文件
            import tempfile
            import os
            file_ext = os.path.splitext(file.name)[1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                for chunk in file.chunks():
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name

            try:
                from app.services.import_service import ImportService

                if file_ext == '.xlsx' or file_ext == '.xls':
                    success, fail, errors = ImportService.import_students_from_excel(tmp_path)
                elif file_ext == '.csv':
                    success, fail, errors = ImportService.import_students_from_csv(tmp_path)
                else:
                    return BaseView.error('不支持的文件格式，请上传Excel或CSV文件')

                result = {
                    'success': success,
                    'fail': fail,
                    'errors': errors[:50]  # 最多返回50个错误
                }

                if success > 0:
                    return BaseView.successData(result)
                else:
                    return BaseView.warn(f'导入失败: {"; ".join(errors[:5])}')
            finally:
                # 删除临时文件
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            return BaseView.error(f'导入失败: {str(e)}')

    # 下载学生导入模板
    @staticmethod
    def downloadStudentsTemplate(request):
        """下载学生导入模板"""
        try:
            from app.services.import_service import ImportService
            import os

            template_path = ImportService.download_student_template()

            with open(template_path, 'rb') as f:
                response = HttpResponse(
                    f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="students_template.xlsx"'

            # 删除临时文件
            if os.path.exists(template_path):
                os.remove(template_path)

            return response
        except Exception as e:
            return BaseView.error(f'下载模板失败: {str(e)}')

    # 获取考试统计
    @staticmethod
    def getExamStatistics(request):
        """获取考试统计信息"""
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

    # 获取学生学习统计
    @staticmethod
    def getStudentStatistics(request):
        """获取学生学习趋势"""
        try:
            student_id = request.GET.get('studentId')
            days = int(request.GET.get('days', 30))

            if not student_id:
                return BaseView.error('请提供学生ID')

            from app.services.statistics_service import StatisticsService
            statistics = StatisticsService.get_student_learning_trend(int(student_id), days)

            if 'error' in statistics:
                return BaseView.error(statistics['error'])

            return BaseView.successData(statistics)
        except Exception as e:
            return BaseView.error(f'获取统计失败: {str(e)}')

    # 获取班级统计
    @staticmethod
    def getClassStatistics(request):
        """获取班级成绩统计"""
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

    # 获取科目统计
    @staticmethod
    def getSubjectStatistics(request):
        """获取科目统计信息"""
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

    # 导出学生列表
    @staticmethod
    def exportStudents(request):
        """导出学生列表"""
        try:
            grade_id = request.GET.get('gradeId')
            college_id = request.GET.get('collegeId')

            from app.services.export_service import ExportService
            response = ExportService.export_student_list(
                grade_id=int(grade_id) if grade_id else None,
                college_id=int(college_id) if college_id else None
            )
            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    # 导出教师列表
    @staticmethod
    def exportTeachers(request):
        """导出教师列表"""
        try:
            from app.services.export_service import ExportService
            response = ExportService.export_teacher_list()
            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    # 导出考试结果
    @staticmethod
    def exportExamResults(request):
        """导出考试结果"""
        try:
            exam_id = request.GET.get('examId')
            if not exam_id:
                return BaseView.error('请提供考试ID')

            from app.services.export_service import ExportService
            response = ExportService.export_exam_results(int(exam_id))
            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')

    # 导出练习结果
    @staticmethod
    def exportPracticeResults(request):
        """导出练习结果"""
        try:
            practice_id = request.GET.get('practiceId')
            if not practice_id:
                return BaseView.error('请提供练习ID')

            from app.services.export_service import ExportService
            response = ExportService.export_practice_results(int(practice_id))
            return response
        except Exception as e:
            return BaseView.error(f'导出失败: {str(e)}')


class AIView(BaseView):
    """AI功能视图类"""

    def get(self, request, module, *args, **kwargs):
        if module == 'generate_questions':
            return AIView.generateQuestions(request)
        elif module == 'analyze_wrong_answer':
            return AIView.analyzeWrongAnswer(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, module, *args, **kwargs):
        if module == 'score_answer':
            return AIView.scoreAnswer(request)
        elif module == 'generate_questions':
            return AIView.generateQuestions(request)
        else:
            return BaseView.error('请求地址不存在')

    @staticmethod
    def scoreAnswer(request):
        """AI评分功能"""
        try:
            from comm.AIUtils import AIUtils

            # 获取参数
            question_content = request.POST.get('questionContent')
            correct_answer = request.POST.get('correctAnswer')
            student_answer = request.POST.get('studentAnswer')
            question_type = int(request.POST.get('questionType', 0))
            max_score = float(request.POST.get('maxScore', 10.0))

            # 参数验证
            if not all([question_content, correct_answer, student_answer]):
                return BaseView.error('缺少必要参数')

            # 初始化AI工具
            ai_utils = AIUtils()

            # 进行AI评分
            result = ai_utils.ai_score_answer(
                question_content=question_content,
                correct_answer=correct_answer,
                student_answer=student_answer,
                question_type=question_type,
                max_score=max_score
            )

            return BaseView.successData(result)

        except Exception as e:
            print(f"AI评分失败: {str(e)}")
            return BaseView.error(f'AI评分失败: {str(e)}')

    @staticmethod
    def generateQuestions(request):
        """AI自动创建题目功能"""
        try:
            from comm.AIUtils import AIUtils

            # 获取参数
            subject = request.POST.get('subject') or request.GET.get('subject')
            topic = request.POST.get('topic') or request.GET.get('topic')
            difficulty = request.POST.get('difficulty') or request.GET.get('difficulty', 'medium')
            question_type = int(request.POST.get('questionType') or request.GET.get('questionType', 0))
            count = int(request.POST.get('count') or request.GET.get('count', 5))

            # 参数验证
            if not all([subject, topic]):
                return BaseView.error('缺少必要参数：科目和主题')

            # 验证难度等级
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'

            # 验证题目类型
            if question_type not in [0, 1, 2, 3]:
                return BaseView.error('无效的题目类型')

            # 验证数量
            if count < 1 or count > 20:
                count = 5

            # 初始化AI工具
            ai_utils = AIUtils()

            # 生成题目
            questions = ai_utils.ai_generate_questions(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                count=count
            )

            if not questions:
                return BaseView.error('AI生成题目失败')

            return BaseView.successData({
                'questions': questions,
                'count': len(questions),
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty,
                'question_type': question_type
            })

        except Exception as e:
            print(f"AI生成题目失败: {str(e)}")
            return BaseView.error(f'AI生成题目失败: {str(e)}')

    @staticmethod
    def analyzeWrongAnswer(request):
        """AI分析错误答案"""
        try:
            from comm.AIUtils import AIUtils

            # 获取参数
            question_content = request.GET.get('questionContent')
            correct_answer = request.GET.get('correctAnswer')
            wrong_answer = request.GET.get('wrongAnswer')
            question_type = int(request.GET.get('questionType', 0))

            # 参数验证
            if not all([question_content, correct_answer, wrong_answer]):
                return BaseView.error('缺少必要参数')

            # 初始化AI工具
            ai_utils = AIUtils()

            # 分析错误答案
            result = ai_utils.ai_analyze_wrong_answer(
                question_content=question_content,
                correct_answer=correct_answer,
                wrong_answer=wrong_answer,
                question_type=question_type
            )

            return BaseView.successData(result)

        except Exception as e:
            print(f"AI分析错误答案失败: {str(e)}")
            return BaseView.error(f'AI分析失败: {str(e)}')
