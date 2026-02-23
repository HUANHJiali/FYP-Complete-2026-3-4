# 🐳 Docker 部署指南

## 📋 简介

本文档介绍如何使用 Docker 和 Docker Compose 一键部署 FYP2025 智能考试系统。

### ✨ 优势

- **零配置**：无需安装 Python、Node.js、MySQL 等开发环境
- **隔离性强**：容器化部署，不影响本地环境
- **一键启动**：一条命令即可启动所有服务
- **易于协作**：团队成员使用相同的容器环境
- **快速重置**：随时可以删除容器并重新开始

## 📦 系统要求

### 必需软件

- ✅ **Docker Desktop** - [Windows](https://www.docker.com/products/docker-desktop-windows/) / [Mac](https://www.docker.com/products/docker-desktop-mac/) / [Linux](https://docs.docker.com/engine/install/)
- ✅ **Git

> **注意**：**不要**在本机安装 MySQL、Python、Node.js。Docker 会处理所有依赖。

## 🚀 快速开始

### 方法1：一键启动（推荐）

#### Windows 用户

```cmd
# 1. 克隆项目
git clone https://github.com/HUANHJiali/25FYP.git
cd 25FYP

# 2. 运行启动脚本
docker-start.bat
```

#### Linux/Mac 用户

```bash
# 1. 克隆项目
git clone https://github.com/HUANHJiali/25FYP.git
cd 25FYP

# 2. 添加执行权限并运行
chmod +x docker-start.sh
./docker-start.sh
```

### 方法2：使用 Docker Compose

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📁 项目结构

```
FYP2025/
├── docker/                      # Docker 配置文件目录
│   ├── backend/               # 后端 Docker 配置
│   │   ├── Dockerfile         # 后端镜像定义
│   │   └── start.sh           # 启动脚本
│   └── frontend/              # 前端 Docker 配置
│       ├── Dockerfile         # 开发环境镜像
│       ├── Dockerfile.prod    # 生产环境镜像
│       └── nginx.conf         # Nginx 配置
├── docker-compose.yml          # 服务编排文件
├── docker-start.bat            # Windows 启动脚本
├── docker-start.sh             # Linux/Mac 启动脚本
├── source/                     # 源代码
│   ├── server/               # Django 后端
│   └── client/               # Vue.js 前端
└── database/                  # 数据库文件
    ├── db_exam.sql           # 数据库结构
    └── init_practice_data.sql # 初始数据
```

## 🌐 访问地址

启动成功后，访问以下地址：

- **前端界面**: http://localhost:8080
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin
- **数据库**: localhost:3306

## 👤 默认账户

| 角色   | 用户名   | 密码   | 说明           |
|------|--------|--------|---------------|
| 管理员 | admin  | 123456 | 系统管理员      |
| 教师   | teacher| 123456 | 教师账户        |
| 学生   | student| 123456 | 学生账户        |

## 🛠️ 常用命令

### 查看服务状态

```bash
# 查看运行中的容器
docker-compose ps

# 查看所有容器（包括停止的）
docker-compose ps -a
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止和删除

```bash
# 停止服务（保留数据）
docker-compose stop

# 停止并删除容器和数据卷
docker-compose down -v
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec db mysql -u examuser -pexam123456 db_exam
```

### 重新构建

```bash
# 重新构建镜像
docker-compose build

# 强制重新构建（不使用缓存）
docker-compose build --no-cache
```

## 🔧 高级配置

### 修改环境变量

编辑 `docker-compose.yml` 文件中的 `environment` 部分：

```yaml
backend:
  environment:
    DEBUG: "True"  # 开发模式
    # 或
    DEBUG: "False" # 生产模式
```

### 配置 AI 功能

1. 获取智谱 AI API 密钥：https://open.bigmodel.cn/
2. 修改 `docker-compose.yml`：

```yaml
backend:
  environment:
    ZHIPUAI_API_KEY: "your-api-key"
```

3. 重启服务：

```bash
docker-compose down
docker-compose up -d
```

### 数据持久化

Docker Compose 会自动创建数据卷存储数据：

- `mysql_data`：数据库数据
- `backend_static`：静态文件
- `backend_media`：媒体文件

### 查看数据卷

```bash
# 查看所有数据卷
docker volume ls

# 查看特定数据卷
docker volume inspect fyp2025_mysql_data
```

## 🐛 故障排除

### 问题1：端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 改为其他端口
```

### 问题2：数据库连接失败

```bash
# 检查数据库服务状态
docker-compose logs db

# 重启数据库
docker-compose restart db
```

### 问题3：镜像构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### 问题4：权限问题（Linux）

```bash
# 添加执行权限
chmod +x docker-start.sh

# 或使用 sudo
sudo ./docker-start.sh
```

## 📊 服务说明

### MySQL 数据库服务

- **容器名**: `fyp_mysql`
- **端口**: `3306`
- **用户名**: `examuser`
- **密码**: `exam123456`
- **数据库名**: `db_exam`

### Django 后端服务

- **容器名**: `fyp_backend`
- **端口**: `8000`
- **工作目录**: `/app`
- **自动功能**：
  - 数据库迁移
  - 收集静态文件
  - 创建管理员账户

### Vue.js 前端服务

- **容器名**: `fyp_frontend`
- **端口**: `8080`
- **热重载**: 支持代码修改实时更新

## 🎯 生产环境部署

### 使用生产环境镜像

修改 `docker-compose.yml` 使用生产镜像：

```yaml
frontend:
  build:
    context: ./source/client
    dockerfile: ../../docker/frontend/Dockerfile.prod
  # ... 其他配置
```

### 使用 Nginx 反向代理

前端会自动使用 Nginx 服务静态文件，并代理后端 API 请求。

## 🔒 安全建议

1. **修改默认密码**：修改 MySQL root 密码和数据库用户密码
2. **设置 SECRET_KEY**：生成新的 Django SECRET_KEY
3. **配置 HTTPS**：生产环境配置 SSL 证书
4. **限制访问**：配置防火墙规则
5. **定期备份**：备份 MySQL 数据卷

## 📚 相关文档

- [README.md](README.md) - 项目总体说明
- [source/快速启动.md](source/快速启动.md) - 快速启动指南
- [source/組員部署指南.md](source/組員部署指南.md) - 组员部署指南

## 💡 提示

1. 第一次启动可能需要较长时间（下载镜像和构建）
2. 使用 `-d` 参数在后台运行服务
3. 使用 `docker-compose logs -f` 实时查看日志
4. 遇到问题先查看日志：`docker-compose logs service_name`

## ✅ 快速检查清单

部署前：
- [ ] 已安装 Docker Desktop
- [ ] Docker 服务已启动
- [ ] 已克隆项目代码

部署后：
- [ ] 后端服务运行正常（http://localhost:8000）
- [ ] 前端服务运行正常（http://localhost:8080）
- [ ] 数据库连接正常
- [ ] 可以访问管理后台
- [ ] 可以登录测试账户

---

**🎉 祝部署顺利！如有问题，请查看日志或联系项目负责人。**
