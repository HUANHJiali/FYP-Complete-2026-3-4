# FYP CDK HA 自动部署（AWS）

本目录提供基于 AWS CDK（CloudFormation）的高可用自动部署骨架：

- VPC（2 AZ）
- ECS Fargate（frontend 2 task + backend 2 task）
- ALB 路由（`/` 到 frontend，`/api/*` 到 backend）
- RDS MySQL（Multi-AZ）
- 自动扩缩容（CPU）

## 1. 前置条件

- Node.js 18+
- AWS CLI 已登录（或已设置环境变量）
- CDK Bootstrap 已完成（每个账号/区域一次）

## 2. 安装与合成

```bash
cd infrastructure/cdk
npm install
npx cdk bootstrap aws://<ACCOUNT_ID>/us-east-1
npx cdk synth
```

## 3. 准备镜像

你需要先将前后端镜像推送到 ECR，得到两个 URI：

- `BACKEND_IMAGE_URI`
- `FRONTEND_IMAGE_URI`

例如：

- `386922361011.dkr.ecr.us-east-1.amazonaws.com/fyp-backend:latest`
- `386922361011.dkr.ecr.us-east-1.amazonaws.com/fyp-frontend:latest`

## 4. 部署（手动）

```bash
cd infrastructure/cdk
$env:BACKEND_IMAGE_URI="<your-backend-image-uri>"
$env:FRONTEND_IMAGE_URI="<your-frontend-image-uri>"
$env:DB_NAME="db_exam"
npx cdk deploy --require-approval never
```

## 4.1 一键本地部署（推荐）

```powershell
cd infrastructure/cdk
.\deploy-local.ps1 -Region us-east-1 -AccountId 386922361011
```

销毁：

```powershell
cd infrastructure/cdk
.\deploy-local.ps1 -Destroy
```

## 5. 销毁

```bash
cd infrastructure/cdk
npx cdk destroy --force
```

## 6. 与当前 Terraform 方案差异

- CDK 以 AWS 原生资源编排为主，更适合单云 AWS 项目答辩。
- ECS/Fargate 避免 EC2 user_data 漂移问题，部署稳定性更高。
- GitHub Actions 可无缝衔接镜像构建与自动发布。

## 7. 注意事项

- 当前栈默认开启 Multi-AZ RDS，成本高于单机 EC2。
- 若预算受限，可把 RDS 改为单 AZ 或先关闭数据库资源。
- 前端镜像默认监听 `80` 端口，如你镜像为 `8080` 请同步修改栈代码。
- 如果 `docker login` 到 ECR 返回 `400 Bad Request`，优先检查 Docker Desktop 代理配置，需关闭代理后重试。
