# Terraform 自动部署指南

## 概述

本 Terraform 配置会自动创建 AWS 基础设施并部署 FYP 应用，**自动处理所有常见问题**，无需手动干预。

## 自动解决的问题

✅ **AMI ID 无效** - 使用正确的 Ubuntu 22.04 LTS AMI  
✅ **操作系统不匹配** - 自动使用 Ubuntu 系统  
✅ **Docker 未安装** - 自动安装 Docker 和 Docker Compose  
✅ **GitHub 仓库访问** - 自动克隆/更新代码  
✅ **gunicorn 缺失** - 自动添加到 requirements.txt  
✅ **mysqlclient 编译慢** - 自动移除，使用 pymysql  
✅ **Migration 冲突** - 自动检测并清空数据库重新迁移  
✅ **CORS 配置错误** - 自动处理 metadata 服务错误  
✅ **Git 安全目录** - 自动配置  
✅ **内存不足** - 自动创建交换空间  

## 快速开始

### Learner Lab 一键自动部署（推荐）

每次 `Launch AWS Academy Learner Lab` 后，更新凭证并执行：

```powershell
cd infrastructure/terraform
.\learner-lab-deploy.ps1
```

说明：
- 默认行为：`init -> validate -> plan -> apply -> 健康检查`。
- 健康检查失败时会自动回滚（`terraform destroy`），避免继续计费。
- 只看计划不部署：

```powershell
.\learner-lab-deploy.ps1 -PlanOnly
```

- 部署后失败但保留资源排查：

```powershell
.\learner-lab-deploy.ps1 -SkipRollback
```

### 1. 配置 AWS 凭证

**⚠️ 重要：永远不要将真实的 AWS 凭证提交到 Git！**

**Windows PowerShell:**

1. 复制示例文件：
   ```powershell
   cd infrastructure/terraform
   Copy-Item set-env.ps1.example set-env.ps1
   ```

2. 编辑 `set-env.ps1`，填入你的 AWS Academy Learner Lab 凭证：
   - 登录 AWS Academy Learner Lab
   - 点击 "AWS Details" → "Show" (在 AWS CLI 或 Credentials 旁边)
   - 复制 Access Key ID、Secret Access Key 和 Session Token
   - 粘贴到 `set-env.ps1` 文件中

3. 运行脚本：
   ```powershell
   .\set-env.ps1
   ```

**Linux/Mac:**
```bash
cd infrastructure/terraform
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # 如果使用临时凭证
export AWS_DEFAULT_REGION="us-east-1"
```

**注意**: `set-env.ps1` 已在 `.gitignore` 中，不会被提交到 Git。

### 2. 初始化 Terraform

```bash
terraform init
```

### 3. 查看计划（可选）

```bash
terraform plan
```

### 4. 部署基础设施

```bash
terraform apply
```

输入 `yes` 确认部署。

### 5. 查看部署状态

部署完成后，Terraform 会输出：
- EC2 实例 IP 地址
- ALB DNS 名称（如果启用 HA）
- SSH 连接命令

### 6. 监控部署进度

SSH 到 EC2 实例查看部署日志：

```bash
# 查看 user_data 日志
sudo tail -f /var/log/user-data.log

# 查看部署脚本日志
tail -f /tmp/deploy.log

# 查看容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看服务日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 配置选项

编辑 `variables.tf` 可以修改：

- `instance_type`: EC2 实例类型（默认: `t3.medium`）
- `ami_id`: Ubuntu AMI ID（默认: Ubuntu 22.04 LTS）
- `enable_ha`: 是否启用高可用性（默认: `false`）
- `aws_region`: AWS 区域（默认: `us-east-1`）
- `acm_certificate_arn`: ACM 证书 ARN（配置后启用 ALB 443 HTTPS，80 自动跳转到 443）

### HTTPS（ALB 443 + ACM）

当你已有 ACM 证书时，可直接在变量中设置：

```bash
terraform apply -var="enable_ha=true" -var="acm_certificate_arn=arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/xxxx"
```

行为说明：
- 配置 `acm_certificate_arn` 后：创建 `443/HTTPS` 监听器，`80/HTTP` 自动 301 跳转到 443。
- 未配置 `acm_certificate_arn` 时：保持当前 HTTP 行为（80 直连）。

## 验证部署

### 方法 1: 通过 ALB（如果启用 HA）

```bash
# 获取 ALB DNS
terraform output alb_dns_name

# 测试前端
curl http://$(terraform output -raw alb_dns_name)/

# 测试后端 API
curl http://$(terraform output -raw alb_dns_name)/api/projects/all/
```

### 方法 2: 直接访问 EC2

```bash
# 获取 EC2 IP
terraform output ec2_public_ips

# 测试前端
curl http://<EC2_IP>/

# 测试后端 API
curl http://<EC2_IP>:8000/api/projects/all/
```

## 故障排查

### 问题 1: 构建镜像很慢

**原因**: EC2 实例资源有限  
**解决**: 
- 等待构建完成（通常 10-15 分钟）
- 或使用更大的实例类型（如 `t3.large`）

### 问题 2: 服务无法访问

**检查步骤**:
```bash
# 1. 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 2. 查看日志
docker-compose -f docker-compose.prod.yml logs --tail=50 backend

# 3. 检查端口监听
sudo ss -tlnp | grep -E ':(80|8000)'

# 4. 检查安全组
# 确保端口 80, 443, 8000 已开放
```

### 问题 3: Migration 冲突

**自动处理**: 部署脚本会自动检测并清空数据库  
**手动修复**:
```bash
docker-compose -f docker-compose.prod.yml exec db mysql -uroot -pExam123456! -e "DROP DATABASE IF EXISTS db_exam; CREATE DATABASE db_exam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
docker-compose -f docker-compose.prod.yml restart backend
```

### 问题 4: AWS 凭证过期

**症状**: `InvalidClientTokenId` 错误  
**解决**: 从 AWS Academy 重新获取凭证并更新环境变量

## 清理资源

**警告**: 这会删除所有创建的资源！

```bash
terraform destroy
```

## 输出信息

部署成功后，Terraform 会输出：

- `ec2_public_ips`: EC2 实例公网 IP 列表
- `ec2_ssh_commands`: SSH 连接命令
- `alb_dns_name`: ALB DNS 名称（如果启用 HA）
- `alb_url`: 完整访问 URL（如果启用 HA）

## 常见问题

### Q: 部署需要多长时间？

A: 通常 15-20 分钟：
- EC2 启动: 2-3 分钟
- Docker 安装: 2-3 分钟
- 代码克隆: 1-2 分钟
- 镜像构建: 10-15 分钟（取决于实例类型）

### Q: 如何查看实时日志？

A: 
```bash
# SSH 到 EC2
ssh -i your-key.pem ubuntu@<EC2_IP>

# 查看部署日志
tail -f /tmp/deploy.log

# 查看容器日志
docker-compose -f docker-compose.prod.yml logs -f
```

### Q: 如何更新应用？

A: 
```bash
# 在 EC2 上
cd /home/ubuntu/25FYP
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Q: 如何启用高可用性？

A: 编辑 `variables.tf`，设置 `enable_ha = true`，然后 `terraform apply`

## 技术支持

如遇问题，请查看：
- `source/docs/部署问题总结与解决方案.md` - 详细问题列表
- `source/docs/AWS部署指南.md` - 完整部署指南
