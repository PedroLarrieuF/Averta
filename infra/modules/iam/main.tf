# =============================================================================
# AvertaSaaS - IAM Module
# Creates IAM roles for ECS tasks, GitHub Actions OIDC, and developers
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "iam"
    },
    var.tags
  )

  name_prefix = "${var.project_name}-${var.environment}"
}

# =============================================================================
# OIDC Provider for GitHub Actions
# =============================================================================

resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = local.common_tags
}

# =============================================================================
# GitHub Actions Role (for CI/CD deployments)
# =============================================================================

resource "aws_iam_role" "github_actions" {
  count = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? 1 : 0

  name = "${local.name_prefix}-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github[0].arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
        }
      }
    }]
  })

  tags = local.common_tags
}

# Policy for GitHub Actions role
resource "aws_iam_policy" "github_actions" {
  count = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? 1 : 0

  name = "${local.name_prefix}-github-actions-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RegisterTaskDefinition",
          "ecs:DeregisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:ListTaskDefinitions",
          "ecs:ListServices",
          "ecs:TagResource",
          "ecs:UntagResource"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.name_prefix}-task-execution-role",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.name_prefix}-task-role"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "application-autoscaling:DescribeScalableTargets",
          "application-autoscaling:DescribeScalingPolicies",
          "application-autoscaling:RegisterScalableTarget",
          "application-autoscaling:DeregisterScalableTarget",
          "application-autoscaling:PutScalingPolicy",
          "application-autoscaling:DeleteScalingPolicy"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetHealth",
          "elasticloadbalancing:DescribeListeners",
          "elasticloadbalancing:DescribeRules"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "github_actions" {
  count = var.create_github_oidc && var.github_org != "" && var.github_repo != "" ? 1 : 0

  role       = aws_iam_role.github_actions[0].name
  policy_arn = aws_iam_policy.github_actions[0].arn
}

# =============================================================================
# ECS Task Execution Role
# =============================================================================

resource "aws_iam_role" "task_execution" {
  count = var.create_task_execution_role ? 1 : 0

  name = "${local.name_prefix}-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "task_execution_managed" {
  count = var.create_task_execution_role ? 1 : 0

  role       = aws_iam_role.task_execution[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional task execution policy for secrets, SSM, etc.
resource "aws_iam_policy" "task_execution_extra" {
  count = var.create_task_execution_role ? 1 : 0

  name = "${local.name_prefix}-task-execution-extra"

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
  count = var.create_task_execution_role ? 1 : 0

  role       = aws_iam_role.task_execution[0].name
  policy_arn = aws_iam_policy.task_execution_extra[0].arn
}

# Attach additional execution policies
resource "aws_iam_role_policy_attachment" "task_execution_additional" {
  count = var.create_task_execution_role ? length(var.additional_execution_policies) : 0

  for_each = toset(var.additional_execution_policies)

  role       = aws_iam_role.task_execution[0].name
  policy_arn = each.value
}

# =============================================================================
# ECS Task Role
# =============================================================================

resource "aws_iam_role" "task" {
  count = var.create_task_role ? 1 : 0

  name = "${local.name_prefix}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

# Task role policy for application permissions
resource "aws_iam_policy" "task" {
  count = var.create_task_role ? 1 : 0

  name = "${local.name_prefix}-task-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}/${var.environment}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${var.aws_region}.amazonaws.com"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-${var.environment}-*",
          "arn:aws:s3:::${var.project_name}-${var.environment}-*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "task" {
  count = var.create_task_role ? 1 : 0

  role       = aws_iam_role.task[0].name
  policy_arn = aws_iam_policy.task[0].arn
}

# Attach additional task policies
resource "aws_iam_role_policy_attachment" "task_additional" {
  count = var.create_task_role ? length(var.additional_task_policies) : 0

  for_each = toset(var.additional_task_policies)

  role       = aws_iam_role.task[0].name
  policy_arn = each.value
}

# =============================================================================
# Developer Roles (optional)
# =============================================================================

resource "aws_iam_role" "developer" {
  for_each = var.create_developer_roles ? var.developer_users : {}

  name = "${local.name_prefix}-developer-${each.key}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      }
      Action = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:userid" = "*"
        }
      }
    }]
  })

  tags = merge(local.common_tags, { Developer = each.key })
}

resource "aws_iam_policy" "developer" {
  for_each = var.create_developer_roles ? var.developer_users : {}

  name = "${local.name_prefix}-developer-${each.key}-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:Describe*",
          "ecs:List*",
          "logs:Describe*",
          "logs:Get*",
          "logs:FilterLogEvents",
          "cloudwatch:GetMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "xray:GetTraceSummaries",
          "xray:BatchGetTraces"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = each.value
        Resource = "*"
      }
    ]
  })

  tags = merge(local.common_tags, { Developer = each.key })
}

resource "aws_iam_role_policy_attachment" "developer" {
  for_each = var.create_developer_roles ? var.developer_users : {}

  role       = aws_iam_role.developer[each.key].name
  policy_arn = aws_iam_policy.developer[each.key].arn
}

# =============================================================================
# ECS Service-Linked Role (if needed)
# =============================================================================

resource "aws_iam_service_linked_role" "ecs" {
  aws_service_name = "ecs.amazonaws.com"
  description      = "Service-linked role for ECS"
}

resource "aws_iam_service_linked_role" "ecs_fargate" {
  aws_service_name = "fargate.amazonaws.com"
  description      = "Service-linked role for ECS Fargate"
}

resource "aws_iam_service_linked_role" "application_autoscaling" {
  aws_service_name = "autoscaling.amazonaws.com"
  description      = "Service-linked role for Application Auto Scaling"
}

# =============================================================================
# Data Sources
# =============================================================================

data "aws_caller_identity" "current" {}