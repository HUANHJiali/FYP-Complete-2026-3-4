# FYP项目自动改进计划

**生成时间**: 2026-02-08
**改进范围**: 安全性、性能、代码质量、文档
**优先级**: 按严重程度排序

---

## 🚨 高优先级问题（立即修复）

### 1. XSS漏洞修复 ⚠️ **严重**
**文件**: `source/client/src/views/pages/messageCenter.vue:164`

**问题**:
```vue
<div class="content-text" v-html="formatContent(selectedMessage.content)"></div>
```

**风险**: 直接渲染用户输入的HTML，可能导致XSS攻击

**修��方案**:
```vue
<!-- 方案1: 使用文本插值（推荐） -->
<div class="content-text">{{ selectedMessage.content }}</div>

<!-- 方案2: 如果必须支持HTML，使用DOMPurify -->
import DOMPurify from 'dompurify';
<div class="content-text" v-html="DOMPurify.sanitize(selectedMessage.content)"></div>

<!-- 方案3: 使用白名单过滤 -->
<div class="content-text">{{ formatContentSafe(selectedMessage.content) }}</div>
```

**预计工作量**: 2小时

---

### 2. 硬编码API密钥 🔐 **严重**
**文件**: `docker-compose.yml:68`

**问题**:
```yaml
ZHIPUAI_API_KEY: fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

**风险**: API密钥暴露在代码中，可能导致密钥泄露和滥用

**修复方案**:

#### 方案1: 使用.env文件（推荐）
```bash
# 1. 创建 .env 文件
echo "ZHIPUAI_API_KEY=your_actual_api_key_here" > .env

# 2. 修改 docker-compose.yml
environment:
  - ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY}

# 3. 添加到 .gitignore
echo ".env" >> .gitignore

# 4. 更新文档
echo "请复制 env.example 为 .env 并填入真实的API密钥"
```

#### 方案2: Docker secrets
```yaml
# 使用Docker secrets存储敏感信息
secrets:
  zhipuai_api_key:
    external: true

services:
  backend:
    secrets:
      - zhipuai_api_key
    environment:
      - ZHIPUAI_API_KEY_FILE=/run/secrets/zhipuai_api_key
```

**预计工作量**: 1小时

---

### 3. 密码字段长度不足 🔐 **严重**
**文件**: `source/server/app/models.py:54`

**问题**:
```python
passWord = models.CharField('用户密码', max_length=32, null=False)
```

**风险**: Django PBKDF2哈希后的密码超过32字符，可能被截断

**修复方案**:

#### 步骤1: 修改模型
```python
# source/server/app/models.py:54
passWord = models.CharField(
    '用户密码',
    db_column='pass_word',
    max_length=255,  # 改为255
    null=False
)
```

#### 步骤2: 创建迁移
```bash
cd source/server
python manage.py makemigrations
python manage.py migrate
```

#### 步骤3: 测试现有密码
```python
# 验证现有密码是否可用
python manage.py shell
>>> from app.models import Users
>>> u = Users.objects.first()
>>> u.check_password('123456')  # 应该返回True
```

**预计工作量**: 4小时（包括测试）

---

### 4. N+1查询问题 🐌 **性能**
**文件**: 多个视图文件

**问题示例**:
```python
# 未优化 - 每次访问外键都触发新查询
exam_logs = ExamLogs.objects.all()
for log in exam_logs:
    print(log.student.name)  # 额外查询
    print(log.exam.name)     # 额外查询
```

**修复方案**:
```python
# 优化后 - 一次查询获取所有数据
exam_logs = ExamLogs.objects.select_related(
    'student',
    'exam',
    'exam__project',
    'exam__grade'
).all()

# 对于一对多关系，使用prefetch_related
exam_logs = ExamLogs.objects.select_related(
    'student', 'exam'
).prefetch_related('answerlogs_set')
```

**需要优化的查询**:
- ✅ `sys_view.py` - 已使用select_related
- ❌ `exam_views.py` - 需要优化
- ❌ `practice_views.py` - 需要优化
- ❌ `user_views.py` - 需要优化

**预计工作量**: 8小时

---

### 5. API文档缺失 📚 **可用性**
**问题**: 缺少交互式API文档

**修复方案**:

#### 步骤1: 安装drf-yasg
```bash
pip install drf-yasg
```

#### 步骤2: 添加到requirements.txt
```
drf-yasg>=1.21.0
```

#### 步骤3: 配置settings.py
```python
# source/server/server/settings.py

