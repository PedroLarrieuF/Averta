# =============================================================================
# AvertaSaaS - Root Variables
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
  default     = ""
}

variable "github_org" {
  description = "GitHub organization for OIDC"
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "GitHub repository for OIDC"
  type        = string
  default     = ""
}

variable "notification_email" {
  description = "Email for alarm notifications"
  type        = string
  default     = ""
}

variable "create_all" {
  description = "Create all resources (set to false for module-by-module deployment)"
  type        = bool
  default     = true
}