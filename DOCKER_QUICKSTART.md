# AvertaSaaS - Docker Quick Start

Complete Docker setup for local development with all services and pre-populated database.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop / Docker Engine 24+
- Docker Compose v2+

### 1. Configure Environment (Optional)
```bash
# Copy the template and customize if needed
cp .env.docker .env
# Edit .env with your custom values
```

### 2. Start All Services
```bash
# Start with environment file
docker compose --env-file .env.docker up -d

# Or without env file (uses defaults)
docker compose up -d
```

### 3. Verify Services
```bash
# Check all containers are running
docker compose ps

# Follow backend logs
docker compose logs -f backend

# Check backend health
curl http://localhost:8000/health
```

### 4. Access Services
| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | - |
| **API Docs (Swagger)** | http://localhost:8000/docs | - |
| **Flower (Celery Monitor)** | http://localhost:5555 | admin/admin |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin |
| **Mailhog (Email UI)** | http://localhost:8025 | - |
| **PostgreSQL** | localhost:5432 | postgres/postgres (db: averta) |
| **Redis** | localhost:6379 | - |
| **PgBouncer** | localhost:6432 | postgres/postgres (db: averta) |

### 5. Default Login
- **Email:** `admin@admin`
- **Password:** `admin`

## 📖 Quick Start Variants

| Document | Use Case |
|----------|----------|
| **This file (DOCKER_QUICKSTART.md)** | Full Docker stack for local development |
| **QUICKSTART_CLIENT_DEMO.md** | Client demo with pre-populated data in <10 min |

## 📦 What's Included

### Infrastructure
- **PostgreSQL 16** - Primary database with extensions (uuid-ossp, pgcrypto, pg_trgm)
- **PgBouncer** - Connection pooling (transaction mode, port 6432)
- **Redis 7** - Cache & Celery broker
- **MinIO** - S3-compatible object storage (port 9000/9001)
- **Mailhog** - Email testing (SMTP 1025, UI 8025)

### Application
- **Backend** - FastAPI on port 8000 (with hot reload)
- **Celery Worker** - Background task processing (4 concurrent)
- **Celery Beat** - Periodic task scheduler
- **Flower** - Celery monitoring dashboard

### Database Population
On first startup, the backend automatically:
1. Runs Prisma migrations
2. Seeds database with comprehensive test data:
   - Admin user (admin@admin / admin)
   - 5 companies with full hierarchy
   - Clients, carriers, branches per company
   - Contracts with freight tables
   - Documents (CTe, NFe) with discrepancies
   - Contests with items, communications, payments
   - 35 validation rules (17 CTe + 18 NFe)
   - Notifications and audit logs

## 🔧 Common Commands

```bash
# Stop all services
docker compose down

# Stop and remove volumes (clean slate - data will be reseeded)
docker compose down -v

# Rebuild images
docker compose build --no-cache

# Shell into backend
docker compose exec backend bash

# Run Prisma commands
docker compose exec backend npx prisma studio
docker compose exec backend npx prisma migrate dev

# Run seed manually
docker compose exec backend python prisma/seed.py

# View logs
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f postgres
```

## 🔄 Resetting Database

To completely reset and reseed:
```bash
docker compose down -v
docker compose --env-file .env.docker up -d
```

## 📁 Project Structure

```
.
├── docker-compose.yml          # Main compose file (all services)
├── .env.docker                 # Environment template
├── backend/
│   ├── Dockerfile              # Multi-stage build (builder → distroless)
│   ├── scripts/
│   │   └── init-db.sh          # DB initialization (migrate + seed)
│   ├── init-scripts/
│   │   └── 01-init-extensions.sql  # PostgreSQL extensions
│   ├── prisma/
│   │   ├── schema.prisma       # Database schema
│   │   └── seed.py             # Comprehensive seed script
│   └── app/                    # Application code
```

## 🛠️ Development Notes

### Hot Reload
The backend uses the **builder stage** of the Dockerfile which includes:
- Full shell access
- Poetry with dev dependencies
- Hot reload via `--reload` flag
- Volume mounts for live code changes

### Production Build
For production, use the **runtime stage** (distroless):
```bash
docker build --target runtime -t averta/backend:prod ./backend
```

### Database Connection
- **Direct:** `postgresql://postgres:postgres@localhost:5432/averta`
- **Via PgBouncer:** `postgresql://postgres:postgres@localhost:6432/averta`

### Environment Variables
Key variables (see `.env.docker` for all):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_BUCKET`
- `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`
- `REDIS_PASSWORD` (optional)
- `SENDGRID_API_KEY` (optional)

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Common issues:
# 1. Database not ready - wait for healthcheck
# 2. Migration failed - check prisma/schema.prisma
# 3. Port conflicts - ensure 8000, 5432, 6379, 9000 free
```

### Database not seeded
```bash
# Check if init script ran
docker compose exec backend ls -la /app/scripts/

# Run manually
docker compose exec backend /app/scripts/init-db.sh
```

### Permission issues
```bash
# Fix script permissions
chmod +x backend/scripts/init-db.sh
```

## 📝 License
Proprietary - Averta Auditoria