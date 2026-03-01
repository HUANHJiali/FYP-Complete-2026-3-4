@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
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

set "COMPOSE_CMD=docker compose"
docker compose version >nul 2>&1
if errorlevel 1 (
    set "COMPOSE_CMD=docker-compose"
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ 未检测到 Docker Compose！
        pause
        exit /b 1
    )
)
echo ✅ Compose 命令: %COMPOSE_CMD%

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
%COMPOSE_CMD% down >nul 2>&1

echo.
echo [4/5] 构建 Docker 镜像...
%COMPOSE_CMD% build
if errorlevel 1 (
    echo ❌ 镜像构建失败！
    pause
    exit /b 1
)

echo.
echo [5/5] 启动所有服务...
%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo ❌ 服务启动失败！
    pause
    exit /b 1
)

echo.
echo [6/7] 等待后端服务就绪...
set /a BACKEND_WAIT=0
:wait_backend
powershell -NoProfile -Command "try { $r=Invoke-RestMethod -Uri 'http://localhost:8000/api/health/simple/' -TimeoutSec 3; if($r.status -eq 'ok'){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 goto backend_ready
set /a BACKEND_WAIT+=1
if !BACKEND_WAIT! geq 60 (
    echo ❌ 后端启动超时（120秒）
    %COMPOSE_CMD% logs --tail=100 backend
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_backend

:backend_ready
echo ✅ 后端已就绪

echo.
echo [7/7] 等待前端服务就绪...
set /a FRONTEND_WAIT=0
:wait_frontend
powershell -NoProfile -Command "try { $r=Invoke-WebRequest -Uri 'http://localhost:8080' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -ge 200 -and $r.StatusCode -lt 500){ exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 goto frontend_ready
set /a FRONTEND_WAIT+=1
if !FRONTEND_WAIT! geq 90 (
    echo ❌ 前端启动超时（180秒）
    %COMPOSE_CMD% logs --tail=100 frontend
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_frontend

:frontend_ready
echo ✅ 前端已就绪

echo.
echo [附加检查] 登录接口自检...
powershell -NoProfile -Command "try { $r=Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/login/' -Body @{userName='admin';passWord='123456'} -TimeoutSec 5; if($r.code -eq 0){ exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
    echo ⚠️ 登录接口自检未通过，请查看日志排查
    %COMPOSE_CMD% logs --tail=120 backend
) else (
    echo ✅ 登录接口自检通过
)

echo.
echo ========================================
echo           启动成功！
echo ========================================
echo.
echo 访问地址：
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000
echo   Admin:    http://localhost:8000/admin
echo.
echo 测试账户：
echo   admin   / 123456
echo   teacher / 123456
echo   student / 123456
echo.
echo 查看日志：
echo   %COMPOSE_CMD% logs -f
echo.
echo 停止服务：
echo   %COMPOSE_CMD% down
echo.

pause
