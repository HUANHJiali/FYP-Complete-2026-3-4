#!/bin/bash

echo "========================================"
echo "   FYP2025 Docker 一键启动脚本"
echo "========================================"
echo

echo "[1/5] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ 未检测到 Docker！"
    echo "请先安装 Docker: https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo "✅ Docker 已安装"

echo
echo "[2/5] 检查 Docker 服务状态..."
if ! docker info &> /dev/null; then
    echo "❌ Docker 服务未运行！"
    echo "请启动 Docker 并重试。"
    exit 1
fi
echo "✅ Docker 服务运行正常"

echo
echo "[3/5] 停止并删除旧容器..."
docker-compose down -v 2>/dev/null

echo
echo "[4/5] 构建 Docker 镜像..."
docker-compose build --no-cache
if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败！"
    exit 1
fi

echo
echo "[5/5] 启动所有服务..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败！"
    exit 1
fi

echo
echo "========================================"
echo "           启动成功！"
echo "========================================"
echo
echo "🌐 访问地址："
echo "  前端界面: http://localhost:8080"
echo "  后端API:  http://localhost:8000"
echo "  管理后台: http://localhost:8000/admin"
echo
echo "👤 测试账户："
echo "  管理员: admin / 123456"
echo "  教师:   teacher / 123456"
echo "  学生:   student / 123456"
echo
echo "📝 查看日志："
echo "  docker-compose logs -f"
echo
echo "🛑 停止服务："
echo "  docker-compose down"
echo

# 给脚本添加执行权限（仅在 Linux/Mac 上需要）
chmod +x docker-start.sh 2>/dev/null
