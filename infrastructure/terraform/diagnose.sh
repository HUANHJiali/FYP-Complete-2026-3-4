#!/bin/bash
# EC2 诊断脚本 - 检查 Docker 服务状态

echo "=== EC2 诊断脚本 ==="
echo ""

# 检查 Docker 是否运行
echo "1. 检查 Docker 服务..."
if systemctl is-active --quiet docker; then
    echo "✅ Docker 服务正在运行"
else
    echo "❌ Docker 服务未运行"
    echo "   尝试启动: sudo systemctl start docker"
fi

# 检查 Docker 容器状态
echo ""
echo "2. 检查 Docker 容器..."
docker ps -a

# 检查端口监听
echo ""
echo "3. 检查端口监听..."
netstat -tlnp 2>/dev/null | grep -E ':(80|8000)' || ss -tlnp | grep -E ':(80|8000)'

# 检查部署日志
echo ""
echo "4. 检查部署日志（最后50行）..."
if [ -f /tmp/deploy.log ]; then
    tail -50 /tmp/deploy.log
else
    echo "⚠️  部署日志不存在: /tmp/deploy.log"
fi

# 检查 user-data 日志
echo ""
echo "5. 检查 user-data 日志（最后50行）..."
if [ -f /var/log/user-data.log ]; then
    tail -50 /var/log/user-data.log
else
    echo "⚠️  user-data 日志不存在: /var/log/user-data.log"
fi

# 检查项目目录
echo ""
echo "6. 检查项目目录..."
if [ -d "/home/ubuntu/25FYP" ]; then
    echo "✅ 项目目录存在"
    ls -la /home/ubuntu/25FYP/ | head -10
else
    echo "❌ 项目目录不存在: /home/ubuntu/25FYP"
fi

# 检查 docker-compose 文件
echo ""
echo "7. 检查 docker-compose 配置..."
if [ -f "/home/ubuntu/25FYP/docker-compose.prod.yml" ]; then
    echo "✅ docker-compose.prod.yml 存在"
else
    echo "❌ docker-compose.prod.yml 不存在"
fi

# 测试本地服务
echo ""
echo "8. 测试本地服务..."
echo "   测试前端 (80端口):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost/ || echo "❌ 前端无法访问"

echo "   测试后端 (8000端口):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:8000/api/projects/all/ || echo "❌ 后端无法访问"

echo ""
echo "=== 诊断完成 ==="

