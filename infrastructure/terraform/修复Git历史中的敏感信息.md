# 修复 Git 历史中的敏感信息

## 问题

GitHub 检测到代码中包含了 AWS 凭证，这些敏感信息已经被提交到 Git 历史中。即使现在删除了，历史记录中仍然存在。

## 解决方案

### 方法 1: 使用 Git Filter-Repo（推荐）

1. **安装 git-filter-repo**:
   ```bash
   # Windows (使用 pip)
   pip install git-filter-repo
   
   # 或使用 scoop
   scoop install git-filter-repo
   ```

2. **移除敏感文件的历史记录**:
   ```bash
   cd d:\作業\fyp\25FYP-main
   git filter-repo --path infrastructure/terraform/set-env.ps1 --invert-paths
   ```

3. **强制推送到远程仓库**:
   ```bash
   git push origin --force --all
   ```

### 方法 2: 使用 BFG Repo-Cleaner（更简单）

1. **下载 BFG**: https://rtyley.github.io/bfg-repo-cleaner/

2. **创建文件列表** (credentials.txt):
   ```
   ASIA4FKJ573GDCM7MSKG
   fheShcK6NN4N+0WEXm3VFvoQv61HHsBF0LaRyIUD
   IQoJb3JpZ2luX2VjELj
   ```

3. **运行 BFG**:
   ```bash
   java -jar bfg.jar --replace-text credentials.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

### 方法 3: 最简单的方法（如果仓库不公开）

如果这是私有仓库且只有你使用，可以：

1. **删除敏感文件**:
   ```bash
   git rm infrastructure/terraform/set-env.ps1
   git commit -m "Remove sensitive credentials"
   ```

2. **在 GitHub 上撤销暴露的凭证**:
   - 访问 GitHub 提供的链接来撤销凭证
   - 在 AWS Console 中删除/轮换这些凭证

3. **创建新的凭证并更新**:
   - 从 AWS Academy 获取新凭证
   - 使用新的 `set-env.ps1.example` 模板

## 立即行动

### 步骤 1: 撤销已暴露的凭证

**重要**: 这些凭证已经暴露，必须立即撤销！

1. 访问 AWS Academy Learner Lab
2. 删除当前的临时凭证
3. 生成新的凭证

### 步骤 2: 修复代码

已完成的修复：
- ✅ 移除了 `set-env.ps1` 中的硬编码凭证
- ✅ 创建了 `set-env.ps1.example` 作为模板
- ✅ 将 `set-env.ps1` 添加到 `.gitignore`

### 步骤 3: 清理 Git 历史（可选但推荐）

如果仓库是公开的，强烈建议清理历史：

```bash
# 使用 git filter-repo
git filter-repo --path infrastructure/terraform/set-env.ps1 --invert-paths
git push origin --force --all
```

**警告**: 这会重写 Git 历史，如果其他人也在使用这个仓库，需要协调。

## 预防措施

1. ✅ **使用 `.gitignore`**: `set-env.ps1` 已在忽略列表中
2. ✅ **使用模板文件**: `set-env.ps1.example` 作为示例
3. ✅ **使用环境变量**: 优先使用系统环境变量
4. ✅ **使用 AWS Secrets Manager**: 生产环境应使用密钥管理服务

## 当前状态

- ✅ 代码已修复（不再包含硬编码凭证）
- ⚠️ Git 历史中仍存在旧凭证（需要清理）
- ⚠️ 已暴露的凭证需要撤销和轮换

## 下一步

1. **立即撤销暴露的凭证**（最重要！）
2. 提交修复后的代码
3. 可选：清理 Git 历史

