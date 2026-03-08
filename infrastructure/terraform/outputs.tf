# Terraform 输出值

output "backend_instance_ips" {
  description = "后端实例公网 IP 地址"
  value       = aws_instance.fyp_backend[*].public_ip
}

output "backend_instance_ids" {
  description = "后端实例 ID"
  value       = aws_instance.fyp_backend[*].id
}

output "load_balancer_dns" {
  description = "负载均衡器 DNS 名称"
  value       = var.enable_ha ? aws_lb.fyp_alb[0].dns_name : "N/A (HA disabled)"
}

output "load_balancer_url" {
  description = "负载均衡器访问 URL"
  value       = var.enable_ha ? "http://${aws_lb.fyp_alb[0].dns_name}" : "http://${aws_eip.fyp_single[0].public_ip}"
}

output "rds_endpoint" {
  description = "RDS 数据库端点"
  value       = var.create_rds ? aws_db_instance.fyp_db[0].endpoint : "N/A (RDS not created)"
}

output "ssh_command" {
  description = "SSH 连接命令"
  value       = var.enable_ha ? "ssh -i ${var.key_pair_name}.pem ubuntu@${aws_instance.fyp_backend[0].public_ip}" : "ssh -i ${var.key_pair_name}.pem ubuntu@${aws_eip.fyp_single[0].public_ip}"
}

output "frontend_url" {
  description = "前端访问 URL"
  value       = var.enable_ha ? "http://${aws_lb.fyp_alb[0].dns_name}" : "http://${aws_eip.fyp_single[0].public_ip}"
}

output "backend_api_url" {
  description = "后端 API 访问 URL"
  value       = var.enable_ha ? "http://${aws_lb.fyp_alb[0].dns_name}/api/" : "http://${aws_eip.fyp_single[0].public_ip}:8000"
}

output "single_instance_eip" {
  description = "单实例模式固定公网 IP（HA 关闭时）"
  value       = var.enable_ha ? "N/A (HA enabled)" : aws_eip.fyp_single[0].public_ip
}




