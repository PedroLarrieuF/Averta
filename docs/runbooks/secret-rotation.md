# Secret Rotation Runbook

> **Document Version:** 1.0  
> **Last Updated:** 2026-11-11  
> **Owner:** Platform Team  
> **Review Cycle:** Quarterly

---

## Overview

This runbook documents the procedures for rotating secrets in AWS Secrets Manager for the AvertaSaaS platform. It covers both automatic rotation (RDS database) and manual rotation (JWT keys, SendGrid, MinIO).

## Secret Inventory

| Secret | Path | Rotation Type | Frequency | Owner |
|--------|------|---------------|-----------|-------|
| Database | `averta/{env}/database` | Automatic (RDS) | 30 days | Platform |
| Redis | `averta/{env}/redis` | Manual | 90 days | Platform |
| MinIO/S3 | `averta/{env}/minio` | Manual | 90 days | Platform |
| JWT Keys | `averta/{env}/jwt` | Manual | 90 days | Platform |
| SendGrid | `averta/{env}/sendgrid` | Manual | 90 days | Platform |
| App Config | `averta/{env}/app` | N/A (config) | N/A | Platform |

---

## Automatic Rotation: Database (RDS)

### How It Works

1. AWS Secrets Manager creates a rotation Lambda automatically when you enable rotation on an RDS secret
2. The Lambda rotates the password every 30 days (configurable)
3. During rotation:
   - New password is generated
   - Secret is updated with new credentials
   - RDS user password is updated
   - Old credentials remain valid until next rotation

### Prerequisites

- RDS instance must exist and be accessible
- Secret must be created with RDS credentials
- Rotation Lambda must have network access to RDS (same VPC, security groups)

### Enable Automatic Rotation

```bash
# Enable rotation (30 days default)
aws secretsmanager rotate-secret \
    --secret-id averta/production/database \
    --rotation-lambda-arn <lambda-arn> \
    --rotation-rules AutomaticallyAfterDays=30

# Or via Terraform (already configured in secrets module)
# rotation_rules { automatically_after_days = 30 }
```

### Verify Rotation Works

```bash
# Check rotation status
aws secretsmanager describe-secret \
    --secret-id averta/production/database \
    --query 'RotationEnabled,RotationRules,LastRotatedDate'

# Trigger manual rotation (for testing)
aws secretsmanager rotate-secret \
    --secret-id averta/production/database
```

### Application Handling

The application must handle database connection failures gracefully:

1. **Connection retry logic** - Implement exponential backoff
2. **Reconnect on auth failure** - Catch authentication errors and re-fetch credentials
3. **Connection pooling** - Use PgBouncer which handles connection lifecycle

```python
# Example: Graceful reconnect in Prisma
# The Prisma client will automatically reconnect on next query
# Ensure your connection pool settings allow for quick recovery
```

### Troubleshooting

| Issue | Resolution |
|-------|------------|
| Rotation fails | Check Lambda logs in CloudWatch: `/aws/lambda/SecretsManagerRotation...` |
| App can't connect after rotation | Verify security groups allow Lambda → RDS traffic |
| Old connections fail | Expected - implement retry logic in app |

---

## Manual Rotation: JWT Keys

### Why Rotate JWT Keys?

- Compromise mitigation
- Compliance requirements
- Key hygiene best practice

### Rotation Strategy: Graceful Key Transition

**DO NOT** immediately invalidate all tokens. Use a grace period:

1. Generate new keys
2. Deploy new keys to Secrets Manager
3. Deploy application (starts signing with new key)
4. Old refresh tokens remain valid for `JWT_REFRESH_TOKEN_EXPIRE_DAYS` (7 days)
5. After grace period, remove old key

### Procedure

#### 1. Generate New Keys

```bash
# Generate new secret keys (32+ chars base64)
NEW_SECRET_KEY=$(openssl rand -base64 32)
NEW_REFRESH_KEY=$(openssl rand -base64 32)

echo "JWT_SECRET_KEY=$NEW_SECRET_KEY"
echo "JWT_REFRESH_SECRET_KEY=$NEW_REFRESH_KEY"
```

#### 2. Update Secrets Manager (Staging First)

```bash
# Get current secret
aws secretsmanager get-secret-value \
    --secret-id averta/staging/jwt \
    --query SecretString --output text | jq . > jwt_current.json

# Create new version with new keys
jq --arg sk "$NEW_SECRET_KEY" --arg rsk "$NEW_REFRESH_KEY" \
   '.secret_key = $sk | .refresh_secret_key = $rsk' \
   jwt_current.json > jwt_new.json

# Update secret
aws secretsmanager put-secret-value \
    --secret-id averta/staging/jwt \
    --secret-string file://jwt_new.json
```

