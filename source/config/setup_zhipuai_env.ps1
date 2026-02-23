# 智谱AI环境变量设置脚本
# 在PowerShell中运行此脚本，或在Django启动前手动设置

Write-Host "Setting up ZhipuAI environment variables..." -ForegroundColor Green

# 设置智谱AI环境变量
# 清除可能存在的错误环境变量
Remove-Item Env:ZHIPUAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ZHIPUAI_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:ZHIPUAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue

# 设置正确的环境变量
$env:ZHIPUAI_API_KEY = "fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf"
$env:ZHIPUAI_MODEL = "glm-4-flash"
$env:ZHIPUAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

# 同时设置OpenAI兼容的环境变量
$env:OPENAI_API_KEY = "fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf"
$env:OPENAI_MODEL = "glm-4-flash"
$env:OPENAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

Write-Host "ZhipuAI environment variables set successfully!" -ForegroundColor Green
Write-Host "API Key: $env:ZHIPUAI_API_KEY" -ForegroundColor Yellow
Write-Host "Model: $env:ZHIPUAI_MODEL" -ForegroundColor Yellow
Write-Host "Base URL: $env:ZHIPUAI_BASE_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "Using correct API key and model name!" -ForegroundColor Magenta
Write-Host "Now you can test AI functionality!" -ForegroundColor Cyan
