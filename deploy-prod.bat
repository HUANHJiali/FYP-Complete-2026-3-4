@echo off
REM ========================================
REM FYP 生产环境部署脚本 (Windows)
REM ========================================

echo.
echo ========================================
echo   FYP 生产环境部署
echo ========================================
echo.

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

REM 检查 .env.production 文件
if not exist .env.production (
    echo [警告] .env.production 文件不存在
    echo [提示] 正在从 .env.production.example 创建...
    copy .env.production.example .env.production >nul
    echo [重要] 请编辑 .env.production 文件，配置您的域名和API密钥
    pause
)

REM 停止开发环境容器
echo [1/5] 停止开发环境容器...
docker-compose down 2>nul

REM 构建生产镜像
echo [2/5] 构建生产镜像...
docker-compose -f docker-compose.prod.yml build --no-cache

REM 启动生产容器
echo [3/5] 启动生产容器...
docker-compose -f docker-compose.prod.yml up -d

REM 等待服务启动
echo [4/5] 等待服务启动...
timeout /t 30 /nobreak >nul

REM 健康检查
echo [5/5] 健康检查...
curl -s http://localhost/api/health/ >nul 2>&1
if errorlevel 1 (
    echo [警告] 服务可能未完全启动，请稍后手动检查
) else (
    echo [成功] 服务已成功启动
)

echo.
echo ========================================
echo   部署完成
echo ========================================
echo.
echo 访问地址:
echo   - 前端: http://localhost
echo   - 后端: http://localhost:8000
echo   - API文档: http://localhost:8000/swagger/
echo.
echo 测试账号:
echo   - 管理员: admin / 123456
echo   - 教师: teacher / 123456
echo   - 学生: student / 123456
echo.
echo [重要] 请记得修改默认密码！
echo.
pause
