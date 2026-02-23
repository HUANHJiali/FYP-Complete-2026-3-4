#!/bin/bash
# 快速检查脚本 - 在 EC2 上运行

echo "=== 快速检查 502 错误 ==="
echo ""

# 1. 检查 Docker 容器
echo "1. Docker 容器状态:"
docker ps -a
echo ""

# 2. 检查端口
echo "2. 端口监听状态:"
if command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep -E ':(80|8000)' || echo "⚠️  端口未监听"
elif command -v ss &> /dev/null; then
    ss -tlnp | grep -E ':(80|8000)' || echo "⚠️  端口未监听"
fi
echo ""

# 3. 测试服务
echo "3. 测试本地服务:"
echo "   前端:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost/ || echo "❌ 失败"
echo "   后端:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/api/projects/all/ || echo "❌ 失败"
echo ""

# 4. 查看日志
echo "4. 最近的错误日志:"
docker-compose -f /home/ubuntu/25FYP/docker-compose.prod.yml logs --tail=20 2>/dev/null || echo "⚠️  无法查看日志"
echo ""

# 5. 检查部署状态
echo "5. 部署日志（最后10行）:"
tail -10 /tmp/deploy.log 2>/dev/null || echo "⚠️  部署日志不存在"
echo ""

echo "=== 检查完成 ==="
echo ""
echo "如果容器未运行，执行:"
echo "  cd /home/ubuntu/25FYP"
echo "  docker-compose -f docker-compose.prod.yml up -d"

