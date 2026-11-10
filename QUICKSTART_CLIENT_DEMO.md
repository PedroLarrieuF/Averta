# Averta SaaS — Quick Start para Demo ao Cliente (MVP)

> **Objetivo**: Subir a plataforma completa com dados reais populados em **< 10 minutos** para demonstrar o fluxo completo de auditoria de frete com success-fee.

---

## ⚡ TL;DR — Comandos Rápidos

```bash
# 1. Backend (Terminal 1)
cd D:/Averta/backend
cp .env.example .env
# Edite .env: JWT_SECRET_KEY=$(openssl rand -base64 32)
docker compose up -d --build
docker compose exec backend poetry run prisma generate
docker compose exec backend poetry run prisma migrate deploy
docker compose exec backend poetry run db-seed

# 2. Frontend (Terminal 2)
cd D:/Averta/frontend
pnpm install
pnpm dev

# 3. Acessar
# Frontend:     http://localhost:3000
# Login:        admin@admin / admin
# API Docs:     http://localhost:8000/docs
# MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
```

---

## 🔐 Credenciais de Acesso (Dados Reais do Seed)

| Usuário | Email | Senha | Role | Empresa |
|---------|-------|-------|------|---------|
| **Admin Principal** | `admin@admin` | `admin` | **ADMIN** | Averta Admin |
| **Manager** | `user1@<cnpj>.com.br` | `admin` | MANAGER | Empresa 001 |
| **Auditor** | `user2@<cnpj>.com.br` | `admin` | AUDITOR | Empresa 001 |
| **Cliente** | `user3@<cnpj>.com.br` | `admin` | CLIENT | Empresa 001 |
| **Transportadora** | `user4@<cnpj>.com.br` | `admin` | CARRIER | Empresa 001 |

> **Dica**: Após login como `admin@admin`, use o seletor de empresa (canto superior direito) para trocar entre as 5 empresas criadas.

---

## 📊 O que o Seed Cria Automaticamente (Dados Reais)

```
┌─────────────────────────────────────────────────────────────────┐
│                    5 EMPRESAS (Company)                        │
├─────────────────────────────────────────────────────────────────┤
│  Empresa 001 Ltda    │  CNPJ único  │  4 usuários + admin      │
│  Empresa 002 Ltda    │  CNPJ único  │  4 usuários              │
│  Empresa 003 Ltda    │  CNPJ único  │  4 usuários              │
│  Empresa 004 Ltda    │  CNPJ único  │  4 usuários              │
│  Empresa 005 Ltda    │  CNPJ único  │  4 usuários              │
└─────────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ 10 CLIENTES  │ │ 8 TRANSPORT. │ │ 3 FILIAIS/   │
    │ por empresa  │ │ por empresa  │ │ cliente      │
    └──────────────┘ └──────────────┘ └──────────────┘
            │               │
            ▼               ▼
    ┌──────────────────────────────────────┐
    │ 2 CONTRATOS/cliente × 5 empresas     │
    │ = 100 contratos com Tabelas de Frete │
    │ Success Fee: 15-30% | Progressive: 5%/10%+ │
    └──────────────────────────────────────┘
            │
            ▼
    ┌──────────────────────────────────────┐
    │ 50 DOCUMENTOS/cliente (CT-e/NF-e)    │
    │ = 2.500 documentos com XMLs simulados│
    │ Status: 60% COMPLETED, 10% PROCESSING│
    └──────────────────────────────────────┘
            │
            ▼
    ┌──────────────────────────────────────┐
    │ ~3 DISCREPÂNCIAS/documento (7.500+)  │
    │ 17 Regras: ICMS, Frete, Peso, Pedágio│
    │ Severidades: LOW → CRITICAL          │
    │ Status: DETECTED → OPEN → IN_REVIEW  │
    └──────────────────────────────────────┘
            │
            ▼
    ┌──────────────────────────────────────┐
    │ 5 CONTESTAÇÕES/cliente (250+)        │
    │ Itens, Comunicações, Pagamentos      │
    │ PDFs de carta formal gerados         │
    │ Success Fee calculado automaticamente│
    └──────────────────────────────────────┘
```

