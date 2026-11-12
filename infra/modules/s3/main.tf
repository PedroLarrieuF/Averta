# =============================================================================
# AvertaSaaS - S3 Module
# Creates S3 buckets for documents, assets, logs with CloudFront
# MinIO-compatible configuration
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "s3"
    },
    var.tags
  )

  # Generate bucket names if not provided
  documents_bucket = var.documents_bucket_name != "" ? var.documents_bucket_name : "${var.project_name.toLower()}-${var.environment}-documents"
  assets_bucket    = var.assets_bucket_name != "" ? var.assets_bucket_name : "${var.project_name.toLower()}-${var.environment}-assets"
  logs_bucket      = var.logs_bucket_name != "" ? var.logs_bucket_name : "${var.project_name.toLower()}-${var.environment}-logs"
}

# =============================================================================
# KMS Key for Encryption (optional)
# =============================================================================

resource "aws_kms_key" "s3" {
  count = var.kms_key_id == "" ? 1 : 0

  description             = "KMS key for ${var.project_name} ${var.environment} S3 buckets"
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
        Sid    = "Allow S3 to use the key"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

data "aws_caller_identity" "current" {}

locals {
  kms_key_id = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.s3[0].id
}

# =============================================================================
# Documents Bucket (Main - MinIO compatible)
# =============================================================================

resource "aws_s3_bucket" "documents" {
  bucket = local.documents_bucket

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = local.kms_key_id
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = var.documents_versioning
  }

  lifecycle_rule {
    id      = "transition-to-ia"
    enabled = true
    transition {
      days          = var.documents_lifecycle_days
      storage_class = "STANDARD_IA"
    }
  }

  lifecycle_rule {
    id      = "transition-to-glacier"
    enabled = true
    transition {
      days          = var.documents_lifecycle_days * 3
      storage_class = "GLACIER"
    }
  }

  lifecycle_rule {
    id      = "expire-old-versions"
    enabled = var.documents_expiration_days > 0
    noncurrent_version_expiration {
      noncurrent_days = var.documents_expiration_days
    }
  }

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age         = 3600
  }

  tags = merge(local.common_tags, { Purpose = "documents" })
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# =============================================================================
# Static Assets Bucket
# =============================================================================

resource "aws_s3_bucket" "assets" {
  bucket = local.assets_bucket

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = local.kms_key_id
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = true
  }

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age         = 3600
  }

  tags = merge(local.common_tags, { Purpose = "assets" })
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = !var.assets_public_read
  block_public_policy     = !var.assets_public_read
  ignore_public_acls      = !var.assets_public_read
  restrict_public_buckets = !var.assets_public_read
}

resource "aws_s3_bucket_policy" "assets" {
  count  = var.assets_public_read ? 1 : 0
  bucket = aws_s3_bucket.assets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "PublicReadGetObject"
      Effect = "Allow"
      Principal = "*"
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.assets.arn}/*"
    }]
  })
}

# =============================================================================
# Logs Bucket
# =============================================================================

resource "aws_s3_bucket" "logs" {
  bucket = local.logs_bucket

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "aws:kms"
        kms_master_key_id = local.kms_key_id
      }
      bucket_key_enabled = true
    }
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "expire-logs"
    enabled = true
    expiration {
      days = var.logs_retention_days
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  tags = merge(local.common_tags, { Purpose = "logs" })
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# =============================================================================
# CloudFront Distribution for Documents
# =============================================================================

resource "aws_cloudfront_distribution" "documents" {
  count = var.enable_cloudfront ? 1 : 0

  comment             = "CloudFront for ${var.project_name} ${var.environment} documents"
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = ""
  price_class         = "PriceClass_All"

  origin {
    domain_name = aws_s3_bucket.documents.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.documents.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.documents.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-${aws_s3_bucket.documents.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  # Signed URLs for private documents
  ordered_cache_behavior {
    path_pattern     = "/private/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-${aws_s3_bucket.documents.id}"

    forwarded_values {
      query_string = true
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "https-only"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    compress               = true

    trusted_signers = ["self"]
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.cloudfront_certificate_arn == "" && var.cloudfront_domain_name == ""
    acm_certificate_arn            = var.cloudfront_certificate_arn != "" ? var.cloudfront_certificate_arn : null
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  custom_error_response {
    error_code         = 403
    response_code      = 403
    response_page_path = "/403.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 404
    response_page_path = "/404.html"
  }

  tags = local.common_tags
}

resource "aws_cloudfront_origin_access_identity" "documents" {
  count = var.enable_cloudfront ? 1 : 0
  comment = "OAI for ${var.project_name} ${var.environment} documents bucket"
}

resource "aws_s3_bucket_policy" "documents_cloudfront" {
  count = var.enable_cloudfront ? 1 : 0
  bucket = aws_s3_bucket.documents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowCloudFrontOAI"
      Effect = "Allow"
      Principal = {
        CanonicalUser = aws_cloudfront_origin_access_identity.documents[0].s3_canonical_user_id
      }
      Action   = "s3:GetObject"
      Resource = "${aws_s3_bucket.documents.arn}/*"
    }]
  })
}

# =============================================================================
# Secrets Manager for MinIO-compatible credentials
# =============================================================================

resource "aws_secretsmanager_secret" "minio_credentials" {
  name        = "${var.project_name}/${var.environment}/minio"
  description = "MinIO/S3 credentials for ${var.project_name} ${var.environment}"
  tags        = local.common_tags
}

resource "aws_secretsmanager_secret_version" "minio_credentials" {
  secret_id = aws_secretsmanager_secret.minio_credentials.id
  secret_string = jsonencode({
    endpoint     = "https://s3.${var.aws_region}.amazonaws.com"
    access_key   = "${var.project_name}-${var.environment}-access"
    secret_key   = random_password.minio_secret.result
    bucket       = local.documents_bucket
    region       = var.aws_region
    cloudfront_domain = var.enable_cloudfront ? aws_cloudfront_distribution.documents[0].domain_name : null
  })
}

resource "random_password" "minio_secret" {
  length  = 40
  special = false
}