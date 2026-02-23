#!/bin/bash

# Terraform 快速部署脚本
# 用于 FYP 演示 - 不使用 Web Console 创建基础设施

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 FYP 项目 - Terraform 部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Terraform 是否安装
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform 未安装${NC}"
    echo -e "${YELLOW}请先安装 Terraform:${NC}"
    echo "  Mac: brew install terraform"
    echo "  Windows: choco install terraform"
    echo "  Linux: 查看 https://www.terraform.io/downloads"
    exit 1
fi

echo -e "${GREEN}✅ Terraform 已安装: $(terraform version | head -n 1)${NC}"

# 检查 AWS 凭证
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}⚠️  AWS 凭证未设置${NC}"
    echo -e "${BLUE}请设置 AWS 凭证:${NC}"
    echo "  export AWS_ACCESS_KEY_ID='your-key'"
    echo "  export AWS_SECRET_ACCESS_KEY='your-secret'"
    echo "  export AWS_SESSION_TOKEN='your-token'  # 如果使用 Learner Lab"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ AWS 凭证已设置${NC}"
fi

# 检查配置文件
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${YELLOW}⚠️  terraform.tfvars 不存在${NC}"
    if [ -f "terraform.tfvars.example" ]; then
        echo -e "${BLUE}从示例文件创建...${NC}"
        cp terraform.tfvars.example terraform.tfvars
        echo -e "${YELLOW}请编辑 terraform.tfvars 文件，填入实际值${NC}"
        read -p "按 Enter 继续..."
    else
        echo -e "${RED}❌ terraform.tfvars.example 也不存在${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}=== 部署步骤 ===${NC}"
echo ""

# 步骤 1: 初始化
echo -e "${YELLOW}[1/4] 初始化 Terraform...${NC}"
terraform init
echo -e "${GREEN}✅ 初始化完成${NC}"
echo ""

# 步骤 2: 验证配置
echo -e "${YELLOW}[2/4] 验证配置...${NC}"
terraform validate
echo -e "${GREEN}✅ 配置验证通过${NC}"
echo ""

# 步骤 3: 预览计划
echo -e "${YELLOW}[3/4] 预览部署计划...${NC}"
echo -e "${BLUE}这将显示将要创建的资源：${NC}"
terraform plan
echo ""

read -p "是否继续部署？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}部署已取消${NC}"
    exit 0
fi

# 步骤 4: 应用配置
echo -e "${YELLOW}[4/4] 创建基础设施（关键演示步骤）...${NC}"
echo -e "${BLUE}这将在 AWS 上创建所有资源，不使用 Web Console！${NC}"
terraform apply -auto-approve

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 显示输出
echo -e "${BLUE}=== 访问信息 ===${NC}"
terraform output

echo ""
echo -e "${BLUE}=== 下一步 ===${NC}"
echo "1. 等待几分钟让应用完全启动"
echo "2. 访问前端: $(terraform output -raw frontend_url 2>/dev/null || echo 'N/A')"
echo "3. 访问后端: $(terraform output -raw backend_api_url 2>/dev/null || echo 'N/A')"
echo ""
echo -e "${YELLOW}查看资源状态:${NC}"
echo "  terraform show"
echo ""
echo -e "${YELLOW}销毁基础设施:${NC}"
echo "  terraform destroy"




