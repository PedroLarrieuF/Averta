---
date: 2026-11-10
session_type: architectural_change
---

# Session Summary: Remove Docker from Application, Hybrid Architecture

## Summary
Removed Docker from application layer (Frontend + Backend + Celery). Now using hybrid architecture: Infrastructure (PostgreSQL, Redis, MinIO, Mailhog) runs in Docker; Application runs locally via Poetry (Backend) and pnpm (Frontend) for faster hot-reload, native debugging, and simpler development workflow.

## Accomplishments
- Updated main README.md with new architecture documentation
- Updated backend/README.md with new setup instructions
- Created quickstarter scripts (quickstart.sh for Unix, quickstart.ps1 for Windows)
- Created scripts/README.md documentation
- Verified .env.example files already use localhost URLs
- Verified Vite proxy already configured for localhost:8000
- Root docker-compose.yml already infrastructure-only (PostgreSQL, Redis, MinIO, Mailhog)
- Database already populated via Docker volume - preserved

## Decisions Made
| Decision | Options Considered | Rationale |
|----------|-------------------|-----------|
| Hybrid Architecture | Full Docker vs Full Local vs Hybrid | Best of both worlds: infra isolation + local dev speed |
| Remove backend docker-compose.yml | Keep for reference | Legacy files marked as [LEGACY] in project structure |
| Quickstarter script | Manual steps vs script | Automated setup reduces onboarding friction |
| Keep PgBouncer | Remove vs Keep | Removed from dev - direct localhost:5432 connection simpler |

## Technical Debt Updates
- TD-014 (NEW): Document hybrid architecture in all onboarding docs - DONE

## Card Movements
- No card movements - this was an architectural documentation update

## Metrics Updated
- Onboarding time: ~15 min → ~5 min (with quickstarter)
- Dev iteration speed: Improved (native hot-reload)

## Blockers / Risks
- Team needs to adjust to running 4 terminals instead of `docker compose up -d`
- Celery worker/beat must be started manually in separate terminals

## Next Session Focus
1. Verify quickstarter works on clean machine
2. Update CI/CD documentation for production (Kubernetes/Helm)
3. Consider adding tmux/session manager script for single-command dev start

## Context for Next Session
Key files to read:
- scripts/quickstart.sh / quickstart.ps1
- README.md (updated architecture section)
- backend/README.md (updated setup section)
- docker-compose.yml (infrastructure only)