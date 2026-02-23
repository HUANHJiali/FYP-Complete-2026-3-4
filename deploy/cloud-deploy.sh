#!/bin/bash

# 云端部署脚本
# 使用方法: ./cloud-deploy.sh

set -e

echo "🚀 开始云端部署..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 root 用户运行此脚本${NC}"
    exit 1
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker 未安装，开始安装...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose 未安装，开始安装...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 获取配置信息
read -p "请输入服务器 IP 或域名: " SERVER_HOST
read -p "请输入数据库密码（留空使用默认）: " DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-exam123456}

read -p "请输入 Django SECRET_KEY（留空自动生成）: " SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
    echo -e "${GREEN}已自动生成 SECRET_KEY${NC}"
fi

# 创建 .env 文件
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
ALLOWED_HOSTS=${SERVER_HOST},localhost,127.0.0.1

# CORS 配置
CORS_ALLOWED_ORIGINS=https://${SERVER_HOST},http://${SERVER_HOST}
EOF

echo -e "${GREEN}环境变量已配置${NC}"

# 修改 docker-compose.yml 使用生产配置
if [ -f "docker-compose.yml" ]; then
    # 备份原文件
    cp docker-compose.yml docker-compose.yml.bak
    
    # 修改后端使用 Gunicorn
    sed -i 's/python manage.py runserver/gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 4/g' docker-compose.yml
    
    # 修改前端使用生产镜像
    sed -i 's|dockerfile: ../../docker/frontend/Dockerfile|dockerfile: ../../docker/frontend/Dockerfile.prod|g' docker-compose.yml
    
    echo -e "${GREEN}docker-compose.yml 已更新为生产配置${NC}"
fi

# 检查 requirements.txt 是否包含 gunicorn
if ! grep -q "gunicorn" source/server/requirements.txt; then
    echo "gunicorn==21.2.0" >> source/server/requirements.txt
    echo -e "${GREEN}已添加 gunicorn 到 requirements.txt${NC}"
fi

# 构建并启动服务
echo -e "${YELLOW}开始构建镜像...${NC}"
docker-compose build

echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 执行数据库迁移
echo -e "${YELLOW}执行数据库迁移...${NC}"
docker-compose exec -T backend python manage.py migrate --noinput || true

# 收集静态文件
echo -e "${YELLOW}收集静态文件...${NC}"
docker-compose exec -T backend python manage.py collectstatic --noinput || true

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker-compose ps

# 显示访问信息
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "前端地址: http://${SERVER_HOST}"
echo -e "后端 API: http://${SERVER_HOST}:8000"
echo -e ""
echo -e "查看日志: docker-compose logs -f"
echo -e "停止服务: docker-compose down"
echo -e "重启服务: docker-compose restart"
echo -e "${GREEN}========================================${NC}"




