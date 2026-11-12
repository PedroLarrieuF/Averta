# =============================================================================
# AvertaSaaS - Monitoring Module Variables
# =============================================================================

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

variable "cluster_name" {
  description = "ECS cluster name"
  type        = string
}

variable "alb_arn" {
  description = "ALB ARN for monitoring"
  type        = string
  default     = ""
}

variable "alb_target_group_arn" {
  description = "ALB target group ARN for monitoring"
  type        = string
  default     = ""
}

variable "rds_instance_identifier" {
  description = "RDS instance identifier for monitoring"
  type        = string
  default     = ""
}

variable "elasticache_cluster_id" {
  description = "ElastiCache cluster ID for monitoring"
  type        = string
  default     = ""
}

variable "s3_bucket_names" {
  description = "S3 bucket names for monitoring"
  type        = list(string)
  default     = []
}

variable "notification_email" {
  description = "Email for alarm notifications"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# Log groups to create
variable "log_group_names" {
  description = "CloudWatch log group names to create"
  type        = list(string)
  default     = []
}

variable "log_group_retention_days" {
  description = "CloudWatch log group retention in days"
  type        = number
  default     = 30
}

# X-Ray
variable "enable_xray" {
  description = "Enable X-Ray tracing"
  type        = bool
  default     = true
}