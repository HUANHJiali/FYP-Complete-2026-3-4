# FYP 项目 - AWS Infrastructure as Code
# 使用 Terraform 自动创建 AWS 基础设施
# 完全不需要使用 Web Console

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # 可选：使用 S3 作为后端存储状态
  # backend "s3" {
  #   bucket = "fyp-terraform-state"
  #   key    = "fyp/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  # 如果使用 AWS Academy Learner Lab，需要配置临时凭证
  # access_key = var.aws_access_key
  # secret_key = var.aws_secret_key
}

# 获取默认 VPC
data "aws_vpc" "default" {
  default = true
}

# 获取默认子网
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# 创建安全组
resource "aws_security_group" "fyp_sg" {
  name        = "fyp-exam-system-sg"
  description = "Security group for FYP Exam System"
  vpc_id      = data.aws_vpc.default.id

  # SSH 访问
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 生产环境应限制为特定 IP
  }

  # HTTP 访问
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS 访问
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 后端 API 访问
  ingress {
    description = "Backend API"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 出站规则 - 允许所有
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "fyp-exam-system-sg"
    Project = "FYP2025"
  }
}

# 创建 EC2 实例（高可用性：2 个实例）
resource "aws_instance" "fyp_backend" {
  count = var.enable_ha ? 2 : 1

  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.fyp_key.key_name

  vpc_security_group_ids = [aws_security_group.fyp_sg.id]
  subnet_id              = data.aws_subnets.default.ids[0]

  # 用户数据脚本 - 自动安装 Docker 和部署
  user_data = <<-EOF
#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== 开始 EC2 初始化 ==="
date

# 更新系统并安装 Docker
apt-get update
apt-get install -y docker.io docker-compose git curl

# 启动并启用 Docker
systemctl start docker
systemctl enable docker

# 将 ubuntu 用户添加到 docker 组
usermod -aG docker ubuntu

# 等待 Docker 服务就绪
sleep 5

cd /home/ubuntu

# 克隆仓库（如已存在则 git pull）
if [ ! -d "25FYP" ]; then
  echo "克隆仓库..."
  git clone https://github.com/HUANHJiali/FYP2025-12-27.git 25FYP 2>&1 | tee /tmp/git-clone.log
else
  echo "更新仓库..."
  cd 25FYP
  git pull 2>&1 | tee /tmp/git-pull.log || true
  cd ..
fi

cd 25FYP

# 修复 Git 安全目录问题（如果存在）
git config --global --add safe.directory /home/ubuntu/25FYP || true

# 确保脚本可执行
chmod +x ./deploy/aws-deploy.sh

# 设置环境变量（非交互式部署）
export DB_PASSWORD=Exam123456!
export SECRET_KEY=$(openssl rand -base64 32)

# 运行部署脚本（使用 nohup 在后台运行，避免超时）
nohup bash ./deploy/aws-deploy.sh > /tmp/deploy.log 2>&1 &

echo "部署脚本已在后台启动，查看日志: tail -f /tmp/deploy.log"
echo "=== EC2 初始化完成 ==="
date
EOF

  tags = {
    Name    = "fyp-backend-${count.index + 1}"
    Project = "FYP2025"
    Role    = "backend"
  }
}

# 创建应用负载均衡器（高可用性）
resource "aws_lb" "fyp_alb" {
  count = var.enable_ha ? 1 : 0

  name               = "fyp-exam-system-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.fyp_sg.id]
  subnets            = data.aws_subnets.default.ids

  enable_deletion_protection = false

  tags = {
    Name    = "fyp-exam-system-alb"
    Project = "FYP2025"
  }
}

# 前端目标组（端口 80）
resource "aws_lb_target_group" "fyp_frontend_tg" {
  count = var.enable_ha ? 1 : 0

  name     = "fyp-frontend-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200,404"
  }

  tags = {
    Name    = "fyp-frontend-tg"
    Project = "FYP2025"
  }
}

# 后端目标组（端口 8000）
resource "aws_lb_target_group" "fyp_backend_tg" {
  count = var.enable_ha ? 1 : 0

  name     = "fyp-backend-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 10
    interval            = 30
    path                = "/api/health/"
    protocol            = "HTTP"
    matcher             = "200"
  }

  tags = {
    Name    = "fyp-backend-tg"
    Project = "FYP2025"
  }
}

# 前端目标组附加
resource "aws_lb_target_group_attachment" "fyp_frontend" {
  count = var.enable_ha ? length(aws_instance.fyp_backend) : 0

  target_group_arn = aws_lb_target_group.fyp_frontend_tg[0].arn
  target_id        = aws_instance.fyp_backend[count.index].id
  port             = 80
}

# 后端目标组附加
resource "aws_lb_target_group_attachment" "fyp_backend" {
  count = var.enable_ha ? length(aws_instance.fyp_backend) : 0

  target_group_arn = aws_lb_target_group.fyp_backend_tg[0].arn
  target_id        = aws_instance.fyp_backend[count.index].id
  port             = 8000
}

# ALB 监听器（使用路径规则路由）
resource "aws_lb_listener" "fyp_main" {
  count = var.enable_ha ? 1 : 0

  load_balancer_arn = aws_lb.fyp_alb[0].arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fyp_frontend_tg[0].arn
  }
}

# ALB 监听器规则：API 请求转发到后端
resource "aws_lb_listener_rule" "fyp_api" {
  count = var.enable_ha ? 1 : 0

  listener_arn = aws_lb_listener.fyp_main[0].arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fyp_backend_tg[0].arn
  }

  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# 创建 RDS 数据库（可选，如果预算允许）
resource "aws_db_instance" "fyp_db" {
  count = var.create_rds ? 1 : 0

  identifier = "fyp-exam-db"

  engine         = "mysql"
  engine_version = "8.0"
  instance_class = var.rds_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "db_exam"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.fyp_db_sg[0].id]
  db_subnet_group_name   = aws_db_subnet_group.fyp_db[0].name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  skip_final_snapshot = true

  tags = {
    Name    = "fyp-exam-db"
    Project = "FYP2025"
  }
}

# RDS 安全组
resource "aws_security_group" "fyp_db_sg" {
  count = var.create_rds ? 1 : 0

  name        = "fyp-db-sg"
  description = "Security group for FYP RDS database"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "MySQL"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.fyp_sg.id]
  }

  tags = {
    Name    = "fyp-db-sg"
    Project = "FYP2025"
  }
}

# RDS 子网组
resource "aws_db_subnet_group" "fyp_db" {
  count = var.create_rds ? 1 : 0

  name       = "fyp-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name    = "fyp-db-subnet-group"
    Project = "FYP2025"
  }
}

# 创建密钥对（如果不存在）
# 注意：需要提供有效的 SSH 公钥
# 方法1: 通过文件路径 (public_key_path)
# 方法2: 直接提供公钥内容 (public_key_content)
resource "aws_key_pair" "fyp_key" {
  key_name   = var.key_pair_name
  public_key = var.public_key_content != "" ? var.public_key_content : file(var.public_key_path)
}

