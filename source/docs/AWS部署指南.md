# ☁️ AWS Academy Learner Lab 部署指南

## 📋 简介

本指南专门针对 **AWS Academy Learner Lab** 环境，帮助你使用 $50 免费额度将 FYP 项目部署到 AWS 云端。

### ✨ AWS Learner Lab 特点

- ✅ $50 免费额度（足够完成 FYP 项目）
- ✅ 提供 EC2、RDS、S3 等核心服务
- ✅ 适合学习和演示
- ⚠️ 某些高级服务可能不可用
- ⚠️ 有资源限制（如实例类型限制）

---

## 🎯 推荐部署方案

### 方案对比

| 方案 | 成本/月 | 复杂度 | 适用场景 |
|------|---------|--------|----------|
| **EC2 + Docker** | ~$10-20 | 低 | ✅ 推荐：简单易用 |
| **ECS Fargate** | ~$15-30 | 中 | 容器化部署 |
| **Elastic Beanstalk** | ~$10-25 | 低 | 自动化部署 |
| **EC2 + RDS** | ~$20-40 | 中 | 需要独立数据库 |

**推荐方案：EC2 + Docker（最简单，成本最低）**

---

## 🚀 方案一：EC2 + Docker（推荐）

### 前置准备

1. **登录 AWS Academy**
   - 访问：https://awsacademy.instructure.com
   - 启动 Learner Lab
   - 获取临时 AWS 凭证

2. **选择区域**
   - 推荐：`us-east-1` (N. Virginia) 或 `ap-southeast-1` (Singapore)
   - 注意：某些区域在 Learner Lab 中可能不可用

### 步骤 1: 创建 EC2 实例

#### 1.1 启动 EC2 实例

1. 登录 AWS Console
2. 进入 **EC2** 服务
3. 点击 **Launch Instance**

#### 1.2 配置实例

**基本信息：**
- **Name**: `fyp-exam-system`
- **AMI**: `Ubuntu Server 22.04 LTS` (免费层)
- **Instance Type**: `t2.micro` 或 `t3.micro` (免费层)
  - 如果免费层不可用，选择 `t2.small` (~$15/月)

**密钥对：**
- 创建新密钥对：`fyp-keypair`
- 下载 `.pem` 文件并保存

**网络设置：**
- **VPC**: 使用默认 VPC
- **Subnet**: 任意可用区
- **Auto-assign Public IP**: Enable
- **Security Group**: 创建新安全组
  - 规则 1: SSH (22) - 来源: My IP
  - 规则 2: HTTP (80) - 来源: 0.0.0.0/0
  - 规则 3: HTTPS (443) - 来源: 0.0.0.0/0
  - 规则 4: Custom TCP (8000) - 来源: 0.0.0.0/0 (后端 API)

**存储：**
- **Volume Size**: 20 GB (gp3, 免费层)
- 或 30 GB 如果需要更多空间

**启动实例**

#### 1.3 获取实例信息

- 记录 **Public IPv4 address** (例如: `54.123.45.67`)
- 记录 **Instance ID**

### 步骤 2: 连接 EC2 实例

#### Windows (使用 PowerShell)

```powershell
# 设置密钥权限
icacls fyp-keypair.pem /inheritance:r
icacls fyp-keypair.pem /grant:r "$env:USERNAME:R"

# 连接实例
ssh -i fyp-keypair.pem ubuntu@your-ec2-ip
```

#### Mac/Linux

```bash
# 设置密钥权限
chmod 400 fyp-keypair.pem

# 连接实例
ssh -i fyp-keypair.pem ubuntu@your-ec2-ip
```

### 步骤 3: 在 EC2 上安装 Docker

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 将当前用户添加到 docker 组（避免每次使用 sudo）
sudo usermod -aG docker ubuntu

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version

# 重新登录以应用组权限（或执行）
newgrp docker
```

### 步骤 4: 上传项目代码

#### 方法 A: 使用 Git（推荐）

```bash
# 在 EC2 上
cd /home/ubuntu
git clone https://github.com/your-username/25FYP.git
cd 25FYP
```

#### 方法 B: 使用 SCP

```bash
# 在本地执行
scp -i fyp-keypair.pem -r /path/to/25FYP ubuntu@your-ec2-ip:/home/ubuntu/
```

#### 方法 C: 使用 AWS CodeCommit（如果可用）

```bash
# 在 EC2 上
git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/25FYP
```

### 步骤 5: 配置环境变量

```bash
cd /home/ubuntu/25FYP

