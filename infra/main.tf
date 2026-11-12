# =============================================================================
# AvertaSaaS - Root Infrastructure Configuration
# Wires all modules together for complete AWS infrastructure deployment
# =============================================================================

# =============================================================================
# Provider & Backend
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket         = "avertasaas-terraform-state"
    key            = "${var.environment}/infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "avertasaas-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Platform Team"
      CostCenter  = "engineering"
    }
  }
}

# =============================================================================
# Variables
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

# =============================================================================
# Data Sources
# =============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# =============================================================================
# Module: VPC
# =============================================================================

module "vpc" {
  source = "./modules/vpc"

  aws_region   = var.aws_region
  project_name = var.project_name
  environment  = var.environment

  vpc_cidr            = var.environment == "production" ? "10.0.0.0/16" : "10.1.0.0/16"
  availability_zones  = slice(data.aws_availability_zones.available.names, 0, 3)

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment == "staging"
  enable_dns_hostnames   = true
  enable_dns_support     = true
  enable_vpc_endpoints   = true

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: Secrets Manager (runs first, creates secrets for other modules)
# =============================================================================

module "secrets" {
  source = "./modules/secrets"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment
  secret_prefix = lower(var.project_name)

  # Database (will be updated by RDS module)
  db_username = "averta_${var.environment}"
  db_password = ""
  db_host     = ""
  db_port     = 5432
  db_name     = "averta_${var.environment}"

  # Redis (will be updated by ElastiCache module)
  redis_host     = ""
  redis_port     = 6379
  redis_password = ""

  # MinIO/S3 (will be updated by S3 module)
  minio_endpoint   = ""
  minio_access_key = ""
  minio_secret_key = ""
  minio_bucket     = "averta-${var.environment}-documents"
  minio_region     = var.aws_region

  # JWT (set manually or via rotation)
  jwt_secret_key        = ""
  jwt_refresh_secret_key = ""
  jwt_algorithm         = "HS256"

  # SendGrid
  sendgrid_api_key     = ""
  sendgrid_from_email  = var.environment == "production" ? "noreply@averta.com.br" : "noreply@staging.averta.com.br"
  sendgrid_from_name   = var.environment == "production" ? "Averta Auditoria" : "Averta Auditoria (Staging)"

  # App Config
  app_environment = var.environment
  app_log_level   = var.environment == "production" ? "info" : "debug"
  cors_origins    = var.environment == "production" ? ["https://app.averta.com.br"] : ["https://staging.averta.com.br", "http://localhost:3000"]

  # Rotation
  enable_db_rotation  = true
  db_rotation_days    = 30

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: RDS
# =============================================================================

module "rds" {
  source = "./modules/rds"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  db_sg_id           = module.vpc.db_sg_id

  # Secrets Manager integration
  secrets_manager_secret_arn = module.secrets.database_secret_arn
  secrets_manager_kms_key_id = module.secrets.kms_key_id

  # Instance configuration
  instance_class           = var.environment == "production" ? "db.r6g.xlarge" : "db.t3.medium"
  allocated_storage        = var.environment == "production" ? 200 : 50
  max_allocated_storage    = var.environment == "production" ? 500 : 100
  multi_az                 = var.environment == "production"
  enable_read_replica      = var.environment == "production"
  read_replica_instance_class = var.environment == "production" ? "db.r6g.large" : "db.t3.medium"

  # Database configuration
  engine_version       = "16.3"
  db_name              = "averta_${var.environment}"
  username             = "averta_${var.environment}"
  port                 = 5432
  parameter_group_name = ""
  enable_performance_insights = var.environment == "production"
  performance_insights_retention_days = 7

  # Backup
  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  # Deletion protection
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment == "staging"

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: ElastiCache
# =============================================================================

module "elasticache" {
  source = "./modules/elasticache"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  redis_sg_id        = module.vpc.redis_sg_id

  # Secrets Manager integration
  secrets_manager_secret_arn = module.secrets.redis_secret_arn
  secrets_manager_kms_key_id = module.secrets.kms_key_id

