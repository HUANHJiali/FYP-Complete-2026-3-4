"""
系统处理视图
处理登录、用户信息等系统级功能

该模块提供了系统级别的视图处理，包括：
- 用户登录/登出
- 用户信息获取和更新
- 用户密码修改
- 用户消息管理
"""

from django_ratelimit.decorators import ratelimit
import uuid
from typing import Optional
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpRequest, HttpResponse

from app import models
from app.services.user_service import UserService
from app.validators import InputValidator
from comm.BaseView import BaseView
from comm.CommUtils import DateUtil, SysUtil
from utils.OperationLogger import OperationLogger

# 导入错误处理（如果可用）
try:
    from comm.error_handler import handle_exceptions, validate_required_fields, validate_user_token
except ImportError:
    def handle_exceptions(func):
        return func
    def validate_required_fields(request, fields, method='POST'):
        return True, None
    def validate_user_token(request):
        return False, None


class SysView(BaseView):
    """系统视图类"""

    def get(self, request, *args, **kwargs):
        module = kwargs.get('module')
        action = kwargs.get('action')
        actual_action = action if action else module
        if actual_action == 'info':
            return SysView.getUserInfo(request)
        elif actual_action == 'messages':
            return SysView.getUserMessages(request)
        else:
            return BaseView.error('请求地址不存在')

    def post(self, request, *args, **kwargs):
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
            return BaseView.error('请求地址不存在')

    # 获取指定用户信息
    @staticmethod
    def getUserInfo(request: HttpRequest) -> HttpResponse:
        """
        获取当前登录用户信息（使用服务层）
        
        Args:
            request: Django HTTP请求对象，需要包含token参数
            
        Returns:
            HttpResponse: 包含用户信息的JSON响应
            
        Example:
            GET /api/info/?token=xxx
        """
        token = request.GET.get('token')
        user = UserService.get_user_by_token(token)
        
        if not user:
            return BaseView.error('用户未登录')
        
        user_info = UserService.build_user_info(user)
        return BaseView.successData(user_info)

    @staticmethod
    def getUserMessages(request: HttpRequest) -> HttpResponse:
        """
        获取当前登录用户的消息列表
        
        Args:
            request: Django HTTP请求对象，需要包含token参数
            
        Returns:
            HttpResponse: 包含消息列表的JSON响应
        """
        try:
            token = request.GET.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            user_id = cache.get(token)
            if not user_id:
                return BaseView.error('用户未登录')

            message_type = request.GET.get('type', '').strip()

            # 获取消息读取记录（包含消息详情和发送者信息）
            reads_qs = models.MessageReads.objects.filter(user_id=user_id).select_related('message', 'message__sender')
            if message_type:
                reads_qs = reads_qs.filter(message__type=message_type)
            
            messages = []
            for read in reads_qs:
                msg = read.message
                messages.append({
                    'id': msg.id,
                    'title': msg.title,
                    'content': msg.content,
                    'senderName': msg.sender.name if msg.sender else '系统',
                    'sendTime': msg.createTime.strftime('%Y-%m-%d %H:%M:%S') if msg.createTime else '',
                    'isRead': read.isRead,
                    'readTime': read.readTime.strftime('%Y-%m-%d %H:%M:%S') if read.readTime else '',
                    'hasAttachments': False  # Messages 模型暂无附件功能
                })

            # 按发送时间倒序排列
            messages.sort(key=lambda x: x['sendTime'], reverse=True)
            
            return BaseView.successData(messages)
        except Exception as e:
            return BaseView.error(f'获取消息失败: {str(e)}')

    @staticmethod
    def manageUserMessages(request: HttpRequest) -> HttpResponse:
        """
        管理用户消息（标记已读、删除等）
        
        Args:
            request: Django HTTP请求对象，需要包含：
                - token: 用户token
                - action: 操作类型（mark_read, mark_all_read, delete）
                - id/messageId: 消息ID（某些操作需要）
                
        Returns:
            HttpResponse: 操作结果的JSON响应
        """
        try:
            token = request.POST.get('token') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
            user_id = cache.get(token)
            if not user_id:
                return BaseView.error('用户未登录')

            action = request.POST.get('action')  # mark_read, mark_all_read, delete
            
            if action == 'mark_read':
                msg_id = request.POST.get('messageId')
                if not msg_id:
                    return BaseView.error('消息ID不能为空')
                mr = models.MessageReads.objects.filter(user_id=user_id, message_id=msg_id).first()
                if mr:
                    from comm.CommUtils import DateUtil
                    mr.isRead = True
                    mr.readTime = DateUtil.getNowDateTime()
                    mr.save()
                return BaseView.success('标记成功')
            elif action == 'mark_all_read':
                from comm.CommUtils import DateUtil
                now = DateUtil.getNowDateTime()
                models.MessageReads.objects.filter(user_id=user_id, isRead=False).update(isRead=True, readTime=now)
                return BaseView.success('全部标记成功')
            elif action == 'delete':
                msg_id = request.POST.get('messageId')
                if not msg_id:
                    return BaseView.error('消息ID不能为空')
                # 学生删除仅删除自己的读取记录，不删除消息本身
                models.MessageReads.objects.filter(user_id=user_id, message_id=msg_id).delete()
                return BaseView.success('删除成功')
            else:
                return BaseView.error('无效的操作类型')
        except Exception as e:
            return BaseView.error(f'消息操作失败: {str(e)}')

    #登陆处理
    @staticmethod
    @ratelimit(key='ip', rate='10/m', method='POST')
    @ratelimit(key='post:userName', rate='20/m', method='POST')
    @handle_exceptions
    def login(request: HttpRequest) -> HttpResponse:
        """
        用户登录API

        ---
        tags:
          - 用户认证
        summary:
          用户登录
        description:
          使用用户名和密码登录系统，支持管理员、教师、学生三种角色
        parameters:
          - name: userName
            in: formData
            type: string
            required: true
            description: 用户名（admin/teacher/student）
          - name: passWord
            in: formData
            type: string
            required: true
            description: 密码（默认测试密码：123456）
        responses:
          200:
            description: 登录成功
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
                  type: object
                  properties:
                    token:
                      type: string
                      description: 认证令牌（24小时有效）
                      example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
          400:
            description: 登录失败
            schema:
              type: object
              properties:
                code:
                  type: integer
                  example: 1
                msg:
                  type: string
                  example: "用户密码输入错误"

        Examples:
          - userName: "admin"
            passWord: "123456"
          - userName: "teacher"
            passWord: "123456"
          - userName: "student"
            passWord: "123456"

        Notes:
          - Token有效期为24小时
          - 支持旧明文密码和新加密密码的兼容验证
          - 登录成功后自动将明文密码迁移为加密密码

        Args:
            request: Django HTTP请求对象，需要包含：
                - userName: 用户名
                - passWord: 密码

        Returns:
            HttpResponse: 包含token的JSON响应，或错误信息
        """
        userName = request.POST.get('userName')
        passWord = request.POST.get('passWord')
        captchaId = request.POST.get('captchaId')
        captchaCode = request.POST.get('captchaCode')

        # 检查账号是否被锁定
        from utils.captcha import LoginSecurity
        is_locked, remaining_time = LoginSecurity.check_locked(userName)
        if is_locked:
            return BaseView.warn(f'账号已被锁定，请{remaining_time // 60}分钟后重试')

        # 验证码验证（如果提供了验证码ID）
        if captchaId:
            from utils.captcha import CaptchaUtil
            if not captchaCode:
                return BaseView.warn('请输入验证码')
            if not CaptchaUtil.verify_captcha(captchaId, captchaCode):
                return BaseView.warn('验证码错误或已过期')

        # 输入验证
        is_valid, error_msg = InputValidator.validate_username(userName)
        if not is_valid:
            return BaseView.warn(error_msg)

        is_valid, error_msg = InputValidator.validate_password(passWord, min_length=1)  # 登录时允许短密码
        if not is_valid and passWord:  # 密码不为空时才验证长度
            return BaseView.warn(error_msg)

        user = models.Users.objects.filter(userName=userName)
        if user.exists():
            user = user.first()
            # 支持旧明文密码和新加密密码的兼容验证
            if len(user.passWord) < 50:
                # 旧明文密码格式，直接比较（向后兼容）
                if user.passWord == passWord:
                    # 登录成功后自动迁移为加密密码
                    user.passWord = make_password(passWord)
                    user.save()
                    token = uuid.uuid4()
                    resl = {
                        'token': str(token)
                    }
                    cache.set(str(token), user.id, 60*60*24)  # 修复：token缓存时间改为24小时

                    # 记录登录成功日志
                    OperationLogger.log_login(
                        user_id=user.id,
                        user_name=user.name,
                        user_type=user.type,
                        status=OperationLogger.STATUS_SUCCESS,
                        request=request
                    )

                    return SysView.successData(resl)
                else:
                    # 记录登录失败日志（密码错误）
                    OperationLogger.log_login(
                        user_id=user.id,
                        user_name=user.name,
                        user_type=user.type,
                        status=OperationLogger.STATUS_FAILURE,
                        request=request,
                        error_message='用户密码输入错误'
                    )
                    return SysView.warn('用户密码输入错误')
            else:
                # 新加密密码格式，使用check_password验证
                if check_password(passWord, user.passWord):
                    token = uuid.uuid4()
                    resl = {
                        'token': str(token)
                    }
                    cache.set(str(token), user.id, 60*60*24)  # 修复：token缓存时间改为24小时

                    # 记录登录成功日志
                    OperationLogger.log_login(
                        user_id=user.id,
                        user_name=user.name,
                        user_type=user.type,
                        status=OperationLogger.STATUS_SUCCESS,
                        request=request
                    )

                    return SysView.successData(resl)
                else:
                    # 记录登录失败日志（密码错误）
                    OperationLogger.log_login(
                        user_id=user.id,
                        user_name=user.name,
                        user_type=user.type,
                        status=OperationLogger.STATUS_FAILURE,
                        request=request,
                        error_message='用户密码输入错误'
                    )
                    return SysView.warn('用户密码输入错误')
        else:
            # 记录登录失败日志（用户不存在）
            OperationLogger.log_login(
                user_id=userName,
                user_name=userName,
                user_type=-1,
                status=OperationLogger.STATUS_FAILURE,
                request=request,
                error_message='用户名输入错误'
            )
            return SysView.warn('用户名输入错误')

    #退出系统
    @staticmethod
    def exit(request: HttpRequest) -> HttpResponse:
        """
        用户退出系统

        Args:
            request: Django HTTP请求对象，需要包含token参数

        Returns:
            HttpResponse: 退出成功的JSON响应
        """
        token = request.POST.get('token')
        if token:
            try:
                # 获取用户信息用于日志记录
                user_id = cache.get(token)
                if user_id:
                    user = models.Users.objects.filter(id=user_id).first()
                    if user:
                        # 记录登出日志
                        OperationLogger.log_logout(
                            user_id=user.id,
                            user_name=user.name,
                            user_type=user.type,
                            request=request
                        )

                cache.delete(token)
            except Exception:
                pass
        return BaseView.success()

    # 修改用户信息
    @staticmethod
    def updUserInfo(request: HttpRequest) -> HttpResponse:
        """
        修改用户信息
        
        Args:
            request: Django HTTP请求对象，需要包含：
                - token: 用户token
                - userName: 新用户名（可选）
                - name: 新姓名（可选）
                - gender: 新性别（可选）
                - age: 新年龄（可选）
                
        Returns:
            HttpResponse: 更新结果的JSON响应
        """
        token = request.POST.get('token')
        user_id = cache.get(token) if token else None
        if not user_id:
            return BaseView.error('用户未登录')

        user_obj = models.Users.objects.filter(id=user_id).first()
        if not user_obj:
            return BaseView.error('用户不存在')

        new_user_name = request.POST.get('userName')
        if SysUtil.isExit(new_user_name) and new_user_name != user_obj.userName and \
                models.Users.objects.filter(userName=new_user_name).exclude(id=user_obj.id).exists():
            return BaseView.warn('用户账号已存在')

        update_data = {}
        if SysUtil.isExit(new_user_name):
            update_data['userName'] = new_user_name

        new_name = request.POST.get('name')
        if SysUtil.isExit(new_name):
            update_data['name'] = new_name

        new_gender = request.POST.get('gender')
        if SysUtil.isExit(new_gender):
            update_data['gender'] = new_gender

        new_age = request.POST.get('age')
        if SysUtil.isExit(new_age):
            try:
                update_data['age'] = int(new_age)
            except Exception:
                return BaseView.warn('年龄格式不正确')

        if not update_data:
            return BaseView.warn('未提供可更新字段')

        models.Users.objects.filter(id=user_obj.id).update(**update_data)
        return BaseView.success()

    # 修改用户密码
    @staticmethod
    def updUserPwd(request: HttpRequest) -> HttpResponse:
        """
        修改用户密码
        
        Args:
            request: Django HTTP请求对象，需要包含：
                - token: 用户token
                - oldPwd: 旧密码
                - newPwd: 新密码
                - rePwd: 确认新密码
                
        Returns:
            HttpResponse: 修改结果的JSON响应
            
        Note:
            - 支持旧明文密码和新加密密码的兼容验证
            - 新密码会使用加密存储
        """
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
