# Card #06 - Secrets Management (AWS Secrets Manager)

## Overview
Migrate all secrets from environment files to AWS Secrets Manager with automatic rotation, least-privilege access, and secure injection into containers.

## Priority: HIGH
## Estimate: M (Medium)

## Current State
- Secrets in `.env.local` (gitignored) and GitHub Actions secrets
- No rotation strategy
- No centralized secret management
- Secrets passed via docker-compose environment variables

## Required Work

### 1. Secret Inventory & Classification
- [ ] Catalog all secrets:
  - Database credentials (POSTGRES_PASSWORD)
  - Redis password (if auth enabled)
  - MinIO credentials (MINIO_ROOT_USER, MINIO_ROOT_PASSWORD)
  - JWT secrets (JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY)
  - SendGrid API key
  - AWS credentials (if any)
  - Any third-party API keys
- [ ] Classify by sensitivity: CRITICAL (DB, JWT), HIGH (API keys), MEDIUM (config)
- [ ] Define rotation frequency: CRITICAL=30 days, HIGH=90 days, MEDIUM=1 year

### 2. Secrets Manager Setup
- [ ] Create secrets in AWS Secrets Manager:
  - `averta/production/database` (username, password, host, port, dbname)
  - `averta/production/redis` (host, port, password)
  - `averta/production/minio` (endpoint, access_key, secret_key, bucket)
  - `averta/production/jwt` (secret_key, refresh_secret_key, algorithm)
  - `averta/production/sendgrid` (api_key, from_email)
  - `averta/production/app` (environment, log_level, cors_origins)
- [ ] Enable automatic rotation for database secret (30 days)
- [ ] Create rotation Lambda for custom secrets (SendGrid, MinIO)
- [ ] Tag secrets: `Project=AvertaSaaS`, `Environment=production`, `Rotation=auto|manual`

### 3. IAM Policies (Least Privilege)
- [ ] ECS Task Role policy:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": ["secretsmanager:GetSecretValue"],
        "Resource": [
          "arn:aws:secretsmanager:*:*:secret:averta/production/*"
        ],
        "Condition": {
          "StringEquals": {
            "secretsmanager:ResourceTag/Project": "AvertaSaaS"
          }
        }
      }
    ]
  }
  ```
- [ ] GitHub Actions role: `secretsmanager:GetSecretValue` for deploy only
- [ ] Developer role: `secretsmanager:GetSecretValue` for staging only
- [ ] Audit: CloudTrail logging for all secret access

### 4. Secret Injection at Runtime
- [ ] **Option A: ECS Secrets** (native, no code changes)
  - Add `secrets` section to task definition
  - Inject as environment variables at container start
  - Pros: Simple, no app changes
  - Cons: Only at start, no refresh without restart
- [ ] **Option B: Application-level fetch** (dynamic, refreshable)
  - Fetch secrets on startup + periodic refresh
  - Cache in memory with TTL
  - Pros: Rotation without restart, fine-grained control
  - Cons: Code changes required
- [ ] Decision: **Option A for MVP**, migrate to Option B later
- [ ] Update task definitions with `secrets` and `secretOptions`

### 5. Local Development
- [ ] Create `.env.local` generator script:
  ```bash
  aws secretsmanager get-secret-value --secret-id averta/staging/database --query SecretString --output text | jq -r 'to_entries|map("\(.key)=\(.value)")|.[]' > .env.local
  ```
- [ ] Add `make dev-secrets` target
- [ ] Document in README

### 6. CI/CD Integration
- [ ] GitHub Actions: fetch secrets at deploy time
- [ ] Use `aws-secretsmanager-get-secret-value` action
- [ ] Pass as environment variables to Terraform/ECS deploy
- [ ] Never log secret values (mask in logs)

### 7. Secret Rotation
- [ ] **Database**: RDS automatic rotation (30 days)
  - Verify application handles rotation (reconnect on auth failure)
  - Test rotation in staging
- [ ] **JWT Keys**: Manual rotation (90 days)
  - Generate new keys, deploy, invalidate old tokens gracefully
  - Maintain old key for `JWT_REFRESH_TOKEN_EXPIRE` period
- [ ] **SendGrid/MinIO**: Manual rotation (90 days)
  - Update in Secrets Manager, redeploy services
- [ ] Document rotation procedures in runbook

### 8. Secret Scanning
- [ ] Add TruffleHog to CI pipeline
- [ ] Add gitleaks pre-commit hook
- [ ] Scan: code, docker images, terraform state
- [ ] Alert on detected secrets

### 9. Migration from .env
- [ ] One-time migration script
- [ ] Verify all services work with Secrets Manager
- [ ] Remove secrets from GitHub Actions (use OIDC + Secrets Manager)
- [ ] Rotate all migrated secrets immediately

## Acceptance Criteria
- [ ] All production secrets in Secrets Manager
- [ ] Automatic rotation enabled for database (30 days)
- [ ] ECS tasks fetch secrets at startup
- [ ] Least-privilege IAM policies applied
- [ ] Secret scanning in CI with 0 findings
- [ ] Local development workflow documented
- [ ] Rotation runbooks tested in staging

## Files to Create/Modify
- `infra/modules/secrets/` (Terraform module - new)
- `backend/app/core/config.py` (update to support secret injection)
- `backend/scripts/fetch_secrets.sh` (local dev helper)
- `.github/workflows/deploy.yml` (secret fetching)
- `docs/runbooks/secret-rotation.md` (new)

## Dependencies
- Card #04 (AWS Infrastructure) for Secrets Manager, IAM
- Card #01 (Docker Hardening) for secure container runtime

## Notes
- ECS Secrets example in task definition:
  ```json
  "secrets": [
    {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:averta/production/database:username::"},
    {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:averta/production/database:password::"}
  ]
  ```
- For JSON secrets, use `valueFrom` with JSON key: `secret:name:key::`
- Rotation Lambda for custom secrets: use AWS-provided template or custom Python
- Test rotation: `aws secretsmanager rotate-secret --secret-id averta/production/database`