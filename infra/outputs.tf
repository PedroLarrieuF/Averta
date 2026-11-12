# =============================================================================
# AvertaSaaS - Root Outputs
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "database_endpoint" {
  description = "RDS cluster endpoint"
  value       = module.rds.cluster_endpoint
}

output "database_reader_endpoint" {
  description = "RDS reader endpoint"
  value       = module.rds.reader_endpoint
}

output "redis_endpoint" {
  description = "ElastiCache primary endpoint"
  value       = module.elasticache.primary_endpoint
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "alb_arn" {
  description = "ALB ARN"
  value       = module.alb.alb_arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = module.ecs.cluster_arn
}

output "backend_service_name" {
  description = "Backend service name"
  value       = module.ecs.backend_service_name
}

output "documents_bucket_name" {
  description = "Documents S3 bucket name"
  value       = module.s3.documents_bucket_name
}

output "certificate_arn" {
  description = "ACM certificate ARN"
  value       = var.domain_name != "" ? module.route53[0].certificate_arn : null
}

output "fqdn" {
  description = "API FQDN"
  value       = var.domain_name != "" ? module.route53[0].fqdn : null
}

output "github_actions_role_arn" {
  description = "GitHub Actions role ARN"
  value       = module.iam.github_actions_role_arn
}

output "task_execution_role_arn" {
  description = "Task execution role ARN"
  value       = module.iam.task_execution_role_arn
}

output "task_role_arn" {
  description = "Task role ARN"
  value       = module.iam.task_role_arn
}

output "monitoring_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${module.monitoring.dashboard_name}"
}