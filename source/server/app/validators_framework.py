"""
输入验证框架

提供全面的输入验证功能，防止SQL注入、XSS、CSRF等安全攻击。
支持链式验证、自定义规则、多字段验证。

使用示例：
    from app.validators_framework import Validator, ValidationError

    # 基本使用
    validator = Validator(request.POST)
    validator.required('userName', '用户名')
    validator.length('userName', min=3, max=32)
    validator.pattern('userName', r'^[a-zA-Z0-9_]+$')
    if not validator.is_valid():
        return validator.error_response()

    # 使用验证器类
    class LoginValidator(BaseValidator):
        userName = StringField(required=True, min_length=3, max_length=32)
        passWord = StringField(required=True, min_length=6, max_length=128)

    validator = LoginValidator(request.POST)
    if not validator.is_valid():
        return validator.error_response()

"""

import re
import html
from typing import Any, List, Dict, Optional, Union
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证错误异常"""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class Validator:
    """
    链式验证器

    提供流畅的验证接口，支持多种验证规则。
    """

    def __init__(self, data: Dict[str, Any]):
        """
        初始化验证器

        Args:
            data: 要验证的数据字典（如request.POST或request.GET）
        """
        self.data = data or {}
        self.errors = {}
        self.validated_data = {}

    def required(self, field: str, message: str = None) -> 'Validator':
        """
        验证必填字段

        Args:
            field: 字段名
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        value = self.data.get(field)
        if value is None or value == '':
            msg = message or f'{field}不能为空'
            self.errors[field] = msg
        else:
            self.validated_data[field] = value
        return self

    def length(self, field: str, min: int = None, max: int = None, message: str = None) -> 'Validator':
        """
        验证字符串长度

        Args:
            field: 字段名
            min: 最小长度
            max: 最大长度
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field, '')
        length = len(str(value))

        if min is not None and length < min:
            msg = message or f'{field}长度不能少于{min}个字符'
            self.errors[field] = msg
        elif max is not None and length > max:
            msg = message or f'{field}长度不能超过{max}个字符'
            self.errors[field] = msg
        else:
            self.validated_data[field] = value

        return self

    def pattern(self, field: str, pattern: Union[str, re.Pattern], message: str = None) -> 'Validator':
        """
        验证正则表达式模式

        Args:
            field: 字段名
            pattern: 正则表达式（字符串或编译后的模式）
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = str(self.data.get(field, ''))
        if not re.match(pattern, value):
            msg = message or f'{field}格式不正确'
            self.errors[field] = msg
        else:
            self.validated_data[field] = value

        return self

    def email(self, field: str, message: str = None) -> 'Validator':
        """
        验证邮箱格式

        Args:
            field: 字段名
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return self.pattern(field, email_pattern, message or f'{field}必须是有效的邮箱地址')

    def numeric(self, field: str, message: str = None) -> 'Validator':
        """
        验证是否为数字

        Args:
            field: 字段名
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field)
        try:
            self.validated_data[field] = float(value)
        except (ValueError, TypeError):
            msg = message or f'{field}必须是数字'
            self.errors[field] = msg

        return self

    def integer(self, field: str, message: str = None) -> 'Validator':
        """
        验证是否为整数

        Args:
            field: 字段名
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field)
        try:
            self.validated_data[field] = int(value)
        except (ValueError, TypeError):
            msg = message or f'{field}必须是整数'
            self.errors[field] = msg

        return self

    def in_range(self, field: str, min_val: float = None, max_val: float = None, message: str = None) -> 'Validator':
        """
        验证数值范围

        Args:
            field: 字段名
            min_val: 最小值
            max_val: 最大值
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field)
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                msg = message or f'{field}不能小于{min_val}'
                self.errors[field] = msg
            elif max_val is not None and num > max_val:
                msg = message or f'{field}不能大于{max_val}'
                self.errors[field] = msg
            else:
                self.validated_data[field] = num
        except (ValueError, TypeError):
            self.errors[field] = f'{field}必须是有效的数字'

        return self

    def in_choices(self, field: str, choices: List[Any], message: str = None) -> 'Validator':
        """
        验证值是否在允许的选项中

        Args:
            field: 字段名
            choices: 允许的值列表
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field)
        if value not in choices:
            choices_str = ', '.join(str(c) for c in choices)
            msg = message or f'{field}必须是以下值之一：{choices_str}'
            self.errors[field] = msg
        else:
            self.validated_data[field] = value

        return self

    def sanitize(self, field: str) -> 'Validator':
        """
        清理字段值（防止XSS攻击）

        Args:
            field: 字段名

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field)
        if isinstance(value, str):
            # HTML转义
            sanitized = html.escape(value)
            # 移除危险字符
            sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", '', sanitized)
            self.validated_data[field] = sanitized
        else:
            self.validated_data[field] = value

        return self

    def custom(self, field: str, validator_func: callable, message: str = None) -> 'Validator':
        """
        自定义验证函数

        Args:
            field: 字段名
            validator_func: 验证函数，接受值作为参数，返回True/False
            message: 自定义错误消息

        Returns:
            self（支持链式调用）
        """
        if field in self.errors:
            return self

        value = self.data.get(field)
        try:
            if not validator_func(value):
                msg = message or f'{field}验证失败'
                self.errors[field] = msg
            else:
                self.validated_data[field] = value
        except Exception as e:
            logger.error(f"自定义验证函数执行失败: {str(e)}")
            self.errors[field] = f'{field}验证时发生错误'

        return self

    def is_valid(self) -> bool:
        """
        检查是否所有验证都通过

        Returns:
            bool: 验证是否通过
        """
        return len(self.errors) == 0

    def get_validated_data(self) -> Dict[str, Any]:
        """
        获取验证后的数据

        Returns:
            验证通过的数据字典
        """
        return self.validated_data

    def error_response(self, status_code: int = 400) -> JsonResponse:
        """
        生成错误响应

        Args:
            status_code: HTTP状态码

        Returns:
            JsonResponse对象
        """
        return JsonResponse({
            'success': False,
            'code': status_code,
            'message': '数据验证失败',
            'errors': self.errors
        }, status=status_code)


