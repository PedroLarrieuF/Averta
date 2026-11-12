# Staging Environment Configuration
# This file defines the staging-specific values for the secrets module

module "secrets" {
  source = "../../modules/secrets"

  aws_region   = "us-east-1"
  environment  = "staging"
  project_name = "AvertaSaaS"
  secret_prefix = "averta"

  # Database (these will be populated by RDS module outputs)
  db_username = "averta_staging"
  db_password = ""  # Will be set via RDS rotation
  db_host     = ""  # Will be set from RDS output
  db_port     = 5432
  db_name     = "averta_staging"

  # Redis (will be set from ElastiCache output)
  redis_host     = ""
  redis_port     = 6379
  redis_password = ""

  # MinIO/S3 (will be set from S3 module output)
  minio_endpoint   = ""
  minio_access_key = ""
  minio_secret_key = ""
  minio_bucket     = "averta-staging-documents"
  minio_region     = "us-east-1"

  # JWT (generate with: openssl rand -base64 32)
  jwt_secret_key        = ""  # Set manually or via rotation
  jwt_refresh_secret_key = ""  # Set manually or via rotation
  jwt_algorithm         = "HS256"

  # SendGrid
  sendgrid_api_key     = ""  # Set manually
  sendgrid_from_email  = "noreply@staging.averta.com.br"
  sendgrid_from_name   = "Averta Auditoria (Staging)"

  # App Config
  app_environment = "staging"
  app_log_level   = "debug"
  cors_origins    = ["https://staging.averta.com.br", "http://localhost:3000"]

  # Rotation
  enable_db_rotation  = true
  db_rotation_days    = 30

  tags = {
    Owner       = "Platform Team"
    CostCenter  = "engineering"
    Environment = "staging"
  }
}

# Provider configuration
terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "avertasaas-terraform-state"
    key            = "staging/secrets/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "avertasaas-terraform-locks"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "AvertaSaaS"
      Environment = "staging"
      ManagedBy   = "Terraform"
    }
  }
}