  # Cluster configuration
  cluster_mode_enabled = var.environment == "production"
  num_node_groups      = var.environment == "production" ? 2 : 1
  replicas_per_node_group = var.environment == "production" ? 2 : 1
  node_type            = var.environment == "production" ? "cache.r6g.xlarge" : "cache.t3.medium"
  engine_version       = "7.1"
  port                 = 6379
  parameter_group_name = ""

  # Multi-AZ
  multi_az_enabled = var.environment == "production"
  automatic_failover_enabled = var.environment == "production"

  # Backup
  snapshot_retention_limit = var.environment == "production" ? 30 : 7
  snapshot_window         = "05:00-06:00"
  maintenance_window      = "sun:06:00-sun:07:00"

  # Deletion protection
  deletion_protection = var.environment == "production"

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: S3
# =============================================================================

module "s3" {
  source = "./modules/s3"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment

  # Secrets Manager integration
  secrets_manager_secret_arn = module.secrets.minio_secret_arn
  secrets_manager_kms_key_id = module.secrets.kms_key_id

  # Bucket configuration
  documents_bucket_name = "averta-${var.environment}-documents"
  backups_bucket_name   = "averta-${var.environment}-backups"
  logs_bucket_name      = "averta-${var.environment}-logs"

  # Versioning
  enable_versioning = true

  # Lifecycle
  documents_transition_days = 30
  documents_expiration_days = var.environment == "production" ? 2555 : 365  # 7 years prod, 1 year staging
  backups_transition_days   = 7
  backups_expiration_days   = var.environment == "production" ? 365 : 30
  logs_transition_days      = 30
  logs_expiration_days      = 365

  # Encryption
  encryption_type = "aws:kms"

  # CloudFront
  enable_cloudfront = var.environment == "production"
  cloudfront_price_class = "PriceClass_All"

  # Public access block
  block_public_access = true

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: ALB
# =============================================================================

module "alb" {
  source = "./modules/alb"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment

  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  alb_sg_id         = module.vpc.alb_sg_id
  target_sg_id      = module.vpc.ecs_tasks_sg_id

  # ALB configuration
  internal                    = false
  alb_type                    = "application"
  idle_timeout                = 60
  enable_deletion_protection  = var.environment == "production"

  # Target group
  target_group_port        = 8000
  target_group_protocol    = "HTTP"
  health_check_path        = "/health"
  health_check_interval    = 30
  health_check_timeout     = 10
  healthy_threshold        = 2
  unhealthy_threshold      = 3
  deregistration_delay     = 30
  stickiness_enabled       = false

  # SSL
  certificate_arn = var.domain_name != "" ? module.route53.certificate_arn : ""
  ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  # Access logs
  access_logs_bucket = module.s3.logs_bucket_name
  access_logs_prefix = "alb"

  # WAF
  enable_waf = var.environment == "production"

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: Route53 (optional - only if domain provided)
# =============================================================================

module "route53" {
  source = "./modules/route53"

  count = var.domain_name != "" ? 1 : 0

  aws_region      = var.aws_region
  project_name    = var.project_name
  environment     = var.environment
  domain_name     = var.domain_name
  alb_dns_name    = module.alb.alb_dns_name
  alb_zone_id     = module.alb.alb_zone_id
  subdomain       = "api"
  create_certificate = true

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: IAM
# =============================================================================

module "iam" {
  source = "./modules/iam"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment
  github_org    = var.github_org
  github_repo   = var.github_repo

  create_task_execution_role = true
  create_task_role           = true
  create_github_oidc         = var.github_org != "" && var.github_repo != ""
  create_developer_roles     = false

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: ECS
# =============================================================================

module "ecs" {
  source = "./modules/ecs"

  aws_region    = var.aws_region
  project_name  = var.project_name
  environment   = var.environment

  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  ecs_tasks_sg_id        = module.vpc.ecs_tasks_sg_id
  alb_target_group_arn   = module.alb.backend_target_group_arn
  rds_cluster_endpoint   = module.rds.cluster_endpoint