# ============================================
# 字段验证器类
# ============================================

class BaseValidator:
    """
    基础验证器类

    使用字段定义的方式进行验证，适合复杂的表单验证。

    使用示例：
        class LoginValidator(BaseValidator):
            userName = StringField(required=True, min_length=3, max_length=32)
            passWord = StringField(required=True, min_length=6)

        validator = LoginValidator(request.POST)
        if validator.is_valid():
            data = validator.validated_data
        else:
            return validator.error_response()
    """

    def __init__(self, data: Dict[str, Any]):
        """
        初始化验证器

        Args:
            data: 要验证的数据字典
        """
        self.data = data or {}
        self.errors = {}
        self.validated_data = {}
        self._validate()

    def _validate(self):
        """执行验证（子类不需要重写）"""
        # 获取所有字段验证器
        fields = [
            (name, attr) for name, attr in self.__class__.__dict__.items()
            if isinstance(attr, Field)
        ]

        for field_name, field_validator in fields:
            try:
                # 执行字段验证
                value = self.data.get(field_name)
                validated_value = field_validator.validate(field_name, value)
                if validated_value is not None:
                    self.validated_data[field_name] = validated_value
            except ValidationError as e:
                self.errors[e.field] = e.message

    def is_valid(self) -> bool:
        """检查是否所有验证都通过"""
        return len(self.errors) == 0

    def error_response(self, status_code: int = 400) -> JsonResponse:
        """生成错误响应"""
        return JsonResponse({
            'success': False,
            'code': status_code,
            'message': '数据验证失败',
            'errors': self.errors
        }, status=status_code)


class Field:
    """字段验证器基类"""

    def __init__(self, required: bool = False, default: Any = None):
        self.required = required
        self.default = default

    def validate(self, field_name: str, value: Any) -> Any:
        """
        验证字段值

        Args:
            field_name: 字段名
            value: 字段值

        Returns:
            验证和清理后的值

        Raises:
            ValidationError: 验证失败时抛出
        """
        # 检查必填
        if value is None or value == '':
            if self.required:
                raise ValidationError(field_name, f'{field_name}不能为空')
            # 如果不是必填且有默认值，返回默认值
            if self.default is not None:
                return self.default
            return None

        # 子类实现具体的验证逻辑
        return self._validate_value(field_name, value)

    def _validate_value(self, field_name: str, value: Any) -> Any:
        """子类实现具体的验证逻辑"""
        return value


