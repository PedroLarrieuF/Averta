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

variable "elasticache_subnet_group_name" {
  description = "ElastiCache Subnet Group name"
  type        = string
}

variable "elasticache_sg_id" {
  description = "ElastiCache Security Group ID"
  type        = string
}

# Cluster configuration
variable "engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.2"
}

variable "node_type" {
  description = "Cache node type"
  type        = string
  default     = "cache.r6g.xlarge"
}

variable "num_cache_nodes" {
  description = "Number of cache nodes (per shard)"
  type        = number
  default     = 1
}

variable "num_node_groups" {
  description = "Number of node groups (shards) for cluster mode"
  type        = number
  default     = 2
}

variable "replicas_per_node_group" {
  description = "Replicas per node group"
  type        = number
  default     = 1
}

variable "automatic_failover_enabled" {
  description = "Enable automatic failover"
  type        = bool
  default     = true
}

variable "multi_az_enabled" {
  description = "Enable Multi-AZ"
  type        = bool
  default     = true
}

# Security
variable "transit_encryption_enabled" {
  description = "Enable in-transit encryption"
  type        = bool
  default     = true
}

variable "at_rest_encryption_enabled" {
  description = "Enable at-rest encryption"
  type        = bool
  default     = true
}

variable "auth_token" {
  description = "Redis AUTH token (if empty, generates random)"
  type        = string
  sensitive   = true
  default     = ""
}

# Backup
variable "snapshot_retention_limit" {
  description = "Snapshot retention in days"
  type        = number
  default     = 7
}

variable "snapshot_window" {
  description = "Snapshot window (UTC)"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Maintenance window (UTC)"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# Parameter group
variable "parameter_group_name" {
  description = "Custom parameter group name (optional)"
  type        = string
  default     = ""
}

# Tags
variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}