# =============================================================================
# AvertaSaaS - Route53 Module Outputs
# =============================================================================

output "hosted_zone_id" {
  description = "Route53 hosted zone ID"
  value       = local.hosted_zone_id
}

output "hosted_zone_name_servers" {
  description = "Route53 hosted zone name servers"
  value       = local.hosted_zone_name_servers
}

output "certificate_arn" {
  description = "ACM certificate ARN"
  value       = local.certificate_arn
}

output "fqdn" {
  description = "Fully qualified domain name"
  value       = local.fqdn
}

output "api_alias_record_fqdn" {
  description = "API alias record FQDN"
  value       = var.alb_dns_name != "" && var.alb_zone_id != "" ? local.fqdn : null
}

output "health_check_id" {
  description = "Route53 health check ID"
  value       = var.alb_dns_name != "" ? aws_route53_health_check.alb[0].id : null
}