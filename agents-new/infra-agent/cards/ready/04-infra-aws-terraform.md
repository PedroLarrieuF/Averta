# Card #04 - AWS Infrastructure (Terraform)

## Overview
Provision complete AWS infrastructure for AvertaSaaS production deployment using Terraform. Target architecture: ECS Fargate, RDS PostgreSQL, ElastiCache Redis, S3, ALB, Route53, ACM.

## Priority: MEDIUM
## Estimate: XL (Extra Large)

## Current State
- Local development via docker-compose
- No AWS infrastructure provisioned
- No Terraform configuration
- GitHub Actions CI only (no CD)

## Target Architecture

```
                                    ┌─────────────────┐
                                    │    Route53      │
                                    │  (DNS + ACM)    │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │      ALB        │
                                    │  (TLS Termination)│
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
            ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
            │ ECS Service │          │ ECS Service │          │ ECS Service │
            │  Backend    │          │  Celery     │          │  Celery     │
            │  API        │          │  Workers    │          │  Beat       │
            └──────┬──────┘          └──────┬──────┘          └──────┬──────┘
                   │                        │                        │
                   └────────────────────────┼────────────────────────┘
                                            │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
            ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
            │   RDS       │          │ ElastiCache │          │     S3      │
            │ PostgreSQL  │          │   Redis     │          │  (MinIO)    │
            │  (Multi-AZ) │          │ (Cluster)   │          │ + CloudFront│
            └─────────────┘          └─────────────┘          └─────────────┘
```

## Required Work

### 1. Terraform Foundation
- [ ] Create `infra/` directory structure
- [ ] Configure backend: S3 + DynamoDB locking
- [ ] Create provider configuration (AWS, random, tls, time)
- [ ] Set up module structure with versioning
- [ ] Configure GitHub Actions OIDC for Terraform

### 2. VPC Module (`modules/vpc/`)
- [ ] VPC with 3 AZs (us-east-1a, 1b, 1c)
- [ ] Public subnets (ALB, NAT Gateway) - /24 each
- [ ] Private subnets (ECS, RDS, ElastiCache) - /20 each
- [ ] Database subnets (RDS, ElastiCache) - /20 each
- [ ] NAT Gateways (1 per AZ for HA)
- [ ] Internet Gateway
- [ ] VPC Flow Logs to CloudWatch
- [ ] Security Groups: ALB, ECS, RDS, ElastiCache, Bastion
- [ ] Output: VPC ID, subnet IDs, SG IDs

### 3. RDS Module (`modules/rds/`)
- [ ] PostgreSQL 16, Multi-AZ deployment
- [ ] Instance class: db.r6g.xlarge (staging: db.t3.medium)
- [ ] Storage: GP3, 500GB, auto-scaling to 2TB
- [ ] Encryption: KMS key (customer managed)
- [ ] Parameter group: tuned for Prisma (work_mem, maintenance_work_mem)
- [ ] PgBouncer: RDS Proxy or separate EC2/ECS
- [ ] Automated backups: 30 days retention, PITR enabled
- [ ] Enhanced monitoring: 60-second granularity
- [ ] Performance Insights: 7-day retention
- [ ] Output: endpoint, port, secret ARN

### 4. ElastiCache Module (`modules/elasticache/`)
- [ ] Redis 7, Cluster mode enabled
- [ ] 3 shards, 1 replica per shard (Multi-AZ)
- [ ] Node type: cache.r6g.xlarge (staging: cache.t3.medium)
- [ ] Encryption: in-transit (TLS), at-rest (KMS)
- [ ] Subnet group: database subnets
- [ ] Parameter group: optimized for Celery (maxmemory-policy allkeys-lru)
- [ ] Output: primary endpoint, reader endpoint, secret ARN

### 5. S3 Module (`modules/s3/`)
- [ ] Buckets: documents, backups, logs, terraform-state
- [ ] Versioning enabled on all
- [ ] Encryption: SSE-KMS (customer managed keys)
- [ ] Lifecycle policies per bucket
- [ ] CloudFront distribution for documents bucket
- [ ] CORS configuration for direct uploads
- [ ] Block public access (except CloudFront OAI)
- [ ] Output: bucket ARNs, CloudFront domain

