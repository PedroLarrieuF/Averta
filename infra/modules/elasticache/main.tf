# =============================================================================
# AvertaSaaS - ElastiCache Module
# Creates Redis cluster with cluster mode, encryption, Multi-AZ
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "elasticache"
    },
    var.tags
  )

  cluster_id = "${var.project_name}-${var.environment}-redis"
}

# =============================================================================
# Random Auth Token Generation (if not provided)
# =============================================================================

resource "random_password" "auth_token" {
  length  = 32
  special = false
}

locals {
  auth_token = var.auth_token != "" ? var.auth_token : random_password.auth_token.result
}

# =============================================================================
# Parameter Group
# =============================================================================

resource "aws_elasticache_parameter_group" "main" {
  count = var.parameter_group_name == "" ? 1 : 0

  name        = "${local.cluster_id}-params"
  family      = "redis7"
  description = "Parameter group for ${local.cluster_id}"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "60"
  }

  tags = local.common_tags
}

locals {
  parameter_group_name = var.parameter_group_name != "" ? var.parameter_group_name : aws_elasticache_parameter_group.main[0].name
}

# =============================================================================
# Subnet Group (referenced from VPC)
# =============================================================================

# Using subnet group name from VPC module
# data "aws_elasticache_subnet_group" "main" {
#   name = var.elasticache_subnet_group_name
# }

# =============================================================================
# Redis Replication Group (Cluster Mode Enabled)
# =============================================================================

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = local.cluster_id
  replication_group_description = "Redis cluster for ${var.project_name} ${var.environment}"

  engine               = "redis"
  engine_version       = var.engine_version
  node_type            = var.node_type
  port                 = 6379
  parameter_group_name = local.parameter_group_name

  # Cluster mode configuration
  number_node_groups           = var.num_node_groups
  replicas_per_node_group      = var.replicas_per_node_group
  automatic_failover_enabled   = var.automatic_failover_enabled
  multi_az_enabled             = var.multi_az_enabled

  # Encryption
  transit_encryption_enabled  = var.transit_encryption_enabled
  at_rest_encryption_enabled  = var.at_rest_encryption_enabled
  auth_token                  = local.auth_token

  # Network
  subnet_group_name = var.elasticache_subnet_group_name
  security_group_ids = [var.elasticache_sg_id]

  # Backup
  snapshot_retention_limit = var.snapshot_retention_limit
  snapshot_window          = var.snapshot_window
  maintenance_window       = var.maintenance_window

  # Logging
  log_delivery_configuration {
    destination_type = "cloudwatch-logs"
    destination_details {
      cloudwatch_logs {
        log_group = "/aws/elasticache/${local.cluster_id}"
      }
    }
    log_format = "json"
    log_type   = "slow-log"
  }

  log_delivery_configuration {
    destination_type = "cloudwatch-logs"
    destination_details {
      cloudwatch_logs {
        log_group = "/aws/elasticache/${local.cluster_id}"
      }
    }
    log_format = "json"
    log_type   = "engine-log"
  }

  tags = local.common_tags
}

# =============================================================================
# CloudWatch Log Group for Redis logs
# =============================================================================

resource "aws_cloudwatch_log_group" "redis" {
  name              = "/aws/elasticache/${local.cluster_id}"
  retention_in_days = 30
  tags              = local.common_tags
}

# =============================================================================
# Secrets Manager Integration
# =============================================================================

resource "aws_secretsmanager_secret" "redis_credentials" {
  name        = "${var.project_name}/${var.environment}/redis"
  description = "Redis credentials for ${var.project_name} ${var.environment}"
  tags        = local.common_tags
}

resource "aws_secretsmanager_secret_version" "redis_credentials" {
  secret_id = aws_secretsmanager_secret.redis_credentials.id
  secret_string = jsonencode({
    host     = aws_elasticache_replication_group.main.primary_endpoint_address
    port     = 6379
    password = local.auth_token
  })
}