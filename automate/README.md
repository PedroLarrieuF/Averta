# Averta Lead Generation Automation

Sistema automatizado de geração de leads B2B para o mercado brasileiro, com foco em empresas de logística, transporte e distribuição.

## 🎯 Visão Geral

Este sistema realiza prospecção ativa em escala nacional utilizando o **Google Maps Scraper** (Go) para coletar dados de empresas, aplica qualificação rigorosa baseada em **ICP (Ideal Customer Profile)** e exporta leads prontos para contato via WhatsApp Business.

### Principais Funcionalidades

- 🇧🇷 **Cobertura Nacional**: 27 estados, 400+ cidades, polos industriais
- 🎯 **ICP Scoring**: Classificação A/B/C/D (0-100) em 3 dimensões
- 📊 **Exportação Excel**: Leads A/B consolidados, C separados, WhatsApp-ready
- 📧 **Email Outreach**: Envio automático personalizado via Zoho SMTP (contato@avertabrasil.com.br)
- 📱 **WhatsApp Business**: Preparação de contatos + envio inteligente (futuro)
- 🗄️ **Persistência**: SQLite master database com deduplicação
- 📈 **Relatórios**: Diários, semanais, cobertura, qualidade, decisores

---

## 📁 Estrutura do Projeto

```
automate/
├── config/
│   ├── settings.yaml          # Configuração principal
│   ├── icp_keywords.yaml      # Definição ICP (10 segmentos)
│   └── brazil_states.yaml     # Estados, cidades, polos industriais
├── src/
│   ├── main.py                # Orquestrador principal + CLI
│   ├── scraper/
│   │   ├── wrapper.py         # Wrapper google-maps-scraper (Go)
│   │   ├── queries.py         # Geração de queries nacionais
│   │   └── runner.py          # Orquestração de scraping
│   ├── qualification/
│   │   ├── icp.py             # Definição ICP e regras
│   │   ├── scorer.py          # Scoring e qualificação
│   │   └── enricher.py        # Enriquecimento de dados
│   ├── storage/
│   │   ├── models.py          # Modelos de dados (dataclasses)
│   │   └── master_db.py       # SQLite + SQLAlchemy
│   ├── export/
│   │   ├── excel_exporter.py  # Exportação Excel formatada
│   │   └── report_generator.py # Geração de relatórios
│   ├── whatsapp/
│   │   ├── prepare.py         # Preparação contatos WhatsApp
│   │   ├── templates.py       # Templates Meta aprovados
│   │   └── client.py          # Engine mensagens (API + Web)
│   └── utils/
│       ├── config_loader.py   # Carregamento configuração
│       ├── logging.py         # Logging estruturado
│       └── helpers.py         # Utilitários diversos
├── queries/generated/         # Queries geradas (.txt)
├── output/                    # Arquivos Excel exportados
├── data/                      # Banco SQLite master.db
├── logs/                      # Logs de execução
├── tests/                     # Testes unitários
├── requirements.txt
├── run.py                     # Entry point simples
├── build_scraper.sh/bat/ps1   # Build do binário Go
├── download_scraper.py        # Download automático binário
└── EXAMPLES.md                # Exemplos de uso programático
```

---

## ⚙️ Configuração

### 1. Configuração Principal (`config/settings.yaml`)

```yaml
general:
  mode: "full"
  paths:
    master_db: "data/master.db"
    output_dir: "output"

scraper:
  execution_mode: "binary"  # binary | rest-api | docker
  params:
    depth: 2
    concurrency: 4
    extract_emails: true
  limits:
    max_queries_per_run: 200
    rate_limit_per_minute: 30

qualification:
  weights:
    operational_fit: 0.40
    commercial_fit: 0.35
    data_confidence: 0.25
  thresholds:
    A_min: 85
    B_min: 70
    C_min: 50

whatsapp:
  enabled: false  # Habilitar quando credenciais estiverem prontas
  provider: "cloud_api"
  cloud_api:
    business_account_id: ""
    phone_number_id: ""
    access_token: ""
```

### 2. ICP Keywords (`config/icp_keywords.yaml`)

Define 10 segmentos prioritários com palavras-chave positivas/negativas:
- Distribuidoras, Atacadistas, Indústrias
- Farma/Hospitalar, Alimentícias, Bebidas
- Autopeças, Material Construção, E-commerce/Logística, Grande Volume

### 3. Estados e Cidades (`config/brazil_states.yaml`)

27 estados com prioridades (1=alta, 2=média, 3=baixa), cidades principais e polos industriais.

---

## 🚀 Execução Rápida

### Instalação

