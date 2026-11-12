output "db_instance_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_instance_address" {
  description = "RDS instance address"
  value       = aws_db_instance.main.address
}

output "db_read_replica_endpoint" {
  description = "Read replica endpoint (production only)"
  value       = var.environment == "production" ? aws_db_instance.read_replica[0].endpoint : null
}

output "db_read_replica_address" {
  description = "Read replica address (production only)"
  value       = var.environment == "production" ? aws_db_instance.read_replica[0].address : null
}

output "db_name" {
  description = "Database name"
  value       = var.db_name
}

output "db_username" {
  description = "Master username"
  value       = var.username
}

output "db_password" {
  description = "Master password (sensitive)"
  value       = local.db_password
  sensitive   = true
}

output "db_parameter_group_name" {
  description = "DB parameter group name"
  value       = local.parameter_group_name
}

output "db_subnet_group_name" {
  description = "DB subnet group name"
  value       = var.db_subnet_group_name
}

output "secrets_manager_secret_arn" {
  description = "Secrets Manager secret ARN for DB credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "secrets_manager_secret_name" {
  description = "Secrets Manager secret name for DB credentials"
  value       = aws_secretsmanager_secret.db_credentials.name
}

output "monitoring_role_arn" {
  description = "IAM role ARN for enhanced monitoring"
  value       = local.monitoring_role_arn
}