# 生成 SECRET_KEY
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')

# 创建 .env 文件
cat > .env << EOF
# 数据库配置
DB_HOST=db
DB_PORT=3306
DB_NAME=db_exam
DB_USER=examuser
DB_PASSWORD=Exam123456!

# Django 配置
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,ec2-54-123-45-67.compute-1.amazonaws.com

# CORS 配置
CORS_ALLOWED_ORIGINS=http://your-ec2-ip,http://ec2-54-123-45-67.compute-1.amazonaws.com

# AI 配置（如果有）
ZHIPUAI_API_KEY=your-api-key
ZHIPUAI_MODEL=glm-4-flash
EOF

# 查看配置
cat .env
```

### 步骤 6: 修改 docker-compose.yml 用于生产

```bash
# 备份原文件
cp docker-compose.yml docker-compose.yml.bak

# 创建生产配置
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: fyp_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:-Exam123456!}
      MYSQL_DATABASE: ${DB_NAME:-db_exam}
      MYSQL_USER: ${DB_USER:-examuser}
      MYSQL_PASSWORD: ${DB_PASSWORD:-Exam123456!}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/db_exam.sql:/docker-entrypoint-initdb.d/01-structure.sql:ro
    ports:
      - "127.0.0.1:3306:3306"
    networks:
      - fyp_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./source/server
      dockerfile: ../../docker/backend/Dockerfile
    container_name: fyp_backend
    restart: always
    depends_on:
      db:
        condition: service_healthy
    command: >
      bash -c "
      sleep 5 &&
      python manage.py migrate --noinput &&
      python manage.py collectstatic --noinput &&
      gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
      "
    environment:
      - DB_HOST=db
      - DB_PORT=3306
      - DB_NAME=${DB_NAME:-db_exam}
      - DB_USER=${DB_USER:-examuser}
      - DB_PASSWORD=${DB_PASSWORD:-Exam123456!}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    volumes:
      - ./source/server:/app
      - static_files:/app/staticfiles
    ports:
      - "8000:8000"
    networks:
      - fyp_network

  frontend:
    build:
      context: ./source/client
      dockerfile: ../../docker/frontend/Dockerfile.prod
    container_name: fyp_frontend
    restart: always
    depends_on:
      - backend
    environment:
      - VUE_APP_API_BASE_URL=http://your-ec2-ip:8000
    ports:
      - "80:80"
    networks:
      - fyp_network

volumes:
  mysql_data:
  static_files:

networks:
  fyp_network:
    driver: bridge
EOF

# 替换 EC2 IP
sed -i "s/your-ec2-ip/$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/g" docker-compose.prod.yml
```

### 步骤 7: 确保 requirements.txt 包含 gunicorn

```bash
# 检查并添加 gunicorn
if ! grep -q "gunicorn" source/server/requirements.txt; then
    echo "gunicorn==21.2.0" >> source/server/requirements.txt
fi
```

### 步骤 8: 构建并启动服务

```bash
# 加载环境变量
export $(cat .env | xargs)

# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 步骤 9: 验证部署

```bash
# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 测试后端 API
curl http://localhost:8000/api/projects/all/

# 测试前端
curl http://localhost/
```

### 步骤 10: 访问系统

在浏览器中访问：
- **前端**: `http://your-ec2-ip`
- **后端 API**: `http://your-ec2-ip:8000`

---

## 🔒 配置安全组（重要）

### 更新安全组规则

1. 进入 **EC2 Console** → **Security Groups**
2. 选择你的安全组
3. 编辑入站规则，确保有以下规则：

| 类型 | 协议 | 端口范围 | 来源 |
|------|------|----------|------|
| SSH | TCP | 22 | My IP |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 |

---

## 💰 成本优化建议

### 1. 使用免费层资源

- **EC2**: `t2.micro` 或 `t3.micro` (750 小时/月免费)
- **EBS**: 30 GB gp3 存储 (免费层)
- **数据传输**: 15 GB 出站流量/月 (免费层)

### 2. 停止不使用的实例

```bash
# 停止实例（不删除数据）
# 在 AWS Console: EC2 → Instances → Stop Instance

# 启动实例
# EC2 → Instances → Start Instance
```

### 3. 监控成本

