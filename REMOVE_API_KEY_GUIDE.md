# 移除硬编码API密钥 - 详细步骤指南

**目标**: 将docker-compose.yml中的硬编码API密钥移到环境变量中

**安全风险**: 🔴 高 - API密钥暴露在代码中可能被滥用

---

## 📋 操作步骤

### 步骤1: 备份当前配置 ✅

```bash
# 备份docker-compose.yml
copy docker-compose.yml docker-compose.yml.backup
```

或者手动备份：
- 打开 `docker-compose.yml`
- 另存为 `docker-compose.yml.backup`

---

### 步骤2: 修改docker-compose.yml ✅

**找到第68行**：
```yaml
ZHIPUAI_API_KEY: fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

**修改为**：
```yaml
ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
```

**完整的环境变量部分应该如下**：
```yaml
environment:
      # 3. 参考 .env.production.example 文件
      SECRET_KEY: django-insecure-bh^5636f!$(au7fy^nzn()6*4ht974p(&pzcd&9z_**=t%^+^4
      DEBUG: "True"  # ⚠️ 生产环境改为 "False"
      ALLOWED_HOSTS: localhost,127.0.0.1,0.0.0.0,backend  # ⚠️ 生产环境改为实际域名
      # CORS 配置
      CORS_ALLOWED_ORIGINS: http://localhost:8080,http://127.0.0.1:8080
      CSRF_TRUSTED_ORIGINS: http://localhost:8080,http://127.0.0.1:8080
      # AI 配置（可选）
      ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}  # ✅ 修改这一行
      ZHIPUAI_MODEL: glm-4-flash
      ZHIPUAI_BASE_URL: https://open.bigbigmodel.cn/api/paas/v4
```

---

### 步骤3: 更新.env文件 ✅

**打开`.env`文件**：
```bash
notepad .env
```

**找到这一行**（第14行）：
```
ZHIPUAI_API_KEY=your_api_key_here
```

**替换为你的真实API密钥**：
```
ZHIPUAI_API_KEY=fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

或者如果你想使用一个新的API密钥，替换为你从ZhipuAI获取的新密钥。

**保存文件** (Ctrl+S)

---

### 步骤4: 重启Docker服务 ✅

#### Windows PowerShell:
```bash
# 停止服务
docker-compose down

# 重新启动
docker-compose up -d
```

#### Windows Git Bash:
```bash
docker-compose down
docker-compose up -d
```

#### Linux/Mac:
```bash
sudo docker-compose down
sudo docker-compose up -d
```

---

### 步骤5: 验证修复 ✅

**检查环境变量是否加载**：
```bash
docker-compose exec backend env | grep ZHIPUAI
```

应该看到：
```
ZHIPUAI_API_KEY=fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

**测试API功能**：
1. 登录系统
2. 尝试使用AI功能（如智能评分或题目生成）
3. 确认功能正常工作

---

## 🔍 验证方法

### 测试1: 检查容器环境变量
```bash
docker-compose exec backend printenv | grep ZHIPUAI
```

**期望输出**:
```
ZHIPUAI_API_KEY=你的API密钥
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### 测试2: 后端日志检查
```bash
docker logs fyp_backend --tail 50
```

查看是否有API密钥相关的错误信息。

### 测试3: 功能验证
```bash
# 访问前端
start http://localhost:8080

# 登录并测试AI功能
```

---

## ⚠️ 常见问题

### Q1: 修改后API不工作？
**A**: 检查以下几点：
1. `.env`文件中的API密钥是否正确
2. docker-compose.yml是否正确修改
3. 服务是否已重启

### Q2: 如何获取新的API密钥？
**A**: 访问 [ZhipuAI开放平台](https://open.bigmodel.cn/)：
1. 注册/登录账号
2. 进入"API密钥管理"
3. 创建新的API密钥
4. 复制密钥并更新到`.env`文件

### Q3: 可以不使用API密钥吗？
**A**: 如果不使用AI功能，可以：
- 临时注释掉`.env`中的API密钥行
- 或在docker-compose.yml中注释掉相关配置

### Q4: 密钥会被提交到Git吗？
**A**: 不会！`.env`文件已在`.gitignore`中，不会被提交：
```bash
# .gitignore 包含:
.env
```

---

## 📝 安全最佳实践

### ✅ 推荐做法

1. **永远不要提交`.env`文件到Git**
2. 使用不同的API密钥用于开发/测试/生产
3. 定期轮换API密钥
4. 为不同项目使用不同的密钥
5. 设置API密钥的使用限额

### ❌ 避免的做法

1. ❌ 在代码中硬编码密钥
2. ❌ 在公开的文档中包含密钥
3. ❌ 在聊天记录中分享密钥
4. ❌ 使用默认或示例密钥

---

## 🎯 快速参考

### 修改前后对比

**修改前** ❌:
```yaml
environment:
  - ZHIPUAI_API_KEY: fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
```

**修改后** ✅:
```yaml
environment:
  - ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
```

### .env文件配置

```bash
# 数据库配置
DB_NAME=db_exam
DB_USER=root
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306

# Django配置
SECRET_KEY=django-insecure-please-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ZhipuAI配置
ZHIPUAI_API_KEY=fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

---

## 🚀 完整操作流程

### 一键执行（推荐）

```bash
# 1. 备份
copy docker-compose.yml docker-compose.yml.backup

# 2. 修改.env文件
notepad .env
# 更新 ZHIPUAI_API_KEY=你的密钥

# 3. 重启服务
docker-compose restart backend

# 4. 验证
docker-compose exec backend env | grep ZHIPUAI
```

### 分步执行

```bash
# 步骤1: 备份
docker-compose.yml.backup
```

```bash
# 步骤2: 编辑docker-compose.yml
# 找到第68行，将:
# ZHIPUAI_API_KEY: fd4abef3ba11457eba10ad862d2b3ec2.PCPLHkU12JIB3aIf
# 改为:
# ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}
```

```bash
# 步骤3: 编辑.env文件
notepad .env
# 确保 ZHIPUAI_API_KEY 有正确的值
```

```bash
# 步骤4: 重启
docker-compose restart backend
```

---

## ✅ 验证成功标志

修复成功后，你应该看到：

1. ✅ `docker-compose.yml`第68行显示: `ZHIPUAI_API_KEY: ${ZHIPUAI_API_KEY}`
2. ✅ `.env`文件包含你的真实API密钥
3. ✅ `docker exec`命令能正确显示环境变量
4. ✅ AI功能正常工作

---

## 📞 需要帮助？

如果遇到问题：

1. **查看详细报告**: `notepad IMPROVEMENT_REPORT_*.md`
2. **查看修复指南**: `notepad fixes/api_key_fix.md`
3. **检查服务日志**: `docker logs fyp_backend`

---

**重要提示**:
- ✅ 修改前先备份
- ✅ 在测试环境验证后再应用到生产
- ✅ 不要在公共场合暴露API密钥
- ✅ 定期轮换密钥以提高安全性

**完成这些步骤后，你的API密钥就安全了！** 🔒
