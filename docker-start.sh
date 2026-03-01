#!/bin/bash

set -e

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

if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ 未检测到 Docker Compose！"
    exit 1
fi
echo "✅ Compose 命令: ${COMPOSE_CMD}"

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
${COMPOSE_CMD} down >/dev/null 2>&1 || true

echo
echo "[4/5] 构建 Docker 镜像..."
${COMPOSE_CMD} build

echo
echo "[5/5] 启动所有服务..."
${COMPOSE_CMD} up -d

echo
echo "[6/7] 等待后端服务就绪..."
for i in {1..60}; do
    if curl -fsS http://localhost:8000/api/health/simple/ >/dev/null 2>&1; then
        echo "✅ 后端已就绪"
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "❌ 后端启动超时（120秒）"
        ${COMPOSE_CMD} logs --tail=100 backend
        exit 1
    fi
    sleep 2
done

echo
echo "[7/7] 等待前端服务就绪..."
for i in {1..90}; do
    if curl -fsS http://localhost:8080 >/dev/null 2>&1; then
        echo "✅ 前端已就绪"
        break
    fi
    if [ "$i" -eq 90 ]; then
        echo "❌ 前端启动超时（180秒）"
        ${COMPOSE_CMD} logs --tail=100 frontend
        exit 1
    fi
    sleep 2
done

echo
echo "[附加检查] 登录接口自检..."
if curl -fsS -X POST http://localhost:8000/api/login/ -d "userName=admin&passWord=123456" >/dev/null 2>&1; then
    echo "✅ 登录接口自检通过"
else
    echo "⚠️ 登录接口自检未通过，请查看日志"
    ${COMPOSE_CMD} logs --tail=120 backend
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
echo "  ${COMPOSE_CMD} logs -f"
echo
echo "🛑 停止服务："
echo "  ${COMPOSE_CMD} down"
echo

# 给脚本添加执行权限（仅在 Linux/Mac 上需要）
chmod +x docker-start.sh 2>/dev/null || true
