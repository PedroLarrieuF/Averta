# =============================================================================
# AvertaSaaS - IAM Module Outputs
# =============================================================================

# GitHub Actions OIDC
output "github_oidc_provider_arn" {
  description = "GitHub OIDC provider ARN"
  value       = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? aws_iam_openid_connect_provider.github[0].arn : null
}

output "github_actions_role_arn" {
  description = "GitHub Actions role ARN"
  value       = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? aws_iam_role.github_actions[0].arn : null
}

output "github_actions_role_name" {
  description = "GitHub Actions role name"
  value       = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? aws_iam_role.github_actions[0].name : null
}

# Task Execution Role
output "task_execution_role_arn" {
  description = "Task execution role ARN"
  value       = var.create_task_execution_role ? aws_iam_role.task_execution[0].arn : null
}

output "task_execution_role_name" {
  description = "Task execution role name"
  value       = var.create_task_execution_role ? aws_iam_role.task_execution[0].name : null
}

# Task Role
output "task_role_arn" {
  description = "Task role ARN"
  value       = var.create_task_role ? aws_iam_role.task[0].arn : null
}

output "task_role_name" {
  description = "Task role name"
  value       = var.create_task_role ? aws_iam_role.task[0].name : null
}

# Developer Roles
output "developer_role_arns" {
  description = "Map of developer role ARNs"
  value       = var.create_developer_roles ? { for k, v in aws_iam_role.developer : k => v.arn } : {}
}

output "developer_role_names" {
  description = "Map of developer role names"
  value       = var.create_developer_roles ? { for k, v in aws_iam_role.developer : k => v.name } : {}
}

# Service-Linked Roles
output "ecs_service_linked_role_arn" {
  description = "ECS service-linked role ARN"
  value       = aws_iam_service_linked_role.ecs.arn
}

output "fargate_service_linked_role_arn" {
  description = "Fargate service-linked role ARN"
  value       = aws_iam_service_linked_role.ecs_fargate.arn
}

output "application_autoscaling_service_linked_role_arn" {
  description = "Application Auto Scaling service-linked role ARN"
  value       = aws_iam_service_linked_role.application_autoscaling.arn
}