"""
JWT登录方法的实现

提供基于JWT的登录功能，同时保持向后兼容。
此文件包含了新的login和exit方法实现，可以复制到app/views.py中使用。

作者：Claude AI
创建时间：2026-02-20
"""

import uuid
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from app import models
from comm.BaseView import BaseView
from comm.auth_utils import JWTUtils, generate_token, revoke_token
import logging

logger = logging.getLogger(__name__)


def login_with_jwt(request):
    """
    使用JWT的登录方法（推荐使用）

    特点：
    1. 返回access_token和refresh_token
    2. 支持token刷新
    3. 自动将明文密码迁移到加密格式
    4. 完整的错误处理

    Returns:
        JSON响应：{
            'code': 0,
            'msg': '处理成功',
            'data': {
                'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                'expires_in': 86400,
                'token_type': 'Bearer'
            }
        }
    """
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
            return BaseView.warn('用户密码输入错误')
    else:
        # 新加密密码格式，使用check_password验证
        if check_password(passWord, user.passWord):
            password_valid = True
        else:
            return BaseView.warn('用户密码输入错误')

    if password_valid:
        # 生成JWT token
        try:
            tokens = JWTUtils.generate_tokens(
                user_id=user.id,
                user_type=user.type,
                additional_claims={
                    'name': user.name,
                    'userName': user.userName
                }
            )

            # 更新最后登录时间
            try:
                user.lastLoginTime = user.lastLoginTime or None  # 触发auto_now更新
                user.save(update_fields=['lastLoginTime'])
            except Exception as e:
                logger.warning(f"更新最后登录时间失败: {str(e)}")

            # 记录登录日志
            logger.info(f"用户 {userName} (ID: {user.id}) 登录成功")

            return BaseView.successData(tokens)

        except Exception as e:
            logger.error(f"生成token失败: {str(e)}")
            return BaseView.error('登录失败，请稍后重试')

    return BaseView.warn('登录失败')


def login_with_jwt_back_compat(request):
    """
    使用JWT但保持向后兼容的登录方法

    为了兼容现有前端，只返回access_token作为token字段。
    当前端准备好后，可以切换到login_with_jwt方法。

    Returns:
        JSON响应：{
            'code': 0,
            'msg': '处理成功',
            'data': {
                'token': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
            }
        }
    """
    userName = request.POST.get('userName')
    passWord = request.POST.get('passWord')

    if not userName:
        return BaseView.warn('用户名不能为空')
    if not passWord:
        return BaseView.warn('密码不能为空')

    user = models.Users.objects.filter(userName=userName).first()
    if not user:
        return BaseView.warn('用户名输入错误')

    # 验证密码
    password_valid = False
    if len(user.passWord) < 50:
        if user.passWord == passWord:
            password_valid = True
            try:
                user.passWord = make_password(passWord)
                user.save()
                logger.info(f"用户 {userName} 密码已自动迁移到加密格式")
            except Exception as e:
                logger.error(f"密码迁移失败: {str(e)}")
        else:
            return BaseView.warn('用户密码输入错误')
    else:
        if check_password(passWord, user.passWord):
            password_valid = True
        else:
            return BaseView.warn('用户密码输入错误')

    if password_valid:
        try:
            # 生成JWT token（只返回access_token以保持兼容性）
            access_token = generate_token(user_id=user.id, user_type=user.type)

            # 为了向后兼容，同时将token存入缓存（旧机制）
            cache.set(access_token, user.id, 60 * 60 * 24)

            # 更新最后登录时间
            try:
                user.lastLoginTime = user.lastLoginTime or None
                user.save(update_fields=['lastLoginTime'])
            except Exception as e:
                logger.warning(f"更新最后登录时间失败: {str(e)}")

            logger.info(f"用户 {userName} (ID: {user.id}) 登录成功")

            return BaseView.successData({'token': access_token})

        except Exception as e:
            logger.error(f"生成token失败: {str(e)}")
            return BaseView.error('登录失败，请稍后重试')

    return BaseView.warn('登录失败')


def exit_with_jwt(request):
    """
    使用JWT的退出方法

    支持两种token：
    1. 新的JWT token
    2. 旧的UUID token（向后兼容）

    Returns:
        JSON响应：{
            'code': 0,
            'msg': '处理成功'
        }
    """
    # 尝试从多个位置获取token
    token = (
        request.POST.get('token') or
        request.GET.get('token') or
        request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    )

    if not token:
        return BaseView.warn('未找到token')

    try:
        # 尝试作为JWT token撤销
        if revoke_token(token):
            logger.info(f"JWT token已撤销")
        else:
            # 如果不是JWT token，尝试从缓存中删除（向后兼容）
            cache.delete(token)
            logger.info(f"旧token已从缓存中删除")
    except Exception as e:
        # 退出操作失败不影响用户体验，记录日志即可
        logger.warning(f'退出登录时删除token失败: {str(e)}')

    return BaseView.success()


def refresh_token_view(request):
    """
    Token刷新端点

    接收refresh_token，返回新的access_token和refresh_token

    Returns:
        JSON响应：{
            'code': 0,
            'msg': '处理成功',
            'data': {
                'access_token': '...',
                'refresh_token': '...',
                'expires_in': 86400,
                'token_type': 'Bearer'
            }
        }
    """
    refresh_token = request.POST.get('refresh_token') or request.POST.get('token')

    if not refresh_token:
        return BaseView.warn('缺少刷新token')

    new_tokens = JWTUtils.refresh_tokens(refresh_token)
    if not new_tokens:
        return BaseView.warn('刷新token失败或已过期')

    return BaseView.successData(new_tokens)


# 使用说明：
# 1. 将login_with_jwt_back_compat方法复制到app/views.py的SysView类中，替换现有的login方法
# 2. 将exit_with_jwt方法复制到SysView类中，替换现有的exit方法
# 3. 如果需要支持token刷新，在urls.py中添加刷新端点：
#    path('refresh/', SysView.as_view()),  # 使用refresh_token_view方法
# 4. 前端可以继续使用现有的token字段，无需修改
# 5. 当前端准备好后，可以切换到login_with_jwt方法以获得完整功能
