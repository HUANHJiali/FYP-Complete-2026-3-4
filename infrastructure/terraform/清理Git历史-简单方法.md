# 清理 Git 历史中的敏感信息 - 简单方法

## 问题

GitHub 检测到 commit `17b7581` 中包含 AWS 凭证，即使现在文件已经修复，历史记录中仍然存在。

## 解决方案（3 种方法）

### 方法 1: 使用 Git Filter-Branch（推荐）

```powershell
# 1. 从历史中移除文件
git filter-branch --force --index-filter `
    "git rm --cached --ignore-unmatch infrastructure/terraform/set-env.ps1" `
    --prune-empty --tag-name-filter cat -- --all

# 2. 清理引用
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 3. 强制推送（⚠️ 会覆盖远程历史）
git push origin --force --all
```

### 方法 2: 使用 BFG Repo-Cleaner（更简单）

1. **下载 BFG**: https://rtyley.github.io/bfg-repo-cleaner/

2. **运行清理**:
   ```powershell
   # 备份仓库
   git clone --mirror https://github.com/HUANHJiali/FYP2025-12-27.git backup.git
   
   # 使用 BFG 移除文件
   java -jar bfg.jar --delete-files set-env.ps1
   
   # 清理
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # 推送
   git push origin --force --all
   ```

### 方法 3: 最简单 - 创建新分支（如果历史不重要）

如果这个仓库只有你使用，且历史不重要：

```powershell
# 1. 创建新分支，不包含那个提交
git checkout --orphan new-main
git add .
git commit -m "Initial commit - cleaned history"
git branch -D main
git branch -m main

# 2. 强制推送
git push origin --force main
```

## 推荐步骤（使用方法 1）

### 步骤 1: 备份当前仓库

```powershell
cd ..
git clone https://github.com/HUANHJiali/FYP2025-12-27.git FYP2025-12-27-backup
```

### 步骤 2: 清理历史

```powershell
cd FYP2025-12-27
git filter-branch --force --index-filter `
    "git rm --cached --ignore-unmatch infrastructure/terraform/set-env.ps1" `
    --prune-empty --tag-name-filter cat -- --all
```

### 步骤 3: 清理引用

```powershell
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 步骤 4: 验证

```powershell
# 检查历史中是否还有 set-env.ps1
git log --all --full-history -- infrastructure/terraform/set-env.ps1

# 应该没有输出（文件已从历史中移除）
```

### 步骤 5: 强制推送

```powershell
# ⚠️ 警告：这会覆盖远程历史！
git push origin --force --all
```

## 如果不想重写历史

如果不想重写历史，可以：

1. **在 GitHub 上允许这个 secret**（不推荐，因为凭证已暴露）
   - 访问 GitHub 提供的链接
   - 但这只是允许推送，凭证仍然暴露

2. **撤销凭证并创建新提交**
   - 在 AWS 中撤销这些凭证
   - 创建新的提交（不包含敏感信息）
   - 但历史中仍然有旧的提交

## 最佳实践

清理历史后：

1. ✅ 确保 `set-env.ps1` 在 `.gitignore` 中
2. ✅ 使用 `set-env.ps1.example` 作为模板
3. ✅ 永远不要提交真实的凭证
4. ✅ 定期轮换 AWS 凭证

