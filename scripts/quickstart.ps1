<#
.SYNOPSIS
    Averta SaaS - Quickstarter para Windows
    Inicializa toda a stack de desenvolvimento: Infra (Docker) + Backend (Poetry) + Frontend (Vite)

.DESCRIPTION
    Este script configura e inicia todo o ambiente de desenvolvimento do Averta SaaS.
    Arquitetura: Infraestrutura (PostgreSQL, Redis, MinIO, Mailhog) em Docker.
    Aplicação (Backend FastAPI + Celery + Frontend React) roda localmente via Poetry/pnpm.

.EXAMPLE
    .\scripts\quickstart.ps1
#>

param(
    [switch]$SkipInfra,
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"

# Cores
$Red = "$([char]27)[31m"
$Green = "$([char]27)[32m"
$Yellow = "$([char]27)[33m"
$Blue = "$([char]27)[34m"
$Reset = "$([char]27)[0m"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "${Blue}╔══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║          Averta SaaS - Quickstarter v1.0.0 (Windows)         ║${Reset}"
Write-Host "${Blue}║     Infra Docker + Backend Local + Frontend Local            ║${Reset}"
Write-Host "${Blue}╚══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""

# Função para verificar comando
function Check-Command {
    param($Command, $Name)
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        Write-Host "${Red}✗ $Name não encontrado. Instale antes de continuar.${Reset}"
        exit 1
    }
    Write-Host "${Green}✓ $Name encontrado${Reset}"
}

# Verificar pré-requisitos
Write-Host "${Yellow}🔍 Verificando pré-requisitos...${Reset}"
Check-Command "docker" "Docker"
Check-Command "docker compose" "Docker Compose"
Check-Command "node" "Node.js"
Check-Command "pnpm" "pnpm"
Check-Command "poetry" "Poetry"
Check-Command "openssl" "OpenSSL"
Write-Host ""

# Verificar se Docker está rodando
try {
    docker info | Out-Null
    Write-Host "${Green}✓ Docker rodando${Reset}"
} catch {
    Write-Host "${Red}✗ Docker não está rodando. Inicie o Docker Desktop.${Reset}"
    exit 1
}
Write-Host ""

if (-not $SkipInfra) {
    # 1. Subir infraestrutura
    Write-Host "${Yellow}📦 [1/5] Subindo infraestrutura (PostgreSQL, Redis, MinIO, Mailhog)...${Reset}"
    Set-Location $ProjectRoot

    $containers = docker compose ps --format "table {{.Status}}" | Select-Object -Skip 1
    if ($containers -match "Up") {
        Write-Host "${Green}✓ Infraestrutura já está rodando${Reset}"
    } else {
        docker compose up -d
        Write-Host "${Green}✓ Infraestrutura iniciada${Reset}"
    }
    Write-Host ""

    # 2. Aguardar serviços ficarem healthy
    Write-Host "${Yellow}⏳ [2/5] Aguardando serviços ficarem prontos...${Reset}"
    Start-Sleep -Seconds 5

    # Verificar PostgreSQL
    for ($i = 1; $i -le 30; $i++) {
        try {
            docker compose exec -T postgres pg_isready -U postgres | Out-Null
            Write-Host "${Green}✓ PostgreSQL pronto${Reset}"
            break
        } catch {
            if ($i -eq 30) {
                Write-Host "${Red}✗ PostgreSQL não ficou pronto a tempo${Reset}"
                exit 1
            }
            Start-Sleep -Seconds 1
        }
    }

    # Verificar Redis
    for ($i = 1; $i -le 10; $i++) {
        try {
            docker compose exec -T redis redis-cli ping | Out-Null
            Write-Host "${Green}✓ Redis pronto${Reset}"
            break
        } catch {
            if ($i -eq 10) {
                Write-Host "${Red}✗ Redis não ficou pronto a tempo${Reset}"
                exit 1
            }
            Start-Sleep -Seconds 1
        }
    }

    # Verificar MinIO
    for ($i = 1; $i -le 15; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -Method Head -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "${Green}✓ MinIO pronto${Reset}"
                break
            }
        } catch {
            if ($i -eq 15) {
                Write-Host "${Red}✗ MinIO não ficou pronto a tempo${Reset}"
                exit 1
            }
            Start-Sleep -Seconds 1
        }
    }
    Write-Host ""
}

