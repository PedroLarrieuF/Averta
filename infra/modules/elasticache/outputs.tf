output "replication_group_id" {
  description = "ElastiCache replication group ID"
  value       = aws_elasticache_replication_group.main.id
}

output "replication_group_arn" {
  description = "ElastiCache replication group ARN"
  value       = aws_elasticache_replication_group.main.arn
}

output "primary_endpoint_address" {
  description = "Primary endpoint address"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "primary_endpoint_port" {
  description = "Primary endpoint port"
  value       = aws_elasticache_replication_group.main.primary_endpoint_port
}

output "reader_endpoint_address" {
  description = "Reader endpoint address (for read replicas)"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "reader_endpoint_port" {
  description = "Reader endpoint port"
  value       = aws_elasticache_replication_group.main.reader_endpoint_port
}

output "configuration_endpoint_address" {
  description = "Configuration endpoint address (for cluster mode)"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_address
}

output "configuration_endpoint_port" {
  description = "Configuration endpoint port"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_port
}

output "auth_token" {
  description = "Redis AUTH token"
  value       = local.auth_token
  sensitive   = true
}

output "secrets_manager_secret_arn" {
  description = "Secrets Manager secret ARN for Redis credentials"
  value       = aws_secretsmanager_secret.redis_credentials.arn
}

output "secrets_manager_secret_name" {
  description = "Secrets Manager secret name for Redis credentials"
  value       = aws_secretsmanager_secret.redis_credentials.name
}

output "parameter_group_name" {
  description = "Parameter group name"
  value       = local.parameter_group_name
}

output "subnet_group_name" {
  description = "Subnet group name"
  value       = var.elasticache_subnet_group_name
}