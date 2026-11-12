output "documents_bucket_name" {
  description = "Documents bucket name"
  value       = aws_s3_bucket.documents.bucket
}

output "documents_bucket_arn" {
  description = "Documents bucket ARN"
  value       = aws_s3_bucket.documents.arn
}

output "documents_bucket_domain_name" {
  description = "Documents bucket domain name"
  value       = aws_s3_bucket.documents.bucket_domain_name
}

output "documents_bucket_regional_domain_name" {
  description = "Documents bucket regional domain name"
  value       = aws_s3_bucket.documents.bucket_regional_domain_name
}

output "assets_bucket_name" {
  description = "Assets bucket name"
  value       = aws_s3_bucket.assets.bucket
}

output "assets_bucket_arn" {
  description = "Assets bucket ARN"
  value       = aws_s3_bucket.assets.arn
}

output "logs_bucket_name" {
  description = "Logs bucket name"
  value       = aws_s3_bucket.logs.bucket
}

output "logs_bucket_arn" {
  description = "Logs bucket ARN"
  value       = aws_s3_bucket.logs.arn
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.documents[0].id : null
}

output "cloudfront_distribution_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.documents[0].domain_name : null
}

output "cloudfront_distribution_arn" {
  description = "CloudFront distribution ARN"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.documents[0].arn : null
}

output "minio_endpoint" {
  description = "S3 endpoint for MinIO compatibility"
  value       = "https://s3.${var.aws_region}.amazonaws.com"
}

output "minio_region" {
  description = "S3 region"
  value       = var.aws_region
}

output "minio_credentials_secret_arn" {
  description = "Secrets Manager secret ARN for MinIO credentials"
  value       = aws_secretsmanager_secret.minio_credentials.arn
}

output "minio_credentials_secret_name" {
  description = "Secrets Manager secret name for MinIO credentials"
  value       = aws_secretsmanager_secret.minio_credentials.name
}

output "kms_key_id" {
  description = "KMS key ID for bucket encryption"
  value       = local.kms_key_id
}