if (-not $SkipBackend) {
    # 3. Configurar e iniciar Backend
    Write-Host "${Yellow}🐍 [3/5] Configurando Backend (Poetry)...${Reset}"
    Set-Location $BackendDir

    # Verificar .env
    if (-not (Test-Path ".env")) {
        Write-Host "${Yellow}⚠ .env não encontrado, copiando de .env.example${Reset}"
        Copy-Item ".env.example" ".env"
        Write-Host "${Red}⚠ IMPORTANTE: Edite o arquivo .env com suas chaves:${Reset}"
        Write-Host "${Yellow}   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta${Reset}"
        Write-Host "${Yellow}   REDIS_URL=redis://localhost:6379/0${Reset}"
        Write-Host "${Yellow}   S3_ENDPOINT=http://localhost:9000${Reset}"
        Write-Host "${Yellow}   JWT_SECRET_KEY=... (gere com: openssl rand -base64 32)${Reset}"
        Read-Host "Pressione Enter após editar o .env..."
    }

    # Instalar dependências se necessário
    if (-not (Test-Path ".venv") -and -not (Test-Path "venv")) {
        Write-Host "${Yellow}📥 Instalando dependências Poetry...${Reset}"
        poetry install --with dev
    }

    # Gerar Prisma Client
    Write-Host "${Yellow}🔧 Gerando Prisma Client...${Reset}"
    poetry run prisma generate

    # Aplicar migrations
    Write-Host "${Yellow}🗄️ Aplicando migrations...${Reset}"
    poetry run prisma migrate deploy

    Write-Host "${Green}✓ Backend configurado${Reset}"
    Write-Host ""
}

if (-not $SkipFrontend) {
    # 4. Configurar Frontend
    Write-Host "${Yellow}⚛️  [4/5] Configurando Frontend (pnpm)...${Reset}"
    Set-Location $FrontendDir

    if (-not (Test-Path "node_modules")) {
        Write-Host "${Yellow}📥 Instalando dependências pnpm...${Reset}"
        pnpm install
    }

    Write-Host "${Green}✓ Frontend configurado${Reset}"
    Write-Host ""
}

# 5. Instruções finais
Write-Host "${Blue}╔══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║                    ✅ SETUP CONCLUÍDO!                        ║${Reset}"
Write-Host "${Blue}╚══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""
Write-Host "${Green}Agora abra 4 terminais (PowerShell) e execute:${Reset}"
Write-Host ""
Write-Host "${Yellow}Terminal 1 - Backend API (porta 8000):${Reset}"
Write-Host "  cd $BackendDir; poetry run start"
Write-Host ""
Write-Host "${Yellow}Terminal 2 - Celery Worker:${Reset}"
Write-Host "  cd $BackendDir; poetry run worker"
Write-Host ""
Write-Host "${Yellow}Terminal 3 - Celery Beat:${Reset}"
Write-Host "  cd $BackendDir; poetry run beat"
Write-Host ""
Write-Host "${Yellow}Terminal 4 - Frontend (porta 3000):${Reset}"
Write-Host "  cd $FrontendDir; pnpm dev"
Write-Host ""
Write-Host "${Blue}📋 URLs de Acesso:${Reset}"
Write-Host "  Frontend:        http://localhost:3000"
Write-Host "  Backend API:     http://localhost:8000"
Write-Host "  Swagger Docs:    http://localhost:8000/docs"
Write-Host "  MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
Write-Host "  Mailhog UI:      http://localhost:8025"
Write-Host "  Prisma Studio:   cd $BackendDir; poetry run prisma studio"
Write-Host "  Flower:          cd $BackendDir; poetry run flower"
Write-Host ""
Write-Host "${Yellow}💡 Dica: Use 'wt' (Windows Terminal) com abas para gerenciar múltiplos terminais.${Reset}"
Write-Host ""