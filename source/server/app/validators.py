"""
输入验证工具
提供各种输入验证方法
"""
from typing import Tuple, Optional
import re


class InputValidator:
    """输入验证器类"""
    
    @staticmethod
    def validate_username(username: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not username:
            return False, '用户名不能为空'
        
        username = username.strip()
        
        if len(username) < 3:
            return False, '用户名长度至少为3个字符'
        
        if len(username) > 50:
            return False, '用户名长度不能超过50个字符'
        
        # 只允许字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, '用户名只能包含字母、数字和下划线'
        
        return True, None
    
    @staticmethod
    def validate_password(password: Optional[str], min_length: int = 6) -> Tuple[bool, Optional[str]]:
        """
        验证密码
        
        Args:
            password: 密码
            min_length: 最小长度，默认为6
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not password:
            return False, '密码不能为空'
        
        if len(password) < min_length:
            return False, f'密码长度至少为{min_length}个字符'
        
        if len(password) > 128:
            return False, '密码长度不能超过128个字符'
        
        return True, None
    
    @staticmethod
    def validate_name(name: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        验证姓名
        
        Args:
            name: 姓名
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not name:
            return False, '姓名不能为空'
        
        name = name.strip()
        
        if len(name) < 1:
            return False, '姓名不能为空'
        
        if len(name) > 50:
            return False, '姓名长度不能超过50个字符'
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        验证手机号
        
        Args:
            phone: 手机号
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not phone:
            return True, None  # 手机号可选
        
        phone = phone.strip()
        
        # 简单的手机号验证（11位数字）
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, '手机号格式不正确（应为11位数字，以1开头）'
        
        return True, None
    
    @staticmethod
    def validate_email(email: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        验证邮箱
        
        Args:
            email: 邮箱地址
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not email:
            return True, None  # 邮箱可选
        
        email = email.strip()
        
        # 简单的邮箱验证
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, '邮箱格式不正确'
        
        return True, None
    
    @staticmethod
    def sanitize_string(text: Optional[str], max_length: Optional[int] = None) -> str:
        """
        清理字符串（去除前后空格，限制长度）
        
        Args:
            text: 待清理的字符串
            max_length: 最大长度
            
        Returns:
            str: 清理后的字符串
        """
        if not text:
            return ''
        
        text = text.strip()
        
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text




