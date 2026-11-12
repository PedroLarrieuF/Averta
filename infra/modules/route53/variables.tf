# =============================================================================
# AvertaSaaS - Route53 Module Variables
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

variable "domain_name" {
  description = "Root domain name (e.g., averta.com)"
  type        = string
}

variable "hosted_zone_id" {
  description = "Existing hosted zone ID (optional, will create if not provided)"
  type        = string
  default     = ""
}

variable "alb_dns_name" {
  description = "ALB DNS name for alias record"
  type        = string
  default     = ""
}

variable "alb_zone_id" {
  description = "ALB zone ID for alias record"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

variable "create_certificate" {
  description = "Create ACM certificate if not provided"
  type        = bool
  default     = true
}

variable "subdomain" {
  description = "Subdomain prefix (e.g., api, app)"
  type        = string
  default     = "api"
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}