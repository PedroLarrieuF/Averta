#!/usr/bin/env bash
# Averta SaaS - Migração Docker PostgreSQL → Local PostgreSQL
# Copia dados do container Docker para instalação local

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Averta SaaS - Migração Docker PostgreSQL → Local         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se Docker está rodando com postgres
echo -e "${YELLOW}🔍 Verificando container PostgreSQL Docker...${NC}"
if ! docker compose ps | grep -q "postgres.*Up"; then
    echo -e "${RED}✗ Container PostgreSQL não está rodando. Execute: docker compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Container PostgreSQL rodando${NC}"

# Verificar se PostgreSQL local está instalado
if ! command -v pg_isready &> /dev/null; then
    echo -e "${RED}✗ PostgreSQL local não instalado. Execute primeiro: ./scripts/setup-local-db.sh --all${NC}"
    exit 1
fi

# Verificar se PostgreSQL local está rodando
if ! pg_isready -h localhost -p 5432 -U postgres &> /dev/null; then
    echo -e "${RED}✗ PostgreSQL local não está rodando. Inicie o serviço.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ PostgreSQL local rodando${NC}"

echo ""

# 1. Backup do Docker
echo -e "${YELLOW}📦 [1/4] Fazendo backup do banco Docker...${NC}"
BACKUP_FILE="/tmp/averta_docker_backup_$(date +%Y%m%d_%H%M%S).sql"
docker compose exec -T postgres pg_dump -U postgres averta > "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup salvo em: $BACKUP_FILE${NC}"

# 2. Verificar tamanho do backup
BACKUP_SIZE=$(wc -c < "$BACKUP_FILE")
echo -e "${YELLOW}   Tamanho: $(numfmt --to=iec $BACKUP_SIZE)${NC}"

# 3. Restaurar no local
echo -e "${YELLOW}🔄 [2/4] Restaurando no PostgreSQL local...${NC}"
psql -U postgres -h localhost -d averta < "$BACKUP_FILE"
echo -e "${GREEN}✓ Dados restaurados${NC}"

# 3. Verificar contagem de registros
echo -e "${YELLOW}🔍 [3/4] Verificando dados migrados...${NC}"
TABLES=$(psql -U postgres -h localhost -d averta -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public';")
for table in $TABLES; do
    count=$(psql -U postgres -h localhost -d averta -t -c "SELECT COUNT(*) FROM $table;")
    echo -e "   $table: ${GREEN}$count${NC} registros"
done

# 4. Resetar sequences (importante para IDs auto-increment)
echo -e "${YELLOW}🔧 [4/4] Resetando sequences...${NC}"
psql -U postgres -h localhost -d averta -c "
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT c.relname FROM pg_class c WHERE c.relkind = 'S' LOOP
        EXECUTE 'SELECT setval(' || quote_literal(r.relname) || ', COALESCE((SELECT MAX(id) FROM ' || replace(r.relname, '_seq', '') || '), 1), false)';
    END LOOP;
END \$\$;
"
echo -e "${GREEN}✓ Sequences resetadas${NC}"

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✅ MIGRAÇÃO CONCLUÍDA!                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Dados migrados do Docker para PostgreSQL local.${NC}"
echo -e "${YELLOW}Agora você pode parar o container Docker:${NC}"
echo -e "  docker compose stop postgres"
echo ""
echo -e "${YELLOW}E atualizar seu .env para usar localhost:${NC}"
echo -e "  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta"