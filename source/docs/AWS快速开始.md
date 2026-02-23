# 🚀 AWS Learner Lab 快速开始（5分钟部署）

## 📋 前置准备

1. ✅ 登录 AWS Academy
2. ✅ 启动 Learner Lab
3. ✅ 获取临时 AWS 凭证

---

## 🎯 快速部署步骤

### 步骤 1: 创建 EC2 实例（2分钟）

1. **登录 AWS Console**
   - 访问：https://console.aws.amazon.com
   - 选择区域：`us-east-1` (N. Virginia)

2. **启动 EC2 实例**
   - 进入 **EC2** → **Launch Instance**
   - **Name**: `fyp-exam-system`
   - **AMI**: `Ubuntu Server 22.04 LTS`
   - **Instance Type**: `t2.micro` (免费层)
   - **Key Pair**: 创建新密钥对 `fyp-keypair`，下载 `.pem` 文件
   - **Network Settings**: 编辑安全组
     - ✅ SSH (22) - My IP
     - ✅ HTTP (80) - Anywhere (0.0.0.0/0)
     - ✅ HTTPS (443) - Anywhere
     - ✅ Custom TCP (8000) - Anywhere
   - **Storage**: 20 GB
   - 点击 **Launch Instance**

3. **记录信息**
   - 记录 **Public IPv4 address** (例如: `54.123.45.67`)

### 步骤 2: 连接 EC2（1分钟）

**Windows (PowerShell):**
```powershell
# 设置密钥权限
icacls fyp-keypair.pem /inheritance:r
icacls fyp-keypair.pem /grant:r "$env:USERNAME:R"

# 连接
ssh -i fyp-keypair.pem ubuntu@your-ec2-ip
```

**Mac/Linux:**
```bash
chmod 400 fyp-keypair.pem
ssh -i fyp-keypair.pem ubuntu@your-ec2-ip
```

### 步骤 3: 部署项目（2分钟）

```bash
# 1. 克隆项目
cd /home/ubuntu
git clone https://github.com/your-username/25FYP.git
cd 25FYP

# 2. 运行部署脚本
chmod +x deploy/aws-deploy.sh
./deploy/aws-deploy.sh

# 3. 按照提示输入配置（或直接回车使用默认值）
```

### 步骤 4: 访问系统

在浏览器中打开：
- **前端**: `http://your-ec2-ip`
- **后端**: `http://your-ec2-ip:8000`

---

## ✅ 验证部署

```bash
# 在 EC2 上检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 更新代码
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 💰 成本控制

### 查看成本

1. 进入 **AWS Console** → **Cost Explorer**
2. 查看当前费用
3. 设置预算警报（建议：$40 警告）

### 节省成本

- ✅ 使用 `t2.micro` 免费层
- ✅ 不使用实例时停止（Stop Instance）
- ✅ 删除不需要的资源
- ✅ 使用 20 GB 存储（免费层）

### 预计成本

- **EC2 t2.micro**: 免费（750小时/月）
- **EBS 20GB**: 免费（30GB/月）
- **数据传输**: 免费（15GB/月）
- **总计**: **$0/月**（如果使用免费层）

---

## 🐛 常见问题

### Q: 无法连接 EC2？

**检查：**
1. 安全组是否允许 SSH (22)
2. 密钥文件权限是否正确
3. 实例是否正在运行

### Q: 服务无法访问？

**检查：**
1. 安全组是否开放 80, 8000 端口
2. 服务是否运行：`docker-compose ps`
3. 查看日志：`docker-compose logs`

### Q: 内存不足？

```bash
# 创建交换空间（脚本会自动创建）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📝 演示准备

### 1. 截图清单

- [ ] AWS Console - EC2 实例列表
- [ ] AWS Console - 安全组配置
- [ ] 系统运行截图（前端、后端）
- [ ] Cost Explorer 截图（显示成本）

### 2. 演示脚本

```bash
# 在 EC2 上创建演示脚本
cat > demo.sh << 'EOF'
#!/bin/bash
IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "=== FYP 系统演示 ==="
echo "前端: http://$IP"
echo "后端: http://$IP:8000"
echo ""
echo "服务状态:"
docker-compose -f docker-compose.prod.yml ps
EOF
chmod +x demo.sh
```

---

## 📚 详细文档

- 📖 [完整 AWS 部署指南](./AWS部署指南.md)
- 🐳 [Docker 部署文档](../../DOCKER_DEPLOYMENT.md)

---

**🎉 部署完成后，记得在演示中展示 AWS 架构和成本控制！**




