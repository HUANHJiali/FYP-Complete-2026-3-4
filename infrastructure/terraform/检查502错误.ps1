# PowerShell 脚本 - 检查 502 Bad Gateway 错误
# 使用方法：在本地运行此脚本，它会 SSH 到 EC2 并检查服务状态

param(
    [string]$EC2_IP = "44.202.74.216",
    [string]$KEY_FILE = "fyp-keypair.pem"
)

Write-Host "=== 检查 502 Bad Gateway 错误 ===" -ForegroundColor Cyan
Write-Host ""

# 检查密钥文件是否存在
if (-not (Test-Path $KEY_FILE)) {
    Write-Host "❌ 密钥文件不存在: $KEY_FILE" -ForegroundColor Red
    Write-Host "请提供正确的密钥文件路径" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. 检查 EC2 实例连接..." -ForegroundColor Yellow
$testConnection = Test-Connection -ComputerName $EC2_IP -Count 1 -Quiet
if ($testConnection) {
    Write-Host "✅ EC2 实例可访问: $EC2_IP" -ForegroundColor Green
} else {
    Write-Host "❌ EC2 实例无法访问: $EC2_IP" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. SSH 连接到 EC2 并检查服务状态..." -ForegroundColor Yellow
Write-Host ""

# 创建临时脚本文件
$checkScript = @"
#!/bin/bash
echo "=== EC2 服务状态检查 ==="
echo ""

echo "1. 检查 Docker 服务状态..."
if systemctl is-active --quiet docker; then
    echo "✅ Docker 服务正在运行"
else
    echo "❌ Docker 服务未运行"
    echo "   尝试启动: sudo systemctl start docker"
fi

echo ""
echo "2. 检查 Docker 容器状态..."
docker ps -a

echo ""
echo "3. 检查端口监听..."
if command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep -E ':(80|8000)' || echo "⚠️  端口 80 或 8000 未监听"
elif command -v ss &> /dev/null; then
    ss -tlnp | grep -E ':(80|8000)' || echo "⚠️  端口 80 或 8000 未监听"
else
    echo "⚠️  无法检查端口（需要 netstat 或 ss）"
fi

echo ""
echo "4. 检查项目目录..."
if [ -d "/home/ubuntu/25FYP" ]; then
    echo "✅ 项目目录存在"
    echo "   目录内容:"
    ls -la /home/ubuntu/25FYP/ | head -5
else
    echo "❌ 项目目录不存在: /home/ubuntu/25FYP"
fi

echo ""
echo "5. 检查 docker-compose 文件..."
if [ -f "/home/ubuntu/25FYP/docker-compose.prod.yml" ]; then
    echo "✅ docker-compose.prod.yml 存在"
else
    echo "❌ docker-compose.prod.yml 不存在"
fi

echo ""
echo "6. 测试本地服务..."
echo "   测试前端 (80端口):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost/ || echo "❌ 前端无法访问"

echo "   测试后端 (8000端口):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:8000/api/projects/all/ || echo "❌ 后端无法访问"

echo ""
echo "7. 查看部署日志（最后30行）..."
if [ -f "/tmp/deploy.log" ]; then
    tail -30 /tmp/deploy.log
else
    echo "⚠️  部署日志不存在: /tmp/deploy.log"
fi

echo ""
echo "8. 查看 user-data 日志（最后30行）..."
if [ -f "/var/log/user-data.log" ]; then
    tail -30 /var/log/user-data.log
else
    echo "⚠️  user-data 日志不存在: /var/log/user-data.log"
fi

echo ""
echo "=== 检查完成 ==="
"@

# 将脚本保存到临时文件
$tempScript = [System.IO.Path]::GetTempFileName()
$checkScript | Out-File -FilePath $tempScript -Encoding UTF8

Write-Host "正在执行检查..." -ForegroundColor Cyan
Write-Host ""

# SSH 并执行检查脚本
ssh -i $KEY_FILE -o StrictHostKeyChecking=no ubuntu@$EC2_IP "bash -s" < $tempScript

# 清理临时文件
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== 检查完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果 Docker 容器未运行，请执行以下命令手动启动:" -ForegroundColor Yellow
Write-Host "  ssh -i $KEY_FILE ubuntu@$EC2_IP" -ForegroundColor White
Write-Host "  cd /home/ubuntu/25FYP" -ForegroundColor White
Write-Host "  docker-compose -f docker-compose.prod.yml up -d" -ForegroundColor White

