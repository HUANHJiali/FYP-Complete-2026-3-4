# PowerShell 脚本：配置 AWS 凭证
# 用于 AWS Academy Learner Lab

Write-Host "========================================" -ForegroundColor Blue
Write-Host "🔐 配置 AWS 凭证" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# 检查 AWS CLI 是否安装
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  AWS CLI 未安装" -ForegroundColor Yellow
    Write-Host "安装 AWS CLI: https://aws.amazon.com/cli/" -ForegroundColor Blue
    Write-Host ""
    Write-Host "或者使用环境变量方式（推荐）" -ForegroundColor Blue
    Write-Host ""
}

# 创建 .aws 目录
$awsDir = "$env:USERPROFILE\.aws"
if (-not (Test-Path $awsDir)) {
    New-Item -ItemType Directory -Path $awsDir -Force | Out-Null
    Write-Host "✅ 已创建 .aws 目录" -ForegroundColor Green
}

# 配置凭证文件
$credentialsFile = "$awsDir\credentials"
$configFile = "$awsDir\config"

Write-Host ""
Write-Host "请选择配置方式：" -ForegroundColor Yellow
Write-Host "1. 使用环境变量（推荐，更安全）" -ForegroundColor Cyan
Write-Host "2. 使用 credentials 文件" -ForegroundColor Cyan
Write-Host ""
$choice = Read-Host "请输入选择 (1 或 2)"

if ($choice -eq "1") {
    # 方法 1: 环境变量
    Write-Host ""
    Write-Host "=== 环境变量配置 ===" -ForegroundColor Blue
    Write-Host ""
    Write-Host "请运行以下命令设置环境变量：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host '$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID_HERE"' -ForegroundColor Green
    Write-Host '$env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY_HERE"' -ForegroundColor Green
    Write-Host '$env:AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN_HERE"' -ForegroundColor Green
    Write-Host '$env:AWS_DEFAULT_REGION="us-east-1"' -ForegroundColor Green
    Write-Host ""
    Write-Host "或者运行以下命令一次性设置：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host '$env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"; $env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"; $env:AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN"; $env:AWS_DEFAULT_REGION="us-east-1"' -ForegroundColor Cyan
    Write-Host ""
    
} elseif ($choice -eq "2") {
    # 方法 2: credentials 文件
    Write-Host ""
    Write-Host "=== 配置 credentials 文件 ===" -ForegroundColor Blue
    Write-Host ""
    
    $credentialsContent = @"
[default]
aws_access_key_id=YOUR_ACCESS_KEY_ID_HERE
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY_HERE
aws_session_token=YOUR_SESSION_TOKEN_HERE
"@
    
    $credentialsContent | Out-File -FilePath $credentialsFile -Encoding utf8 -Force
    Write-Host "✅ 已创建 credentials 文件: $credentialsFile" -ForegroundColor Green
    
    # 配置 region
    $configContent = @"
[default]
region=us-east-1
output=json
"@
    $configContent | Out-File -FilePath $configFile -Encoding utf8 -Force
    Write-Host "✅ 已创建 config 文件: $configFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "✅ 配置完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 测试连接: aws sts get-caller-identity" -ForegroundColor Cyan
Write-Host "2. 运行 Terraform: terraform plan" -ForegroundColor Cyan
Write-Host ""




