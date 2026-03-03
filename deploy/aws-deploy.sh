#!/bin/bash

# AWS EC2 部署脚本
# 使用方法: 在 EC2 实例上运行此脚本

set -e

echo "🚀 开始 AWS EC2 部署..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取 EC2 公网 IP（添加错误处理）
EC2_IP=$(curl -s --max-time 5 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
EC2_HOSTNAME=$(curl -s --max-time 5 http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || echo "")

# 如果无法获取，尝试其他方法
if [ -z "$EC2_IP" ] || [[ "$EC2_IP" == *"401"* ]] || [[ "$EC2_IP" == *"Unauthorized"* ]]; then
    echo -e "${YELLOW}无法从 metadata 服务获取 IP，使用 localhost${NC}"
    EC2_IP="localhost"
    EC2_HOSTNAME="localhost"
else
    echo -e "${BLUE}检测到 EC2 信息:${NC}"
    echo -e "  IP: ${GREEN}${EC2_IP}${NC}"
    echo -e "  Hostname: ${GREEN}${EC2_HOSTNAME}${NC}"
fi

# 检查是否为 root 或 ubuntu 用户
if [ "$USER" != "root" ] && [ "$USER" != "ubuntu" ]; then
    echo -e "${RED}请使用 root 或 ubuntu 用户运行此脚本${NC}"
    exit 1
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker 未安装，开始安装...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    # 将当前用户添加到 docker 组
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker 安装完成${NC}"
    echo -e "${YELLOW}请重新登录或执行: newgrp docker${NC}"
fi

# 检查 Docker Compose（优先使用 docker-compose，如果没有则尝试 docker compose）
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Docker Compose 未安装，开始安装...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose 安装完成${NC}"
fi

# 设置 docker-compose 命令别名（如果使用 docker compose）
if ! command -v docker-compose &> /dev/null && docker compose version &> /dev/null; then
    alias docker-compose='docker compose'
fi

# 验证安装
docker --version
docker-compose --version

# 获取配置信息（非交互式，使用环境变量或默认值）
echo ""
echo -e "${BLUE}=== 配置信息 ===${NC}"
DB_PASSWORD=${DB_PASSWORD:-Exam123456!}
echo -e "${GREEN}使用数据库密码: ${DB_PASSWORD}${NC}"

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || openssl rand -base64 32)
    echo -e "${GREEN}已自动生成 SECRET_KEY${NC}"
else
    echo -e "${GREEN}使用提供的 SECRET_KEY${NC}"
fi

# 创建 .env 文件
echo -e "${YELLOW}创建环境变量文件...${NC}"
cat > .env << EOF
# 数据库配置
DB_HOST=db
DB_PORT=3306
DB_NAME=db_exam
DB_USER=examuser
DB_PASSWORD=${DB_PASSWORD}
MYSQL_ROOT_PASSWORD=${DB_PASSWORD}

# Django 配置
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${EC2_IP},${EC2_HOSTNAME},localhost,127.0.0.1

# CORS 配置
CORS_ALLOWED_ORIGINS=http://${EC2_IP},http://${EC2_HOSTNAME}

# AI 配置（可选）
ZHIPUAI_API_KEY=${ZHIPUAI_API_KEY:-}
ZHIPUAI_MODEL=glm-4-flash
EOF

echo -e "${GREEN}环境变量已配置${NC}"

# 确保在项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}当前工作目录: $(pwd)${NC}"

