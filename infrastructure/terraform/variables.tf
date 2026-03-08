# Terraform 变量定义

variable "aws_region" {
  description = "AWS 区域"
  type        = string
  default     = "us-east-1"
}

variable "ami_id" {
  description = "AMI ID (Ubuntu 22.04 LTS)"
  type        = string
  # 默认值需要根据区域调整
  # us-east-1: ami-0c55b159cbfafe1f0
  # ap-southeast-1: ami-0c55b159cbfafe1f0
  default = "ami-0ecb62995f68bb549" # Ubuntu 22.04 LTS
}

variable "instance_type" {
  description = "EC2 实例类型"
  type        = string
  default     = "t2.micro" # 免费层
}

variable "key_pair_name" {
  description = "EC2 密钥对名称"
  type        = string
  default     = "fyp-keypair"
}

variable "public_key_path" {
  description = "SSH 公钥文件路径"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "public_key_content" {
  description = "SSH 公钥内容（如果文件不存在，可以直接提供公钥内容）"
  type        = string
  default     = ""
  sensitive   = false
}

variable "enable_ha" {
  description = "是否启用高可用性（多实例 + 负载均衡）"
  type        = bool
  default     = true
}

variable "acm_certificate_arn" {
  description = "ACM 证书 ARN（配置后启用 ALB 443 HTTPS）"
  type        = string
  default     = ""
}

variable "create_rds" {
  description = "是否创建 RDS 数据库（需要额外预算）"
  type        = bool
  default     = false # 默认使用 EC2 上的 MySQL
}

variable "rds_instance_class" {
  description = "RDS 实例类型"
  type        = string
  default     = "db.t2.micro" # 免费层
}

variable "db_username" {
  description = "数据库用户名"
  type        = string
  default     = "examuser"
  sensitive   = true
}

variable "db_password" {
  description = "数据库密码"
  type        = string
  sensitive   = true
}

variable "github_repo_url" {
  description = "GitHub 仓库 URL"
  type        = string
  default     = "https://github.com/HUANHJiali/FYP-2026-3-1.git"
}

variable "github_deploy_key_private" {
  description = "GitHub Deploy Key 私钥内容（PEM，多行；用于克隆私有仓库）"
  type        = string
  default     = ""
  sensitive   = true
}

# AWS 凭证（如果使用 AWS Academy Learner Lab）
variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Key"
  type        = string
  default     = ""
  sensitive   = true
}