INSTALLED_APPS = [
    ...
    'drf_yasg',
    'rest_framework',
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Token格式: Bearer <token>'
        }
    }
}
```

#### 步骤4: 配置URLs
```python
# source/server/app/urls.py
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ...
]
```

**访问地址**:
- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

**预计工作量**: 16小时（包括编写API文档注释）

---

## 📋 中优先级问题（近期修复）

### 6. 重复代码消除

**问题**: 用户信息获取代码重复14次

**修复方案**:
```python
# app/utils/helpers.py（新建）
def get_user_with_cache(user_id):
    """获取用户信息（带缓存）"""
    cache_key = f'user:{user_id}'
    user = cache.get(cache_key)
    if not user:
        user = Users.objects.select_related('students', 'teachers').get(id=user_id)
        cache.set(cache_key, user, 300)  # 缓存5分钟
    return user
```

---

### 7. 错误处理改进

**问题**: 大量裸Exception捕获

**修复方案**:
```python
# app/exceptions.py（新建）
class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message, code=2, details=None):
        self.message = message
        self.code = code
        self.details = details

class ValidationException(AppException):
    """数据验证异常"""
    pass

class NotFoundException(AppException):
    """资源不存在异常"""
    pass

# 使用示例
try:
    user = Users.objects.get(id=user_id)
except Users.DoesNotExist:
    raise NotFoundException('用户不存在')
```

---

### 8. 日志记录扩展

**修复方案**:
```python
# app/middleware/logging_middleware.py（新建）
import logging
import time
from django.utils.deprecation import Deprecated

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """请求日志中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # 记录慢请求
        if duration > 1.0:
            logger.warning(
                f"慢请求: {request.method} {request.path} "
                f"耗时: {duration:.2f}s"
            )

        return response
```

---

## 🔧 低优先级改进（长期优化）

### 9. 测试覆盖率提升
- 目标: 80%+代码覆盖率
- 工具: pytest + coverage

### 10. 移动端优化
- 响应式设计完善
- 触摸交互优化
- PWA实现

### 11. 性能监控
- 集成Sentry进行错误追踪
- 实现APM监控
- 添加性能指标收集

---

## 🚀 自动化修复脚本

创建自动化脚本 `auto_fix.sh`:

```bash
#!/bin/bash
# FYP项目自动修复脚本

echo "=== FYP项目自动改进工具 ==="
echo ""

# 1. 备份当前代码
echo "📦 创建备份..."
git add . && git commit -m "自动改进前的备份"

# 2. 修复XSS漏洞
echo "🔒 修复XSS漏洞..."
# 自动替换v-html为文本插值

# 3. 移除硬编码密钥
echo "🔐 移除硬编码密钥..."
# 自动从docker-compose.yml移除敏感信息

# 4. 更新依赖
echo "📦 更新依赖..."
pip install -r requirements.txt

# 5. 运行测试
echo "🧪 运行测试..."
python manage.py test

# 6. 代码质量检查
echo "🔍 代码质量检查..."
flake8 app/
black app/

echo "✅ 自动修复完成！"
```

---

## 📊 改进优先级矩阵

```
紧急且重要     │ 重要不紧急
─────────────────────────────────
• XSS漏洞      │ • API文档
• API密钥泄露  │ • 测试覆盖
• 密码字段     │ • 日志系统
─────────────────────────────────
紧急不重要     │ 不重要不紧急
─────────────────────────────────
• (无)        │ • 代码注释
              │ • 移动端优化
──────────────────────────��──────
```

---

## ✅ 实施建议

### 第一周（安全修复）
1. ✅ 修复XSS漏洞
2. ✅ 移除硬编码密钥
3. ✅ 修复密码字段

### 第二周（性能优化）
4. ✅ 优化数据库查询
5. ✅ 添加缓存机制

### 第三-四周（文档和测试）
6. ✅ 集成API文档
7. ✅ 提升测试覆盖率

### 后续（持续改进）
8. ⏳ 代码质量提升
9. ⏳ 移动端优化
10. ⏳ 性能监控

---

## 📝 改进记录

每次改进后，记录到 `IMPROVEMENT_LOG.md`:

```markdown
## [日期] - 改进记录

### 修复的问题
- [ ] XSS漏洞修复
- [ ] API密钥移除
- [ ] 密码字段修复

### 测试结果
- 所有测试通过 ✅
- 无回归问题 ✅

### Git提交
- Commit: abc123
- 分支: improvement/security-fix
```

---

**总结**: 通过系统化的改进计划，FYP项目可以在保证安全的前提下，逐步提升代码质量、性能和可维护性。

**下一步**: 开始执行第一周的安全修复任务。
