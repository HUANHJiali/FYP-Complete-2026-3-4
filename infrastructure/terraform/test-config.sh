#!/bin/bash

# Terraform 配置测试脚本
# 用于验证配置是否正确，不实际创建资源

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 Terraform 配置测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Terraform 版本: $(terraform version | head -n 1)${NC}"
echo ""

# 步骤 1: 格式化检查
echo -e "${YELLOW}[1/4] 检查代码格式...${NC}"
if terraform fmt -check -recursive .; then
    echo -e "${GREEN}✅ 代码格式正确${NC}"
else
    echo -e "${YELLOW}⚠️  代码格式需要调整，运行: terraform fmt${NC}"
    terraform fmt -recursive .
    echo -e "${GREEN}✅ 已自动格式化${NC}"
fi
echo ""

# 步骤 2: 初始化
echo -e "${YELLOW}[2/4] 初始化 Terraform...${NC}"
if terraform init -upgrade > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 初始化成功${NC}"
else
    echo -e "${RED}❌ 初始化失败${NC}"
    terraform init -upgrade
    exit 1
fi
echo ""

# 步骤 3: 验证配置
echo -e "${YELLOW}[3/4] 验证配置语法...${NC}"
if terraform validate; then
    echo -e "${GREEN}✅ 配置验证通过${NC}"
else
    echo -e "${RED}❌ 配置验证失败${NC}"
    exit 1
fi
echo ""

# 步骤 4: 检查变量
echo -e "${YELLOW}[4/4] 检查变量配置...${NC}"
if [ -f "terraform.tfvars" ]; then
    echo -e "${GREEN}✅ terraform.tfvars 存在${NC}"
else
    echo -e "${YELLOW}⚠️  terraform.tfvars 不存在${NC}"
    if [ -f "terraform.tfvars.example" ]; then
        echo -e "${BLUE}从示例文件创建测试配置...${NC}"
        cp terraform.tfvars.example terraform.tfvars
        echo -e "${GREEN}✅ 已创建 terraform.tfvars${NC}"
        echo -e "${YELLOW}请编辑 terraform.tfvars 填入实际值${NC}"
    fi
fi
echo ""

# 步骤 5: 尝试 plan（如果有 AWS 凭证）
echo -e "${YELLOW}[5/5] 尝试生成部署计划...${NC}"
if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${GREEN}✅ 检测到 AWS 凭证${NC}"
    echo -e "${BLUE}运行 terraform plan（不实际创建资源）...${NC}"
    if terraform plan -out=tfplan > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 部署计划生成成功${NC}"
        echo -e "${BLUE}计划文件已保存: tfplan${NC}"
        echo -e "${YELLOW}查看计划: terraform show tfplan${NC}"
        echo -e "${YELLOW}应用计划: terraform apply tfplan${NC}"
    else
        echo -e "${YELLOW}⚠️  无法生成部署计划（可能需要配置变量）${NC}"
        echo -e "${BLUE}运行完整计划查看详情:${NC}"
        terraform plan
    fi
else
    echo -e "${YELLOW}⚠️  未检测到 AWS 凭证${NC}"
    echo -e "${BLUE}设置 AWS 凭证后可以运行: terraform plan${NC}"
    echo ""
    echo -e "${BLUE}配置 AWS 凭证:${NC}"
    echo "  export AWS_ACCESS_KEY_ID='your-key'"
    echo "  export AWS_SECRET_ACCESS_KEY='your-secret'"
    echo "  export AWS_SESSION_TOKEN='your-token'  # 如果使用 Learner Lab"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 配置测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}下一步:${NC}"
echo "1. 编辑 terraform.tfvars 填入实际值"
echo "2. 配置 AWS 凭证"
echo "3. 运行: terraform plan"
echo "4. 运行: terraform apply"