#### 3. Deploy to Staging

```bash
# Trigger staging deployment
gh workflow run deploy.yml -f environment=staging

# Verify staging works
curl -H "Authorization: Bearer <new-token>" https://staging.averta.com.br/api/v1/health
```

#### 4. Monitor Staging (24-48 hours)

- Check error rates for auth endpoints
- Verify token refresh works
- Check logs for "invalid signature" errors

#### 5. Deploy to Production

```bash
# Update production secret (same process)
aws secretsmanager put-secret-value \
    --secret-id averta/production/jwt \
    --secret-string file://jwt_new.json

# Trigger production deployment
gh workflow run deploy.yml -f environment=production
```

#### 6. Cleanup (After 7+ Days)

```bash
# Remove old key reference (optional - keep for audit)
# Old refresh tokens will have expired by now
```

### Rollback Procedure

If issues detected:

```bash
# Revert to previous secret version
aws secretsmanager get-secret-value \
    --secret-id averta/production/jwt \
    --version-stage AWSPREVIOUS \
    --query SecretString --output text > jwt_previous.json

aws secretsmanager put-secret-value \
    --secret-id averta/production/jwt \
    --secret-string file://jwt_previous.json

# Redeploy
gh workflow run deploy.yml -f environment=production
```

---

## Manual Rotation: SendGrid API Key

### Procedure

1. **Generate new API key** in SendGrid dashboard
2. **Update Secrets Manager**:

```bash
aws secretsmanager put-secret-value \
    --secret-id averta/production/sendgrid \
    --secret-string '{"api_key": "SG.new-key", "from_email": "noreply@averta.com.br", "from_name": "Averta Auditoria"}'
```

3. **Deploy application** (picks up new key at startup)
4. **Verify email sending** works
5. **Revoke old API key** in SendGrid dashboard

### Timing

- No grace period needed (API key used for outbound only)
- Deploy immediately after updating secret

---

## Manual Rotation: MinIO/S3 Credentials

### Procedure

1. **Generate new credentials** in MinIO console or AWS IAM
2. **Update Secrets Manager**:

```bash
aws secretsmanager put-secret-value \
    --secret-id averta/production/minio \
    --secret-string '{"endpoint": "https://s3.us-east-1.amazonaws.com", "access_key": "NEW_KEY", "secret_key": "NEW_SECRET", "bucket": "averta-prod-documents", "region": "us-east-1"}'
```

3. **Deploy application**
4. **Verify file upload/download** works
5. **Revoke old credentials**

---

## Manual Rotation: Redis Password

### Procedure

1. **Update Redis auth** (ElastiCache or self-hosted)
2. **Update Secrets Manager**:

```bash
aws secretsmanager put-secret-value \
    --secret-id averta/production/redis \
    --secret-string '{"host": "redis.xxx.use1.cache.amazonaws.com", "port": 6379, "password": "NEW_PASSWORD"}'
```

3. **Deploy application** (Celery workers + backend)
4. **Verify queue processing** works

---

## Emergency Rotation (Compromise Response)

If a secret is suspected compromised:

### 1. Immediate Actions (< 1 hour)

```bash
# Rotate database immediately
aws secretsmanager rotate-secret --secret-id averta/production/database

# Rotate JWT keys immediately (no grace period for compromise)
# Generate new keys and update secret
NEW_SECRET_KEY=$(openssl rand -base64 32)
NEW_REFRESH_KEY=$(openssl rand -base64 32)
jq -n --arg sk "$NEW_SECRET_KEY" --arg rsk "$NEW_REFRESH_KEY" \
   '{secret_key: $sk, refresh_secret_key: $rsk, algorithm: "HS256"}' \
   | aws secretsmanager put-secret-value --secret-id averta/production/jwt --secret-string file:///dev/stdin

# Force redeploy all services
gh workflow run deploy.yml -f environment=production
```

### 2. Invalidate Sessions

```bash
# Option A: Change JWT secret (invalidates ALL tokens immediately)
# Done above

# Option B: Add blocklist for specific tokens (if targeted)
# Requires application support
```

### 3. Audit Access

```bash
# Check CloudTrail for suspicious access
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=ResourceName,AttributeValue=averta/production/database \
    --start-time $(date -d '24 hours ago' -u +%Y-%m-%dT%H:%M:%SZ) \
    --max-results 50
```

### 4. Notify Stakeholders

- Security team
- Engineering lead
- Compliance (if required)

### 5. Post-Incident

- Document timeline
- Rotate ALL secrets (not just compromised)
- Review access controls
- Update incident response plan

---

