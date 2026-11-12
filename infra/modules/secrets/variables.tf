variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be staging or production."
  }
}

variable "project_name" {
  description = "Project name for resource naming and tagging"
  type        = string
  default     = "AvertaSaaS"
}

variable "secret_prefix" {
  description = "Prefix for secret names"
  type        = string
  default     = "averta"
}

variable "kms_key_id" {
  description = "KMS key ID for encrypting secrets (optional, uses AWS managed key if not provided)"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

# Database secret values (for initial creation - rotation handled by RDS)
variable "db_username" {
  description     = "Database username"
  type            = string
  sensitive       = true
  default         = ""
}

variable "db_password" {
  description     = "Database password"
  type            = string
  sensitive       = true
  default         = ""
}

variable "db_host" {
  description     = "Database host"
  type            = string
  default         = ""
}

variable "db_port" {
  description     = "Database port"
  type            = number
  default         = 5432
}

variable "db_name" {
  description     = "Database name"
  type            = string
  default         = "averta"
}

# Redis secret values
variable "redis_host" {
  description     = "Redis host"
  type            = string
  default         = ""
}

variable "redis_port" {
  description     = "Redis port"
  type            = number
  default         = 6379
}

variable "redis_password" {
  description     = "Redis password (optional)"
  type            = string
  sensitive       = true
  default         = ""
}

# MinIO/S3 secret values
variable "minio_endpoint" {
  description     = "MinIO/S3 endpoint"
  type            = string
  default         = ""
}

variable "minio_access_key" {
  description     = "MinIO access key"
  type            = string
  sensitive       = true
  default         = ""
}

variable "minio_secret_key" {
  description     = "MinIO secret key"
  type            = string
  sensitive       = true
  default         = ""
}

variable "minio_bucket" {
  description     = "MinIO bucket name"
  type            = string
  default         = "averta-documents"
}

variable "minio_region" {
  description     = "MinIO region"
  type            = string
  default         = "us-east-1"
}

# JWT secret values
variable "jwt_secret_key" {
  description     = "JWT secret key (min 32 chars)"
  type            = string
  sensitive       = true
  default         = ""
}

variable "jwt_refresh_secret_key" {
  description     = "JWT refresh secret key (min 32 chars)"
  type            = string
  sensitive       = true
  default         = ""
}

variable "jwt_algorithm" {
  description     = "JWT algorithm"
  type            = string
  default         = "HS256"
}

# SendGrid secret values
variable "sendgrid_api_key" {
  description     = "SendGrid API key"
  type            = string
  sensitive       = true
  default         = ""
}

variable "sendgrid_from_email" {
  description     = "SendGrid from email"
  type            = string
  default         = "noreply@averta.com.br"
}

variable "sendgrid_from_name" {
  description     = "SendGrid from name"
  type            = string
  default         = "Averta Auditoria"
}

# App config values (non-sensitive)
variable "app_environment" {
  description     = "Application environment"
  type            = string
  default         = "production"
}

variable "app_log_level" {
  description     = "Application log level"
  type            = string
  default         = "info"
}

variable "cors_origins" {
  description     = "CORS allowed origins"
  type            = list(string)
  default         = ["https://app.averta.com.br"]
}

# Rotation configuration
variable "enable_db_rotation" {
  description = "Enable automatic rotation for database secret (requires RDS)"
  type        = bool
  default     = true
}

variable "db_rotation_days" {
  description = "Database secret rotation interval in days"
  type        = number
  default     = 30
}

variable "rotation_lambda_arn" {
  description = "ARN of custom rotation Lambda (for non-RDS secrets)"
  type        = string
  default     = ""
}