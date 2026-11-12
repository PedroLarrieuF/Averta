# =============================================================================
# AvertaSaaS - Monitoring Module
# Creates CloudWatch dashboards, alarms, log groups, and X-Ray
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "monitoring"
    },
    var.tags
  )

  name_prefix = "${var.project_name}-${var.environment}"
}

# =============================================================================
# SNS Topic for Alarms
# =============================================================================

resource "aws_sns_topic" "alarms" {
  count = var.notification_email != "" ? 1 : 0

  name = "${local.name_prefix}-alarms"

  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "email" {
  count = var.notification_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}

locals {
  alarm_topic_arn = var.notification_email != "" ? aws_sns_topic.alarms[0].arn : null
}

# =============================================================================
# CloudWatch Log Groups
# =============================================================================

resource "aws_cloudwatch_log_group" "app_logs" {
  for_each = toset(var.log_group_names)

  name              = each.value
  retention_in_days = var.log_group_retention_days
  tags              = local.common_tags
}

# =============================================================================
# CloudWatch Dashboard
# =============================================================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = local.name_prefix

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# ${var.project_name} - ${var.environment} Dashboard"
        }
      },
      # ECS Cluster Metrics
      {
        type   = "metric"
        x      = 0
        y      = 1
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.cluster_name],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.cluster_name],
            ["AWS/ECS", "RunningTaskCount", "ClusterName", var.cluster_name],
            ["AWS/ECS", "PendingTaskCount", "ClusterName", var.cluster_name]
          ]
          view                = "timeSeries"
          stacked             = false
          region              = var.aws_region
          title               = "ECS Cluster Overview"
          period              = 300
          stat                = "Average"
          yAxis = {
            left = {
              label = "Percent/Count"
              min   = 0
            }
          }
        }
      },
      # ALB Metrics
      {
        type   = "metric"
        x      = 12
        y      = 1
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", split("/", var.alb_arn)[1]],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", split("/", var.alb_arn)[1]],
            ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", split("/", var.alb_arn)[1]],
            ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", split("/", var.alb_arn)[1]],
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", split("/", var.alb_arn)[1]]
          ]
          view                = "timeSeries"
          stacked             = false
          region              = var.aws_region
          title               = "ALB Metrics"
          period              = 300
          stat                = "Sum"
          yAxis = {
            left = {
              label = "Count/Time"
              min   = 0
            }
          }
        }
      },
      # RDS Metrics
      {
        type   = "metric"
        x      = 0
        y      = 7
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", var.rds_instance_identifier],
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", var.rds_instance_identifier],
            ["AWS/RDS", "ReadLatency", "DBInstanceIdentifier", var.rds_instance_identifier],
            ["AWS/RDS", "WriteLatency", "DBInstanceIdentifier", var.rds_instance_identifier],
            ["AWS/RDS", "FreeableMemory", "DBInstanceIdentifier", var.rds_instance_identifier],
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", var.rds_instance_identifier]
          ]
          view                = "timeSeries"
          stacked             = false
          region              = var.aws_region
          title               = "RDS Metrics"
          period              = 300
          stat                = "Average"
        }
      },
      # ElastiCache Metrics
      {
        type   = "metric"
        x      = 12
        y      = 7
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", var.elasticache_cluster_id],
            ["AWS/ElastiCache", "DatabaseMemoryUsagePercentage", "CacheClusterId", var.elasticache_cluster_id],
            ["AWS/ElastiCache", "CurrConnections", "CacheClusterId", var.elasticache_cluster_id],
            ["AWS/ElastiCache", "CacheHits", "CacheClusterId", var.elasticache_cluster_id],
            ["AWS/ElastiCache", "CacheMisses", "CacheClusterId", var.elasticache_cluster_id],
            ["AWS/ElastiCache", "NetworkBytesIn", "CacheClusterId", var.elasticache_cluster_id],
            ["AWS/ElastiCache", "NetworkBytesOut", "CacheClusterId", var.elasticache_cluster_id]
          ]
          view                = "timeSeries"
          stacked             = false
          region              = var.aws_region
          title               = "ElastiCache Metrics"
          period              = 300
          stat                = "Average"
        }
      },
      # S3 Metrics
      {
        type   = "metric"
        x      = 0
        y      = 13
        width  = 12
        height = 6
        properties = {
          metrics = [
            for bucket in var.s3_bucket_names : [
              "AWS/S3", "BucketSizeBytes", "BucketName", bucket, "StorageType", "StandardStorage"
            ]
          ]
          view                = "timeSeries"
          stacked             = false
          region              = var.aws_region
          title               = "S3 Storage Metrics"
          period              = 86400
          stat                = "Average"
        }
      },
      # ECS Service Metrics
      {
        type   = "metric"
        x      = 12
        y      = 13
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.cluster_name, "ServiceName", "${local.name_prefix}-backend"],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.cluster_name, "ServiceName", "${local.name_prefix}-backend"],
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.cluster_name, "ServiceName", "${local.name_prefix}-celery-worker"],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.cluster_name, "ServiceName", "${local.name_prefix}-celery-worker"]
          ]
          view                = "timeSeries"
          stacked             = false
          region              = var.aws_region
          title               = "ECS Service Metrics"
          period              = 300
          stat                = "Average"
        }
      }
    ]
  })

  tags = local.common_tags
}

# =============================================================================
# CloudWatch Alarms
# =============================================================================

# High CPU Alarm for ECS Cluster
resource "aws_cloudwatch_metric_alarm" "ecs_high_cpu" {
  alarm_name          = "${local.name_prefix}-ecs-high-cpu"
  alarm_description   = "ECS cluster CPU utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = local.common_tags
}

# High Memory Alarm for ECS Cluster
resource "aws_cloudwatch_metric_alarm" "ecs_high_memory" {
  alarm_name          = "${local.name_prefix}-ecs-high-memory"
  alarm_description   = "ECS cluster memory utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = local.common_tags
}

# ALB High Latency Alarm
resource "aws_cloudwatch_metric_alarm" "alb_high_latency" {
  count               = var.alb_arn != "" ? 1 : 0
  alarm_name          = "${local.name_prefix}-alb-high-latency"
  alarm_description   = "ALB target response time is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Average"
  threshold           = 2
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    LoadBalancer = split("/", var.alb_arn)[1]
  }

  tags = local.common_tags
}

# ALB 5XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  count               = var.alb_arn != "" ? 1 : 0
  alarm_name          = "${local.name_prefix}-alb-5xx-errors"
  alarm_description   = "ALB 5XX error rate is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    LoadBalancer = split("/", var.alb_arn)[1]
  }

  tags = local.common_tags
}

# RDS High CPU Alarm
resource "aws_cloudwatch_metric_alarm" "rds_high_cpu" {
  count               = var.rds_instance_identifier != "" ? 1 : 0
  alarm_name          = "${local.name_prefix}-rds-high-cpu"
  alarm_description   = "RDS CPU utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  tags = local.common_tags
}

# RDS Low Free Storage Alarm
resource "aws_cloudwatch_metric_alarm" "rds_low_storage" {
  count               = var.rds_instance_identifier != "" ? 1 : 0
  alarm_name          = "${local.name_prefix}-rds-low-storage"
  alarm_description   = "RDS free storage space is low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 5368709120  # 5GB in bytes
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  tags = local.common_tags
}

# ElastiCache High CPU Alarm
resource "aws_cloudwatch_metric_alarm" "elasticache_high_cpu" {
  count               = var.elasticache_cluster_id != "" ? 1 : 0
  alarm_name          = "${local.name_prefix}-elasticache-high-cpu"
  alarm_description   = "ElastiCache CPU utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    CacheClusterId = var.elasticache_cluster_id
  }

  tags = local.common_tags
}

# ElastiCache High Memory Alarm
resource "aws_cloudwatch_metric_alarm" "elasticache_high_memory" {
  count               = var.elasticache_cluster_id != "" ? 1 : 0
  alarm_name          = "${local.name_prefix}-elasticache-high-memory"
  alarm_description   = "ElastiCache memory utilization is high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    CacheClusterId = var.elasticache_cluster_id
  }

  tags = local.common_tags
}

# ECS Service Running Task Count Alarm (Backend)
resource "aws_cloudwatch_metric_alarm" "backend_low_task_count" {
  alarm_name          = "${local.name_prefix}-backend-low-tasks"
  alarm_description   = "Backend service has too few running tasks"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "RunningTaskCount"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Minimum"
  threshold           = 1
  treat_missing_data  = "missing"
  alarm_actions       = local.alarm_topic_arn != null ? [local.alarm_topic_arn] : []

  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = "${local.name_prefix}-backend"
  }

  tags = local.common_tags
}

# =============================================================================
# X-Ray
# =============================================================================

resource "aws_xray_sampling_rule" "default" {
  count = var.enable_xray ? 1 : 0

  rule_name        = "${local.name_prefix}-default"
  priority         = 1000
  fixed_target     = 1
  rate             = 0.1
  service_name     = "*"
  service_type     = "*"
  host             = "*"
  http_method      = "*"
  url_path         = "*"
  resource_arn     = "*"
  attributes       = {}
}