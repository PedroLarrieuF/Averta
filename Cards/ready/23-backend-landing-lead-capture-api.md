---
id: 23
title: "Backend — Lead Capture API Endpoint + Email Notification"
priority: high
type: feature
agent: backend
sprint: 1
estimate: S
status: ready
created: 2026-11-10
reviewed_by: techlead
---

## Description

Create the lead capture API endpoint for the landing page calculator and contact forms, with email notification to sales team.

## Acceptance Criteria

### API Endpoint
- [ ] POST `/api/v1/leads` (public, no auth required)
- [ ] Rate limiting: 10 req/min per IP (slowapi + Redis)
- [ ] Validation: Pydantic model with all fields from frontend spec
- [ ] Idempotency: deduplicate by email + source_section within 24h
- [ ] Response: 201 with `{ "lead_id": "uuid", "calendly_url": "string" }`

### Data Model (Prisma)
- [ ] New model `LandingLead`:
  ```prisma
  model LandingLead {
    id                    String   @id @default(uuid())
    name                  String
    email                 String
    phone                 String
    company               String
    monthlyFreightSpend   Decimal  @db.Decimal(15,2)
    monthlyCteVolume      Int
    estimatedErrorPct     Float
    pricingModel          PricingModel  // enum: PROGRESSIVE, FIXED
    preferredContactTime  ContactTime   // enum: MORNING, AFTERNOON, ANY
    source                String        // "landing_page"
    sourceSection         String        // "hero", "calculator", "rules", "how_it_works", "faq"
    utmSource             String?
    utmMedium             String?
    utmCampaign           String?
    utmContent            String?
    calculatorProjection  Json          // { monthlyRecovery, monthlyFeeM1, monthlyFeeM2, netM1, netM2, annualProjection }
    status                LeadStatus    @default(NEW)  // NEW, CONTACTED, QUALIFIED, CLOSED_WON, CLOSED_LOST
    createdAt             DateTime      @default(now())
    updatedAt             DateTime      @updatedAt
    
    @@index([email, createdAt])
    @@index([status])
    @@index([source])
  }
  ```

### Email Notification
- [ ] Send to sales team (configurable list) on new lead
- [ ] Template: lead details + calculator projection + Calendly link
- [ ] Subject: `[Averta Lead] {company} — R$ {monthly_recovery}/mês potencial`
- [ ] Async via Celery task (non-blocking)

### Calendly Integration
- [ ] Return Calendly booking URL in response
- [ ] URL includes pre-filled: name, email, company, utm params
- [ ] Configurable via env: `CALENDLY_URL_TEMPLATE`

### Admin Endpoints (Protected, ADMIN/MANAGER only)
- [ ] GET `/api/v1/leads` — paginated, filterable (status, date range, source)
- [ ] GET `/api/v1/leads/{id}` — detail
- [ ] PATCH `/api/v1/leads/{id}` — update status, notes
- [ ] GET `/api/v1/leads/export` — CSV export

### Testing
- [ ] Unit tests: validation, deduplication, projection calculations
- [ ] Integration test: full POST flow + email task enqueued
- [ ] Rate limit test

## Dependencies

- Prisma migration (run `prisma db push`)
- Celery + Redis configured (existing)
- Email service (existing: `app/services/email.py`)
- Slowapi rate limiter (Card 04 - must be done first)

## Configuration (env)
```env
LEADS_EMAIL_RECIPIENTS="sales@averta.com.br,comercial@averta.com.br"
CALENDLY_URL_TEMPLATE="https://calendly.com/averta-demo/30min?name={name}&email={email}&company={company}&utm_source={utm_source}&utm_medium={utm_medium}&utm_campaign={utm_campaign}"
LEAD_RATE_LIMIT="10/minute"
```

## Notes

- This endpoint is PUBLIC — no JWT auth. Rate limiting is critical.
- Deduplication prevents spam: same email + section within 24h returns existing lead_id
- Calculator projection stored as JSON for reporting/analytics
- Future: HubSpot/Salesforce sync via webhook or scheduled job