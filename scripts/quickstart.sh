#!/usr/bin/env bash
# Averta SaaS - Quickstarter
# Inicializa toda a stack de desenvolvimento: Infra (Docker) + Backend (Poetry) + Frontend (Vite)
# Uso: ./scripts/quickstart.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Averta SaaS - Quickstarter v1.0.0                   ║${NC}"
echo -e "${BLUE}║     Infra Docker + Backend Local + Frontend Local            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Função para verificar se comando existe
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}✗ $1 não encontrado. Instale antes de continuar.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1 encontrado${NC}"
}

# Verificar pré-requisitos
echo -e "${YELLOW}🔍 Verificando pré-requisitos...${NC}"
check_command docker
check_command docker compose
check_command node
check_command pnpm
check_command poetry
check_command openssl
echo ""

# Verificar se Docker está rodando
if ! docker info &> /dev/null; then
    echo -e "${RED}✗ Docker não está rodando. Inicie o Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker rodando${NC}"
echo ""

# 1. Subir infraestrutura
echo -e "${YELLOW}📦 [1/5] Subindo infraestrutura (PostgreSQL, Redis, MinIO, Mailhog)...${NC}"
cd "$PROJECT_ROOT"
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Infraestrutura já está rodando${NC}"
else
    docker compose up -d
    echo -e "${GREEN}✓ Infraestrutura iniciada${NC}"
fi
echo ""

# 2. Aguardar serviços ficarem healthy
echo -e "${YELLOW}⏳ [2/5] Aguardando serviços ficarem prontos...${NC}"
sleep 5

# Verificar PostgreSQL
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL pronto${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ PostgreSQL não ficou pronto a tempo${NC}"
        exit 1
    fi
    sleep 1
done

# Verificar Redis
for i in {1..10}; do
    if docker compose exec -T redis redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓ Redis pronto${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}✗ Redis não ficou pronto a tempo${NC}"
        exit 1
    fi
    sleep 1
done

# Verificar MinIO
for i in {1..15}; do
    if curl -sf http://localhost:9000/minio/health/live &> /dev/null; then
        echo -e "${GREEN}✓ MinIO pronto${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}✗ MinIO não ficou pronto a tempo${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# 3. Configurar e iniciar Backend
echo -e "${YELLOW}🐍 [3/5] Configurando Backend (Poetry)...${NC}"
cd "$BACKEND_DIR"

# Verificar .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env não encontrado, copiando de .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}⚠ IMPORTANTE: Edite o arquivo .env com suas chaves (JWT_SECRET_KEY, SENDGRID_API_KEY, etc.)${NC}"
    echo -e "${YELLOW}   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta${NC}"
    echo -e "${YELLOW}   REDIS_URL=redis://localhost:6379/0${NC}"
    echo -e "${YELLOW}   S3_ENDPOINT=http://localhost:9000${NC}"
    read -p "Pressione Enter após editar o .env..."
fi

# Instalar dependências se necessário
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo -e "${YELLOW}📥 Instalando dependências Poetry...${NC}"
    poetry install --with dev
fi

# Gerar Prisma Client
echo -e "${YELLOW}🔧 Gerando Prisma Client...${NC}"
poetry run prisma generate

# Aplicar migrations (banco já populado)
echo -e "${YELLOW}🗄️ Aplicando migrations...${NC}"
poetry run prisma migrate deploy

echo -e "${GREEN}✓ Backend configurado${NC}"
echo ""

# 4. Configurar Frontend
echo -e "${YELLOW}⚛️  [4/5] Configurando Frontend (pnpm)...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📥 Instalando dependências pnpm...${NC}"
    pnpm install
fi

echo -e "${GREEN}✓ Frontend configurado${NC}"
echo ""

# 5. Instruções finais
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    ✅ SETUP CONCLUÍDO!                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Agora abra 4 terminais e execute:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend API (porta 8000):${NC}"
echo -e "  cd $BACKEND_DIR && poetry run start"
echo ""
echo -e "${YELLOW}Terminal 2 - Celery Worker:${NC}"
echo -e "  cd $BACKEND_DIR && poetry run worker"
echo ""
echo -e "${YELLOW}Terminal 3 - Celery Beat:${NC}"
echo -e "  cd $BACKEND_DIR && poetry run beat"
echo ""
echo -e "${YELLOW}Terminal 4 - Frontend (porta 3000):${NC}"
echo -e "  cd $FRONTEND_DIR && pnpm dev"
echo ""
echo -e "${BLUE}📋 URLs de Acesso:${NC}"
echo -e "  Frontend:        http://localhost:3000"
echo -e "  Backend API:     http://localhost:8000"
echo -e "  Swagger Docs:    http://localhost:8000/docs"
echo -e "  MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
echo -e "  Mailhog UI:      http://localhost:8025"
echo -e "  Prisma Studio:   cd $BACKEND_DIR && poetry run prisma studio"
echo -e "  Flower:          cd $BACKEND_DIR && poetry run flower"
echo ""
echo -e "${YELLOW}💡 Dica: Use 'tmux' ou 'screen' para gerenciar múltiplos terminais facilmente.${NC}"
echo ""