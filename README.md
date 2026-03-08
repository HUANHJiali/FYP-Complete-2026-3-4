# 运行说明

本仓库当前保留了应用源码、Docker 部署文件，以及 Terraform/CDK 基础设施目录。

## 1. 当前可用性

- 本地运行：可用
- Docker 开发环境：可用
- Docker 生产环境：可用，但必须先补齐生产环境变量
- 服务器部署：可用，建议使用 `deploy/setup_server.sh`
- Terraform：已通过 `terraform init -backend=false` 和 `terraform validate`
- CDK：当前不可直接使用，缺少 `infrastructure/cdk/lib/fyp-ha-stack.ts`

## 2. 目录说明

- `source/client`：Vue 前端
- `source/server`：Django 后端
- `docker-compose.yml`：本地 Docker 开发启动
- `docker-compose.prod.yml`：生产 Docker 启动
- `deploy`：服务器部署脚本和 Nginx/systemd 配置
- `infrastructure/terraform`：Terraform 基础设施代码
- `infrastructure/cdk`：CDK 基础设施代码（当前不完整）

## 3. 本地运行

### 3.1 环境要求

- Python 3.10 或 3.11
- Node.js 18+
- MySQL 8

### 3.2 准备环境变量

在 `source` 目录中复制环境模板：

```powershell
Copy-Item source/env.example source/.env
```

至少修改以下配置：

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

如果不使用 AI，可将 `ZHIPUAI_API_KEY` 留空。

### 3.3 启动后端

```powershell
Set-Location source/server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3.4 启动前端

新开一个终端：

```powershell
Set-Location source/client
npm install
npm run serve
```

默认访问地址：

- 前端：`http://localhost:8080`
- 后端：`http://localhost:8000`

## 4. Docker 开发运行

### 4.1 直接启动

```powershell
docker compose up -d --build
```

或使用仓库自带脚本：

```powershell
.\docker-start.bat
```

### 4.2 默认端口

- 前端：`http://localhost:8080`
- 后端：`http://localhost:8000`
- MySQL：`localhost:3307`

### 4.3 停止

```powershell
docker compose down
```

## 5. Docker 生产运行

### 5.1 准备生产环境变量

将根目录的生产模板复制为 `.env`：

```powershell
Copy-Item .env.production.example .env
```

至少填写以下变量：

- `SECRET_KEY`
- `MYSQL_ROOT_PASSWORD`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

### 5.2 启动

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

### 5.3 停止

```powershell
docker compose -f docker-compose.prod.yml down
```

默认端口：

- 前端：`http://localhost`
- 后端：`http://localhost:8000`

## 6. 服务器部署

适用于已经准备好的 Linux 云服务器。

### 6.1 基础要求

- Ubuntu 20.04/22.04+
- 已安装 Git
- 服务器已放通 80、443、8000 端口

### 6.2 推荐方式

```bash
sudo bash deploy/setup_server.sh \
  --project-root /opt/FYP2025-main \
  --domain your.domain.com \
  --env-file /etc/exam/.env \
  --db-import no
```

说明：

- `--db-import no` 表示使用 Django migration 建表
- 若你有现成 SQL 数据库文件，可改为 `yes`

## 7. Terraform 使用

Terraform 当前可用。

### 7.1 基本命令

```powershell
Set-Location infrastructure/terraform
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
terraform plan
```

使用前需要准备：

- AWS 凭证
- `terraform.tfvars` 中的实际变量值

## 8. CDK 状态

CDK 目录已恢复，但当前不能直接 `build` 或 `synth`。

原因：

- `infrastructure/cdk/bin/fyp-cdk.ts` 引用了缺失文件 `../lib/fyp-ha-stack`

因此当前建议：

- 基础设施优先使用 Terraform
- 不要把 CDK 作为当前版本的可运行入口

## 9. 补充说明

- 如果只想最快启动，优先使用 `docker compose up -d --build`
- 如果要提交答辩或演示，优先使用 Docker 生产版或服务器部署
- 如果不使用 AI 功能，可以不填写 `ZHIPUAI_API_KEY`