```bash
cd automate

# 1. Ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Dependências
pip install -r requirements.txt

# 3. Binário do scraper (escolha uma opção)
# Opção A: Download automático (recomendado)
python download_scraper.py

# Opção B: Build from source (requer Go 1.21+)
./build_scraper.sh      # Linux/Mac
.\build_scraper.ps1     # Windows PowerShell
build_scraper.bat       # Windows CMD

# 4. Verificar
python run.py --generate-queries --max-queries 5
```

### Pipeline Completo

```bash
# Execução completa (padrão: prioridades 1 e 2)
# Inclui: Queries → Scraping → Qualificação → Enriquecimento → Export → WhatsApp Prep → Email Prep → Reports
python run.py --full

# Apenas prioridade 1 (estados top: SP, RJ, MG, RS, PR, SC)
python run.py --full --priorities 1

# Teste rápido (limite de queries e leads)
python run.py --full --max-queries 50 --max-leads 100
```

### Etapas do Pipeline (--full)

| Etapa | Descrição |
|-------|-----------|
| 1 | **Query Generation** - Gera queries nacionais por estado/segmento |
| 2 | **Scraping** - Executa google-maps-scraper para coletar empresas |
| 3 | **Qualification** - Aplica ICP scoring (A/B/C/D) |
| 4 | **Enrichment** - Enriquece leads C (prioridade) e B |
| 5 | **Export** - Gera Excel leads A/B, C, WhatsApp-ready, Decisores |
| 6 | **WhatsApp Prep** - Prepara contatos para WhatsApp Business |
| 7 | **Email Prep** - Prepara contatos para Email Outreach (NOVO) |
| 8 | **Reports** - Gera relatórios diários, cobertura, qualidade |

### Etapas Individuais

```bash
# Apenas gerar queries
python run.py --generate-queries --priorities 1 --max-queries 20

# Apenas executar scraper (usa queries existentes)
python run.py --scrape

# Apenas qualificar leads existentes
python run.py --qualify --max-leads 1000

# Apenas exportar resultados
python run.py --export
```

### Modo Contínuo

```bash
# Executar a cada 24h indefinidamente
python run.py --continuous --interval 24

# Executar 7 vezes (uma semana) a cada 24h
python run.py --continuous --interval 24 --max-runs 7

# A cada 12h apenas prioritários
python run.py --continuous --interval 12 --priorities 1
```

---

## 📊 Saída e Resultados

Após execução, arquivos são gerados em `output/`:

```
output/
├── leads_A_B.xlsx           # Leads A e B (principais - prontos para contato)
├── leads_C.xlsx             # Leads C (precisam enriquecimento)
├── whatsapp_ready/
│   └── leads_whatsapp_YYYYMMDD.xlsx  # Contatos prontos para WhatsApp
├── email_ready/
│   ├── leads_email_YYYYMMDD.csv      # Contatos prontos para email (CSV)
│   └── leads_sendgrid_YYYYMMDD.csv   # Formato SendGrid
├── reports/
│   ├── daily_YYYYMMDD.xlsx  # Relatório diário completo
│   ├── coverage_YYYYMMDD.xlsx        # Cobertura por estado/segmento
│   └── decision_makers_YYYYMMDD.xlsx # Decisores identificados
```

### Colunas Principais (leads_A_B.xlsx)

| Coluna | Descrição |
|--------|-----------|
| `id` | ID único do lead |
| `classification` | A ou B |
| `score` | Score 0-100 |
| `company_name` | Razão social |
| `trade_name` | Nome fantasia |
| `segment` | Segmento ICP |
| `city` / `state` | Localização |
| `phone` / `whatsapp` | Telefones |
| `email` | E-mail corporativo |
| `website` / `linkedin` | Canais digitais |
| `operational_fit_score` | Fit operacional (0-100) |
| `commercial_fit_score` | Fit comercial (0-100) |
| `data_confidence_score` | Confiança dados (0-100) |
| `decision_makers` | JSON com decisores |
| `institutional_contacts` | JSON contatos institucionais |
| `whatsapp_ready` | Pronto para WhatsApp |
| `whatsapp_template_suggested` | Template sugerido |

---

## 📱 WhatsApp Business (Preparação Atual)

**Status atual**: Sistema prepara contatos e números - **não envia mensagens ainda**.

### O que está pronto:

1. **Preparação de contatos** (`src/whatsapp/prepare.py`):
   - Filtra leads A/B com WhatsApp válido
   - Extrai decisor principal (nome + cargo)
   - Sugere template ideal por segmento/classificação
   - Agenda envios respeitando horário comercial (8h-18h)
   - Rate limiting: 20 msg/min, 500 msg/hora, 2000 msg/dia

