# 输入验证框架实施指南

## 概述

本文档��明了FYP考试系统中输入验证框架的实施情况，包括如何使用验证器来防止SQL注入、XSS、CSRF等安全攻击。

## 已完成的工作

### 1. 核心文件创建

#### `app/validators_framework.py`

完整的验证框架实现，包括：

- **链式验证器 (Validator)**: 流畅的验证接口
- **字段验证器 (Field系列)**: 类型安全的字段验证
- **预定义验证器**: 常用场景的现成验证器
- **辅助函数**: 便捷的验证和清理函数

### 2. 支持的验证类型

#### 基础验证
- ✅ 必填字段验证
- ✅ 字符串长度验证
- ✅ 数值范围验证
- ✅ 正则表达式验证
- ✅ 枚举值验证

#### 安全验证
- ✅ XSS防护（HTML转义）
- ✅ SQL注入检测
- ✅ 控制字符过滤
- ✅ 自定义验证函数

#### 特殊字段
- ✅ 邮箱字���验证
- ✅ 密码强度验证
- ✅ 整数字段验证
- ✅ 字符串字段验证

## 使用方法

### 方式1：链式验证器

适合简单的验证场景：

```python
from app.validators_framework import Validator

def login(request):
    validator = Validator(request.POST)
    validator.required('userName', '用户名') \
             .length('userName', min=3, max=32) \
             .pattern('userName', r'^[a-zA-Z0-9_]+$') \
             .required('passWord', '密码') \
             .length('passWord', min=6, max=128)

    if not validator.is_valid():
        return validator.error_response()

    # 使用验证后的数据
    data = validator.get_validated_data()
    userName = data['userName']
    passWord = data['passWord']

    # 业务逻辑...
```

### 方式2：字段验证器类

适合复杂的表单验证：

```python
from app.validators_framework import BaseValidator, StringField, PasswordField

class LoginValidator(BaseValidator):
    userName = StringField(required=True, min_length=3, max_length=32,
                           pattern=r'^[a-zA-Z0-9_]+$')
    passWord = PasswordField(required=True, min_length=8)

def login(request):
    validator = LoginValidator(request.POST)

    if not validator.is_valid():
        return validator.error_response()

    # 使用验证后的数据
    data = validator.validated_data
    userName = data['userName']
    passWord = data['passWord']

    # 业务逻辑...
```

### 方式3：预定义验证器

直接使用现成的验证器：

```python
from app.validators_framework import LoginValidator, validate_request_data

def login(request):
    is_valid, result = validate_request_data(request, LoginValidator)

    if not is_valid:
        return JsonResponse({
            'success': False,
            'code': 400,
            'message': '数据验证失败',
            'errors': result
        }, status=400)

    # 使用验证后的数据
    validator = result
    userName = validator.validated_data['userName']
    passWord = validator.validated_data['passWord']

    # 业务逻辑...
```

### 方式4：规则字典验证

适合动态验证场景：

```python
from app.validators_framework import validate_and_sanitize

def add_user(request):
    rules = {
        'userName': {
            'required': True,
            'type': 'string',
            'min_length': 3,
            'max_length': 32,
            'pattern': r'^[a-zA-Z0-9_]+$',
            'sanitize': True
        },
        'age': {
            'required': True,
            'type': 'int',
            'min_value': 1,
            'max_value': 150
        }
    }

    is_valid, result = validate_and_sanitize(request.POST, rules)

    if not is_valid:
        return JsonResponse({
            'success': False,
            'code': 400,
            'message': '数据验证失败',
            'errors': result
        }, status=400)

    # 使用验证后的数据
    user_name = result['userName']
    age = result['age']

    # 业务逻辑...
```

## 实际应用示例

### 1. 登录接口验证

```python
from app.validators_framework import LoginValidator

@handle_exceptions
def login(request):
    # 使用预定义的LoginValidator
    validator = LoginValidator(request.POST)

    if not validator.is_valid():
        return validator.error_response()

    # 验证通过，获取数据
    userName = validator.validated_data['userName']
    passWord = validator.validated_data['passWord']

    # 业务逻辑...
```

### 2. 用户注册验证

```python
from app.validators_framework import RegisterValidator

@handle_exceptions
def register(request):
    # 使用预定义的RegisterValidator
    validator = RegisterValidator(request.POST)

    if not validator.is_valid():
        return validator.error_response()

    # 验证通过
    userName = validator.validated_data['userName']
    passWord = validator.validated_data['passWord']
    name = validator.validated_data['name']
    gender = validator.validated_data['gender']
    age = validator.validated_data['age']
    type = validator.validated_data['type']

    # 创建用户...
```

### 3. 密码修改验证

```python
from app.validators_framework import PasswordChangeValidator

@handle_exceptions
def updUserPwd(request):
    # 使用预定义的PasswordChangeValidator
    validator = PasswordChangeValidator(request.POST)

    if not validator.is_valid():
        return validator.error_response()

    # 验证通过
    oldPwd = validator.validated_data['oldPwd']
    newPwd = validator.validated_data['newPwd']

    # 修改密码...
```

### 4. 题目添加验证

```python
from app.validators_framework import BaseValidator, StringField, IntegerField

class QuestionValidator(BaseValidator):
    name = StringField(required=True, max_length=64)
    answer = StringField(required=True, max_length=500)
    type = IntegerField(required=True, min_value=0, max_value=3)
    projectId = IntegerField(required=True)

@handle_exceptions
def addPractise(request):
    validator = QuestionValidator(request.POST)

    if not validator.is_valid():
        return validator.error_response()

    # 验证通过，添加题目...
```

### 5. 考试创建验证

```python
from app.validators_framework import BaseValidator, StringField, IntegerField

class ExamValidator(BaseValidator):
    name = StringField(required=True, max_length=64)
    startTime = StringField(required=True)  # 可以添加日期验证
    endTime = StringField(required=True)
    duration = IntegerField(required=True, min_value=1, max_value=600)
    projectId = IntegerField(required=True)
    gradeId = IntegerField(required=True)

@handle_exceptions
def addExam(request):
    validator = ExamValidator(request.POST)

    if not validator.is_valid():
        return validator.error_response()

    # 验证通过，创建考试...
```

## 安全特性

### 1. SQL注入防护

```python
from app.validators_framework import is_sql_injection

# 检测SQL注入
user_input = "admin' OR '1'='1"
if is_sql_injection(user_input):
    # 记录攻击尝试
    logger.warning(f"SQL注入攻击: {user_input}")
    return JsonResponse({'error': '非法输入'}, status=400)
```

### 2. XSS防护

```python
from app.validators_framework import sanitize_input

# 清理用户输入
dirty_input = "<script>alert('XSS')</script>"
clean_input = sanitize_input(dirty_input)
# 结果: "&lt;script&gt;alert('XSS')&lt;/script&gt;"
```

### 3. 密码强度验证

```python
from app.validators_framework import PasswordField

# 强密码要求
strong_password = PasswordField(
    required=True,
    min_length=8,
    require_uppercase=True,   # 必须包含大写字母
    require_lowercase=True,   # 必须包含小写字母
    require_digit=True,       # 必须包含数字
    require_special=True      # 必须包含特殊字符
)
```

## 集成到现有代码

### 最小化修改方案

为了最小化对现有代码的影响，可以采用以下策略：

#### 方案A：装饰器方式

```python
from functools import wraps
from app.validators_framework import LoginValidator

def validate_login(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        validator = LoginValidator(request.POST)
        if not validator.is_valid():
            return validator.error_response()
        return view_func(request, *args, **kwargs)
    return wrapped_view

# 使用
@validate_login
def login(request):
    # 原有代码不变
    userName = request.POST.get('userName')
    passWord = request.POST.get('passWord')
    # ...
```

#### 方案B：中间件方式

```python
from django.utils.deprecation import MiddlewareMixin
from app.validators_framework import Validator

class ValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 为特定路径添加验证
        if request.path == '/api/login/':
            validator = Validator(request.POST)
            validator.required('userName') \
                     .required('passWord')
            if not validator.is_valid():
                return validator.error_response()
```

#### 方案C：逐步迁移

1. 先在新端点使用验证器
2. 逐步更新现有端点
3. 保持向后兼容

```python
def login(request):
    # 新的验证逻辑
    validator = LoginValidator(request.POST)
    if not validator.is_valid():
        return validator.error_response()

    # 原有业务逻辑保持不变
    userName = validator.validated_data['userName']
    passWord = validator.validated_data['passWord']
    # ...
```

## 测试验证

### 单元测试示例

```python
import pytest
from app.validators_framework import LoginValidator, Validator

class TestValidators:
    def test_login_validator_success(self):
        """测试登录验证成功"""
        data = {
            'userName': 'admin',
            'passWord': 'password123'
        }
        validator = LoginValidator(data)
        assert validator.is_valid()
        assert validator.validated_data['userName'] == 'admin'

    def test_login_validator_missing_username(self):
        """测试缺少用户名"""
        data = {
            'passWord': 'password123'
        }
        validator = LoginValidator(data)
        assert not validator.is_valid()
        assert 'userName' in validator.errors

    def test_sql_injection_detection(self):
        """测试SQL注入检测"""
        from app.validators_framework import is_sql_injection
        assert is_sql_injection("admin' OR '1'='1")
        assert not is_sql_injection("admin")

    def test_xss_sanitization(self):
        """测试XSS清理"""
        from app.validators_framework import sanitize_input
        dirty = "<script>alert('XSS')</script>"
        clean = sanitize_input(dirty)
        assert '<script>' not in clean
        assert '&lt;script&gt;' in clean
```

## 最佳实践

### 1. 始终验证用户输入

```python
# ❌ 错误：直接使用用户输入
def add_user(request):
    name = request.POST.get('name')
    models.Users.objects.create(name=name)  # 危险！

# ✅ 正确：先验证再使用
def add_user(request):
    validator = Validator(request.POST)
    validator.required('name').sanitize('name')
    if not validator.is_valid():
        return validator.error_response()
    name = validator.get_validated_data()['name']
    models.Users.objects.create(name=name)  # 安全
```

### 2. 使用类型安全的字段验证器

```python
# ✅ 推荐：使用字段验证器
class UserValidator(BaseValidator):
    age = IntegerField(required=True, min_value=1, max_value=150)
    email = EmailField(required=True)
```

### 3. 自定义验证逻辑

```python
# ✅ 使用自定义验证函数
validator = Validator(request.POST)
validator.custom('userName', lambda x: x.isalnum(), '用户名只能是字母和数字')
```

### 4. 记录验证失败

```python
if not validator.is_valid():
    logger.warning(f"验证失败: {validator.errors}")
    return validator.error_response()
```

## 性能考虑

1. **编译正则表达式**: 对于频繁使用的正则表达式，预编译可以提高性能
2. **缓存验证器**: 对于相同的验证规则，可以重用验证器实例
3. **快速失败**: 将最可能失败的验证放在前面

## 未来增强

### 短期（1-2周）

1. 添加更多字段类型（日期、URL、电话号码等）
2. 支持条件验证（如：密码确认匹配）
3. 添加国际化错误消息

### 中期（1-2月）

1. 集成Django REST Framework的序列化器
2. 支持嵌套对象验证
3. 添加异步验证支持

### 长期（3-6月）

1. 机器学习驱动的异常检测
2. 自动生成验证规则
3. 可视化验证规则配置

## 总结

输入验证框架已完全实现并可以立即使用。提供了多种使用方式，可以根据具体场景选择最合适的方法。

关键成就：
- ✅ 全面的安全防护（SQL注入、XSS等）
- ✅ 灵活的使用方式（4种方法）
- ✅ 类型安全的验证
- ✅ 向后兼容的设计
- ✅ 完整的文档和示例

建议：
1. 在新端点优先使用验证器
2. 逐步更新现有端点
3. 使用预定义验证器减少重复代码
4. 定期审查和更新验证规则

---

**文档版本**: 1.0
**最后更新**: 2026-02-20
**维护者**: Claude AI
