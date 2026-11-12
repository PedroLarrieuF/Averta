# =============================================================================
# AvertaSaaS - ECS Module
# Creates ECS cluster, services, task definitions for backend, celery, pgbouncer
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "ecs"
    },
    var.tags
  )

  cluster_name = var.cluster_name != "" ? var.cluster_name : "${var.project_name}-${var.environment}-cluster"
}

# =============================================================================
# ECS Cluster
# =============================================================================

resource "aws_ecs_cluster" "main" {
  name = local.cluster_name

  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs_exec.name
      }
    }
  }

  tags = local.common_tags
}

# CloudWatch log group for ECS exec
resource "aws_cloudwatch_log_group" "ecs_exec" {
  name              = "/aws/ecs/${local.cluster_name}/exec"
  retention_in_days = var.log_group_retention_days
  tags              = local.common_tags
}

# =============================================================================
# IAM Roles
# =============================================================================

# Task Execution Role
resource "aws_iam_role" "task_execution" {
  count = var.task_execution_role_arn == "" ? 1 : 0

  name = "${local.cluster_name}-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  count = var.task_execution_role_arn == "" ? 1 : 0

  role       = aws_iam_role.task_execution[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional permissions for secrets, SSM, etc.
resource "aws_iam_policy" "task_execution_extra" {
  count = var.task_execution_role_arn == "" ? 1 : 0

  name = "${local.cluster_name}-task-execution-extra"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "kms:Decrypt",
          "ssm:GetParameters",
          "ssm:GetParameter",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "task_execution_extra" {
  count = var.task_execution_role_arn == "" ? 1 : 0

  role       = aws_iam_role.task_execution[0].name
  policy_arn = aws_iam_policy.task_execution_extra[0].arn
}

locals {
  task_execution_role_arn = var.task_execution_role_arn != "" ? var.task_execution_role_arn : aws_iam_role.task_execution[0].arn
}

# Task Role
resource "aws_iam_role" "task" {
  count = var.task_role_arn == "" ? 1 : 0

  name = "${local.cluster_name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

locals {
  task_role_arn = var.task_role_arn != "" ? var.task_role_arn : aws_iam_role.task[0].arn
}

# =============================================================================
# CloudWatch Log Groups
# =============================================================================

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/aws/ecs/${local.cluster_name}/backend"
  retention_in_days = var.log_group_retention_days
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "celery_worker" {
  name              = "/aws/ecs/${local.cluster_name}/celery-worker"
  retention_in_days = var.log_group_retention_days
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "celery_beat" {
  name              = "/aws/ecs/${local.cluster_name}/celery-beat"
  retention_in_days = var.log_group_retention_days
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "pgbouncer" {
  name              = "/aws/ecs/${local.cluster_name}/pgbouncer"
  retention_in_days = var.log_group_retention_days
  tags              = local.common_tags
}

# =============================================================================
# Task Definitions
# =============================================================================

# Backend Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.cluster_name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = local.task_execution_role_arn
  task_role_arn            = local.task_role_arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([{
    name      = "backend"
    image     = var.backend_image
    essential = true
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "AWS_REGION", value = var.aws_region }
    ]
    secrets = [
      { name = "DATABASE_URL", valueFrom = "${var.project_name}/${var.environment}/database:username::" },
      { name = "DATABASE_PASSWORD", valueFrom = "${var.project_name}/${var.environment}/database:password::" },
      { name = "REDIS_URL", valueFrom = "${var.project_name}/${var.environment}/redis::" },
      { name = "JWT_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/jwt:secret_key::" },
      { name = "JWT_REFRESH_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/jwt:refresh_secret_key::" },
      { name = "S3_ACCESS_KEY", valueFrom = "${var.project_name}/${var.environment}/minio:access_key::" },
      { name = "S3_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/minio:secret_key::" },
      { name = "SENDGRID_API_KEY", valueFrom = "${var.project_name}/${var.environment}/sendgrid:api_key::" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/aws/ecs/${local.cluster_name}/backend"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "backend"
      }
    }
    healthCheck = {
      command  = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)\" || exit 1"]
      interval = 30
      timeout  = 10
      retries  = 3
      startPeriod = 60
    }
  }])

  tags = local.common_tags
}

# Celery Worker Task Definition
resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "${local.cluster_name}-celery-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.celery_worker_cpu
  memory                   = var.celery_worker_memory
  execution_role_arn       = local.task_execution_role_arn
  task_role_arn            = local.task_role_arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([{
    name      = "celery-worker"
    image     = var.celery_worker_image != "" ? var.celery_worker_image : var.backend_image
    essential = true
    command   = ["celery", "-A", "app.core.celery_app", "worker", "--loglevel=info", "--concurrency=4", "--pool=prefork"]
    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "AWS_REGION", value = var.aws_region }
    ]
    secrets = [
      { name = "DATABASE_URL", valueFrom = "${var.project_name}/${var.environment}/database:username::" },
      { name = "DATABASE_PASSWORD", valueFrom = "${var.project_name}/${var.environment}/database:password::" },
      { name = "REDIS_URL", valueFrom = "${var.project_name}/${var.environment}/redis::" },
      { name = "JWT_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/jwt:secret_key::" },
      { name = "JWT_REFRESH_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/jwt:refresh_secret_key::" },
      { name = "S3_ACCESS_KEY", valueFrom = "${var.project_name}/${var.environment}/minio:access_key::" },
      { name = "S3_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/minio:secret_key::" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/aws/ecs/${local.cluster_name}/celery-worker"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "celery-worker"
      }
    }
  }])

  tags = local.common_tags
}

# Celery Beat Task Definition
resource "aws_ecs_task_definition" "celery_beat" {
  family                   = "${local.cluster_name}-celery-beat"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.celery_beat_cpu
  memory                   = var.celery_beat_memory
  execution_role_arn       = local.task_execution_role_arn
  task_role_arn            = local.task_role_arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([{
    name      = "celery-beat"
    image     = var.celery_beat_image != "" ? var.celery_beat_image : var.backend_image
    essential = true
    command   = ["celery", "-A", "app.core.celery_app", "beat", "--loglevel=info", "--scheduler", "celery.beat.PersistentScheduler"]
    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "AWS_REGION", value = var.aws_region }
    ]
    secrets = [
      { name = "DATABASE_URL", valueFrom = "${var.project_name}/${var.environment}/database:username::" },
      { name = "DATABASE_PASSWORD", valueFrom = "${var.project_name}/${var.environment}/database:password::" },
      { name = "REDIS_URL", valueFrom = "${var.project_name}/${var.environment}/redis::" },
      { name = "JWT_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/jwt:secret_key::" },
      { name = "JWT_REFRESH_SECRET_KEY", valueFrom = "${var.project_name}/${var.environment}/jwt:refresh_secret_key::" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/aws/ecs/${local.cluster_name}/celery-beat"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "celery-beat"
      }
    }
  }])

  tags = local.common_tags
}

# PgBouncer Task Definition
resource "aws_ecs_task_definition" "pgbouncer" {
  family                   = "${local.cluster_name}-pgbouncer"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.pgbouncer_cpu
  memory                   = var.pgbouncer_memory
  execution_role_arn       = local.task_execution_role_arn
  task_role_arn            = local.task_role_arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([{
    name      = "pgbouncer"
    image     = var.pgbouncer_image
    essential = true
    portMappings = [{
      containerPort = 6432
      protocol      = "tcp"
    }]
    environment = [
      { name = "DATABASES_HOST", value = var.rds_cluster_endpoint },
      { name = "DATABASES_PORT", value = "5432" },
      { name = "DATABASES_DBNAME", value = "averta" },
      { name = "POOL_MODE", value = "transaction" },
      { name = "MAX_CLIENT_CONN", value = "1000" },
      { name = "DEFAULT_POOL_SIZE", "50" }
    ]
    secrets = [
      { name = "DATABASES_USER", valueFrom = "${var.project_name}/${var.environment}/database:username::" },
      { name = "DATABASES_PASSWORD", valueFrom = "${var.project_name}/${var.environment}/database:password::" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/aws/ecs/${local.cluster_name}/pgbouncer"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "pgbouncer"
      }
    }
    healthCheck = {
      command  = ["CMD-SHELL", "pg_isready -p 6432 -U averta || exit 1"]
      interval = 30
      timeout  = 10
      retries  = 3
      startPeriod = 30
    }
  }])

  tags = local.common_tags
}