2. **Templates aprovados Meta** (`src/whatsapp/templates.py`):
   - `initial_contact` - Primeiro contato com botões
   - `follow_up_1` / `follow_up_2` - Follow-ups
   - `value_proposition` - Proposta de valor
   - `case_study` - Case de sucesso
   - `meeting_confirmation` - Confirmação reunião
   - `not_interested` - Opt-out respeitoso

3. **Exportação para API** (`whatsapp_ready/leads_whatsapp_YYYYMMDD.xlsx`):
   - Colunas: id, company_name, contact_name, contact_role, phone, whatsapp, email, segment, city, state, score, template_suggested, opt_in_status

### Para habilitar envio futuro:

```yaml
# config/settings.yaml
whatsapp:
  enabled: true
  cloud_api:
    business_account_id: "SEU_BUSINESS_ACCOUNT_ID"
    phone_number_id: "SEU_PHONE_NUMBER_ID"
    access_token: "SEU_ACCESS_TOKEN_PERMANENTE"
    webhook_verify_token: "SEU_WEBHOOK_TOKEN"
```

Comandos futuros (já implementados, aguardam credenciais):
```bash
# Dry run - ver quem seria contatado
python run.py --whatsapp-campaign --campaign-name "Q1_2024" --classifications A B --min-score 75

# Execução real (quando credenciais configuradas)
python run.py --whatsapp-campaign --execute --campaign-name "Q1_2024"

# Teste unitário
python run.py --whatsapp-test --lead-id LEAD_123 --template initial_contact

# Estatísticas
python run.py --whatsapp-stats
```

---

## 📧 Email Outreach (NOVO - Zoho SMTP)

**Status**: ✅ **Configurado e pronto para uso** - usando `contato@avertabrasil.com.br`

### O que está pronto:

1. **Templates personalizados** (`src/email_outreach/templates.py`) - **Foco em Auditoria de Fretes (CT-e/NF-e)**:
   - `initial_outreach` - Primeiro contato: identifica divergências/cobranças indevidas em faturas de frete, apresenta Averta como plataforma de inteligência e auditoria logística
   - `follow_up_1` / `follow_up_2` - Follow-ups com casos de sucesso e proof social
   - `value_proposition` - Proposta detalhada: 5 benefícios (cobranças acima do contratado, divergências fiscais, auditoria automática, organização de contestações, acompanhamento de valores recuperados)
   - `case_study` - Case de sucesso com métricas reais de recuperação financeira
   - `meeting_request` - Call-to-action direto para agendamento de 15 min
   - `breakup` - Último email respeitoso (opt-out LGPD compliant)

2. **Personalização inteligente** (`src/email_outreach/client.py`):
   - Nome da empresa prospectada (`{{company_name}}`)
   - Nome do decisor se encontrado (`{{contact_name}}`, `{{contact_first_name}}`)
   - Cargo do decisor (`{{contact_role}}`)
   - Segmento ICP (`{{segment}}`)
   - Cidade/Estado (`{{city}}/{{state}}`)
   - Score e classificação do lead
   - Case study relevante por segmento (`{{case_study}}`)
   - Value props específicas por pilar (`{{value_prop_1}}`, etc.)
   - Links de tracking (abertura, cliques, unsubscribe)
   - Logo da empresa nos templates (`https://averta.com.br/assets/Logo_Averte_Auditoria_Especializada.png`)

3. **Sequência automática** (configurável em `config/settings.yaml`):
   - Dia 0: `initial_outreach` - Apresentação + Oportunidade de auditoria
   - Dia 3: `follow_up_1` - Reforço + Case similar
   - Dia 7: `follow_up_2` - Case study completo
   - Dia 14: `value_proposition` - 5 benefícios + features de auditoria
   - Dia 21: `case_study` - Case detalhado com métricas
   - Dia 30: `meeting_request` - CTA direto agendar 15 min
   - Dia 45: `breakup` - Opt-out respeitoso

4. **Rate limiting conservador** (respeita reputação do domínio):
   - 10 emails/minuto
   - 200 emails/hora
   - 1000 emails/dia
   - Apenas horário comercial (8h-18h, Seg-Sex)
   - Timezone: America/Sao_Paulo

5. **LGPD Compliant**:
   - Opt-out em todos os emails (List-Unsubscribe header + link visível)
   - Palavras-chave de opt-out monitoradas em respostas (automático)
   - Processamento automático de bounces/unsubscribes
   - Headers: List-Unsubscribe, List-Unsubscribe-Post

### Configuração SMTP (já no .env):