---

## 🎯 Roteiro de Demo (15-20 min)

### 1. **Login & Dashboard** (2 min)
```
→ http://localhost:3000
→ Login: admin@admin / admin
→ Mostrar: KPIs cards, gráficos evolução, top 5 transportadoras com discrepâncias
→ Trocar empresa no seletor (canto sup. dir.) → Mostrar multi-tenancy
```

### 2. **Documentos & Upload** (3 min)
```
→ Menu: Documentos
→ Mostrar: Lista 2.500 docs, filtros (cliente, transportadora, status, datas)
→ Clicar em um "COMPLETED" → Modal detalhe: dados parseados (chave, valores, ICMS, peso)
→ Upload Zone: Arrastar XML real (se tiver) ou mostrar que aceita multipart/base64
```

### 3. **Discrepâncias (Coração da Auditoria)** (5 min)
```
→ Menu: Discrepâncias
→ Mostrar: 7.500+ discrepâncias, filtros avançados
→ Cards Resumo: Total, Por Severidade (CRITICAL/HIGH/MEDIUM/LOW), Valor Total
→ Tabela: Rule Code (CTE-001, NFE-003...), Expected vs Actual vs Diff%, Severidade
→ Clicar em uma CRITICAL → Modal: Evidências XML, Cálculo, Notas do auditor
→ Bulk Actions: Selecionar 5 → "Aprovar" → "Exportar Excel"
```

### 4. **Motor de Regras (Diferencial Técnico)** (2 min)
```
→ Menu: Regras (ou Developer → Regras)
→ Mostrar: 17 Rules ativas com tags de relevância
→ Clicar CTE-010 (Valor Mínimo Frete - CRITICAL) → Config JSON: tabela ANTT 2024
→ Explicar: Filtragem O(tag) — só roda rules relevantes ao contexto do documento
→ Dados: icms_rules.json (27 UFs), sicoban_table.json (22 faixas CEP)
```

### 5. **Contestação & Success-Fee (Fluxo de Negócio)** (5 min)
```
→ Menu: Contestações
→ Lista: 250+ contestações com status workflow
→ Criar Nova: Selecionar discrepâncias → Agrupa por transportadora → Cria contestação
→ Detalhe Contestação (27K linhas código):
   - Timeline visual: Created → Sent → Negotiating → Accepted
   - Itens: Expected, Contested, Recovered, Status
   - Comunicações: Email, Carta, WhatsApp, Reunião
   - PDF Carta Formal: Gerar → Visualizar (ReportLab, tabelas, base legal)
   - Success Fee Calculator: Recovered × 20% = Fee | Net = Recovered - Fee
   - Pagamento: Registrar PIX → Atualiza Net Recovery → Notificação
```

### 6. **Contratos & Tabelas de Frete** (2 min)
```
→ Menu: Contratos → Settings → Contratos
→ Mostrar: Versionamento, Success Fee %, Progressive Pricing (5% mês 1, 10%+ mês 2+)
→ Tabelas de Frete: baseRate, perKm, perKg, minCharge, ICMS incluso, Pedágios
```

### 7. **Relatórios & Export** (1 min)
```
→ Menu: Relatórios
→ Dashboard: KPIs, evolução temporal, top carriers
→ Export: PDF (ReportLab) / Excel (OpenPyXL, múltiplas abas)
→ Agendamento: Email semanal automático (Celery Beat)
```

---

## 🌐 URLs de Acesso Rápido

| Serviço | URL | Uso na Demo |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Demo principal |
| **Swagger API** | http://localhost:8000/docs | Mostrar endpoints técnicos |
| **MinIO Console** | http://localhost:9001 | Armazenamento XMLs/PDFs (minioadmin/minioadmin) |
| **Flower (Celery)** | http://localhost:5555 | Tasks assíncronas, workers |
| **Prisma Studio** | `poetry run prisma studio` | Banco visual (opcional) |

