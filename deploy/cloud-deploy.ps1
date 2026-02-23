# 云端部署脚本 (PowerShell)
# 使用方法: .\cloud-deploy.ps1

Write-Host "🚀 开始云端部署..." -ForegroundColor Green

# 检查是否为管理员
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "请使用管理员权限运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查 Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker 未安装，请先安装 Docker Desktop" -ForegroundColor Yellow
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# 检查 Docker Compose
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "Docker Compose 未安装" -ForegroundColor Yellow
    exit 1
}

# 获取配置信息
$SERVER_HOST = Read-Host "请输入服务器 IP 或域名"
$DB_PASSWORD = Read-Host "请输入数据库密码（留空使用默认）"
if ([string]::IsNullOrWhiteSpace($DB_PASSWORD)) {
    $DB_PASSWORD = "exam123456"
}

$SECRET_KEY = Read-Host "请输入 Django SECRET_KEY（留空自动生成）"
if ([string]::IsNullOrWhiteSpace($SECRET_KEY)) {
    # 生成随机密钥
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    $SECRET_KEY = [Convert]::ToBase64String($bytes)
    Write-Host "已自动生成 SECRET_KEY" -ForegroundColor Green
}

# 创建 .env 文件
$envContent = @"
# 数据库配置
DB_HOST=db
DB_PORT=3306
DB_NAME=db_exam
DB_USER=examuser
DB_PASSWORD=$DB_PASSWORD
MYSQL_ROOT_PASSWORD=$DB_PASSWORD

# Django 配置
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$SERVER_HOST,localhost,127.0.0.1

# CORS 配置
CORS_ALLOWED_ORIGINS=https://$SERVER_HOST,http://$SERVER_HOST
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "环境变量已配置" -ForegroundColor Green

# 检查 requirements.txt 是否包含 gunicorn
$requirementsPath = "source\server\requirements.txt"
if (Test-Path $requirementsPath) {
    $content = Get-Content $requirementsPath -Raw
    if ($content -notmatch "gunicorn") {
        Add-Content -Path $requirementsPath -Value "`ngunicorn==21.2.0"
        Write-Host "已添加 gunicorn 到 requirements.txt" -ForegroundColor Green
    }
}

# 构建并启动服务
Write-Host "开始构建镜像..." -ForegroundColor Yellow
docker-compose build

Write-Host "启动服务..." -ForegroundColor Yellow
docker-compose up -d

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 执行数据库迁移
Write-Host "执行数据库迁移..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py migrate --noinput

# 收集静态文件
Write-Host "收集静态文件..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py collectstatic --noinput

# 检查服务状态
Write-Host "检查服务状态..." -ForegroundColor Yellow
docker-compose ps

# 显示访问信息
Write-Host "========================================" -ForegroundColor Green
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "前端地址: http://$SERVER_HOST"
Write-Host "后端 API: http://$SERVER_HOST`:8000"
Write-Host ""
Write-Host "查看日志: docker-compose logs -f"
Write-Host "停止服务: docker-compose down"
Write-Host "重启服务: docker-compose restart"
Write-Host "========================================" -ForegroundColor Green




