<#
.SYNOPSIS
    Migra dados do PostgreSQL Docker para PostgreSQL Local

.DESCRIPTION
    Copia todos os dados do container Docker PostgreSQL para instalação local.
    Útil para transição de arquitetura híbrida para 100% local.
#>

$ErrorActionPreference = "Stop"

$Red = "$([char]27)[31m"
$Green = "$([char]27)[32m"
$Yellow = "$([char]27)[33m"
$Blue = "$([char]27)[34m"
$Reset = "$([char]27)[0m"

Write-Host "${Blue}╔══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║     Averta SaaS - Migração Docker PostgreSQL → Local         ║${Reset}"
Write-Host "${Blue}╚══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""

# Verificar Docker
Write-Host "${Yellow}🔍 Verificando container PostgreSQL Docker...${Reset}"
$dockerPs = docker compose ps --format "table {{.Service}}\t{{.Status}}" | Select-Object -Skip 1
if (-not ($dockerPs -match "postgres.*Up")) {
    Write-Host "${Red}✗ Container PostgreSQL não está rodando. Execute: docker compose up -d${Reset}"
    exit 1
}
Write-Host "${Green}✓ Container PostgreSQL rodando${Reset}"

# Verificar PostgreSQL local
Write-Host "${Yellow}🔍 Verificando PostgreSQL local...${Reset}"
try {
    & "C:\Program Files\PostgreSQL\16\bin\pg_isready.exe" -h localhost -p 5432 -U postgres | Out-Null
    Write-Host "${Green}✓ PostgreSQL local rodando${Reset}"
} catch {
    Write-Host "${Red}✗ PostgreSQL local não está rodando. Inicie o serviço.${Reset}"
    exit 1
}
Write-Host ""

# 1. Backup do Docker
Write-Host "${Yellow}📦 [1/4] Fazendo backup do banco Docker...${Reset}"
$backupFile = "$env:TEMP\averta_docker_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
docker compose exec -T postgres pg_dump -U postgres averta > $backupFile
Write-Host "${Green}✓ Backup salvo em: $backupFile${Reset}"

$backupSize = (Get-Item $backupFile).Length
Write-Host "${Yellow}   Tamanho: $([math]::Round($backupSize/1MB, 2)) MB${Reset}"

# 2. Restaurar no local
Write-Host "${Yellow}🔄 [2/4] Restaurando no PostgreSQL local...${Reset}"
$env:PGPASSWORD = "postgres"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h localhost -d averta -f $backupFile
Write-Host "${Green}✓ Dados restaurados${Reset}"

# 3. Verificar contagem
Write-Host "${Yellow}🔍 [3/4] Verificando dados migrados...${Reset}"
$tables = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h localhost -d averta -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
foreach ($table in $tables) {
    $table = $table.Trim()
    if ($table) {
        $count = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h localhost -d averta -t -c "SELECT COUNT(*) FROM $table;"
        Write-Host "   $table: ${Green}$($count.Trim())${Reset} registros"
    }
}

# 4. Resetar sequences
Write-Host "${Yellow}🔧 [4/4] Resetando sequences...${Reset}"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -h localhost -d averta -c @"
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT c.relname FROM pg_class c WHERE c.relkind = 'S' LOOP
        EXECUTE 'SELECT setval(' || quote_literal(r.relname) || ', COALESCE((SELECT MAX(id) FROM ' || replace(r.relname, '_seq', '') || '), 1), false)';
    END LOOP;
END \$\$;
"@
Write-Host "${Green}✓ Sequences resetadas${Reset}"

Write-Host ""
Write-Host "${Blue}╔══════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║                    ✅ MIGRAÇÃO CONCLUÍDA!                     ║${Reset}"
Write-Host "${Blue}╚══════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""
Write-Host "${Green}Dados migrados do Docker para PostgreSQL local.${Reset}"
Write-Host "${Yellow}Agora você pode parar o container Docker:${Reset}"
Write-Host "  docker compose stop postgres"
Write-Host ""
Write-Host "${Yellow}E atualizar seu .env para usar localhost:${Reset}"
Write-Host "  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta"