# =============================================================================
# AvertaSaaS - RDS Module
# Creates PostgreSQL RDS instance with Multi-AZ, encryption, monitoring
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "rds"
    },
    var.tags
  )

  db_identifier = "${var.project_name}-${var.environment}-db"
}

# =============================================================================
# Random Password Generation (if not provided)
# =============================================================================

resource "random_password" "db_password" {
  length  = 32
  special = false
  override_special = "_"
}

locals {
  db_password = var.password != "" ? var.password : random_password.db_password.result
}

# =============================================================================
# DB Parameter Group
# =============================================================================

resource "aws_db_parameter_group" "main" {
  count = var.parameter_group_name == "" ? 1 : 0

  name        = "${local.db_identifier}-params"
  family      = "postgres16"
  description = "Parameter group for ${local.db_identifier}"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,auto_explain"
  }

  parameter {
    name  = "pg_stat_statements.track"
    value = "all"
  }

  parameter {
    name  = "auto_explain.log_min_duration"
    value = "1000"
  }

  parameter {
    name  = "auto_explain.log_analyze"
    value = "true"
  }

  parameter {
    name  = "auto_explain.log_buffers"
    value = "true"
  }

  parameter {
    name  = "log_statement"
    value = "ddl"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "idle_in_transaction_session_timeout"
    value = "300000"
  }

  parameter {
    name  = "max_connections"
    value = "200"
  }

  tags = local.common_tags
}

locals {
  parameter_group_name = var.parameter_group_name != "" ? var.parameter_group_name : aws_db_parameter_group.main[0].name
}

# =============================================================================
# DB Subnet Group (referenced from VPC)
# =============================================================================

# Using the subnet group name passed from VPC module
# data "aws_db_subnet_group" "main" {
#   name = var.db_subnet_group_name
# }

# =============================================================================
# RDS Instance (Primary)
# =============================================================================

resource "aws_db_instance" "main" {
  identifier             = local.db_identifier
  engine                 = "postgres"
  engine_version         = var.engine_version
  instance_class         = var.instance_class
  allocated_storage      = var.allocated_storage
  max_allocated_storage  = var.max_allocated_storage
  storage_type           = var.storage_type
  storage_encrypted      = var.storage_encrypted
  kms_key_id             = var.kms_key_id != "" ? var.kms_key_id : null

  db_name  = var.db_name
  username = var.username
  password = local.db_password
  port     = var.port

  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = [var.rds_sg_id]
  parameter_group_name   = local.parameter_group_name

  multi_az               = var.multi_az
  publicly_accessible    = false

  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window
  maintenance_window      = var.maintenance_window
  copy_tags_to_snapshot   = var.copy_tags_to_snapshot

  deletion_protection    = var.deletion_protection
  skip_final_snapshot    = false
  final_snapshot_identifier = "${local.db_identifier}-final-\${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_retention_period

  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn != "" ? var.monitoring_role_arn : null

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = local.common_tags
}

# =============================================================================
# Read Replica (for reporting queries)
# =============================================================================

resource "aws_db_instance" "read_replica" {
  count = var.environment == "production" ? 1 : 0

  identifier              = "${local.db_identifier}-replica"
  replicate_source_db     = aws_db_instance.main.identifier
  instance_class          = var.instance_class
  db_subnet_group_name    = var.db_subnet_group_name
  vpc_security_group_ids  = [var.rds_sg_id]
  parameter_group_name    = local.parameter_group_name
  publicly_accessible     = false

  performance_insights_enabled = var.performance_insights_enabled
  monitoring_interval         = var.monitoring_interval
  monitoring_role_arn         = var.monitoring_role_arn != "" ? var.monitoring_role_arn : null

  tags = merge(local.common_tags, { Role = "read-replica" })
}

# =============================================================================
# PgBouncer (Connection Pooler) - Deployed on ECS (defined in ECS module)
# This module just creates the security group reference
# =============================================================================

# =============================================================================
# IAM Role for Enhanced Monitoring
# =============================================================================

resource "aws_iam_role" "rds_monitoring" {
  count = var.monitoring_interval > 0 && var.monitoring_role_arn == "" ? 1 : 0

  name = "${local.db_identifier}-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.monitoring_interval > 0 && var.monitoring_role_arn == "" ? 1 : 0

  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

locals {
  monitoring_role_arn = var.monitoring_role_arn != "" ? var.monitoring_role_arn : aws_iam_role.rds_monitoring[0].arn
}

# =============================================================================
# Secrets Manager Integration (for rotation)
# =============================================================================

resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.project_name}/${var.environment}/database"
  description = "Database credentials for ${var.project_name} ${var.environment}"
  tags        = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.username
    password = local.db_password
    host     = aws_db_instance.main.endpoint
    port     = var.port
    dbname   = var.db_name
    engine   = "postgres"
  })
}

# =============================================================================
# Secret Rotation (requires Lambda - simplified here)
# =============================================================================

# Note: Full rotation requires a Lambda function.
# This is configured but the Lambda association is done separately.
# See: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html