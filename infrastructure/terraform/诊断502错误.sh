#!/bin/bash

# 502 Bad Gateway 诊断脚本
# 在 EC2 实例上运行此脚本来诊断问题

echo "=========================================="
echo "502 Bad Gateway 诊断工具"
echo "=========================================="
echo ""

# 1. 检查 Docker 容器状态
echo "1. 检查 Docker 容器状态..."
docker ps -a
echo ""

# 2. 检查端口监听
echo "2. 检查端口监听..."
sudo ss -tlnp | grep -E ':(80|8000)' || echo "⚠️  端口 80 或 8000 未监听"
echo ""

# 3. 测试本地服务
echo "3. 测试本地服务..."
echo "测试前端 (http://localhost/):"
curl -s -o /dev/null -w "HTTP 状态码: %{http_code}\n" http://localhost/ || echo "❌ 前端无法访问"
echo ""

echo "测试后端 (http://localhost:8000/api/projects/all/):"
curl -s -o /dev/null -w "HTTP 状态码: %{http_code}\n" http://localhost:8000/api/projects/all/ || echo "❌ 后端无法访问"
echo ""

# 4. 检查后端日志
echo "4. 检查后端容器日志（最后 20 行）..."
docker-compose -f docker-compose.prod.yml logs --tail=20 backend 2>/dev/null || echo "⚠️  无法查看后端日志"
echo ""

# 5. 检查前端日志
echo "5. 检查前端容器日志（最后 20 行）..."
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend 2>/dev/null || echo "⚠️  无法查看前端日志"
echo ""

# 6. 检查部署日志
echo "6. 检查部署日志..."
if [ -f /tmp/deploy.log ]; then
    echo "部署日志最后 30 行:"
    tail -30 /tmp/deploy.log
else
    echo "⚠️  部署日志不存在"
fi
echo ""

# 7. 检查环境变量
echo "7. 检查 .env 文件..."
if [ -f .env ]; then
    echo "✅ .env 文件存在"
    echo "CORS_ALLOWED_ORIGINS:"
    grep CORS_ALLOWED_ORIGINS .env || echo "⚠️  CORS_ALLOWED_ORIGINS 未设置"
else
    echo "❌ .env 文件不存在"
fi
echo ""

# 8. 检查数据库连接
echo "8. 检查数据库连接..."
docker-compose -f docker-compose.prod.yml exec -T db mysqladmin ping -h localhost -u root -pExam123456! 2>/dev/null && echo "✅ 数据库连接正常" || echo "❌ 数据库连接失败"
echo ""

# 9. 检查 gunicorn 进程
echo "9. 检查 gunicorn 进程..."
docker-compose -f docker-compose.prod.yml exec -T backend ps aux | grep gunicorn || echo "❌ gunicorn 未运行"
echo ""

# 10. 检查安全组（需要 AWS CLI）
echo "10. 检查 EC2 实例信息..."
if command -v aws &> /dev/null; then
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    echo "实例 ID: $INSTANCE_ID"
    echo "公网 IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
else
    echo "⚠️  AWS CLI 未安装，跳过"
fi
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""
echo "如果服务未运行，尝试："
echo "1. cd /home/ubuntu/25FYP"
echo "2. docker-compose -f docker-compose.prod.yml up -d"
echo "3. docker-compose -f docker-compose.prod.yml logs -f"
echo ""

