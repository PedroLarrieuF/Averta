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

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "ecs_tasks_sg_id" {
  description = "ECS tasks Security Group ID"
  type        = string
}

variable "alb_target_group_arn" {
  description = "ALB target group ARN for backend service"
  type        = string
}

variable "rds_cluster_endpoint" {
  description = "RDS cluster endpoint (writer endpoint)"
  type        = string
}

# ECS Cluster
variable "cluster_name" {
  description = "ECS cluster name"
  type        = string
  default     = ""
}

# Task execution role
variable "task_execution_role_arn" {
  description = "Task execution role ARN (optional, will create if not provided)"
  type        = string
  default     = ""
}

# Task role
variable "task_role_arn" {
  description = "Task role ARN (optional, will create if not provided)"
  type        = string
  default     = ""
}

# Backend service
variable "backend_image" {
  description = "Backend Docker image URI"
  type        = string
  default     = ""
}

variable "backend_cpu" {
  description = "Backend task CPU units"
  type        = number
  default     = 1024
}

variable "backend_memory" {
  description = "Backend task memory in MB"
  type        = number
  default     = 2048
}

variable "backend_desired_count" {
  description = "Backend desired task count"
  type        = number
  default     = 2
}

variable "backend_min_count" {
  description = "Backend min task count (autoscaling)"
  type        = number
  default     = 2
}

variable "backend_max_count" {
  description = "Backend max task count (autoscaling)"
  type        = number
  default     = 10
}

# Celery worker service
variable "celery_worker_image" {
  description = "Celery worker Docker image URI"
  type        = string
  default     = ""
}

variable "celery_worker_cpu" {
  description = "Celery worker task CPU units"
  type        = number
  default     = 1024
}

variable "celery_worker_memory" {
  description = "Celery worker task memory in MB"
  type        = number
  default     = 2048
}

variable "celery_worker_desired_count" {
  description = "Celery worker desired task count"
  type        = number
  default     = 2
}

variable "celery_worker_min_count" {
  description = "Celery worker min task count"
  type        = number
  default     = 1
}

variable "celery_worker_max_count" {
  description = "Celery worker max task count"
  type        = number
  default     = 5
}

# Celery beat service
variable "celery_beat_image" {
  description = "Celery beat Docker image URI"
  type        = string
  default     = ""
}

variable "celery_beat_cpu" {
  description = "Celery beat task CPU units"
  type        = number
  default     = 256
}

variable "celery_beat_memory" {
  description = "Celery beat task memory in MB"
  type        = number
  default     = 512
}

variable "celery_beat_desired_count" {
  description = "Celery beat desired task count (always 1)"
  type        = number
  default     = 1
}

# PgBouncer service
variable "pgbouncer_image" {
  description = "PgBouncer Docker image URI"
  type        = string
  default     = "edoburu/pgbouncer:latest"
}

variable "pgbouncer_cpu" {
  description = "PgBouncer task CPU units"
  type        = number
  default     = 256
}

variable "pgbouncer_memory" {
  description = "PgBouncer task memory in MB"
  type        = number
  default     = 512
}

variable "pgbouncer_desired_count" {
  description = "PgBouncer desired task count"
  type        = number
  default     = 2
}

# Container insights
variable "enable_container_insights" {
  description = "Enable Container Insights"
  type        = bool
  default     = true
}

# Logs
variable "log_group_retention_days" {
  description = "CloudWatch log group retention in days"
  type        = number
  default     = 30
}

# Tags
variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}