```bash
ZOHO_EMAIL=pedrolarrieuceo@avertabrasil.com.br
ZOHO_PASSWORD=aV6PB8.x7mywd!N
ZOHO_SMTP_HOST=smtppro.zoho.com
ZOHO_SMTP_PORT=465
```

### Comandos Email:

```bash
# Preparar contatos para email (exporta CSV para revisão/envio)
python run.py --email-prepare --classifications A B --min-score 70

# Dry run - ver quem seria contatado
python run.py --email-campaign --campaign-name "Q1_2024" --classifications A B --min-score 75

# Execução real (enviar emails via Zoho SMTP)
python run.py --email-campaign --execute --campaign-name "Q1_2024"

# Enviar email de teste para um lead específico
python run.py --email-test --lead-id LEAD_123 --email-template initial_outreach

# Estatísticas de campanhas
python run.py --email-stats
```

### Opções de campanha:

```bash
--campaign-name "Nome da Campanha"     # Nome personalizado
--classifications A B                  # Classificações alvo (padrão: A B)
--min-score 70                         # Score mínimo (padrão: 70)
--max-emails 4                         # Max emails por lead na sequência
--segments distribuidoras industrias   # Filtrar por segmentos
--states SP RJ MG                      # Filtrar por estados
--sendgrid                             # Exportar também formato SendGrid
--execute                              # Executar de verdade (padrão: dry run)
```

---

## 📈 KPIs Monitorados

Relatório diário inclui:
- **Queries executadas**
- **Empresas encontradas / únicas**
- **Leads por classificação (A, B, C, D)**
- **Decisores identificados**
- **Contatos válidos** (tel, email, WhatsApp, LinkedIn)
- **Cobertura por estado / segmento**
- **Custo por lead qualificado com contato verificável** (KPI principal)
- **Taxa de qualificação**

---

## 🧪 Testes

```bash
# Todos os testes
PYTHONPATH=src python -m pytest tests/ -v

# Testes específicos
PYTHONPATH=src python -m pytest tests/test_automation.py::TestScorer -v
PYTHONPATH=src python -m pytest tests/test_automation.py::TestQueryGenerator -v
```

---

## 📅 Agendamento Automático

### systemd (Linux)
```ini
# /etc/systemd/system/averta-leads.service
[Unit]
Description=Averta Lead Generation
After=network.target

[Service]
Type=simple
User=averta
WorkingDirectory=/opt/averta/automate
Environment=PATH=/opt/averta/automate/venv/bin
ExecStart=/opt/averta/automate/venv/bin/python run.py --continuous --interval 24
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
```

### Cron (diário às 6h)
```bash
crontab -e
# Adicionar:
0 6 * * * cd /opt/averta/automate && /opt/averta/automate/venv/bin/python run.py --full >> /var/log/averta-leads.log 2>&1
```

---

## 🔧 Solução de Problemas

### Binário não encontrado
```bash
python download_scraper.py
# ou
./build_scraper.sh
```

### Erro de permissão (Linux/Mac)
```bash
chmod +x google-maps-scraper
```

### Timeout do scraper
```yaml
# config/settings.yaml
scraper:
  params:
    exit_on_inactivity: "10m"  # Aumentar de 5m para 10m
```

### Poucos leads qualificados
1. Verificar se queries não estão muito restritivas
2. Aumentar `max_queries_per_run`
3. Reduzir thresholds:
```yaml
qualification:
  thresholds:
    A_min: 80
    B_min: 65
    C_min: 45
```

### Memória insuficiente
```yaml
performance:
  batch_size_scrape: 50
  batch_size_qualify: 200
  max_workers_scraper: 2
```

---

## 🗺️ Roadmap

- [x] Pipeline completo de coleta e qualificação
- [x] Cobertura nacional 27 estados
- [x] ICP scoring 3 dimensões
- [x] Exportação Excel + relatórios
- [x] Preparação WhatsApp (contatos + templates)
- [x] **Email Outreach completo** (Zoho SMTP + templates + sequências + LGPD)
- [ ] **Integração WhatsApp Business API** (envio real)
- [ ] Enriquecimento externo (Hunter.io, Apollo, Clearbit)
- [ ] Dashboard Web (visualização leads, funil, KPIs)
- [ ] API REST (expor leads para CRM/ERP)
- [ ] ML Scoring (modelo para melhorar qualificação)
- [ ] Deduplicação avançada (fuzzy matching)
- [ ] Alertas (novos leads A em tempo real)

---

## 📝 Licença

Proprietário - Averta Logística Inteligente

---

## 🤝 Contato

Para dúvidas ou suporte: equipe-dados@averta.com.br