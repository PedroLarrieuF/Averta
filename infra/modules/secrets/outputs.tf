output "database_secret_arn" {
  description = "ARN of the database secret"
  value       = aws_secretsmanager_secret.database.arn
}

output "database_secret_name" {
  description = "Name of the database secret"
  value       = aws_secretsmanager_secret.database.name
}

output "redis_secret_arn" {
  description = "ARN of the Redis secret"
  value       = aws_secretsmanager_secret.redis.arn
}

output "redis_secret_name" {
  description = "Name of the Redis secret"
  value       = aws_secretsmanager_secret.redis.name
}

output "minio_secret_arn" {
  description = "ARN of the MinIO/S3 secret"
  value       = aws_secretsmanager_secret.minio.arn
}

output "minio_secret_name" {
  description = "Name of the MinIO/S3 secret"
  value       = aws_secretsmanager_secret.minio.name
}

output "jwt_secret_arn" {
  description = "ARN of the JWT secret"
  value       = aws_secretsmanager_secret.jwt.arn
}

output "jwt_secret_name" {
  description = "Name of the JWT secret"
  value       = aws_secretsmanager_secret.jwt.name
}

output "sendgrid_secret_arn" {
  description = "ARN of the SendGrid secret"
  value       = aws_secretsmanager_secret.sendgrid.arn
}

output "sendgrid_secret_name" {
  description = "Name of the SendGrid secret"
  value       = aws_secretsmanager_secret.sendgrid.name
}

output "app_secret_arn" {
  description = "ARN of the app config secret"
  value       = aws_secretsmanager_secret.app.arn
}

output "app_secret_name" {
  description = "Name of the app config secret"
  value       = aws_secretsmanager_secret.app.name
}

output "ecs_task_secrets_policy_arn" {
  description = "ARN of the ECS task secrets IAM policy"
  value       = aws_iam_policy.ecs_task_secrets.arn
}

output "ecs_task_secrets_policy_name" {
  description = "Name of the ECS task secrets IAM policy"
  value       = aws_iam_policy.ecs_task_secrets.name
}

output "github_actions_deploy_policy_arn" {
  description = "ARN of the GitHub Actions deploy IAM policy"
  value       = aws_iam_policy.github_actions_deploy.arn
}

output "github_actions_deploy_policy_name" {
  description = "Name of the GitHub Actions deploy IAM policy"
  value       = aws_iam_policy.github_actions_deploy.name
}

output "developer_staging_policy_arn" {
  description = "ARN of the developer staging IAM policy (staging only)"
  value       = var.environment == "staging" ? aws_iam_policy.developer_staging[0].arn : null
}

output "developer_staging_policy_name" {
  description = "Name of the developer staging IAM policy (staging only)"
  value       = var.environment == "staging" ? aws_iam_policy.developer_staging[0].name : null
}

output "kms_key_id" {
  description = "KMS key ID used for secret encryption"
  value       = local.kms_key_id
}

output "kms_key_arn" {
  description = "KMS key ARN used for secret encryption"
  value       = var.kms_key_id != "" ? var.kms_key_id : aws_kms_key.secrets[0].arn
}

output "cloudtrail_arn" {
  description = "ARN of the CloudTrail for secret access auditing"
  value       = aws_cloudtrail.secrets_audit.arn
}

output "cloudtrail_logs_bucket" {
  description = "S3 bucket for CloudTrail logs"
  value       = aws_s3_bucket.cloudtrail_logs.bucket
}

output "all_secret_arns" {
  description = "Map of all secret ARNs for easy reference"
  value = {
    database  = aws_secretsmanager_secret.database.arn
    redis     = aws_secretsmanager_secret.redis.arn
    minio     = aws_secretsmanager_secret.minio.arn
    jwt       = aws_secretsmanager_secret.jwt.arn
    sendgrid  = aws_secretsmanager_secret.sendgrid.arn
    app       = aws_secretsmanager_secret.app.arn
  }
}

output "all_secret_names" {
  description = "Map of all secret names for easy reference"
  value = {
    database  = aws_secretsmanager_secret.database.name
    redis     = aws_secretsmanager_secret.redis.name
    minio     = aws_secretsmanager_secret.minio.name
    jwt       = aws_secretsmanager_secret.jwt.name
    sendgrid  = aws_secretsmanager_secret.sendgrid.name
    app       = aws_secretsmanager_secret.app.name
  }
}