@echo off
chcp 65001 >nul
echo ========================================
echo    FYP2025 Docker 一键启动脚本
echo ========================================
echo.

echo [1/5] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Docker！
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo ✅ Docker 已安装

echo.
echo [2/5] 检查 Docker 服务状态...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 服务未运行！
    echo 请启动 Docker Desktop 并重试。
    pause
    exit /b 1
)
echo ✅ Docker 服务运行正常

echo.
echo [3/5] 停止并删除旧容器...
docker-compose down -v >nul 2>&1

echo.
echo [4/5] 构建 Docker 镜像...
docker-compose build --no-cache
if errorlevel 1 (
    echo ❌ 镜像构建失败！
    pause
    exit /b 1
)

echo.
echo [5/5] 启动所有服务...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 服务启动失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo           启动成功！
echo ========================================
echo.
echo 🌐 访问地址：
echo   前端界面: http://localhost:8080
echo   后端API:  http://localhost:8000
echo   管理后台: http://localhost:8000/admin
echo.
echo 👤 测试账户：
echo   管理员: admin / 123456
echo   教师:   teacher / 123456
echo   学生:   student / 123456
echo.
echo 📝 查看日志：
echo   docker-compose logs -f
echo.
echo 🛑 停止服务：
echo   docker-compose down
echo.

pause
