# 鏅鸿氨AI鐜鍙橀噺璁剧疆鑴氭湰
# 鍦≒owerShell涓繍琛屾鑴氭湰锛屾垨鍦―jango鍚姩鍓嶆墜鍔ㄨ缃?

Write-Host "Setting up ZhipuAI environment variables..." -ForegroundColor Green

# 璁剧疆鏅鸿氨AI鐜鍙橀噺
# 娓呴櫎鍙兘瀛樺湪鐨勯敊璇幆澧冨彉閲?
Remove-Item Env:ZHIPUAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ZHIPUAI_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:ZHIPUAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue

# 璁剧疆姝ｇ‘鐨勭幆澧冨彉閲?
$env:ZHIPUAI_API_KEY = "YOUR_ZHIPUAI_API_KEY"
$env:ZHIPUAI_MODEL = "glm-4-flash"
$env:ZHIPUAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

# 鍚屾椂璁剧疆OpenAI鍏煎鐨勭幆澧冨彉閲?
$env:OPENAI_API_KEY = "YOUR_ZHIPUAI_API_KEY"
$env:OPENAI_MODEL = "glm-4-flash"
$env:OPENAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

Write-Host "ZhipuAI environment variables set successfully!" -ForegroundColor Green
Write-Host "API Key: $env:ZHIPUAI_API_KEY" -ForegroundColor Yellow
Write-Host "Model: $env:ZHIPUAI_MODEL" -ForegroundColor Yellow
Write-Host "Base URL: $env:ZHIPUAI_BASE_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "Using correct API key and model name!" -ForegroundColor Magenta
Write-Host "Now you can test AI functionality!" -ForegroundColor Cyan

