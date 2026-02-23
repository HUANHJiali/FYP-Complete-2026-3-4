# 修复包含敏感信息的提交
# 使用交互式 rebase 修改提交 17b7581

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "修复包含敏感信息的提交" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# 找到问题提交之前的提交
$parentCommit = "46e3389"

Write-Host "步骤 1: 开始交互式 rebase..." -ForegroundColor Cyan
Write-Host "目标: 修改提交 17b7581，移除敏感信息" -ForegroundColor Cyan
Write-Host ""

# 设置 Git 编辑器为 PowerShell（使用临时脚本）
$editorScript = @"
# 自动编辑 rebase todo 列表
`$content = Get-Content `$args[0]
`$content = `$content -replace '^pick 17b7581', 'edit 17b7581'
`$content | Set-Content `$args[0]
"@

$editorPath = "$env:TEMP\git-editor.ps1"
$editorScript | Out-File -FilePath $editorPath -Encoding UTF8

# 设置 Git 编辑器
$env:GIT_EDITOR = "powershell -File $editorPath"
$env:GIT_SEQUENCE_EDITOR = "powershell -File $editorPath"

Write-Host "步骤 2: 开始 rebase..." -ForegroundColor Cyan
git rebase -i $parentCommit

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Rebase 失败或已取消" -ForegroundColor Red
    git rebase --abort
    exit 1
}

Write-Host ""
Write-Host "步骤 3: 修改提交中的文件..." -ForegroundColor Cyan

# 检查是否在 rebase 状态
if (Test-Path ".git/rebase-merge" -or Test-Path ".git/rebase-apply") {
    # 移除文件（如果存在）
    if (Test-Path "infrastructure/terraform/set-env.ps1") {
        # 检查文件内容，如果是旧版本（包含敏感信息），则删除
        $content = Get-Content "infrastructure/terraform/set-env.ps1" -Raw
        if ($content -match 'ASIA4FKJ573GDCM7MSKG') {
            Write-Host "发现旧版本文件，移除..." -ForegroundColor Yellow
            git rm infrastructure/terraform/set-env.ps1
        }
    }
    
    # 继续 rebase
    git rebase --continue
} else {
    Write-Host "⚠️  不在 rebase 状态，可能需要手动处理" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ 完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 验证: git log --oneline -5" -ForegroundColor Cyan
Write-Host "  2. 检查: git show HEAD:infrastructure/terraform/set-env.ps1" -ForegroundColor Cyan
Write-Host "  3. 推送: git push origin --force main" -ForegroundColor Cyan
Write-Host ""