- 进入 **AWS Cost Explorer**
- 设置预算警报（例如：$40 警告，$45 停止）

### 4. 使用 Spot Instances（高级）

如果 Learner Lab 支持，可以使用 Spot Instances 节省成本。

---

## 🌐 配置域名（可选）

### 使用 Route 53（如果可用）

1. 进入 **Route 53** 服务
2. 创建托管区域
3. 添加 A 记录指向 EC2 公网 IP
4. 更新 `.env` 中的 `ALLOWED_HOSTS`

### 使用免费域名服务

- **Freenom**: 提供免费 .tk, .ml, .ga 域名
- **No-IP**: 提供免费动态 DNS

---

## 📊 监控和日志

### CloudWatch（如果可用）

```bash
# 安装 CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### 本地日志查看

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

---

## 🔄 更新代码

```bash
# 在 EC2 上
cd /home/ubuntu/25FYP

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

---

## 🗄️ 使用 RDS（可选，如果预算允许）

### 创建 RDS MySQL 实例

1. 进入 **RDS** 服务
2. 创建数据库
   - **Engine**: MySQL 8.0
   - **Template**: Free tier (如果可用)
   - **Instance class**: db.t2.micro
   - **Storage**: 20 GB
   - **Master username**: examuser
   - **Master password**: 设置强密码

3. 配置安全组，允许 EC2 访问

4. 更新 `.env`:

```bash
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=3306
DB_NAME=db_exam
DB_USER=examuser
DB_PASSWORD=your-password
```

5. 导入数据：

```bash
mysql -h your-rds-endpoint -u examuser -p db_exam < database/db_exam.sql
```

6. 从 `docker-compose.prod.yml` 删除 `db` 服务

---

## 🐛 常见问题

### Q1: 无法连接 EC2

**检查：**
- 安全组是否允许 SSH (22) 端口
- 密钥文件权限是否正确
- 实例是否正在运行

### Q2: 服务无法访问

**检查：**
- 安全组是否开放 80, 443, 8000 端口
- 服务是否正常运行：`docker-compose ps`
- 查看日志：`docker-compose logs`

### Q3: 内存不足

**解决方案：**
```bash
# 创建交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Q4: 成本超出预算

**解决方案：**
- 停止不使用的实例
- 使用更小的实例类型
- 删除不需要的资源
- 设置成本警报

### Q5: Learner Lab 限制

**常见限制：**
- 某些区域不可用
- 某些服务不可用（如某些高级 EC2 类型）
- 资源配额限制

**解决方案：**
- 使用默认区域
- 选择免费层资源
- 联系导师获取帮助

---

## 📝 部署检查清单

- [ ] EC2 实例已创建并运行
- [ ] 安全组规则已配置
- [ ] 已成功 SSH 连接到实例
- [ ] Docker 和 Docker Compose 已安装
- [ ] 项目代码已上传
- [ ] 环境变量已配置
- [ ] 服务已启动并运行
- [ ] 前端可以访问
- [ ] 后端 API 可以访问
- [ ] 数据库连接正常
- [ ] 成本监控已设置

---

## 💡 演示建议

### 1. 准备演示脚本

```bash
# 创建演示脚本
cat > demo.sh << 'EOF'
#!/bin/bash
echo "=== FYP 系统演示 ==="
echo "1. 前端地址: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "2. 后端 API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "3. 服务状态:"
docker-compose ps
EOF
chmod +x demo.sh
```

### 2. 截图准备

- AWS Console 截图（EC2、安全组）
- 系统运行截图
- 成本监控截图

### 3. 演示流程

1. 展示 AWS 架构图
2. 展示系统运行状态
3. 演示主要功能
4. 展示成本控制

---

## 📚 相关资源

- [AWS Academy 文档](https://awsacademy.instructure.com)
- [AWS EC2 文档](https://docs.aws.amazon.com/ec2/)
- [Docker 文档](https://docs.docker.com/)
- [项目 Docker 部署指南](../DOCKER_DEPLOYMENT.md)

---

## 🎯 快速命令参考

```bash
# 连接 EC2
ssh -i fyp-keypair.pem ubuntu@your-ec2-ip

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 更新代码
git pull && docker-compose -f docker-compose.prod.yml up -d --build

# 查看成本
# 在 AWS Console: Cost Explorer
```

---

**🎉 祝你 FYP 部署顺利！如有问题，请查看日志或联系导师。**




