# 清理 Git 历史中的敏感信息
# 从所有提交中移除 set-env.ps1 文件

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "清理 Git 历史中的敏感信息" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "警告: 这将重写 Git 历史！" -ForegroundColor Red
Write-Host "如果其他人也在使用这个仓库，需要协调。" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "确认继续? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "步骤 1: 从历史中移除 set-env.ps1 文件..." -ForegroundColor Cyan

# 使用 git filter-branch 从历史中移除文件
git filter-branch --force --index-filter `
    "git rm --cached --ignore-unmatch infrastructure/terraform/set-env.ps1" `
    --prune-empty --tag-name-filter cat -- --all

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 成功从历史中移除文件" -ForegroundColor Green
} else {
    Write-Host "❌ 操作失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "步骤 2: 清理引用..." -ForegroundColor Cyan
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "✅ 清理完成" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 检查历史: git log --oneline -10" -ForegroundColor Cyan
Write-Host "  2. 强制推送: git push origin --force --all" -ForegroundColor Cyan
Write-Host "  3. 警告: 强制推送会覆盖远程历史，确保没有其他人在使用这个仓库！" -ForegroundColor Red
Write-Host ""

