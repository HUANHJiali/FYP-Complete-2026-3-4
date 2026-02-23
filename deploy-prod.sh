#!/bin/bash
# ========================================
# FYP 生产环境部署脚本 (Linux/Mac)
# ========================================

set -e

echo ""
echo "========================================"
echo "  FYP 生产环境部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}[错误] Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 检查 .env.production 文件
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}[警告] .env.production 文件不存在${NC}"
    echo "[提示] 正在从 .env.production.example 创建..."
    cp .env.production.example .env.production
    echo -e "${YELLOW}[重要] 请编辑 .env.production 文件，配置您的域名和API密钥${NC}"
    exit 1
fi

# 停止开发环境容器
echo -e "${GREEN}[1/5] 停止开发环境容器...${NC}"
docker-compose down 2>/dev/null || true

# 构建生产镜像
echo -e "${GREEN}[2/5] 构建生产镜像...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# 启动生产容器
echo -e "${GREEN}[3/5] 启动生产容器...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo -e "${GREEN}[4/5] 等待服务启动...${NC}"
sleep 30

# 健康检查
echo -e "${GREEN}[5/5] 健康检查...${NC}"
if curl -s http://localhost/api/health/ | grep -q "healthy"; then
    echo -e "${GREEN}[成功] 服务已成功启动${NC}"
else
    echo -e "${YELLOW}[警告] 服务可能未完全启动，请稍后手动检查${NC}"
fi

echo ""
echo "========================================"
echo "  部署完成"
echo "========================================"
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost"
echo "  - 后端: http://localhost:8000"
echo "  - API文档: http://localhost:8000/swagger/"
echo ""
echo "测试账号:"
echo "  - 管理员: admin / 123456"
echo "  - 教师: teacher / 123456"
echo "  - 学生: student / 123456"
echo ""
echo -e "${RED}[重要] 请记得修改默认密码！${NC}"
echo ""
