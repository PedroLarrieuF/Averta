# Card #07 - Disaster Recovery Plan

## Overview
Define and implement comprehensive disaster recovery plan with documented RPO/RTO, cross-region failover, tested runbooks, and quarterly drills.

## Priority: MEDIUM
## Estimate: L (Large)

## Current State
- No DR plan documented
- No cross-region infrastructure
- No failover procedures
- No DR testing

## Required Work

### 1. RPO/RTO Definition (Per Service Tier)
- [ ] **Tier 1 - Critical (RPO: 1hr, RTO: 4hr)**:
  - Documents API (upload, process, retrieve)
  - Discrepancies API (list, review, bulk actions)
  - Contests API (create, negotiate, payments)
  - Database (PostgreSQL)
- [ ] **Tier 2 - Important (RPO: 4hr, RTO: 8hr)**:
  - Reports API (dashboard, export, schedules)
  - Settings API (company, users, carriers, contracts)
  - Redis Cache (session, rate limits, Celery broker)
- [ ] **Tier 3 - Standard (RPO: 24hr, RTO: 24hr)**:
  - Developer Portal (docs, keys, analytics)
  - MinIO/S3 (document storage)
  - Email notifications (SendGrid)
- [ ] Get business stakeholder sign-off

### 2. DR Architecture (Active-Passive)
- [ ] **Primary Region**: us-east-1 (N. Virginia)
- [ ] **DR Region**: us-west-2 (Oregon) - ~70ms latency
- [ ] **Data Replication**:
  - RDS: Cross-region read replica (async, ~1min lag)
  - ElastiCache: Global Datastore (cross-region replication)
  - S3: CRR (Cross-Region Replication) for all buckets
  - ECR: Cross-region replication for Docker images
- [ ] **Infrastructure as Code**: Terraform deployed to both regions
- [ ] **DNS Failover**: Route53 health checks + failover records

### 3. Failover Runbooks
- [ ] **Runbook 1: Database Failover (RDS)**
  - Detect: RDS unavailable, replica lag > 5min, manual trigger
  - Steps: Promote read replica, update DNS, verify connections
  - Validation: Write test record, read back, check replication
  - Rollback: Re-establish replication, demote old primary
- [ ] **Runbook 2: Full Region Failover**
  - Detect: ALB health checks failing, CloudWatch alarms, AWS status page
  - Steps: Update Route53 to DR ALB, scale DR ECS services, verify
  - Validation: Synthetic canaries, API smoke tests, business transaction
  - Communication: Status page, Slack, email stakeholders
- [ ] **Runbook 3: Partial Service Failure**
  - Redis failure: Fail to read replica, restart workers
  - S3 failure: CloudFront origin failover, direct S3 access
  - Celery failure: Scale workers, purge dead letter queues
- [ ] **Runbook 4: Data Corruption/Deletion**
  - Detect: Application errors, audit logs, user reports
  - Steps: PITR restore to clean point, verify integrity
  - Validation: Row counts, checksums, business logic tests

### 4. Failback Runbooks
- [ ] **Runbook 5: Database Failback**
  - Steps: Re-establish replication, sync, planned cutover
  - Validation: Zero data loss, replication healthy
- [ ] **Runbook 6: Full Region Failback**
  - Steps: Sync data, verify DR region caught up, planned cutover
  - Schedule: Low-traffic window, stakeholder notification

### 5. DR Testing Schedule
- [ ] **Quarterly**: Full region failover drill (simulated)
  - Schedule: 2 weeks notice, 4-hour maintenance window
  - Execute: Runbook 2, validate all Tier 1 services
  - Document: Actual RTO, issues found, action items
- [ ] **Monthly**: Component-level tests
  - Month 1: Database failover (Runbook 1)
  - Month 2: Redis failover (Runbook 3)
  - Month 3: S3/CloudFront failover
  - Rotate
- [ ] **Weekly**: Backup restore verification (Card #03)

### 6. Communication Plan
- [ ] **Internal**: Slack #incidents, PagerDuty, email on-call
- [ ] **Status Page**: status.averta.com.br (external)
- [ ] **Stakeholders**: Customer success, sales, leadership
- [ ] **Templates**: Incident declaration, update, resolution
- [ ] **Post-Incident**: Blameless postmortem within 48 hours

### 7. Infrastructure for DR
- [ ] Deploy Terraform to DR region (us-west-2)
- [ ] RDS cross-region read replica
- [ ] ElastiCache Global Datastore
- [ ] S3 CRR configuration
- [ ] ECR replication rules
- [ ] Route53 health checks + failover records
- [ ] ALB in DR region (scaled to 0, auto-scale on failover)
- [ ] ECS cluster in DR region (capacity reserved)

### 8. Compliance & Documentation
- [ ] DR Plan document (PDF, version controlled)
- [ ] Runbooks in Git (Markdown, reviewed quarterly)
- [ ] LGPD considerations: Data residency, breach notification
- [ ] Audit trail: All failover/failback events logged
- [ ] Insurance: Cyber insurance coverage verification

## Acceptance Criteria
- [ ] DR Plan document approved by leadership
- [ ] Cross-region infrastructure deployed and healthy
- [ ] All runbooks written and peer-reviewed
- [ ] First quarterly drill completed successfully
- [ ] Actual RTO measured and within targets
- [ ] Communication plan tested (status page update)
- [ ] Post-drill retrospective with action items

## Files to Create
- `docs/dr/dr-plan.md` (main plan)
- `docs/dr/runbooks/` (6 runbooks)
- `docs/dr/communication-plan.md`
- `infra/modules/dr/` (Terraform for DR region)
- `.github/workflows/dr-drill.yml` (scheduled drill trigger)

## Dependencies
- Card #03 (Database Backup) for PITR capability
- Card #04 (AWS Infrastructure) for primary region
- Card #05 (Monitoring) for detection/alerting
- Card #06 (Secrets Management) for secret replication

## Notes
- RDS Cross-Region Read Replica: ~$0.10/GB/month data transfer + replica cost
- ElastiCache Global Datastore: Additional cost for secondary cluster
- Route53 Failover: Health check every 10s, failover ~1-2min
- Test with `aws rds failover-db-cluster` for Aurora, or promote read replica for RDS
- LGPD: 72-hour breach notification - ensure DR plan includes notification procedures
- Cost estimate: DR region ~40% of primary (~$1,000/month for warm standby)