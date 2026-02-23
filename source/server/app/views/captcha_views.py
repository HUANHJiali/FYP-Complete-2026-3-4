"""
验证码视图
提供验证码生成和登录状态检查功能
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from comm.BaseView import BaseView


@require_http_methods(['GET'])
def get_captcha(request):
    """获取验证码"""
    try:
        from utils.captcha import CaptchaUtil
        captcha_data = CaptchaUtil.create_captcha()
        return BaseView.successData(captcha_data)
    except Exception as e:
        return BaseView.error(f'生成验证码失败: {str(e)}')


@require_http_methods(['GET'])
def check_login_status(request):
    """检查登录状态（是否被锁定）"""
    try:
        username = request.GET.get('userName', '')
        if not username:
            return BaseView.successData({'locked': False, 'remainingAttempts': 5})
        
        from utils.captcha import LoginSecurity
        
        # 检查是否被锁定
        is_locked, remaining_time = LoginSecurity.check_locked(username)
        if is_locked:
            return BaseView.successData({
                'locked': True,
                'remainingTime': remaining_time,
                'message': f'账号已被锁定，请{remaining_time // 60}分钟后重试'
            })
        
        # 返回剩余尝试次数
        remaining_attempts = LoginSecurity.get_remaining_attempts(username)
        return BaseView.successData({
            'locked': False,
            'remainingAttempts': remaining_attempts
        })
    except Exception as e:
        return BaseView.error(f'检查状态失败: {str(e)}')
