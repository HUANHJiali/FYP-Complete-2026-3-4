"""
用户服务层
处理用户相关的业务逻辑

该模块提供了用户相关的业务逻辑处理，包括用户信息构建、
Token验证和用户数据验证等功能。
"""
from typing import Dict, Any, Optional, Tuple
from django.core.cache import cache
from app import models
from app.validators import InputValidator


class UserService:
    """用户服务类"""
    
    @staticmethod
    def build_user_info(user: models.Users) -> Dict[str, Any]:
        """
        构建用户信息字典
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 用户信息字典
        """
        base_info = {
            'id': user.id,
            'userName': user.userName,
            'name': user.name,
            'gender': user.gender,
            'age': user.age,
            'type': user.type,
        }
        
        if user.type == 1:  # 教师
            teacher = models.Teachers.objects.filter(user=user).first()
            if teacher:
                base_info.update({
                    'phone': teacher.phone,
                    'record': teacher.record,
                    'job': teacher.job,
                })
        elif user.type == 2:  # 学生
            student = models.Students.objects.filter(user=user).select_related('grade', 'college').first()
            if student:
                base_info.update({
                    'gradeId': student.grade.id,
                    'gradeName': student.grade.name,
                    'collegeId': student.college.id,
                    'collegeName': student.college.name,
                })
        
        return base_info
    
    @staticmethod
    def get_user_by_token(token: str) -> Optional[models.Users]:
        """
        通过token获取用户
        
        Args:
            token: 用户token
            
        Returns:
            User对象或None
        """
        if not token:
            return None
        
        user_id = cache.get(token)
        if not user_id:
            return None
        
        try:
            return models.Users.objects.filter(id=user_id).first()
        except Exception:
            return None
    
    @staticmethod
    def validate_user_creation_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证用户创建数据
        
        Args:
            data: 用户数据字典
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # 验证用户名
        if 'userName' in data:
            is_valid, error_msg = InputValidator.validate_username(data['userName'])
            if not is_valid:
                return False, error_msg
        
        # 验证姓名
        if 'name' in data:
            is_valid, error_msg = InputValidator.validate_name(data['name'])
            if not is_valid:
                return False, error_msg
        
        # 验证密码（如果提供）
        if 'passWord' in data and data['passWord']:
            is_valid, error_msg = InputValidator.validate_password(data['passWord'])
            if not is_valid:
                return False, error_msg
        
        return True, None
