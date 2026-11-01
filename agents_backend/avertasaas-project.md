---
name: averta-saas-project
description: AvertaSaaS - Freight Audit SaaS with success-based billing
metadata:
  node_type: memory
  type: project
  originSessionId: bd960958-7f5e-4119-a441-16b5237b7edc
  modified: 2026-11-01T14:20:40.590Z
---

# AvertaSaaS - Freight Audit SaaS

**Purpose**: B2B platform for automated freight invoice auditing (CT-e/NF-e) with success-fee billing model.

## Backend Stack (Complete)
- **Framework**: FastAPI 0.109 (async Python)
- **ORM**: Prisma Client Python with PostgreSQL 16
- **Cache/Queue**: Redis 7 + Celery 5 (workers + beat)
- **Storage**: MinIO/S3 for XML/PDF documents
- **Auth**: JWT (access 15min + refresh 7d) + RBAC
- **Multi-tenancy**: Company isolation via `company_id` on all models
- **API Prefix**: `/api/v1`

## Core Domain Models (25 Prisma models)
- **Auth**: User, RefreshToken (roles: ADMIN, MANAGER, AUDITOR, CLIENT)
- **Entities**: Company, Client, Carrier, Branch
- **Contracts**: Contract + FreightTable (versioned, date-ranged rules)
- **Documents**: Document (CT-e/NF-e) with parsed XML data
- **Discrepancies**: 17 rule types detecting overcharges
- **Contests**: Contest + Items + Communications + Payments (workflow: DRAFT→SENT→ACKNOWLEDGED→NEGOTIATING→ACCEPTED/PARTIAL/REJECTED)
- **Reports**: Dashboard KPIs, Recovery, Success Fee, Discrepancy stats
- **Notifications**: In-app + Email with preferences

## Rules Engine v2 (17 Rules)
ICMS_DIFAL, ICMS_FCP, ICMS_ST, FRETE_PESO_VALOR, FRETE_CUBAGE, PESO_REAL_VS_FATURADO, VALOR_MINIMO_FRETE, REDESPACHO_VALIDACAO, PEDAGIO_CONFERENCIA, AD_VALOREM, GRIS, SICOBAN_TABLE_REAL, CTE_ANULACAO, CTE_SUBSTITUICAO, CTE_COMPLEMENTO_VALOR, COMPLEMENTARY_CTE

## Key API Endpoints
- `POST /api/v1/auth/login` - JWT auth
- `GET /api/v1/companies/me` - Current company
- `GET/POST /api/v1/clients` - Client CRUD
- `GET/POST /api/v1/carriers` - Carrier CRUD
- `GET/POST /api/v1/contracts` - Contracts + Freight Tables
- `POST /api/v1/documents/upload` - XML upload (multipart)
- `GET /api/v1/discrepancies` - List with filters + summary
- `GET /api/v1/contests` - Full contest workflow + PDF generation
- `GET /api/v1/reports/dashboard` - Main KPIs
- `GET /api/v1/notifications` - In-app notifications

## Frontend Requirements (To Build)
- React 18 + TypeScript + Vite
- TanStack Query for server state
- React Router v6
- Tailwind CSS + shadcn/ui components
- JWT auth with refresh token handling
- Role-based UI (ADMIN/MANAGER/AUDITOR/CLIENT)
- Dashboards with charts (Recharts)
- File upload (XML drag-drop)
- PDF viewing for contest letters
- Export to Excel/PDF

## Dev Environment
- Backend: `cd backend && poetry run start` (port 8000)
- Frontend: Will be at `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

**Why**: Need persistent context for this multi-session project.
**How to apply**: Reference this memory when working on AvertaSaaS frontend/backend.