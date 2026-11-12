# =============================================================================
# AvertaSaaS - Route53 Module
# Creates hosted zone, DNS records, and ACM certificate
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "route53"
    },
    var.tags
  )

  fqdn = "${var.subdomain}.${var.domain_name}"
}

# =============================================================================
# Hosted Zone (or data source for existing)
# =============================================================================

resource "aws_route53_zone" "main" {
  count = var.hosted_zone_id == "" ? 1 : 0

  name = var.domain_name

  tags = local.common_tags
}

data "aws_route53_zone" "main" {
  count = var.hosted_zone_id != "" ? 1 : 0

  zone_id = var.hosted_zone_id
}

locals {
  hosted_zone_id = var.hosted_zone_id != "" ? data.aws_route53_zone.main[0].zone_id : aws_route53_zone.main[0].zone_id
  hosted_zone_name_servers = var.hosted_zone_id != "" ? data.aws_route53_zone.main[0].name_servers : aws_route53_zone.main[0].name_servers
}

# =============================================================================
# ACM Certificate
# =============================================================================

resource "aws_acm_certificate" "main" {
  count = var.certificate_arn == "" && var.create_certificate ? 1 : 0

  domain_name       = local.fqdn
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${local.fqdn}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = local.common_tags
}

resource "aws_acm_certificate_validation" "main" {
  count = var.certificate_arn == "" && var.create_certificate ? 1 : 0

  certificate_arn         = aws_acm_certificate.main[0].arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

locals {
  certificate_arn = var.certificate_arn != "" ? var.certificate_arn : (var.create_certificate ? aws_acm_certificate.main[0].arn : null)
}

# =============================================================================
# Certificate DNS Validation Records
# =============================================================================

resource "aws_route53_record" "cert_validation" {
  count = var.certificate_arn == "" && var.create_certificate ? length(aws_acm_certificate.main[0].domain_validation_options) : 0

  for_each = { for dvo in aws_acm_certificate.main[0].domain_validation_options : dvo.domain => dvo }

  zone_id = local.hosted_zone_id
  name    = each.value.resource_record_name
  type    = each.value.resource_record_type
  ttl     = 60
  records = [each.value.resource_record_value]
}

# =============================================================================
# DNS Records
# =============================================================================

# A record (alias) for API subdomain pointing to ALB
resource "aws_route53_record" "api_alias" {
  count = var.alb_dns_name != "" && var.alb_zone_id != "" ? 1 : 0

  zone_id = local.hosted_zone_id
  name    = local.fqdn
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# AAAA record (alias) for API subdomain pointing to ALB (IPv6)
resource "aws_route53_record" "api_alias_ipv6" {
  count = var.alb_dns_name != "" && var.alb_zone_id != "" ? 1 : 0

  zone_id = local.hosted_zone_id
  name    = local.fqdn
  type    = "AAAA"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# CNAME for www subdomain (optional)
resource "aws_route53_record" "www" {
  count = var.alb_dns_name != "" && var.alb_zone_id != "" ? 1 : 0

  zone_id = local.hosted_zone_id
  name    = "www.${local.fqdn}"
  type    = "CNAME"
  ttl     = 300
  records = [var.alb_dns_name]
}

# TXT record for domain verification (optional, for Google, Microsoft, etc.)
resource "aws_route53_record" "domain_verification" {
  count = 0  # Set to 1 and provide value if needed

  zone_id = local.hosted_zone_id
  name    = var.domain_name
  type    = "TXT"
  ttl     = 300
  records = ["verification-code-here"]
}

# =============================================================================
# Health Check (for ALB endpoint)
# =============================================================================

resource "aws_route53_health_check" "alb" {
  count = var.alb_dns_name != "" ? 1 : 0

  fqdn                            = var.alb_dns_name
  port                            = 443
  type                            = "HTTPS"
  resource_path                   = "/health"
  failure_threshold               = 3
  request_interval                = 30
  measure_latency                 = true
  enable_sni                      = true
  regions                         = ["us-east-1", "us-west-2", "eu-west-1"]

  tags = local.common_tags
}