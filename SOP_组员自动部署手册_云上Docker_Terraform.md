# SOP：组员自动部署手册（Docker + Terraform + 上云）

> 目标：让组员按本文一步一步操作，即可独立完成：
> 1) 云资源创建（Terraform）
> 2) 应用部署（Docker Compose）
> 3) 域名连通（Cloudflare）
> 4) HTTPS 启用

---

## 0. 适用范围
- 项目仓库：FYP 在线考试系统
- 云平台：AWS（Learner Lab 或普通 AWS 账号）
- 本地系统：Windows（PowerShell）

---

## 1. 组员分工建议（先分工，再执行）
- A 同学：基础设施负责人（Terraform）
- B 同学：应用部署负责人（Docker + 后端/前端）
- C 同学：域名与 HTTPS 负责人（Cloudflare + Certbot）
- D 同学：测试验收负责人（接口、登录、AI 功能）

---

## 2. 部署前准备清单

### 2.1 本地安装
- Git
- Docker Desktop
- Node.js 16+
- Python 3.9+
- Terraform 1.0+
- OpenSSH（Windows 默认已带）

### 2.2 云账号准备
- 有效 AWS 凭证（Access Key / Secret / Session Token）
- 已确认可创建：EC2、安全组、EIP

### 2.3 域名准备
- 已购买域名（如 Namecheap）
- Cloudflare 账号可登录

### 2.4 密钥准备（SSH/部署连接必做）

#### A. 创建 EC2 登录密钥（Windows）
在 PowerShell 执行：

```powershell
mkdir $HOME\.ssh -ErrorAction SilentlyContinue
ssh-keygen -t ed25519 -C "fyp-deploy" -f $HOME\.ssh\fyp_deploy_key -N ""
Get-Content $HOME\.ssh\fyp_deploy_key.pub
```

说明：
- `fyp_deploy_key`：私钥（仅自己保存，严禁外传）
- `fyp_deploy_key.pub`：公钥（可写入 Terraform）

#### B. 把公钥注入 Terraform（推荐）
```powershell
$env:TF_VAR_public_key_content = Get-Content -Raw "$HOME\.ssh\fyp_deploy_key.pub"
$env:TF_VAR_key_pair_name = "fyp-keypair"
```

#### C. （可选）私有仓库自动拉取 Deploy Key
如果仓库是 Private，需要给 GitHub 配置 Deploy Key：

```powershell
cd D:\fyp-2026-2-8-master\fyp-2026-2-8-master\infrastructure\terraform
ssh-keygen -t ed25519 -C "github-deploy" -f .\github_deploy_key -N ""
Get-Content .\github_deploy_key.pub
```

操作：
1) 将 `github_deploy_key.pub` 添加到 GitHub 仓库 `Settings -> Deploy keys`（建议只读）。  
2) 在执行 Terraform 前注入私钥：

```powershell
$env:TF_VAR_github_deploy_key_private = Get-Content -Raw .\infrastructure\terraform\github_deploy_key
```

#### D. 密钥安全要求
- 私钥文件不要提交到 Git。
- 私钥不要发群聊，不要放网盘公开链接。
- 若疑似泄露，立即重新生成并替换。

---

## 3. 一次性目录约定（全员统一）
- 本地仓库根目录：
  - `D:\fyp-2026-2-8-master\fyp-2026-2-8-master`
- Terraform 目录：
  - `infrastructure/terraform`

> 注意：全员统一目录和命令，减少“我这边可以、你那边不行”。

---

## 4. 第一步：拉代码并检查基础环境
在 PowerShell 执行：

```powershell
cd D:\
git clone <你的仓库地址> fyp-2026-2-8-master
cd .\fyp-2026-2-8-master\fyp-2026-2-8-master
terraform -version
docker --version
```

通过标准：
- Terraform、Docker 命令均能输出版本。

---

## 5. 第二步：Terraform 自动创建云资源

### 5.1 设置 AWS 凭证（PowerShell 当前会话）
```powershell
$env:AWS_ACCESS_KEY_ID="你的Key"
$env:AWS_SECRET_ACCESS_KEY="你的Secret"
$env:AWS_SESSION_TOKEN="你的SessionToken"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### 5.2 进入 Terraform 目录
```powershell
cd .\infrastructure\terraform
```

### 5.3 执行 IaC
```powershell
terraform init
terraform validate
terraform plan -var="enable_ha=false"
terraform apply -auto-approve -var="enable_ha=false"
```

### 5.4 记录输出
```powershell
terraform output
```
重点记录：
- 服务器公网地址（单机模式通常是 EIP）
- SSH 连接命令

---

## 6. 第三步：服务器应用自动部署（Docker）

### 6.1 SSH 到服务器
```powershell
ssh -i <你的私钥文件> ubuntu@<服务器IP>
```

### 6.1.1 常用连接命令（建议抄这段）
```powershell
# 连接服务器
ssh -o StrictHostKeyChecking=accept-new -i $HOME\.ssh\fyp_deploy_key ubuntu@<服务器IP>

# 上传文件到服务器
scp -o StrictHostKeyChecking=accept-new -i $HOME\.ssh\fyp_deploy_key .\docker-compose.prod.yml ubuntu@<服务器IP>:/tmp/