## Testing Rotation in Staging

### Monthly Rotation Drill

```bash
#!/bin/bash
# rotation-drill.sh - Run monthly in staging

set -e

echo "=== Starting Monthly Rotation Drill ==="

# 1. Rotate database (automatic - just trigger)
echo "Triggering database rotation..."
aws secretsmanager rotate-secret --secret-id averta/staging/database

# 2. Wait for rotation to complete
echo "Waiting for rotation..."
sleep 60

# 3. Verify application still works
echo "Testing application connectivity..."
curl -f https://staging.averta.com.br/api/v1/health || exit 1

# 4. Rotate JWT keys (with grace period)
echo "Rotating JWT keys..."
NEW_SK=$(openssl rand -base64 32)
NEW_RSK=$(openssl rand -base64 32)
aws secretsmanager get-secret-value --secret-id averta/staging/jwt --query SecretString --output text \
  | jq --arg sk "$NEW_SK" --arg rsk "$NEW_RSK" '.secret_key=$sk | .refresh_secret_key=$rsk' \
  | aws secretsmanager put-secret-value --secret-id averta/staging/jwt --secret-string file:///dev/stdin

# 5. Redeploy staging
echo "Redeploying staging..."
gh workflow run deploy.yml -f environment=staging

# 6. Wait and verify
sleep 120
curl -f https://staging.averta.com.br/api/v1/health || exit 1

echo "=== Rotation Drill Complete ==="
```

### Verify Application Resilience

Test these scenarios:
- [ ] Database connection recovery after password change
- [ ] Token validation with new JWT key
- [ ] Token refresh with old refresh token + new key
- [ ] Celery worker reconnection to Redis
- [ ] File upload to MinIO with new credentials

---

## Monitoring & Alerts

### CloudWatch Alarms

| Alarm | Condition | Action |
|-------|-----------|--------|
| `SecretRotationFailed` | Rotation Lambda returns error | PagerDuty + Slack |
| `SecretAccessAnomaly` | Unusual access patterns (CloudTrail) | Security team |
| `SecretNearExpiry` | Secret not rotated in > 35 days (DB) | Platform team |

### Dashboard Metrics

- Secret rotation success rate
- Time since last rotation per secret
- Application auth error rate post-rotation
- Deployment success rate after secret updates

---

## Access Control

### IAM Policies

| Role | Permissions |
|------|-------------|
| `ECS Task Role` | `secretsmanager:GetSecretValue` on `averta/{env}/*` |
| `GitHub Actions Deploy` | `secretsmanager:GetSecretValue`, `ListSecrets` on `averta/{env}/*` |
| `Developer (Staging)` | `secretsmanager:GetSecretValue` on `averta/staging/*` |
| `Platform Admin` | Full access to all secrets |

### Audit Logging

All secret access logged to CloudTrail → S3 (`avertasaas-{env}-cloudtrail-logs`)

Query example:
```bash
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=GetSecretValue \
    --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## Compliance

### Standards Met

- **SOC 2 Type II**: Automated rotation, audit logging, least privilege
- **ISO 27001**: A.9.2.3 (Secret management), A.12.4.1 (Event logging)
- **PCI DSS**: Requirement 3 (Protect stored cardholder data - encryption), Requirement 8 (Identify and authenticate)

### Evidence for Auditors

- Terraform state showing secret configuration
- CloudTrail logs showing access
- Rotation Lambda execution logs
- This runbook with last execution dates

---

## Quick Reference

### Useful Commands

```bash
# List all secrets
aws secretsmanager list-secrets --filters Key=Name,Values=averta

# Get secret metadata
aws secretsmanager describe-secret --secret-id averta/production/database

# Get secret value (requires permission)
aws secretsmanager get-secret-value --secret-id averta/production/jwt --query SecretString --output text | jq .

# Check rotation status
aws secretsmanager describe-secret --secret-id averta/production/database --query 'RotationEnabled,LastRotatedDate,RotationRules'

# Force rotation
aws secretsmanager rotate-secret --secret-id averta/production/database

# Get previous version (for rollback)
aws secretsmanager get-secret-value --secret-id averta/production/jwt --version-stage AWSPREVIOUS
```

### Environment Variables for Local Dev

```bash
# Enable AWS Secrets Manager in local dev
export AWS_SECRETS_MANAGER_ENABLED=true
export AWS_SECRETS_MANAGER_PREFIX=averta
export AWS_SECRETS_MANAGER_ENVIRONMENT=staging
export AWS_REGION=us-east-1
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-11 | Infra Agent | Initial creation |

---

*This runbook should be reviewed and tested quarterly. Update after any rotation procedure changes.*