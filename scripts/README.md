# Scripts

Scripts de automação para o Averta SaaS.

## quickstart.sh / quickstart.ps1

Script principal para inicializar todo o ambiente de desenvolvimento.

### O que faz:
1. ✅ Verifica pré-requisitos (Docker, Node.js, pnpm, Poetry, OpenSSL)
2. ✅ Sobe infraestrutura via Docker Compose (PostgreSQL, Redis, MinIO, Mailhog)
3. ✅ Aguarda serviços ficarem healthy
4. ✅ Configura Backend (Poetry install, Prisma generate, migrations)
5. ✅ Configura Frontend (pnpm install)

### Uso:

**Linux/macOS/Git Bash:**
```bash
./scripts/quickstart.sh
```

**Windows PowerShell:**
```powershell
.\scripts\quickstart.ps1
```

### Opções (PowerShell):
```powershell
# Pular infraestrutura (se já estiver rodando)
.\scripts\quickstart.ps1 -SkipInfra

# Pular configuração do backend
.\scripts\quickstart.ps1 -SkipBackend

# Pular configuração do frontend
.\scripts\quickstart.ps1 -SkipFrontend
```

### Após o script:
Abra 4 terminais e execute:

```bash
# Terminal 1 - Backend API
cd backend && poetry run start

# Terminal 2 - Celery Worker
cd backend && poetry run worker

# Terminal 3 - Celery Beat
cd backend && poetry run beat

# Terminal 4 - Frontend
cd frontend && pnpm dev
```

### URLs:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- Mailhog: http://localhost:8025