# 远程执行命令
ssh -o StrictHostKeyChecking=accept-new -i $HOME\.ssh\fyp_deploy_key ubuntu@<服务器IP> "hostname; docker ps"
```

### 6.2 进入部署目录（约定）
```bash
cd /home/ubuntu/25FYP
```

### 6.3 环境变量文件
- 复制模板为 `.env` 并填写关键项：
  - `SECRET_KEY`
  - `DB_PASSWORD`
  - `ALLOWED_HOSTS`
  - `CORS_ALLOWED_ORIGINS`
  - `CSRF_TRUSTED_ORIGINS`
  - `ZHIPUAI_API_KEY`（如需 AI 功能）

示例：
```bash
cp .env.production.example .env
nano .env
```

### 6.4 启动容器（生产）
```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 6.5 检查状态
```bash
docker-compose -f docker-compose.prod.yml ps
curl -s http://127.0.0.1:8000/api/health/simple/
```

通过标准：
- `backend/frontend/mysql` 为 Up
- 健康接口返回 `{"status":"ok"}`

---

## 7. 第四步：域名接入（Cloudflare）

### 7.1 域名 NS 切换
在注册商后台，把 NS 改为 Cloudflare 提供的两条 NS。

### 7.2 Cloudflare DNS 记录
- `A`：`@` -> 服务器公网 IP（建议 Proxied 开启）
- `CNAME`：`www` -> `@`

### 7.3 连通检查
```powershell
nslookup <你的域名> 1.1.1.1
curl.exe -I http://<你的域名>
```

---

## 8. 第五步：HTTPS 启用（Let’s Encrypt）

在服务器上执行：
```bash
sudo apt-get update
sudo apt-get install -y certbot
```

若源站 80 被前端占用，先临时停前端：
```bash
cd /home/ubuntu/25FYP
docker-compose -f docker-compose.prod.yml stop frontend
sudo certbot certonly --standalone --non-interactive --agree-tos --register-unsafely-without-email -d <你的域名> -d www.<你的域名>
docker-compose -f docker-compose.prod.yml start frontend
```

Nginx 使用证书路径：
- `/etc/letsencrypt/live/<你的域名>/fullchain.pem`
- `/etc/letsencrypt/live/<你的域名>/privkey.pem`

---

## 9. 第六步：AI API 接入（智谱）

### 9.1 写入 `.env`
```env
ZHIPUAI_API_KEY=你的智谱Key
ZHIPUAI_MODEL=glm-4-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

### 9.2 重启后端
```bash
cd /home/ubuntu/25FYP
docker-compose -f docker-compose.prod.yml up -d backend
```

### 9.3 连通测试
```powershell
curl.exe -sS -X POST "https://www.<你的域名>/api/ai/generate_questions/" -H "Content-Type: application/x-www-form-urlencoded" --data "subject=数学&topic=一次函数&difficulty=easy&questionType=0&count=1"
```

通过标准：
- 返回 `code: 0`
- `data.questions` 有内容

---

## 10. 第七步：验收清单（组员交付标准）

### 10.1 基础访问
- [ ] 首页能打开
- [ ] HTTPS 证书正常
- [ ] `/api/health/simple/` 返回 200

### 10.2 业务功能
- [ ] admin 登录成功
- [ ] teacher 登录成功
- [ ] student 登录成功
- [ ] AI 出题接口成功返回

### 10.3 移动端体验
- [ ] 登录页手机可用
- [ ] 筛选区手机换行正常
- [ ] 抽屉菜单手机可打开/关闭

---

## 11. 故障排查 SOP（最常见）

### 问题 A：域名打开到错误页面（如 GitHub）
处理：
1) 查 NS 是否已切 Cloudflare
2) 查 A/CNAME 是否正确
3) 清本地 DNS 缓存
4) 等待 DNS 传播

### 问题 B：HTTPS 报 521
处理：
1) 检查源站 443 是否监听
2) 检查 Nginx 证书配置路径
3) 检查 Cloudflare SSL 模式（建议 Full / Full strict）

### 问题 C：登录页报 websocket 安全错误
处理：
1) 确认前端为生产静态部署（非 dev server）
2) 重新 build frontend 并 up

### 问题 D：AI 接口失败
处理：
1) 检查 `.env` 的 `ZHIPUAI_API_KEY` 是否非空
2) 重启 backend 容器
3) 用 `/api/ai/generate_questions/` 做最小请求测试

### 问题 E：SSH 连接失败（Permission denied publickey）
处理：
1) 确认 Terraform 部署时已注入 `TF_VAR_public_key_content`。  
2) 确认使用的是对应私钥（例如 `fyp_deploy_key` 或项目内指定 key）。  
3) 检查用户名是否为 `ubuntu`。  
4) 用 `terraform output` 再确认当前实例 IP 是否已变化。

---

## 12. 回滚与销毁（成本控制）

### 12.1 应用回滚（容器层）
```bash
cd /home/ubuntu/25FYP
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 12.2 基础设施销毁（Terraform）
```powershell
cd .\infrastructure\terraform
terraform destroy -auto-approve -var="enable_ha=false"
```

---

## 13. 安全注意事项（必须执行）
- 不要把 API Key、云凭证提交到 Git。
- `.env`、私钥文件必须加入忽略并限制权限。
- 共享演示账号后，答辩结束及时修改密码。
- 若 Key 在聊天或日志中暴露，立即轮换。

---

## 14. 最终一句话流程（给组员）
**先 Terraform 出云资源，再 Docker 起应用，再 Cloudflare 连域名，再 Certbot 上 HTTPS，最后 AI 接口验收。**
