# 智能考试系统后端服务

## 项目概述
基于Django 4.1.3的智能考试系统后端服务，提供REST API接口和AI集成功能。

## 技术栈
- **框架**: Django 4.1.3
- **数据库**: MySQL 8.0
- **AI服务**: 智谱AI (GLM-4-Flash)
- **认证**: JWT Token
- **API**: Django REST Framework

## 本地开发部署

### 1. 环境准备
```bash
# 确保已安装Python 3.9+
python --version

# 确保MySQL服务运行
# Windows: 启动MySQL服务
# Linux/Mac: sudo service mysql start
```

### 2. 数据库设置
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# 导入数据库结构
mysql -u root -p db_exam < ../database/db_exam.sql
mysql -u root -p db_exam < ../database/init_practice_data.sql
```

### 3. 安装依赖
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 环境配置
```bash
# 复制环境配置文件
cp ../env.example ../.env

# 编辑.env文件，设置数据库连接信息
# DB_NAME=db_exam
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
```

### 5. 运行服务
```bash
# 运行数据库迁移
python manage.py migrate

# 创建管理员账户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

## API接口

### 认证接口
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `POST /api/auth/register/` - 用户注册

### 用户管理
- `GET /api/users/` - 获取用户列表
- `GET /api/users/{id}/` - 获取用户详情
- `PUT /api/users/{id}/` - 更新用户信息

### 考试管理
- `GET /api/exams/` - 获取考试列表
- `POST /api/exams/` - 创建考试
- `GET /api/exams/{id}/` - 获取考试详情

### AI功能
- `POST /api/ai/score/` - AI智能评分
- `POST /api/ai/generate/` - AI自动出题

## 项目结构
```
server/
├── app/                    # 主应用
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图函数
│   ├── urls.py            # URL路由
│   └── migrations/        # 数据库迁移
├── comm/                  # 公共工具
│   ├── AIUtils.py         # AI工具类
│   ├── BaseView.py        # 基础视图
│   └── CommUtils.py       # 通用工具
├── server/                # Django配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # 主URL配置
│   └── wsgi.py            # WSGI配置
├── manage.py              # Django管理脚本
└── requirements.txt       # Python依赖
```

## 开发指南

### 添加新功能
1. 在`app/models.py`中定义数据模型
2. 在`app/views.py`中实现视图逻辑
3. 在`app/urls.py`中添加URL路由
4. 运行`python manage.py makemigrations`创建迁移
5. 运行`python manage.py migrate`应用迁移

### 测试
```bash
# 运行所有测试
python manage.py test

# 运行特定测试
python manage.py test app.tests.TestClass
```

### 调试
```bash
# 启用调试模式
# 在settings.py中设置DEBUG=True

# 查看SQL查询
# 在settings.py中设置LOGGING配置
```

## 部署注意事项

1. **环境变量**: 使用 `.env` 管理，生产建议放置 `/etc/exam/.env` 并在 systemd 中通过 `EnvironmentFile` 加载；确保 `ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`、`CSRF_TRUSTED_ORIGINS` 正确
2. **数据库**: 确保MySQL服务正常运行
3. **AI配置**: 配置智谱AI API密钥（仅在启用AI功能时需要）
4. **静态文件**: 生产环境运行 `python manage.py collectstatic --noinput` 并由 Nginx 提供 `/static/`、`/media/`
5. **安全设置**: 生产设置 `DEBUG=False`，更换强随机 `SECRET_KEY`
6. **驱动兼容**: Windows 上如 `mysqlclient` 构建失败，可使用 `PyMySQL` 作为兼容方案

### 生产部署（快速参考）

推荐在仓库根目录使用一键脚本：

```bash
sudo bash deploy/setup_server.sh \
  --project-root /path/to/FYP2025-main \
  --domain your.domain.com \
  --env-file /etc/exam/.env \
  --db-import yes
```

示例 Nginx 与 systemd 配置见 `deploy/nginx.conf`、`deploy/exam-gunicorn.service`。

## 故障排除

### 常见问题
1. **数据库连接失败**: 检查MySQL服务和连接配置
2. **AI功能异常**: 检查智谱AI API密钥配置
3. **权限错误**: 检查用户权限和JWT配置
4. **端口占用**: 检查8000端口是否被占用

### 日志查看
```bash
# 查看Django日志
tail -f logs/django.log

# 查看错误日志
tail -f logs/error.log
```

## 联系信息
如有问题，请查看项目文档或联系开发团队。