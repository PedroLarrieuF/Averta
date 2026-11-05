# Card #05 - Monitoring & Observability Stack

## Overview
Implement comprehensive monitoring, logging, and observability stack for production operations. Choose between CloudWatch-native or Grafana stack.

## Priority: MEDIUM
## Estimate: L (Large)

## Current State
- Basic CloudWatch logs from ECS (if deployed)
- No centralized logging, metrics, or tracing
- No alerting or dashboards
- No synthetic monitoring

## Required Work

### 1. Stack Selection
- [ ] **Option A: CloudWatch + X-Ray** (AWS-native, lower cost, less features)
- [ ] **Option B: Grafana + Loki + Tempo + Prometheus** (full-featured, higher cost)
- [ ] **Option C: DataDog** (SaaS, easiest, highest cost)
- [ ] Decision: **CloudWatch + X-Ray** (start) → migrate to Grafana if needed
- [ ] Document decision in ADR

### 2. Centralized Logging
- [ ] Configure ECS log driver: `awslogs` → CloudWatch Logs
- [ ] Create log groups: `/ecs/backend`, `/ecs/celery-worker`, `/ecs/celery-beat`, `/ecs/nginx`
- [ ] Set retention: 30 days hot, 1 year cold (S3 export)
- [ ] Add structured JSON logging to backend (structlog)
- [ ] Include: trace_id, span_id, user_id, company_id in all logs
- [ ] Create metric filters for: ERROR, WARN, slow queries, rate limits

### 3. Metrics Collection
- [ ] **RED Metrics (Request/Error/Duration)** per endpoint:
  - Rate: requests/second
  - Errors: 5xx rate, 4xx rate
  - Duration: p50, p95, p99 latency
- [ ] **USE Metrics (Utilization/Saturation/Errors)** per resource:
  - CPU, Memory, Disk, Network
  - RDS: connections, CPU, IOPS, replication lag
  - ElastiCache: CPU, memory, evictions, hit rate
  - ALB: target response time, healthy hosts
  - Celery: queue depth, task latency, worker count
- [ ] Custom metrics: documents processed, discrepancies found, contests created

### 4. Distributed Tracing (X-Ray)
- [ ] Enable X-Ray daemon in ECS tasks
- [ ] Instrument FastAPI with `aws-xray-sdk`
- [ ] Trace: HTTP requests, DB queries, Redis ops, Celery tasks
- [ ] Add annotations: user_id, company_id, document_id
- [ ] Configure sampling: 10% base, 100% errors

### 5. Dashboards
- [ ] **API Overview**: RED metrics, top endpoints, error breakdown
- [ ] **Database**: Connections, query latency, slow queries, replication lag
- [ ] **Cache**: Hit rate, memory, CPU, evictions
- [ ] **Queue**: Depth, processing rate, latency, failed tasks
- [ ] **Business**: Documents/day, Discrepancies/day, Contests/week, Revenue
- [ ] **Infrastructure**: ECS CPU/Memory, ALB targets, Costs

### 6. Alerting
- [ ] **Critical (PagerDuty + Slack)**:
  - API 5xx rate > 1% for 5min
  - API p99 latency > 2s for 5min
  - RDS CPU > 80% for 10min
  - RDS connections > 80% max
  - Celery queue depth > 1000 for 10min
  - Celery worker count < desired for 5min
  - Disk space > 85%
- [ ] **Warning (Slack only)**:
  - API 4xx rate > 5% for 10min
  - Cache hit rate < 90%
  - Backup job failed
  - SSL cert expiry < 30 days
- [ ] Alert routing: critical → PagerDuty, warning → Slack #infra-alerts

### 7. Synthetic Monitoring
- [ ] CloudWatch Canaries or external (Pingdom, Better Uptime)
- [ ] Canaries: health endpoint, auth login, document upload, report generation
- [ ] Run every 5 minutes from 3 regions
- [ ] Alert on 2/3 regions failing

### 8. Log Retention & Compliance
- [ ] Export CloudWatch logs to S3 (daily)
- [ ] S3 lifecycle: 1 year standard, 7 years Glacier
- [ ] Encrypt exports with KMS
- [ ] Audit log access (CloudTrail)

## Acceptance Criteria
- [ ] All logs centralized in CloudWatch with 30-day retention
- [ ] RED/USE metrics visible in dashboards
- [ ] X-Ray traces available for sampled requests
- [ ] Critical alerts firing correctly (tested)
- [ ] Synthetic canaries running and alerting
- [ ] Log export to S3 verified

## Files to Create/Modify
- `backend/app/core/logging.py` (structured logging with structlog)
- `backend/app/core/tracing.py` (X-Ray instrumentation)
- `infra/modules/monitoring/` (Terraform module)
- `.github/workflows/monitoring-test.yml` (alert testing)

## Dependencies
- Card #04 (AWS Infrastructure) for CloudWatch, X-Ray, SNS
- Card #01 (Docker Hardening) for X-Ray daemon sidecar

## Notes
- X-Ray sampling rule example:
  ```json
  {
    "RuleName": "AvertaSampling",
    "Priority": 100,
    "FixedRate": 0.1,
    "ReservoirSize": 5,
    "ServiceName": "averta-backend",
    "ServiceType": "AWS::ECS::Service"
  }
  ```
- Structlog config for JSON + trace context:
  ```python
  structlog.configure(
      processors=[
          structlog.stdlib.add_log_level,
          structlog.processors.TimeStamper(fmt="iso"),
          structlog.processors.JSONRenderer()
      ],
      context_class=dict,
      logger_factory=structlog.stdlib.LoggerFactory(),
      wrapper_class=structlog.stdlib.BoundLogger,
  )
  ```