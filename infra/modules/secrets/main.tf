# =============================================================================
# AWS Secrets Manager Module for AvertaSaaS
# Creates and manages all application secrets with proper rotation and access control
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )

  secret_name_prefix = "${var.secret_prefix}/${var.environment}"
}

# =============================================================================
# KMS Key for Secret Encryption (optional - uses AWS managed key if not provided)
# =============================================================================

resource "aws_kms_key" "secrets" {
  count = var.kms_key_id == "" ? 1 : 0

  description             = "KMS key for ${var.project_name} ${var.environment} secrets"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Allow root account full access"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager to use the key"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.${var.aws_region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:EncryptionContext:SecretARN" = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${local.secret_name_prefix}/*"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

data "aws_caller_identity" "current" {}

locals {
  kms_key_id = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.secrets[0].id
}

# =============================================================================
# Database Secret (with automatic rotation via RDS)
# =============================================================================

resource "aws_secretsmanager_secret" "database" {
  name        = "${local.secret_name_prefix}/database"
  description = "Database credentials for ${var.project_name} ${var.environment}"
  kms_key_id  = local.kms_key_id

  tags = merge(local.common_tags, {
    Rotation = var.enable_db_rotation ? "auto" : "manual"
    Type     = "database"
  })

  # Automatic rotation configuration (for RDS)
  rotation_rules {
    automatically_after_days = var.db_rotation_days
  }
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    host     = var.db_host
    port     = var.db_port
    dbname   = var.db_name
    engine   = "postgres"
  })
}

# Secret rotation for RDS (requires RDS instance to be linked separately)
# This is configured but the actual association is done via aws_secretsmanager_secret_rotation
# when the RDS instance is created in the RDS module

# =============================================================================
# Redis Secret
# =============================================================================

resource "aws_secretsmanager_secret" "redis" {
  name        = "${local.secret_name_prefix}/redis"
  description = "Redis credentials for ${var.project_name} ${var.environment}"
  kms_key_id  = local.kms_key_id

  tags = merge(local.common_tags, {
    Rotation = "manual"
    Type     = "redis"
  })
}

resource "aws_secretsmanager_secret_version" "redis" {
  secret_id = aws_secretsmanager_secret.redis.id
  secret_string = jsonencode({
    host     = var.redis_host
    port     = var.redis_port
    password = var.redis_password
  })
}

# =============================================================================
# MinIO/S3 Secret
# =============================================================================

resource "aws_secretsmanager_secret" "minio" {
  name        = "${local.secret_name_prefix}/minio"
  description = "MinIO/S3 credentials for ${var.project_name} ${var.environment}"
  kms_key_id  = local.kms_key_id

  tags = merge(local.common_tags, {
    Rotation = "manual"
    Type     = "object-storage"
  })
}

resource "aws_secretsmanager_secret_version" "minio" {
  secret_id = aws_secretsmanager_secret.minio.id
  secret_string = jsonencode({
    endpoint     = var.minio_endpoint
    access_key   = var.minio_access_key
    secret_key   = var.minio_secret_key
    bucket       = var.minio_bucket
    region       = var.minio_region
  })
}

# =============================================================================
# JWT Secret
# =============================================================================

resource "aws_secretsmanager_secret" "jwt" {
  name        = "${local.secret_name_prefix}/jwt"
  description = "JWT signing keys for ${var.project_name} ${var.environment}"
  kms_key_id  = local.kms_key_id

  tags = merge(local.common_tags, {
    Rotation = "manual"
    Type     = "auth"
  })
}

resource "aws_secretsmanager_secret_version" "jwt" {
  secret_id = aws_secretsmanager_secret.jwt.id
  secret_string = jsonencode({
    secret_key        = var.jwt_secret_key
    refresh_secret_key = var.jwt_refresh_secret_key
    algorithm         = var.jwt_algorithm
  })
}

# =============================================================================
# SendGrid Secret
# =============================================================================

resource "aws_secretsmanager_secret" "sendgrid" {
  name        = "${local.secret_name_prefix}/sendgrid"
  description = "SendGrid API credentials for ${var.project_name} ${var.environment}"
  kms_key_id  = local.kms_key_id

  tags = merge(local.common_tags, {
    Rotation = "manual"
    Type     = "email"
  })
}

resource "aws_secretsmanager_secret_version" "sendgrid" {
  secret_id = aws_secretsmanager_secret.sendgrid.id
  secret_string = jsonencode({
    api_key     = var.sendgrid_api_key
    from_email  = var.sendgrid_from_email
    from_name   = var.sendgrid_from_name
  })
}

# =============================================================================
# App Config Secret (non-sensitive configuration)
# =============================================================================

resource "aws_secretsmanager_secret" "app" {
  name        = "${local.secret_name_prefix}/app"
  description = "Application configuration for ${var.project_name} ${var.environment}"
  kms_key_id  = local.kms_key_id

  tags = merge(local.common_tags, {
    Rotation = "manual"
    Type     = "config"
  })
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    environment   = var.app_environment
    log_level     = var.app_log_level
    cors_origins  = var.cors_origins
  })
}

# =============================================================================
# IAM Policy for ECS Task Role (Least Privilege)
# =============================================================================

resource "aws_iam_policy" "ecs_task_secrets" {
  name        = "${var.project_name}-${var.environment}-ecs-task-secrets"
  description = "Allows ECS tasks to read secrets for ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${local.secret_name_prefix}/*"
        ]
        Condition = {
          StringEquals = {
            "secretsmanager:ResourceTag/Project" = var.project_name
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = local.kms_key_id
        Condition = {
          StringEquals = {
            "kms:EncryptionContext:SecretARN" = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${local.secret_name_prefix}/*"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

# =============================================================================
# IAM Policy for GitHub Actions Deploy Role
# =============================================================================

resource "aws_iam_policy" "github_actions_deploy" {
  name        = "${var.project_name}-${var.environment}-github-actions-deploy"
  description = "Allows GitHub Actions to read secrets for deployment"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecrets"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${local.secret_name_prefix}/*"
        ]
        Condition = {
          StringEquals = {
            "secretsmanager:ResourceTag/Project" = var.project_name
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

# =============================================================================
# IAM Policy for Developer Access (Staging Only)
# =============================================================================

resource "aws_iam_policy" "developer_staging" {
  count = var.environment == "staging" ? 1 : 0

  name        = "${var.project_name}-staging-developer-secrets"
  description = "Allows developers to read staging secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${local.secret_name_prefix}/*"
        ]
        Condition = {
          StringEquals = {
            "secretsmanager:ResourceTag/Project"  = var.project_name
            "secretsmanager:ResourceTag/Environment" = "staging"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

# =============================================================================
# CloudTrail Data Event for Secret Access Auditing
# =============================================================================

resource "aws_cloudtrail" "secrets_audit" {
  name                          = "${var.project_name}-${var.environment}-secrets-audit"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.bucket
  enable_logging                = true
  include_global_service_events = false
  is_multi_region_trail         = false
  event_selector {
    read_write_type           = "All"
    include_management_events = true
    data_resource {
      type   = "AWS::SecretsManager::Secret"
      values = ["arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${local.secret_name_prefix}/*"]
    }
  }

  tags = local.common_tags
}

resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "${var.project_name.toLower()}-${var.environment}-cloudtrail-logs-${data.aws_caller_identity.current.account_id}"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true
    expiration {
      days = 365
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  tags = local.common_tags
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}