### 6. ECS Module (`modules/ecs/`)
- [ ] Fargate cluster with capacity providers
- [ ] Task definitions: backend, celery-worker, celery-beat
- [ ] Services with ALB integration (backend only)
- [ ] Auto-scaling: CPU > 70%, Memory > 80%, Request count
- [ ] Min/Max: Backend 2/10, Workers 1/20, Beat 1/1
- [ ] Execution role with Secrets Manager, CloudWatch, ECR permissions
- [ ] Task role with S3, RDS, ElastiCache permissions
- [ ] Health checks: /health endpoint
- [ ] Deployment circuit breaker
- [ ] Output: service ARNs, target group ARNs

### 7. ALB Module (`modules/alb/`)
- [ ] Application Load Balancer (internal=false)
- [ ] HTTPS listener (443) with ACM certificate
- [ ] HTTP listener (80) redirect to HTTPS
- [ ] Target groups: backend (port 8000)
- [ ] WAF: AWS Managed Rules + custom rate limiting
- [ ] Access logs to S3
- [ ] Output: ALB DNS name, ARN, target group ARNs

### 8. Route53 Module (`modules/route53/`)
- [ ] Hosted zone for averta.com.br (or subdomain)
- [ ] A record (ALB alias) for api.averta.com.br
- [ ] A record (CloudFront alias) for app.averta.com.br
- [ ] ACM certificate validation (DNS)
- [ ] Health check for ALB
- [ ] Output: zone ID, record names

### 9. IAM Module (`modules/iam/`)
- [ ] GitHub Actions OIDC provider
- [ ] Roles: terraform-plan, terraform-apply, deploy-backend
- [ ] Least-privilege policies per role
- [ ] Service roles: ECS execution, ECS task, RDS monitoring
- [ ] Output: role ARNs

### 10. Monitoring Module (`modules/monitoring/`)
- [ ] CloudWatch log groups (ECS, RDS, ALB)
- [ ] Metric filters for error patterns
- [ ] Dashboards: API, Database, Cache, Queue
- [ ] Alarms: CPU, Memory, Latency, Errors, Queue depth
- [ ] SNS topics for alerts
- [ ] X-Ray tracing enabled

### 11. Environment Configurations
- [ ] `environments/staging/` - smaller instances, single NAT
- [ ] `environments/production/` - HA, larger instances
- [ ] `terraform.tfvars` per environment
- [ ] Workspace separation

### 12. CI/CD Pipeline
- [ ] GitHub Actions: terraform fmt, validate, plan
- [ ] Plan on PR, apply on merge to main (staging)
- [ ] Manual approval for production apply
- [ ] Drift detection scheduled weekly
- [ ] Cost estimation in PR comments (infracost)

## Acceptance Criteria
- [ ] `terraform plan` passes for both environments
- [ ] Staging environment deployed and accessible
- [ ] All services healthy (ECS, RDS, ElastiCache, ALB)
- [ ] DNS resolves correctly with valid TLS
- [ ] Backend API responds at api.averta.com.br
- [ ] Monitoring dashboards showing metrics
- [ ] GitHub Actions deploy pipeline working
- [ ] Drift detection alerting configured

## Files to Create
```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── providers.tf
├── backend.tf
├── modules/
│   ├── vpc/
│   ├── rds/
│   ├── elasticache/
│   ├── s3/
│   ├── ecs/
│   ├── alb/
│   ├── route53/
│   ├── iam/
│   └── monitoring/
└── environments/
    ├── staging/
    │   ├── main.tf
    │   ├── terraform.tfvars
    │   └── backend.tf
    └── production/
        ├── main.tf
        ├── terraform.tfvars
        └── backend.tf
```

## Dependencies
- Card #01 (Docker Hardening) for production-ready images
- Card #06 (Secrets Management) for secret injection
- AWS account with appropriate permissions

## Notes
- Use Terraform Cloud or S3 backend with DynamoDB locking
- Tag all resources: `Project=AvertaSaaS`, `Environment=staging|production`, `ManagedBy=Terraform`
- Estimate monthly cost: ~$2,500/month (production), ~$400/month (staging)
- Use `terraform-docs` for auto-generated documentation
- Consider Terragrunt for DRY if modules grow complex