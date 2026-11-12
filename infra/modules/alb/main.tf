# =============================================================================
# AvertaSaaS - ALB Module
# Creates Application Load Balancer with target groups, listeners, WAF
# =============================================================================

locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Component   = "alb"
    },
    var.tags
  )

  alb_name = "${var.project_name}-${var.environment}-alb"
}

# =============================================================================
# Application Load Balancer
# =============================================================================

resource "aws_lb" "main" {
  name               = local.alb_name
  internal           = var.internal
  load_balancer_type = var.alb_type
  security_groups    = [var.alb_sg_id]
  subnets            = var.public_subnet_ids
  idle_timeout       = var.idle_timeout
  enable_deletion_protection = var.enable_deletion_protection
  enable_waf         = var.enable_waf && var.waf_acl_arn != ""
  waf_acl_arn        = var.enable_waf && var.waf_acl_arn != "" ? var.waf_acl_arn : null

  access_logs {
    bucket  = var.access_logs_bucket != "" ? var.access_logs_bucket : null
    prefix  = var.access_logs_prefix
    enabled = var.access_logs_bucket != ""
  }

  tags = local.common_tags
}

# =============================================================================
# Target Group (Backend API)
# =============================================================================

resource "aws_lb_target_group" "backend" {
  name        = "${local.alb_name}-backend"
  port        = var.target_group_port
  protocol    = var.target_group_protocol
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = var.health_check_path
    interval            = var.health_check_interval
    timeout             = var.health_check_timeout
    healthy_threshold   = var.healthy_threshold
    unhealthy_threshold = var.unhealthy_threshold
    matcher             = "200"
    protocol            = "HTTP"
  }

  stickiness {
    type            = var.stickiness_enabled ? "lb_cookie" : ""
    cookie_duration = var.stickiness_duration
    enabled         = var.stickiness_enabled
  }

  deregistration_delay = var.deregistration_delay

  tags = local.common_tags
}

# =============================================================================
# Target Group Attachment (Security Group Rule)
# =============================================================================

# Allow ALB to communicate with target group
resource "aws_security_group_rule" "alb_to_target" {
  type              = "ingress"
  from_port         = var.target_group_port
  to_port           = var.target_group_port
  protocol          = "tcp"
  source_security_group_id = var.alb_sg_id
  security_group_id = var.target_sg_id
  description       = "Allow ALB to backend targets"
}

# =============================================================================
# HTTP Listener (redirect to HTTPS)
# =============================================================================

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# =============================================================================
# HTTPS Listener
# =============================================================================

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = var.ssl_policy
  certificate_arn   = var.certificate_arn != "" ? var.certificate_arn : null

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# =============================================================================
# Additional Listeners (optional - for WebSocket, gRPC, etc.)
# =============================================================================

# WebSocket upgrade support
resource "aws_lb_listener_rule" "websocket" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    http_header {
      http_header_name = "Upgrade"
      values           = ["websocket"]
    }
  }
}

# API versioning
resource "aws_lb_listener_rule" "api_v1" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/*"]
    }
  }
}

# Health check endpoint (no auth)
resource "aws_lb_listener_rule" "health" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 300

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/health", "/health/*"]
    }
  }
}

# =============================================================================
# WAF Integration (if enabled)
# =============================================================================

resource "aws_wafv2_web_acl" "alb" {
  count = var.enable_waf && var.waf_acl_arn == "" ? 1 : 0

  name  = "${local.alb_name}-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimit"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimit"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "KnownBadInputs"
      sampled_requests_enabled   = true
    }
  }

  tags = local.common_tags
}

resource "aws_wafv2_web_acl_association" "alb" {
  count = var.enable_waf && var.waf_acl_arn == "" ? 1 : 0

  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.alb[0].arn
}