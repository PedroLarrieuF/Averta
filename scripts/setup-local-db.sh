#!/usr/bin/env bash
# Averta SaaS - Setup PostgreSQL Local (Linux/macOS)
# Configura PostgreSQL 16 localmente fora do Docker

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_POSTGRES=false
CREATE_DATABASE=false
RUN_MIGRATIONS=false
SEED_DATA=false

for arg in "$@"; do
    case $arg in
        --install-postgres) INSTALL_POSTGRES=true ;;
        --create-database) CREATE_DATABASE=true ;;
        --run-migrations) RUN_MIGRATIONS=true ;;
        --seed-data) SEED_DATA=true ;;
        --all)
            INSTALL_POSTGRES=true
            CREATE_DATABASE=true
            RUN_MIGRATIONS=true
            SEED_DATA=true
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Averta SaaS - Setup PostgreSQL Local (Linux/macOS)       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Instalar PostgreSQL
if [ "$INSTALL_POSTGRES" = true ]; then
    echo -e "${YELLOW}📦 [1/4] Instalando PostgreSQL 16...${NC}"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql@16
            brew services start postgresql@16
        else
            echo -e "${RED}✗ Homebrew não encontrado. Instale manualmente.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux (Ubuntu/Debian)
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y postgresql-16 postgresql-client-16
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y postgresql16-server postgresql16
            sudo postgresql-16-setup initdb
            sudo systemctl start postgresql-16
            sudo systemctl enable postgresql-16
        else
            echo -e "${RED}✗ Gerenciador de pacotes não suportado. Instale manualmente.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ SO não suportado para instalação automática.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ PostgreSQL instalado${NC}"
    echo ""
fi

# 2. Criar banco e usuário
if [ "$CREATE_DATABASE" = true ]; then
    echo -e "${YELLOW}🗄️  [2/4] Criando banco de dados 'averta'...${NC}"

    # Aguardar PostgreSQL estar pronto
    for i in {1..30}; do
        if pg_isready -h localhost -p 5432 -U postgres &> /dev/null; then
            echo -e "${GREEN}✓ PostgreSQL pronto${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ PostgreSQL não ficou pronto a tempo${NC}"
            exit 1
        fi
        sleep 1
    done

    # Criar banco (ignora erro se já existe)
    createdb -U postgres averta 2>/dev/null || true
    echo -e "${GREEN}✓ Banco 'averta' criado/verificado${NC}"

    # Criar extensões
    psql -U postgres -d averta -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
    psql -U postgres -d averta -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
    psql -U postgres -d averta -c "CREATE EXTENSION IF NOT EXISTS \"btree_gin\";"
    echo -e "${GREEN}✓ Extensões criadas${NC}"
    echo ""
fi

# 3. Aplicar migrations
if [ "$RUN_MIGRATIONS" = true ]; then
    echo -e "${YELLOW}🔄 [3/4] Aplicando migrations Prisma...${NC}"
    cd "$(dirname "$0")/../backend"

    # Verificar .env
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠ .env criado a partir do .env.example${NC}"
    fi

    # Garantir DATABASE_URL para localhost
    if grep -q "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta" .env; then
        echo -e "${GREEN}✓ DATABASE_URL já configurado para localhost${NC}"
    else
        echo -e "${YELLOW}⚠ Atualizando DATABASE_URL para localhost...${NC}"
        sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta|' .env
    fi

    # Gerar Prisma Client
    echo -e "${YELLOW}🔧 Gerando Prisma Client...${NC}"
    poetry run prisma generate

    # Aplicar migrations
    echo -e "${YELLOW}📦 Aplicando migrations...${NC}"
    poetry run prisma migrate deploy

    echo -e "${GREEN}✓ Migrations aplicadas${NC}"
    echo ""
fi

# 4. Seed data
if [ "$SEED_DATA" = true ]; then
    echo -e "${YELLOW}🌱 [4/4] Executando seed data...${NC}"
    cd "$(dirname "$0")/../backend"
    poetry run db-seed
    echo -e "${GREEN}✓ Seed data executado${NC}"
    echo ""
fi

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✅ SETUP CONCLUÍDO!                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}PostgreSQL local rodando em: localhost:5432${NC}"
echo -e "${GREEN}Banco: averta | Usuário: postgres | Senha: postgres${NC}"
echo ""
echo -e "${YELLOW}Para conectar:${NC}"
echo "  psql -U postgres -d averta -h localhost"
echo ""
echo -e "${YELLOW}Para backup:${NC}"
echo "  pg_dump -U postgres -h localhost averta > backup_\$(date +%Y%m%d).sql"
echo ""
echo -e "${YELLOW}Para restore:${NC}"
echo "  psql -U postgres -h localhost averta < backup_20240115.sql"