  # IAM roles
  task_execution_role_arn = module.iam.task_execution_role_arn
  task_role_arn           = module.iam.task_role_arn

  # Images (to be filled in CI/CD)
  backend_image          = ""
  celery_worker_image    = ""
  celery_beat_image      = ""
  pgbouncer_image        = "edoburu/pgbouncer:latest"

  # Backend service
  backend_cpu                 = var.environment == "production" ? 1024 : 512
  backend_memory              = var.environment == "production" ? 2048 : 1024
  backend_desired_count       = var.environment == "production" ? 3 : 2
  backend_min_count           = var.environment == "production" ? 3 : 1
  backend_max_count           = var.environment == "production" ? 20 : 5

  # Celery worker
  celery_worker_cpu           = var.environment == "production" ? 1024 : 512
  celery_worker_memory        = var.environment == "production" ? 2048 : 1024
  celery_worker_desired_count = var.environment == "production" ? 3 : 2
  celery_worker_min_count     = var.environment == "production" ? 2 : 1
  celery_worker_max_count     = var.environment == "production" ? 10 : 3

  # Celery beat
  celery_beat_cpu             = 256
  celery_beat_memory          = 512
  celery_beat_desired_count   = 1

  # PgBouncer
  pgbouncer_cpu               = 256
  pgbouncer_memory            = 512
  pgbouncer_desired_count     = var.environment == "production" ? 2 : 1

  # Observability
  enable_container_insights   = true
  log_group_retention_days    = var.environment == "production" ? 90 : 30

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Module: Monitoring
# =============================================================================

module "monitoring" {
  source = "./modules/monitoring"

  aws_region              = var.aws_region
  project_name            = var.project_name
  environment             = var.environment
  cluster_name            = module.ecs.cluster_name
  alb_arn                 = module.alb.alb_arn
  alb_target_group_arn    = module.alb.backend_target_group_arn
  rds_instance_identifier = module.rds.db_instance_identifier
  elasticache_cluster_id  = module.elasticache.cluster_id
  s3_bucket_names         = [module.s3.documents_bucket_name, module.s3.backups_bucket_name, module.s3.logs_bucket_name]
  notification_email      = var.notification_email
  log_group_names         = [
    module.ecs.backend_log_group_name,
    module.ecs.celery_worker_log_group_name,
    module.ecs.celery_beat_log_group_name,
    module.ecs.pgbouncer_log_group_name,
    module.ecs.ecs_exec_log_group_name
  ]
  log_group_retention_days = var.environment == "production" ? 90 : 30
  enable_xray             = true

  tags = {
    Environment = var.environment
  }
}

# =============================================================================
# Outputs
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "database_endpoint" {
  description = "RDS cluster endpoint"
  value       = module.rds.cluster_endpoint
}

output "database_reader_endpoint" {
  description = "RDS reader endpoint"
  value       = module.rds.reader_endpoint
}

output "redis_endpoint" {
  description = "ElastiCache primary endpoint"
  value       = module.elasticache.primary_endpoint
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "alb_arn" {
  description = "ALB ARN"
  value       = module.alb.alb_arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = module.ecs.cluster_arn
}

output "backend_service_name" {
  description = "Backend service name"
  value       = module.ecs.backend_service_name
}

output "documents_bucket_name" {
  description = "Documents S3 bucket name"
  value       = module.s3.documents_bucket_name
}

output "certificate_arn" {
  description = "ACM certificate ARN"
  value       = var.domain_name != "" ? module.route53[0].certificate_arn : null
}

output "fqdn" {
  description = "API FQDN"
  value       = var.domain_name != "" ? module.route53[0].fqdn : null
}

output "github_actions_role_arn" {
  description = "GitHub Actions role ARN"
  value       = module.iam.github_actions_role_arn
}

output "task_execution_role_arn" {
  description = "Task execution role ARN"
  value       = module.iam.task_execution_role_arn
}

output "task_role_arn" {
  description = "Task role ARN"
  value       = module.iam.task_role_arn
}

output "monitoring_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${module.monitoring.dashboard_name}"
}