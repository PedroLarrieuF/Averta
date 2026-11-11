<#
.SYNOPSIS
    Configura PostgreSQL local para desenvolvimento (fora do Docker)

.DESCRIPTION
    Este script instala e configura PostgreSQL 16 localmente no Windows,
    cria o banco 'averta', usuário 'postgres' e aplica as migrations.

.NOTES
    Requer: PostgreSQL 16 instalado (via winget/chocolatey/installer)
    Execute como Administrator para instalação via winget.
#>

param(
    [switch]$InstallPostgres,
    [switch]$CreateDatabase,
    [switch]$RunMigrations,
    [switch]$SeedData,
    [switch]$All
)

$ErrorActionPreference = "Stop"

$Red = "$([char]27)[31m"
$Green = "$([char]27)[32m"
$Yellow = "$([char]27)[33m"
$Blue = "$([char]27)[34m"
$Reset = "$([char]27)[0m"

Write-Host "${Blue}╔══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║     Averta SaaS - Setup PostgreSQL Local (Windows)           ║${Reset}"
Write-Host "${Blue}╚══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""

if ($All) {
    $InstallPostgres = $true
    $CreateDatabase = $true
    $RunMigrations = $true
    $SeedData = $true
}

# 1. Instalar PostgreSQL via winget
if ($InstallPostgres) {
    Write-Host "${Yellow}📦 [1/4] Instalando PostgreSQL 16 via winget...${Reset}"
    try {
        winget install --id PostgreSQL.PostgreSQL --version 16.4 --accept-source-agreements --accept-package-agreements
        Write-Host "${Green}✓ PostgreSQL instalado${Reset}"
    } catch {
        Write-Host "${Red}✗ Falha ao instalar. Tente manualmente: https://www.postgresql.org/download/windows/${Reset}"
    }
    Write-Host ""
}

# Verificar se PostgreSQL está instalado
$pgPath = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
if (-not (Test-Path $pgPath)) {
    Write-Host "${Yellow}⚠ PostgreSQL não encontrado em $pgPath${Reset}"
    Write-Host "${Yellow}   Instale manualmente ou use: .\scripts\setup-local-db.ps1 -InstallPostgres${Reset}"
    Write-Host ""
}

# 2. Criar banco e usuário
if ($CreateDatabase) {
    Write-Host "${Yellow}🗄️  [2/4] Criando banco de dados 'averta'...${Reset}"

    $env:PGPASSWORD = "postgres"

    try {
        # Verificar se cluster existe
        & "$pgPath" -U postgres -c "SELECT 1" -d postgres 2>$null
        Write-Host "${Green}✓ Cluster PostgreSQL já existe${Reset}"
    } catch {
        Write-Host "${Yellow}⚠ Cluster não encontrado. Inicializando...${Reset}"
        $dataDir = "C:\Program Files\PostgreSQL\16\data"
        if (-not (Test-Path $dataDir)) {
            & "C:\Program Files\PostgreSQL\16\bin\initdb.exe" -D $dataDir -U postgres -A scram-sha-256
            Write-Host "${Green}✓ Cluster inicializado${Reset}"
        }
    }

    # Criar banco
    try {
        & "$pgPath" -U postgres -c "CREATE DATABASE averta;" -d postgres 2>$null
        Write-Host "${Green}✓ Banco 'averta' criado${Reset}"
    } catch {
        Write-Host "${Yellow}⚠ Banco 'averta' já existe${Reset}"
    }

    # Criar extensões necessárias
    & "$pgPath" -U postgres -d averta -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
    & "$pgPath" -U postgres -d averta -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
    & "$pgPath" -U postgres -d averta -c "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";"
    Write-Host "${Green}✓ Extensões criadas${Reset}"
    Write-Host ""
}

# 3. Aplicar migrations
if ($RunMigrations) {
    Write-Host "${Yellow}🔄 [3/4] Aplicando migrations Prisma...${Reset}"
    Set-Location "D:\Averta\backend"

    # Verificar .env para localhost
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "${Yellow}⚠ .env criado a partir do .env.example${Reset}"
    }

    # Garantir DATABASE_URL para localhost
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta") {
        Write-Host "${Green}✓ DATABASE_URL já configurado para localhost${Reset}"
    } else {
        Write-Host "${Yellow}⚠ Atualizando DATABASE_URL para localhost...${Reset}"
        $envContent = $envContent -replace 'DATABASE_URL=.*', 'DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta'
        Set-Content ".env" $envContent
    }

    # Gerar Prisma Client
    Write-Host "${Yellow}🔧 Gerando Prisma Client...${Reset}"
    poetry run prisma generate

    # Aplicar migrations
    Write-Host "${Yellow}📦 Aplicando migrations...${Reset}"
    poetry run prisma migrate deploy

    Write-Host "${Green}✓ Migrations aplicadas${Reset}"
    Write-Host ""
}

# 4. Seed data
if ($SeedData) {
    Write-Host "${Yellow}🌱 [4/4] Executando seed data...${Reset}"
    Set-Location "D:\Averta\backend"
    poetry run db-seed
    Write-Host "${Green}✓ Seed data executado${Reset}"
    Write-Host ""
}

Write-Host "${Blue}╔══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║                    ✅ SETUP CONCLUÍDO!                        ║${Reset}"
Write-Host "${Blue}╚══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""
Write-Host "${Green}PostgreSQL local rodando em: localhost:5432${Reset}"
Write-Host "${Green}Banco: averta | Usuário: postgres | Senha: postgres${Reset}"
Write-Host ""
Write-Host "${Yellow}Para conectar:${Reset}"
Write-Host "  psql -U postgres -d averta -h localhost"
Write-Host ""
Write-Host "${Yellow}Para backup:${Reset}"
Write-Host "  pg_dump -U postgres -h localhost averta > backup_$(date +%Y%m%d).sql"
Write-Host ""
Write-Host "${Yellow}Para restore:${Reset}"
Write-Host "  psql -U postgres -h localhost averta < backup_20240115.sql"