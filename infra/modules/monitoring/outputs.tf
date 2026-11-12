# =============================================================================
# AvertaSaaS - Monitoring Module Outputs
# =============================================================================

output "sns_topic_arn" {
  description = "SNS topic ARN for alarms"
  value       = local.alarm_topic_arn
}

output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "dashboard_arn" {
  description = "CloudWatch dashboard ARN"
  value       = aws_cloudwatch_dashboard.main.dashboard_arn
}

output "log_group_names" {
  description = "Created CloudWatch log group names"
  value       = { for k, v in aws_cloudwatch_log_group.app_logs : k => v.name }
}

output "alarm_names" {
  description = "Created CloudWatch alarm names"
  value       = [
    aws_cloudwatch_metric_alarm.ecs_high_cpu.alarm_name,
    aws_cloudwatch_metric_alarm.ecs_high_memory.alarm_name,
    var.alb_arn != "" ? aws_cloudwatch_metric_alarm.alb_high_latency[0].alarm_name : null,
    var.alb_arn != "" ? aws_cloudwatch_metric_alarm.alb_5xx_errors[0].alarm_name : null,
    var.rds_instance_identifier != "" ? aws_cloudwatch_metric_alarm.rds_high_cpu[0].alarm_name : null,
    var.rds_instance_identifier != "" ? aws_cloudwatch_metric_alarm.rds_low_storage[0].alarm_name : null,
    var.elasticache_cluster_id != "" ? aws_cloudwatch_metric_alarm.elasticache_high_cpu[0].alarm_name : null,
    var.elasticache_cluster_id != "" ? aws_cloudwatch_metric_alarm.elasticache_high_memory[0].alarm_name : null,
    aws_cloudwatch_metric_alarm.backend_low_task_count.alarm_name
  ]
}