---

## 🛠 Troubleshooting Rápido (Se algo der errado)

```bash
# Backend não sobe?
docker compose logs backend
# Verificar se pgbouncer subiu após postgres
docker compose logs pgbouncer

# Prisma Client erro?
docker compose exec backend poetry run prisma generate

# Banco vazio / seed não rodou?
docker compose exec backend poetry run db-seed

# Frontend não conecta na API?
# Verificar vite.config.ts proxy /api → localhost:8000
# Verificar CORS_ORIGINS no backend .env inclui http://localhost:3000

# Porta ocupada?
netstat -ano | findstr :3000  # Windows
kill -9 <PID>                 # Linux/Mac

# Reset total (apaga tudo!):
cd D:/Averta/backend
docker compose down -v
docker compose up -d --build
docker compose exec backend poetry run prisma migrate deploy
docker compose exec backend poetry run db-seed
```

---

## 📋 Checklist Pré-Demo (5 min antes)

- [ ] `docker compose ps` → Todos 8 containers `Up (healthy)`
- [ ] `curl http://localhost:8000/health` → `{"status":"ok"}`
- [ ] Frontend carrega em http://localhost:3000
- [ ] Login `admin@admin` / `admin` funciona
- [ ] Dashboard mostra KPIs > 0 (não vazio)
- [ ] Discrepâncias lista > 1000 itens
- [ ] Contestações lista > 50 itens
- [ ] MinIO Console abre em :9001
- [ ] PDF de contestação gera sem erro (testar uma)

---

## 💡 Dicas de Apresentação

| Situação | O que Dizer / Mostrar |
|----------|----------------------|
| **"Como sabe que o frete está errado?"** | Abrir Discrepância → Mostrar Expected vs Actual vs Diff% → Evidências XML |
| **"E se a transportadora não concordar?"** | Fluxo Contestação: PDF formal → Envio → Negociação → Partial/Accepted |
| **"Como calculam o success fee?"** | SuccessFeeCalculator: `Recuperado × 20% = Fee | Líquido = Recuperado - Fee` |
| **"Suporta NF-e também?"** | Rules: NFE-001 a NFE-007 (CFOP, NCM, Destinatário, Transportadora, Valores) |
| **"E se eu tiver 100 mil CT-es/mês?"** | Celery workers (4 concorrentes), PgBouncer (pool 25), Read Replica, Índices compostos |
| **"Dados ficam onde?"** | PostgreSQL (dados), MinIO/S3 (XMLs/PDFs), Redis (cache/queue) |
| **"É multi-tenant de verdade?"** | Trocar empresa no seletor → Todos os dados filtram por company_id automaticamente |

---

## 🎬 Fluxo Completo em 1 Clique (Para gravar vídeo)

```bash
# Script único para gravar demo
cd D:/Averta/backend && docker compose up -d && \
docker compose exec backend poetry run prisma generate && \
docker compose exec backend poetry run prisma migrate deploy && \
docker compose exec backend poetry run db-seed && \
echo "✅ Backend pronto! Inicie frontend em outro terminal: cd ../frontend && pnpm dev"
```

---

## 📞 Suporte Durante Demo

| Problema | Solução Rápida |
|----------|----------------|
| Página carrega lento | `docker compose logs -f backend` → ver se worker processando |
| Discrepâncias não aparecem | Verificar se docs têm status `COMPLETED` (são processados async) |
| PDF não gera | `docker compose logs celery-worker` → ver erro ReportLab |
| Login falha | Verificar `JWT_SECRET_KEY` no .env (mín 32 chars) |

---

**Pronto para demo!** 🚀

> Todos os dados são **reais do seed** — não é mock, não é demo mode. São 5 empresas, 50 clientes, 40 transportadoras, 100 contratos, 2.500 documentos, 7.500+ discrepâncias, 250+ contestações com PDFs, pagamentos e success-fee calculado.