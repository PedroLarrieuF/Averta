# Card #03 - Database Backup & Restore Strategy

## Overview
Implement comprehensive database backup and restore strategy with defined RPO/RTO, automated backups, point-in-time recovery, and tested restore procedures.

## Priority: HIGH
## Estimate: M (Medium)

## Current State
- PostgreSQL 16 in Docker (local) / RDS (future)
- No automated backup strategy
- No point-in-time recovery configured
- No restore runbooks or tested procedures

## Required Work

### 1. Define RPO/RTO
- [ ] **RPO (Recovery Point Objective): 1 hour** - Maximum data loss acceptable
- [ ] **RTO (Recovery Time Objective): 4 hours** - Maximum downtime acceptable
- [ ] Document per service tier (critical: documents, discrepancies, contests)
- [ ] Get stakeholder sign-off on RPO/RTO

### 2. Automated Daily Backups
- [ ] Create backup script using `pg_dump` with:
  - `--format=custom` (compressed, parallel restore)
  - `--jobs=4` (parallel dump)
  - `--no-owner --no-privileges` (portable restore)
  - Schema + data separation option
- [ ] Schedule daily at 02:00 UTC (low traffic)
- [ ] Upload to S3 with lifecycle policy:
  - Daily: 30 days
  - Weekly: 12 weeks
  - Monthly: 12 months
  - Yearly: 7 years (compliance)
- [ ] Encrypt backups with KMS (SSE-KMS)

### 3. Point-in-Time Recovery (PITR)
- [ ] Enable WAL archiving: `archive_mode=on`, `archive_command='aws s3 cp %p s3://bucket/wals/%f'`
- [ ] Configure `wal_level=replica`, `max_wal_senders=10`
- [ ] Set up continuous base backup (pg_basebackup) weekly
- [ ] Document PITR restore procedure to any second

### 4. Cross-Region Replication
- [ ] Enable S3 Cross-Region Replication (CRR) to DR region
- [ ] Replicate: daily backups, WAL archives, base backups
- [ ] Verify replication latency < 15 minutes
- [ ] Test restore from DR region

### 5. Restore Runbooks
- [ ] **Full Restore Runbook**: From latest daily + WAL replay
- [ ] **Point-in-Time Restore Runbook**: To specific timestamp
- [ ] **Table-Level Restore Runbook**: Single table recovery
- [ ] **Schema-Only Restore Runbook**: For migration rollback
- [ ] Include: prerequisites, steps, validation queries, rollback plan

### 6. Backup Verification
- [ ] Weekly automated test restore to staging
- [ ] Verify: row counts, checksums, foreign key integrity
- [ ] Alert on verification failure
- [ ] Monthly full DR drill (simulated region loss)

### 7. Backup Monitoring & Alerts
- [ ] Monitor: backup job success/failure
- [ ] Monitor: backup size trends (detect anomalies)
- [ ] Monitor: WAL archive lag
- [ ] Monitor: S3 replication status
- [ ] Alert channels: Slack #infra-alerts, PagerDuty critical

### 8. Retention & Compliance
- [ ] Implement retention policy enforcement (lifecycle rules)
- [ ] Document data classification per table
- [ ] Ensure LGPD compliance (Brazilian data protection)
- [ ] Add backup audit trail (who restored when)

## Acceptance Criteria
- [ ] Daily backups running automatically for 7 consecutive days
- [ ] Test restore from backup completes in <2 hours (RTO)
- [ ] PITR tested to 5-minute granularity
- [ ] Cross-region replication verified
- [ ] Runbooks documented and reviewed
- [ ] Monitoring alerts configured and tested

## Files to Create/Modify
- `backend/scripts/backup.sh` (new)
- `backend/scripts/restore.sh` (new)
- `backend/scripts/verify_backup.sh` (new)
- `infra/modules/rds/backup.tf` (new - Terraform)
- `infra/modules/s3/backup_replication.tf` (new - Terraform)
- `.github/workflows/backup-verification.yml` (new)
- `docs/runbooks/db-restore.md` (new)

## Dependencies
- Card #04 (AWS Infrastructure) for S3, RDS, KMS
- Card #06 (Secrets Management) for backup encryption keys

## Notes
- pg_dump command template:
  ```bash
  pg_dump -h $PGHOST -U $PGUSER -d $PGDATABASE \
    --format=custom --jobs=4 --no-owner --no-privileges \
    --file=/tmp/backup_$(date +%Y%m%d_%H%M%S).dump
  ```
- Restore command:
  ```bash
  pg_restore -h $PGHOST -U $PGUSER -d $PGDATABASE \
    --jobs=4 --no-owner --no-privileges \
    /path/to/backup.dump
  ```
- PITR: `recovery_target_time = '2026-11-05 14:30:00'` in recovery.signal
- LGPD: Personal data in `User`, `Client`, `Carrier` tables - ensure encryption at rest