# 使用项目根目录的 docker-compose.prod.yml（如果存在）
if [ -f "docker-compose.prod.yml" ]; then
    echo -e "${GREEN}使用现有的 docker-compose.prod.yml${NC}"
    # 确保环境变量正确替换（如果需要，转义特殊字符）
    if grep -q "EC2_IP_PLACEHOLDER" docker-compose.prod.yml 2>/dev/null; then
        ESCAPED_IP=$(echo "$EC2_IP" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i "s/EC2_IP_PLACEHOLDER/${ESCAPED_IP}/g" docker-compose.prod.yml
    fi
    # 更新 VUE_APP_API_BASE_URL 环境变量
    if grep -q "VUE_APP_API_BASE_URL" docker-compose.prod.yml 2>/dev/null; then
        ESCAPED_IP=$(echo "$EC2_IP" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i "s|VUE_APP_API_BASE_URL=.*|VUE_APP_API_BASE_URL=http://${ESCAPED_IP}:8000|g" docker-compose.prod.yml
    fi
else
    echo -e "${YELLOW}创建生产环境配置...${NC}"
    cat > docker-compose.prod.yml << 'COMPOSE_EOF'
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
      (python manage.py init_data || echo '⚠️ 演示数据初始化失败，系统继续启动') &&
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
      - VUE_APP_API_BASE_URL=http://EC2_IP_PLACEHOLDER:8000
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
COMPOSE_EOF

    # 替换 EC2 IP
    sed -i "s/EC2_IP_PLACEHOLDER/${EC2_IP}/g" docker-compose.prod.yml
    echo -e "${GREEN}生产环境配置已创建${NC}"
fi

# 修复 requirements.txt（自动处理常见问题）
if [ -f "source/server/requirements.txt" ]; then
    # 移除 mysqlclient（避免编译慢，使用 pymysql 即可）
    if grep -q "mysqlclient" source/server/requirements.txt; then
        sed -i '/mysqlclient==/d' source/server/requirements.txt
        echo -e "${GREEN}已移除 mysqlclient（使用 pymysql 替代）${NC}"
    fi
    
    # 确保 gunicorn 存在
    if ! grep -q "gunicorn" source/server/requirements.txt; then
        echo "gunicorn==21.2.0" >> source/server/requirements.txt
        echo -e "${GREEN}已添加 gunicorn 到 requirements.txt${NC}"
    fi
fi

# 创建交换空间（如果内存不足）
if [ ! -f /swapfile ]; then
    echo -e "${YELLOW}创建交换空间（2GB）...${NC}"
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}交换空间已创建${NC}"
fi

# 构建并启动服务（已在项目根目录）
echo -e "${YELLOW}开始构建镜像（这可能需要几分钟，请耐心等待）...${NC}"
echo -e "${BLUE}提示: 已自动移除 mysqlclient，使用 pymysql 替代（避免编译慢）${NC}"

echo -e "${YELLOW}清理旧 Docker 缓存（释放磁盘）...${NC}"
docker system prune -af || true
docker volume prune -f || true

# 构建镜像（如果 timeout 命令可用，设置 30 分钟超时）
if command -v timeout &> /dev/null; then
    timeout 1800 docker-compose -f docker-compose.prod.yml build --no-cache || {
        echo -e "${YELLOW}构建超时或失败，尝试使用缓存构建...${NC}"
        docker-compose -f docker-compose.prod.yml build || {
            echo -e "${RED}构建失败，请查看日志: docker-compose -f docker-compose.prod.yml logs${NC}"
            exit 1
        }
    }
else
    # 如果没有 timeout 命令，直接构建
    docker-compose -f docker-compose.prod.yml build --no-cache || {
        echo -e "${YELLOW}构建失败，尝试使用缓存构建...${NC}"
        docker-compose -f docker-compose.prod.yml build || {
            echo -e "${RED}构建失败，请查看日志: docker-compose -f docker-compose.prod.yml logs${NC}"
            exit 1
        }
    }
fi

echo -e "${YELLOW}启动服务...${NC}"
MAX_UP_RETRIES=6
UP_RETRY=0
UP_OK=0
while [ $UP_RETRY -lt $MAX_UP_RETRIES ]; do
  if docker-compose -f docker-compose.prod.yml up -d; then
    UP_OK=1
    break
  fi
  UP_RETRY=$((UP_RETRY + 1))
  echo -e "${YELLOW}启动服务失败（第 ${UP_RETRY}/${MAX_UP_RETRIES} 次），等待数据库健康后重试...${NC}"
  docker-compose -f docker-compose.prod.yml ps || true
  sleep 15
done

if [ $UP_OK -ne 1 ]; then
  echo -e "${RED}多次尝试后服务仍启动失败，请检查日志${NC}"
  docker-compose -f docker-compose.prod.yml logs --tail=200 || true
  exit 1
fi

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 15

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker-compose -f docker-compose.prod.yml ps

# 等待数据库就绪
echo -e "${YELLOW}等待数据库就绪...${NC}"
sleep 10

# 执行数据库迁移（自动处理冲突）
echo -e "${YELLOW}执行数据库迁移...${NC}"
MAX_RETRIES=3
RETRY_COUNT=0
MIGRATION_OK=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput > /tmp/migrate.log 2>&1; then
    cat /tmp/migrate.log
        echo -e "${GREEN}数据库迁移成功${NC}"
    MIGRATION_OK=1
        break
    else
    cat /tmp/migrate.log
        if grep -q "already exists" /tmp/migrate.log; then
            echo -e "${YELLOW}检测到 migration 冲突，清空数据库重新迁移...${NC}"
            docker-compose -f docker-compose.prod.yml exec -T db mysql -uroot -p${DB_PASSWORD} -e "DROP DATABASE IF EXISTS db_exam; CREATE DATABASE db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || \
            docker-compose -f docker-compose.prod.yml exec -T db mysql -uexamuser -p${DB_PASSWORD} -e "DROP DATABASE IF EXISTS db_exam; CREATE DATABASE db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true
            sleep 5
            RETRY_COUNT=$((RETRY_COUNT + 1))
        else
            echo -e "${RED}数据库迁移失败，请查看日志${NC}"
            break
        fi
    fi
done

    if [ $MIGRATION_OK -ne 1 ]; then
      echo -e "${RED}迁移未成功，终止部署。${NC}"
      exit 1
    fi

# 收集静态文件
echo -e "${YELLOW}收集静态文件...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput || true

# 初始化演示数据（幂等，可重复执行）
echo -e "${YELLOW}初始化演示数据...${NC}"
INIT_DATA_RETRIES=${INIT_DATA_RETRIES:-3}
INIT_DATA_OK=0
for i in $(seq 1 "$INIT_DATA_RETRIES"); do
  if docker-compose -f docker-compose.prod.yml exec -T backend python manage.py init_data; then
    INIT_DATA_OK=1
    echo -e "${GREEN}演示数据初始化成功（第 ${i} 次）${NC}"
    break
  fi
  echo -e "${YELLOW}演示数据初始化失败（第 ${i}/${INIT_DATA_RETRIES} 次），5 秒后重试...${NC}"
  sleep 5
done

if [ $INIT_DATA_OK -ne 1 ]; then
  echo -e "${RED}演示数据初始化失败，终止部署。${NC}"
  exit 1
fi

# 校验是否确实存在基础数据，避免“服务可用但无数据”
USER_COUNT=$(docker-compose -f docker-compose.prod.yml exec -T backend python manage.py shell -c "from app import models; print(models.Users.objects.count())" 2>/dev/null | tail -n 1 | tr -d '\r')
if ! [[ "$USER_COUNT" =~ ^[0-9]+$ ]] || [ "$USER_COUNT" -le 0 ]; then
  echo -e "${RED}初始化后未检测到用户数据，终止部署。USER_COUNT=${USER_COUNT}${NC}"
  exit 1
fi
echo -e "${GREEN}数据校验通过：Users=${USER_COUNT}${NC}"

# 显示部署信息
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}访问地址:${NC}"
echo -e "  前端: ${GREEN}http://${EC2_IP}${NC}"
echo -e "  后端: ${GREEN}http://${EC2_IP}:8000${NC}"
echo -e ""
echo -e "${BLUE}常用命令:${NC}"
echo -e "  查看日志: ${YELLOW}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "  查看状态: ${YELLOW}docker-compose -f docker-compose.prod.yml ps${NC}"
echo -e "  重启服务: ${YELLOW}docker-compose -f docker-compose.prod.yml restart${NC}"
echo -e "  停止服务: ${YELLOW}docker-compose -f docker-compose.prod.yml down${NC}"
echo -e ""
echo -e "${BLUE}默认账户:${NC}"
echo -e "  管理员: admin / 123456"
echo -e "  教师: teacher / 123456"
echo -e "  学生: student / 123456"
echo -e "${GREEN}========================================${NC}"

# 测试服务
echo ""
echo -e "${YELLOW}测试服务连接...${NC}"
sleep 5

if curl -f -s http://localhost:8000/api/projects/all/ > /dev/null; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
else
    echo -e "${RED}⚠️  后端服务可能未就绪，请查看日志${NC}"
fi

if curl -f -s http://localhost/ > /dev/null; then
    echo -e "${GREEN}✅ 前端服务运行正常${NC}"
else
    echo -e "${RED}⚠️  前端服务可能未就绪，请查看日志${NC}"
fi

echo ""
echo -e "${BLUE}如果服务未就绪，请等待几分钟后再次检查${NC}"
echo -e "${BLUE}或查看日志: docker-compose -f docker-compose.prod.yml logs -f${NC}"




