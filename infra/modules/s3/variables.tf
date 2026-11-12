variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "AvertaSaaS"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be staging or production."
  }
}

# Main bucket (documents)
variable "documents_bucket_name" {
  description = "Documents bucket name (must be globally unique)"
  type        = string
  default     = ""
}

variable "documents_versioning" {
  description = "Enable versioning on documents bucket"
  type        = bool
  default     = true
}

variable "documents_lifecycle_days" {
  description = "Lifecycle transition days for documents"
  type        = number
  default     = 30
}

variable "documents_expiration_days" {
  description = "Expiration days for documents (0 to disable)"
  type        = number
  default     = 2555  # 7 years
}

# Static assets bucket
variable "assets_bucket_name" {
  description = "Static assets bucket name"
  type        = string
  default     = ""
}

variable "assets_public_read" {
  description = "Enable public read for assets bucket"
  type        = bool
  default     = false
}

# Logs bucket
variable "logs_bucket_name" {
  description = "Logs bucket name"
  type        = string
  default     = ""
}

variable "logs_retention_days" {
  description = "Logs retention in days"
  type        = number
  default     = 365
}

# CloudFront
variable "enable_cloudfront" {
  description = "Create CloudFront distribution for documents bucket"
  type        = bool
  default     = true
}

variable "cloudfront_certificate_arn" {
  description = "ACM certificate ARN for CloudFront (optional)"
  type        = string
  default     = ""
}

variable "cloudfront_domain_name" {
  description = "Custom domain name for CloudFront (optional)"
  type        = string
  default     = ""
}

# Encryption
variable "kms_key_id" {
  description = "KMS key ID for bucket encryption (optional)"
  type        = string
  default     = ""
}

# Tags
variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}