class StringField(Field):
    """字符串字段验证器"""

    def __init__(self, required: bool = False, min_length: int = None,
                 max_length: int = None, pattern: str = None,
                 sanitize: bool = True, **kwargs):
        super().__init__(required, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.sanitize = sanitize

    def _validate_value(self, field_name: str, value: Any) -> Any:
        value = str(value)

        # 长度验证
        if self.min_length and len(value) < self.min_length:
            raise ValidationError(field_name, f'{field_name}长度不能少于{self.min_length}个字符')

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(field_name, f'{field_name}长度不能超过{self.max_length}个字符')

        # 正则表达式验证
        if self.pattern and not re.match(self.pattern, value):
            raise ValidationError(field_name, f'{field_name}格式不正确')

        # XSS防护
        if self.sanitize:
            value = html.escape(value)
            value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", '', value)

        return value


class IntegerField(Field):
    """整数字段验证器"""

    def __init__(self, required: bool = False, min_value: int = None,
                 max_value: int = None, **kwargs):
        super().__init__(required, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def _validate_value(self, field_name: str, value: Any) -> Any:
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(field_name, f'{field_name}必须是整数')

        if self.min_value is not None and int_value < self.min_value:
            raise ValidationError(field_name, f'{field_name}不能小于{self.min_value}')

        if self.max_value is not None and int_value > self.max_value:
            raise ValidationError(field_name, f'{field_name}不能大于{self.max_value}')

        return int_value


class EmailField(StringField):
    """邮箱字段验证器"""

    def __init__(self, required: bool = False, **kwargs):
        # 邮箱正则表达式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(required=required, pattern=email_pattern, **kwargs)

    def _validate_value(self, field_name: str, value: Any) -> Any:
        value = super()._validate_value(field_name, value)
        # 进一步验证邮箱格式
        if '@' not in value:
            raise ValidationError(field_name, f'{field_name}必须是有效的邮箱地址')
        return value.lower()  # 邮箱转小写


class PasswordField(StringField):
    """密码字段验证器（带强度验证）"""

    def __init__(self, required: bool = False, min_length: int = 8,
                 max_length: int = 128, require_uppercase: bool = True,
                 require_lowercase: bool = True, require_digit: bool = True,
                 require_special: bool = False, **kwargs):
        super().__init__(required=required, min_length=min_length,
                        max_length=max_length, **kwargs)
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special

    def _validate_value(self, field_name: str, value: Any) -> Any:
        value = super()._validate_value(field_name, value)

        # 密码强度验证
        errors = []
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            errors.append('必须包含大写字母')
        if self.require_lowercase and not re.search(r'[a-z]', value):
            errors.append('必须包含小写字母')
        if self.require_digit and not re.search(r'[0-9]', value):
            errors.append('必须包含数字')
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append('必须包含特殊字符')

        if errors:
            error_msg = f'{field_name}' + ''.join(errors)
            raise ValidationError(field_name, error_msg)

        return value


# ============================================
# 预定义的验证器
# ============================================

class LoginValidator(BaseValidator):
    """登录验证器"""

    userName = StringField(required=True, min_length=3, max_length=32,
                           pattern=r'^[a-zA-Z0-9_]+$')
    passWord = StringField(required=True, min_length=6, max_length=128)


class RegisterValidator(BaseValidator):
    """注册验证器"""

    userName = StringField(required=True, min_length=3, max_length=32,
                           pattern=r'^[a-zA-Z0-9_]+$')
    passWord = PasswordField(required=True, min_length=8)
    name = StringField(required=True, max_length=20)
    gender = StringField(required=True, pattern=r'^(男|女)$')
    age = IntegerField(required=True, min_value=1, max_value=150)
    type = IntegerField(required=True, min_value=0, max_value=2)


class UserUpdateValidator(BaseValidator):
    """用户信息更新验证器"""

    userName = StringField(required=False, min_length=3, max_length=32,
                           pattern=r'^[a-zA-Z0-9_]+$')
    name = StringField(required=False, max_length=20)
    gender = StringField(required=False, pattern=r'^(男|女)$')
    age = IntegerField(required=False, min_value=1, max_value=150)


class PasswordChangeValidator(BaseValidator):
    """密码修改验证器"""

    oldPwd = StringField(required=True, min_length=6, max_length=128)
    newPwd = PasswordField(required=True, min_length=8)
    rePwd = StringField(required=True, min_length=8, max_length=128)

    def _validate(self):
        """重写验证方法以添加确认密码验证"""
        super()._validate()

        # 验证新密码和确认密码是否一致
        new_pwd = self.data.get('newPwd')
        re_pwd = self.data.get('rePwd')

        if new_pwd and re_pwd and new_pwd != re_pwd:
            self.errors['rePwd'] = '两次输入的密码不一致'


# ============================================
# 辅助函数
# ============================================

def validate_request_data(request, validator_class: BaseValidator,
                         method: str = 'POST') -> tuple:
    """
    验证请求数据的便捷函数

    Args:
        request: Django request对象
        validator_class: 验证器类
        method: 请求方法（'POST'或'GET'）

    Returns:
        (is_valid, validator_or_errors)
        - 如果验证成功：(True, validator)
        - 如果验证失败：(False, errors)
    """
    data = request.POST if method == 'POST' else request.GET
    validator = validator_class(data)

    if validator.is_valid():
        return True, validator
    else:
        return False, validator.errors


def sanitize_input(value: str) -> str:
    """
    清理单个输入值（防止XSS）

    Args:
        value: 输入字符串

    Returns:
        清理后的字符串
    """
    if not isinstance(value, str):
        return value

    # HTML转义
    sanitized = html.escape(value)
    # 移除控制字符
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", '', sanitized)

    return sanitized


def is_sql_injection(value: str) -> bool:
    """
    检测SQL注入攻击

    Args:
        value: 输入字符串

    Returns:
        bool: 是否检测到SQL注入
    """
    if not isinstance(value, str):
        return False

    # 常见的SQL注入模式
    sql_patterns = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bexec\b|\bexecute\b)",
        r"(--)|(#)|(/\*|\*/)",
        r"(\bor\b.*=.*\bor\b)",
        r"(\band\b.*=.*\band\b)",
        r"(['"]*;)",
        r"(\bxp_cmdshell\b)",
        r"(\bsp_\w+)",
    ]

    value_lower = value.lower()
    for pattern in sql_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            logger.warning(f"检测到SQL注入攻击: {value}")
            return True

    return False


