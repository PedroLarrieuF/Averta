# =============================================================================
# AvertaSaaS - IAM Module Variables
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

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# ECS Task Execution Role
variable "create_task_execution_role" {
  description = "Create ECS task execution role"
  type        = bool
  default     = true
}

# ECS Task Role
variable "create_task_role" {
  description = "Create ECS task role"
  type        = bool
  default     = true
}

# GitHub Actions OIDC
variable "create_github_oidc" {
  description = "Create GitHub Actions OIDC provider and role"
  type        = bool
  default     = true
}

# Developer roles
variable "create_developer_roles" {
  description = "Create developer IAM roles"
  type        = bool
  default     = false
}

variable "developer_users" {
  description = "Map of developer usernames to their IAM policies"
  type        = map(list(string))
  default     = {}
}

# Custom policies
variable "additional_task_policies" {
  description = "Additional IAM policy ARNs to attach to task role"
  type        = list(string)
  default     = []
}

variable "additional_execution_policies" {
  description = "Additional IAM policy ARNs to attach to execution role"
  type        = list(string)
  default     = []
}