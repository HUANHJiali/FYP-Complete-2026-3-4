# 自动部署选型对比（CDK vs Terraform vs Kubernetes）

## 结论

结合当前项目（Django + Vue + Docker，单云 AWS，课程演示需要 HA + 自动化）：

**推荐优先级：CDK > Terraform > Kubernetes**

## 对比维度

| 维度 | CDK（CloudFormation） | Terraform | Kubernetes（EKS） |
|---|---|---|---|
| 云厂商适配 | AWS 最优 | 跨云最优 | 跨云可行但复杂 |
| 与你现状匹配 | 高（已在 AWS） | 高（已有代码） | 中（改造大） |
| HA 能力 | 高（ALB+ECS+RDS） | 高（取决于设计） | 很高 |
| 自动化落地 | 高（GitHub Actions + CDK） | 高（Actions + Terraform） | 高（Argo/Helm/GitOps） |
| 运维复杂度 | 中 | 中 | 高 |
| 成本可控性 | 中 | 中 | 低-中（集群成本） |
| 答辩可解释性 | 高（AWS 原生） | 高（IaC 标准） | 中（术语多） |

## 为什么你当前更适合 CDK

- 你已验证 Terraform 在 `EC2 + user_data` 路径存在脆弱点（启动脚本、SSH、主机键、镜像拉取等）。
- CDK 直接落到 `ECS Fargate`，消除了大部分主机初始化不确定性。
- 使用 AWS 原生资源图谱，更易向评审解释“高可用 + 自动化”闭环。

## 建议实施路线（两周内可完成）

1. **第1阶段（1-2天）**：CDK 创建网络/ALB/ECS/RDS 基础栈。
2. **第2阶段（1-2天）**：把前后端镜像推送到 ECR，完成服务上线。
3. **第3阶段（1天）**：加 GitHub Actions 自动部署。
4. **第4阶段（1天）**：压测与故障演练（停一个 task 仍可服务）。
5. **第5阶段（半天）**：准备答辩演示脚本与对比说明。

## 当前环境实测限制（AWS Academy Learner Lab）

- 已完成：前后端镜像可构建并推送到 ECR。
- 受限点：CDK `bootstrap/deploy` 需要创建 IAM Role（如 `cdk-hnb659fds-*`、ECS Task Role），当前临时角色无 `iam:CreateRole` 权限。
- 实际报错：`not authorized to perform iam:CreateRole`。

### 可执行应对

1. **课程演示优先**：继续使用现有 Terraform（无需新增 IAM Role 路径）完成自动化与 HA 演示。
2. **若必须 CDK 上云**：让管理员预创建/授权以下能力后再部署：
	- `iam:CreateRole`
	- `iam:AttachRolePolicy`
	- `iam:PassRole`
3. **报告写法建议**：注明“工具选型推荐 CDK，但受实验账号 IAM 权限约束，实装演示采用 Terraform 路径”。

## 评分点映射（HA + Automation）

- **HA**：多 AZ VPC、ALB、ECS `desiredCount>=2`、RDS Multi-AZ。
- **Automation**：`git push -> build image -> push ECR -> cdk deploy -> health check`。
- **可重复性**：`cdk deploy/destroy` 一键创建和回收。
