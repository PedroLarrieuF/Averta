<#
.SYNOPSIS
    Averta SaaS - Quickstarter para Windows
    Inicializa toda a stack de desenvolvimento: Infra (Docker) + Backend (Poetry) + Frontend (Vite)

.DESCRIPTION
    Este script configura e inicia todo o ambiente de desenvolvimento do Averta SaaS.
    Arquitetura: Infraestrutura (PostgreSQL, Redis, MinIO, Mailhog) em Docker.
    Aplicacao (Backend FastAPI + Celery + Frontend React) roda localmente via Poetry/pnpm.

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

Write-Host "${Blue}================================================================${Reset}"
Write-Host "${Blue}          Averta SaaS - Quickstarter v1.0.0 (Windows)           ${Reset}"
Write-Host "${Blue}     Infra Docker + Backend Local + Frontend Local              ${Reset}"
Write-Host "${Blue}================================================================${Reset}"
Write-Host ""

# Funcao para verificar comando
function Check-Command {
    param($Command, $Name)
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        Write-Host "${Red}[ERRO] $Name nao encontrado. Instale antes de continuar.${Reset}"
        exit 1
    }
    Write-Host "${Green}[OK] $Name encontrado${Reset}"
}

# Verificar pre-requisitos
Write-Host "${Yellow}[*] Verificando pre-requisitos...${Reset}"
Check-Command "docker" "Docker"

# Verificacao especifica para Docker Compose v2 (subcomando)
docker compose version *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "${Red}[ERRO] Docker Compose nao encontrado. Instale antes de continuar.${Reset}"
    exit 1
}
Write-Host "${Green}[OK] Docker Compose encontrado${Reset}"

Check-Command "node" "Node.js"
Check-Command "pnpm" "pnpm"
Check-Command "poetry" "Poetry"
Check-Command "openssl" "OpenSSL"
Write-Host ""

# Verificar se Docker esta rodando
try {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) { throw "Docker daemon offline" }
    Write-Host "${Green}[OK] Docker rodando${Reset}"
} catch {
    Write-Host "${Red}[ERRO] Docker nao esta rodando. Inicie o Docker Desktop.${Reset}"
    exit 1
}
Write-Host ""

if (-not $SkipInfra) {
    # 1. Subir infraestrutura
    Write-Host "${Yellow}[1/5] Subindo infraestrutura (PostgreSQL, Redis, MinIO, Mailhog)...${Reset}"
    Set-Location $ProjectRoot

    $containers = docker compose ps --format "table {{.Status}}" | Select-Object -Skip 1
    if ($containers -match "Up") {
        Write-Host "${Green}[OK] Infraestrutura ja esta rodando${Reset}"
    } else {
        docker compose up -d
        Write-Host "${Green}[OK] Infraestrutura iniciada${Reset}"
    }
    Write-Host ""

    # 2. Aguardar servicos ficarem healthy
    Write-Host "${Yellow}[2/5] Aguardando servicos ficarem prontos...${Reset}"
    Start-Sleep -Seconds 5

    # Verificar PostgreSQL
    for ($i = 1; $i -le 30; $i++) {
        try {
            docker compose exec -T postgres pg_isready -U postgres *> $null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "${Green}[OK] PostgreSQL pronto${Reset}"
                break
            }
            throw "Aguardando"
        } catch {
            if ($i -eq 30) {
                Write-Host "${Red}[ERRO] PostgreSQL nao ficou pronto a tempo${Reset}"
                exit 1
            }
            Start-Sleep -Seconds 1
        }
    }

    # Verificar Redis
    for ($i = 1; $i -le 10; $i++) {
        try {
            docker compose exec -T redis redis-cli ping *> $null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "${Green}[OK] Redis pronto${Reset}"
                break
            }
            throw "Aguardando"
        } catch {
            if ($i -eq 10) {
                Write-Host "${Red}[ERRO] Redis nao ficou pronto a tempo${Reset}"
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
                Write-Host "${Green}[OK] MinIO pronto${Reset}"
                break
            }
        } catch {
            if ($i -eq 15) {
                Write-Host "${Red}[ERRO] MinIO nao ficou pronto a tempo${Reset}"
                exit 1
            }
            Start-Sleep -Seconds 1
        }
    }
    Write-Host ""
}

if (-not $SkipBackend) {
    # 3. Configurar e iniciar Backend
    Write-Host "${Yellow}[3/5] Configurando Backend (Poetry)...${Reset}"
    Set-Location $BackendDir

    # Verificar .env
    if (-not (Test-Path ".env")) {
        Write-Host "${Yellow}[AVISO] .env nao encontrado, copiando de .env.example${Reset}"
        Copy-Item ".env.example" ".env"
        Write-Host "${Red}[IMPORTANTE] Edite o arquivo .env com suas chaves:${Reset}"
        Write-Host "${Yellow}   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta${Reset}"
        Write-Host "${Yellow}   REDIS_URL=redis://localhost:6379/0${Reset}"
        Write-Host "${Yellow}   S3_ENDPOINT=http://localhost:9000${Reset}"
        Write-Host "${Yellow}   JWT_SECRET_KEY=... (gere com: openssl rand -base64 32)${Reset}"
        Read-Host "Pressione Enter apos editar o .env..."
    }

    # Instalar dependencias se necessario
    if (-not (Test-Path ".venv") -and -not (Test-Path "venv")) {
        Write-Host "${Yellow}[*] Instalando dependencias Poetry...${Reset}"
        poetry install --with dev
    }

    # Gerar Prisma Client
    Write-Host "${Yellow}[*] Gerando Prisma Client...${Reset}"
    poetry run prisma generate

    # Aplicar migrations
    Write-Host "${Yellow}[*] Aplicando migrations...${Reset}"
    poetry run prisma migrate deploy

    Write-Host "${Green}[OK] Backend configurado${Reset}"
    Write-Host ""
}

if (-not $SkipFrontend) {
    # 4. Configurar Frontend
    Write-Host "${Yellow}[4/5] Configurando Frontend (pnpm)...${Reset}"
    Set-Location $FrontendDir

    if (-not (Test-Path "node_modules")) {
        Write-Host "${Yellow}[*] Instalando dependencias pnpm...${Reset}"
        pnpm install
    }

    Write-Host "${Green}[OK] Frontend configurado${Reset}"
    Write-Host ""
}

# 5. Instrucoes finais
Write-Host "${Blue}================================================================${Reset}"
Write-Host "${Blue}                     SETUP CONCLUIDO!                           ${Reset}"
Write-Host "${Blue}================================================================${Reset}"
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
Write-Host "${Blue}URLs de Acesso:${Reset}"
Write-Host "  Frontend:        http://localhost:3000"
Write-Host "  Backend API:     http://localhost:8000"
Write-Host "  Swagger Docs:    http://localhost:8000/docs"
Write-Host "  MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
Write-Host "  Mailhog UI:      http://localhost:8025"
Write-Host "  Prisma Studio:   cd $BackendDir; poetry run prisma studio"
Write-Host "  Flower:          cd $BackendDir; poetry run flower"
Write-Host ""
Write-Host "${Yellow}Dica: Use 'wt' (Windows Terminal) com abas para gerenciar multiplos terminais.${Reset}"
Write-Host ""