# =============================================================================
# ECS Services
# =============================================================================

# Backend Service
resource "aws_ecs_service" "backend" {
  name            = "${local.cluster_name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"
  platform_version = "LATEST"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.ecs_tasks_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.alb_target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = local.common_tags
}

# Backend Service Autoscaling
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = var.backend_max_count
  min_capacity       = var.backend_min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "backend_scale_up" {
  name               = "${local.cluster_name}-backend-scale-up"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

resource "aws_appautoscaling_policy" "backend_scale_down" {
  name               = "${local.cluster_name}-backend-scale-down"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Celery Worker Service
resource "aws_ecs_service" "celery_worker" {
  name            = "${local.cluster_name}-celery-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  desired_count   = var.celery_worker_desired_count
  launch_type     = "FARGATE"
  platform_version = "LATEST"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.ecs_tasks_sg_id]
    assign_public_ip = false
  }

  deployment_controller {
    type = "ECS"
  }

  tags = local.common_tags
}

# Celery Worker Autoscaling
resource "aws_appautoscaling_target" "celery_worker" {
  max_capacity       = var.celery_worker_max_count
  min_capacity       = var.celery_worker_min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.celery_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "celery_worker_scale" {
  name               = "${local.cluster_name}-celery-worker-scale"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.celery_worker.resource_id
  scalable_dimension = aws_appautoscaling_target.celery_worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.celery_worker.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Celery Beat Service (Singleton)
resource "aws_ecs_service" "celery_beat" {
  name            = "${local.cluster_name}-celery-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_beat.arn
  desired_count   = var.celery_beat_desired_count
  launch_type     = "FARGATE"
  platform_version = "LATEST"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.ecs_tasks_sg_id]
    assign_public_ip = false
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = local.common_tags
}

# PgBouncer Service
resource "aws_ecs_service" "pgbouncer" {
  name            = "${local.cluster_name}-pgbouncer"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.pgbouncer.arn
  desired_count   = var.pgbouncer_desired_count
  launch_type     = "FARGATE"
  platform_version = "LATEST"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.ecs_tasks_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.pgbouncer.arn
    container_name   = "pgbouncer"
    container_port   = 6432
  }

  deployment_controller {
    type = "ECS"
  }

  tags = local.common_tags
}

# PgBouncer Target Group (for internal NLB or ALB)
resource "aws_lb_target_group" "pgbouncer" {
  name        = "${local.cluster_name}-pgbouncer"
  port        = 6432
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    port     = "6432"
    protocol = "TCP"
    interval = 30
    timeout  = 10
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = local.common_tags
}

# =============================================================================
# Service Discovery (Cloud Map)
# =============================================================================

resource "aws_service_discovery_private_dns_namespace" "ecs" {
  name        = "${var.environment}.internal"
  vpc         = var.vpc_id
  description = "Service discovery for ${var.project_name} ${var.environment}"

  tags = local.common_tags
}

resource "aws_service_discovery_service" "backend" {
  name = "backend"
  dns_config {
    dns_records = [{
      type = "A"
      ttl  = 60
    }]
    routing_policy = "MULTIVALUE"
  }
  namespace_id = aws_service_discovery_private_dns_namespace.ecs.id
  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_service_discovery_service" "pgbouncer" {
  name = "pgbouncer"
  dns_config {
    dns_records = [{
      type = "A"
      ttl  = 60
    }]
    routing_policy = "MULTIVALUE"
  }
  namespace_id = aws_service_discovery_private_dns_namespace.ecs.id
  health_check_custom_config {
    failure_threshold = 1
  }
}