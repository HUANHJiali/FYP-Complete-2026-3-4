"""
用户主题设置视图
支持主题切换、主题设置保存等功能
"""
from app import models
from app.permissions import get_user_from_request
from comm.BaseView import BaseView


class ThemeViews:
    """用户主题设置"""

    @staticmethod
    def _require_owner_or_admin(request, user_id):
        user = get_user_from_request(request)
        if not user:
            return None, BaseView.error('用户未登录')
        if user.type != 0 and str(user.id) != str(user_id):
            return None, BaseView.error('权限不足')
        return user, None
    
    @staticmethod
    def get_theme(request):
        """
        获取用户主题设置
        
        参数:
            userId: 用户ID
        
        返回:
            主题设置
        """
        user_id = request.GET.get('userId')
        
        if not user_id:
            return BaseView.warn('缺少用户ID')

        _, err = ThemeViews._require_owner_or_admin(request, user_id)
        if err:
            return err
        
        try:
            theme_setting = models.UserThemeSettings.objects.get(user_id=user_id)
            return BaseView.successData({
                'theme': theme_setting.theme,
                'primaryColor': theme_setting.primaryColor,
                'fontSize': theme_setting.fontSize,
                'sidebarCollapsed': theme_setting.sidebarCollapsed,
                'showAnimations': theme_setting.showAnimations,
                'compactMode': theme_setting.compactMode
            })
        except models.UserThemeSettings.DoesNotExist:
            # 返回默认设置
            return BaseView.successData({
                'theme': 'light',
                'primaryColor': '#2d8cf0',
                'fontSize': 'medium',
                'sidebarCollapsed': False,
                'showAnimations': True,
                'compactMode': False
            })
    
    @staticmethod
    def save_theme(request):
        """
        保存用户主题设置
        
        参数:
            userId: 用户ID
            theme: 主题名称 (light/dark)
            primaryColor: 主题色
            fontSize: 字体大小
            sidebarCollapsed: 侧边栏折叠
            showAnimations: 显示动画
            compactMode: 紧凑模式
        
        返回:
            保存结果
        """
        user_id = request.POST.get('userId')
        
        if not user_id:
            return BaseView.warn('缺少用户ID')

        _, err = ThemeViews._require_owner_or_admin(request, user_id)
        if err:
            return err
        
        # 获取或创建主题设置
        theme_setting, created = models.UserThemeSettings.objects.get_or_create(
            user_id=user_id,
            defaults={
                'theme': request.POST.get('theme', 'light'),
                'primaryColor': request.POST.get('primaryColor', '#2d8cf0'),
                'fontSize': request.POST.get('fontSize', 'medium'),
                'sidebarCollapsed': request.POST.get('sidebarCollapsed', 'false').lower() == 'true',
                'showAnimations': request.POST.get('showAnimations', 'true').lower() == 'true',
                'compactMode': request.POST.get('compactMode', 'false').lower() == 'true'
            }
        )
        
        # 更新设置
        if not created:
            if 'theme' in request.POST:
                theme_setting.theme = request.POST.get('theme')
            if 'primaryColor' in request.POST:
                theme_setting.primaryColor = request.POST.get('primaryColor')
            if 'fontSize' in request.POST:
                theme_setting.fontSize = request.POST.get('fontSize')
            if 'sidebarCollapsed' in request.POST:
                theme_setting.sidebarCollapsed = request.POST.get('sidebarCollapsed').lower() == 'true'
            if 'showAnimations' in request.POST:
                theme_setting.showAnimations = request.POST.get('showAnimations').lower() == 'true'
            if 'compactMode' in request.POST:
                theme_setting.compactMode = request.POST.get('compactMode').lower() == 'true'
            theme_setting.save()
        
        return BaseView.successData({
            'theme': theme_setting.theme,
            'primaryColor': theme_setting.primaryColor,
            'fontSize': theme_setting.fontSize,
            'sidebarCollapsed': theme_setting.sidebarCollapsed,
            'showAnimations': theme_setting.showAnimations,
            'compactMode': theme_setting.compactMode
        })
    
    @staticmethod
    def reset_theme(request):
        """
        重置用户主题设置为默认值
        
        参数:
            userId: 用户ID
        
        返回:
            重置结果
        """
        user_id = request.POST.get('userId')
        
        if not user_id:
            return BaseView.warn('缺少用户ID')

        _, err = ThemeViews._require_owner_or_admin(request, user_id)
        if err:
            return err
        
        try:
            theme_setting = models.UserThemeSettings.objects.get(user_id=user_id)
            theme_setting.theme = 'light'
            theme_setting.primaryColor = '#2d8cf0'
            theme_setting.fontSize = 'medium'
            theme_setting.sidebarCollapsed = False
            theme_setting.showAnimations = True
            theme_setting.compactMode = False
            theme_setting.save()
        except models.UserThemeSettings.DoesNotExist:
            pass
        
        return BaseView.success('重置成功')