def validate_and_sanitize(data: Dict[str, Any], rules: Dict[str, Dict]) -> tuple:
    """
    根据规则验证和清理数据字典

    Args:
        data: 输入数据字典
        rules: 验证规则字典，格式为：
            {
                'field_name': {
                    'required': True,
                    'type': 'string|int|email',
                    'min_length': 3,
                    'max_length': 32,
                    'pattern': r'^[a-z]+$',
                    'sanitize': True
                }
            }

    Returns:
        (is_valid, validated_data_or_errors)
    """
    errors = {}
    validated_data = {}

    for field, rule in rules.items():
        value = data.get(field)

        # 检查必填
        if rule.get('required', False) and (value is None or value == ''):
            errors[field] = f'{field}不能为空'
            continue

        # 如果值不存在且不是必填，跳过
        if value is None or value == '':
            continue

        # 类型验证
        field_type = rule.get('type', 'string')
        try:
            if field_type == 'int':
                value = int(value)
            elif field_type == 'float':
                value = float(value)
            elif field_type == 'email':
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                    errors[field] = f'{field}必须是有效的邮箱地址'
                    continue
        except (ValueError, TypeError):
            errors[field] = f'{field}类型不正确'
            continue

        # 长度验证（仅字符串）
        if field_type == 'string':
            if 'min_length' in rule and len(value) < rule['min_length']:
                errors[field] = f'{field}长度不能少于{rule["min_length"]}个字符'
                continue
            if 'max_length' in rule and len(value) > rule['max_length']:
                errors[field] = f'{field}长度不能超过{rule["max_length"]}个字符'
                continue

            # 正则表达式验证
            if 'pattern' in rule and not re.match(rule['pattern'], value):
                errors[field] = f'{field}格式不正确'
                continue

            # XSS防护
            if rule.get('sanitize', True):
                value = sanitize_input(value)

        # SQL注入检测
        if isinstance(value, str) and is_sql_injection(value):
            errors[field] = f'{field}包含非法字符'
            continue

        validated_data[field] = value

    is_valid = len(errors) == 0
    return is_valid, validated_data if is_valid else errors
