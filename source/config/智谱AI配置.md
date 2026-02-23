# 智谱AI配置说明

## 🔑 API Key格式要求

智谱AI的API Key必须采用 `id.secret` 格式，例如：
```
1234567890abcdef.abcdef1234567890abcdef1234567890abcdef1234567890
```

## ⚠️ 当前问题

您的API Key格式不正确，缺少 `.` 分隔符，导致JWT生成失败。

## 🛠️ 解决方法

### 方法1：设置环境变量（推荐）

在启动Django服务前，在PowerShell中运行：

```powershell
# 运行设置脚本
.\setup_zhipuai_env.ps1

# 或者手动设置
$env:ZHIPUAI_API_KEY = "您的API_ID.您的API_SECRET"
$env:ZHIPUAI_MODEL = "glm-4-flash"
$env:ZHIPUAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
```

### 方法2：修改配置文件

编辑 `server/server/settings.py` 文件：
```python
OPENAI_API_KEY = '您的API_ID.您的API_SECRET'
OPENAI_MODEL = 'glm-4-flash'  # 使用免费模型
```

## 📍 获取API Key

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账户
3. 在控制台中创建API Key
4. 复制格式为 `id.secret` 的API Key

## ✅ 验证成功

配置成功后，您应该看到：
```
正在解析API Key: 您的API_ID.您的API_SECRET...
API ID: 您的API_ID..., API Secret: 您的API_SECRET...
JWT Token生成成功: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
JWT解码验证: {'api_key': '您的API_ID', 'exp': 1734472800, 'iat': 1734469200, 'nbf': 1734469200}
智谱AI请求URL: https://open.bigmodel.cn/api/paas/v4/chat/completions
智谱AI请求Headers: {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...', 'Content-Type': 'application/json'}
```

## 🚨 如果仍然出现HTTP 401错误

即使JWT生成成功，仍可能出现认证失败，可能的原因：

1. **API Key已过期**：检查智谱AI控制台中的API Key状态
2. **账户余额不足**：确认账户有足够的调用额度
3. **权限不足**：验证账户是否有调用GLM-4-Flash模型的权限
4. **JWT格式问题**：虽然生成了JWT，但格式可能不符合智谱AI要求

## 🔧 调试步骤

1. **运行测试脚本**：
   ```bash
   python test_zhipuai_api.py
   ```

2. **检查智谱AI控制台**：
   - API Key状态
   - 账户余额
   - 调用日志

3. **查看详细错误信息**：
   重启Django服务，观察控制台输出的调试信息

## 🆕 最新修复

### JWT生成优化
- 添加了完整的JWT payload字段（iat, nbf, exp）
- 使用标准的HS256算法
- 改进了错误处理和调试信息

### 模型配置更新
- 将模型名称更新为免费模型 `glm-4-flash`
- 确保使用智谱AI v4兼容的模型

### 环境变量支持
- 优先使用环境变量配置
- 提供PowerShell设置脚本
- 支持OpenAI兼容的配置格式

## 🚀 快速启动

1. **设置环境变量**：
   ```powershell
   .\setup_zhipuai_env.ps1
   ```

2. **测试API连接**：
   ```bash
   python test_zhipuai_api.py
   ```

3. **启动Django服务**：
   ```bash
   python manage.py runserver
   ```

## 📞 技术支持

如果问题仍然存在，请：
1. 检查智谱AI控制台的API Key状态
2. 确认账户权限和余额
3. 查看智谱AI的官方文档和更新日志
