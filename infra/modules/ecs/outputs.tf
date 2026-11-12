# =============================================================================
# AvertaSaaS - ECS Module Outputs
# =============================================================================

# Cluster
output "cluster_id" {
  description = "ECS Cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  description = "ECS Cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

# Task Execution Role
output "task_execution_role_arn" {
  description = "Task execution role ARN"
  value       = local.task_execution_role_arn
}

output "task_execution_role_name" {
  description = "Task execution role name"
  value       = var.task_execution_role_arn != "" ? "" : aws_iam_role.task_execution[0].name
}

# Task Role
output "task_role_arn" {
  description = "Task role ARN"
  value       = local.task_role_arn
}

output "task_role_name" {
  description = "Task role name"
  value       = var.task_role_arn != "" ? "" : aws_iam_role.task[0].name
}

# Task Definitions
output "backend_task_definition_arn" {
  description = "Backend task definition ARN"
  value       = aws_ecs_task_definition.backend.arn
}

output "backend_task_definition_family" {
  description = "Backend task definition family"
  value       = aws_ecs_task_definition.backend.family
}

output "celery_worker_task_definition_arn" {
  description = "Celery worker task definition ARN"
  value       = aws_ecs_task_definition.celery_worker.arn
}

output "celery_worker_task_definition_family" {
  description = "Celery worker task definition family"
  value       = aws_ecs_task_definition.celery_worker.family
}

output "celery_beat_task_definition_arn" {
  description = "Celery beat task definition ARN"
  value       = aws_ecs_task_definition.celery_beat.arn
}

output "celery_beat_task_definition_family" {
  description = "Celery beat task definition family"
  value       = aws_ecs_task_definition.celery_beat.family
}

output "pgbouncer_task_definition_arn" {
  description = "PgBouncer task definition ARN"
  value       = aws_ecs_task_definition.pgbouncer.arn
}

output "pgbouncer_task_definition_family" {
  description = "PgBouncer task definition family"
  value       = aws_ecs_task_definition.pgbouncer.family
}

# Services
output "backend_service_name" {
  description = "Backend service name"
  value       = aws_ecs_service.backend.name
}

output "backend_service_arn" {
  description = "Backend service ARN"
  value       = aws_ecs_service.backend.arn
}

output "celery_worker_service_name" {
  description = "Celery worker service name"
  value       = aws_ecs_service.celery_worker.name
}

output "celery_worker_service_arn" {
  description = "Celery worker service ARN"
  value       = aws_ecs_service.celery_worker.arn
}

output "celery_beat_service_name" {
  description = "Celery beat service name"
  value       = aws_ecs_service.celery_beat.name
}

output "celery_beat_service_arn" {
  description = "Celery beat service ARN"
  value       = aws_ecs_service.celery_beat.arn
}

output "pgbouncer_service_name" {
  description = "PgBouncer service name"
  value       = aws_ecs_service.pgbouncer.name
}

output "pgbouncer_service_arn" {
  description = "PgBouncer service ARN"
  value       = aws_ecs_service.pgbouncer.arn
}

# Log Groups
output "backend_log_group_name" {
  description = "Backend CloudWatch log group name"
  value       = aws_cloudwatch_log_group.backend.name
}

output "celery_worker_log_group_name" {
  description = "Celery worker CloudWatch log group name"
  value       = aws_cloudwatch_log_group.celery_worker.name
}

output "celery_beat_log_group_name" {
  description = "Celery beat CloudWatch log group name"
  value       = aws_cloudwatch_log_group.celery_beat.name
}

output "pgbouncer_log_group_name" {
  description = "PgBouncer CloudWatch log group name"
  value       = aws_cloudwatch_log_group.pgbouncer.name
}

output "ecs_exec_log_group_name" {
  description = "ECS exec CloudWatch log group name"
  value       = aws_cloudwatch_log_group.ecs_exec.name
}

# PgBouncer Target Group
output "pgbouncer_target_group_arn" {
  description = "PgBouncer target group ARN"
  value       = aws_lb_target_group.pgbouncer.arn
}

output "pgbouncer_target_group_name" {
  description = "PgBouncer target group name"
  value       = aws_lb_target_group.pgbouncer.name
}

# Service Discovery
output "service_discovery_namespace_id" {
  description = "Service discovery namespace ID"
  value       = aws_service_discovery_private_dns_namespace.ecs.id
}

output "service_discovery_namespace_arn" {
  description = "Service discovery namespace ARN"
  value       = aws_service_discovery_private_dns_namespace.ecs.arn
}

output "backend_service_discovery_service_id" {
  description = "Backend service discovery service ID"
  value       = aws_service_discovery_service.backend.id
}

output "pgbouncer_service_discovery_service_id" {
  description = "PgBouncer service discovery service ID"
  value       = aws_service_discovery_service.pgbouncer.id
}