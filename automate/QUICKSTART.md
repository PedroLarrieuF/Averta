# Quickstart - Averta Lead Generation Automation

Guia de 5 minutos para rodar a primeira prospecção e obter leads qualificados com números de WhatsApp e emails corporativos.

---

## ⚡ TL;DR (Resumo Rápido)

```bash
cd automate
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python download_scraper.py
python run.py --full --max-queries 50 --max-leads 200
# Resultados em: output/leads_A_B.xlsx, output/whatsapp_ready/ e output/email_ready/
```

---

## 📋 Pré-requisitos

- **Python 3.10+** (testado em 3.11, 3.12, 3.13)
- **Windows 10/11**, Linux ou macOS
- **4 GB RAM** mínimo (8 GB recomendado)
- **Conexão internet** para scraping Google Maps

---

## 🛠️ Passo a Passo Completo

### 1. Clone/Entre no Diretório

```bash
cd D:\Averta\automate  # Ou onde estiver o projeto
```

### 2. Crie Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale Dependências

```bash
pip install -r requirements.txt
```

> ⏱️ Leva ~30-60 segundos. Ignore warnings de PATH.

### 4. Obtenha o Binário do Scraper

**Opção A: Download Automático (Recomendado)**
```bash
python download_scraper.py
```
Baixa binário pré-compilado para sua arquitetura (Windows/Linux/Mac).

**Opção B: Compilar do Source (Requer Go 1.21+)**
```bash
# Linux/Mac
./build_scraper.sh

# Windows PowerShell
.\build_scraper.ps1

# Windows CMD
build_scraper.bat
```

### 5. Teste Rápido (Opcional)

```bash
# Gera 5 queries de teste para MG
python run.py --generate-queries --priorities 1 --max-queries 5
```
Deve criar arquivo em `queries/generated/queries_only_YYYYMMDD_HHMMSS.txt`

### 6. Execute Primeira Prospecção

**Teste Rápido (2-3 min):**
```bash
python run.py --full --max-queries 50 --max-leads 200
```

**Produção (15-30 min):**
```bash
python run.py --full --priorities 1 2
```

---

## 📁 Onde Encontrar os Resultados

Após execução, verifique a pasta `output/`:

```
output/
├── leads_A_B.xlsx              ← LEADS PRINCIPAIS (A e B)
├── leads_C.xlsx                ← Leads para enriquecer (C)
├── whatsapp_ready/
│   └── leads_whatsapp_YYYYMMDD.xlsx  ← PRONTOS PARA WHATSAPP
├── email_ready/
│   ├── leads_email_YYYYMMDD.csv      ← PRONTOS PARA EMAIL (CSV)
│   └── leads_sendgrid_YYYYMMDD.csv   ← FORMATO SENDGRID
└── reports/
    ├── daily_YYYYMMDD.xlsx     ← Relatório completo do dia
    └── coverage_YYYYMMDD.xlsx  ← Cobertura por estado/segmento
```

### O que tem no `leads_A_B.xlsx`?

| Coluna | Exemplo | Uso |
|--------|---------|-----|
| `company_name` | "Distribuidora Alimentos LTDA" | Nome da empresa |
| `trade_name` | "Distribuidora Alimentos" | Nome fantasia |
| `segment` | "distribuidoras" | Segmento ICP |
| `city` / `state` | "Campinas" / "SP" | Localização |
| `whatsapp` | "+55 19 99999-9999" | **WhatsApp Business** |
| `phone` | "+55 19 3333-4444" | Telefone fixo |
| `email` | "contato@distribuidora.com.br" | E-mail corporativo |
| `decision_makers` | `[{"name":"João Silva","role":"Dir. Logística"}]` | Decisor + cargo |
| `score` | `87.5` | Score 0-100 |
| `classification` | `A` | A=85+, B=70-84 |

### O que tem no `whatsapp_ready/leads_whatsapp_YYYYMMDD.xlsx`?

| Coluna | Descrição |
|--------|-----------|
| `contact_name` | Nome do decisor (ex: "João") |
| `contact_role` | Cargo (ex: "Diretor de Logística") |
| `whatsapp` | Número WhatsApp validado |
| `template_suggested` | Template ideal (ex: "initial_contact") |
| `opt_in_status` | "unknown" (ainda não contatado) |

### O que tem no `email_ready/leads_email_YYYYMMDD.csv`?

| Coluna | Descrição |
|--------|-----------|
| `company_name` | Razão social da empresa |
| `trade_name` | Nome fantasia |
| `contact_name` | Nome do decisor (ex: "João") |
| `contact_first_name` | Primeiro nome (ex: "João") |
| `contact_role` | Cargo (ex: "Diretor de Logística") |
| `email` | Email corporativo validado |
| `segment` | Segmento ICP (ex: "distribuidoras") |
| `city` / `state` | Localização |
| `score` | Score 0-100 |
| `classification` | A ou B |
| `template_suggested` | Template inicial (ex: "initial_outreach") |
| `scheduled_at` | Data/hora agendada para envio |
| `priority` | 1=Alta, 2=Média, 3=Baixa |

---

## 🎯 Entendendo as Classificações

| Classe | Score | Significado | Ação |
|--------|-------|-------------|------|
| **A** | 85-100 | **Excelente** - Fit perfeito, dados completos | Contatar prioridade 1 |
| **B** | 70-84 | **Qualificado** - Bom fit, dados bons | Contatar prioridade 2 |
| **C** | 50-69 | **Precisa enriquecer** - Fit médio, dados parciais | Enriquecer antes de contatar |
| **D** | < 50 | **Não qualificado** - Negativo ou dados ruins | Ignorar |

**Meta**: Focar em **A + B** para prospecção ativa.

---

## 🔧 Comandos Úteis do Dia a Dia

```bash
# Ver help completo
python run.py --help

# Apenas gerar queries (rápido)
python run.py --generate-queries --priorities 1 --max-queries 100

# Re-qualificar leads existentes (sem rescrapear)
python run.py --qualify --max-leads 5000

# Re-exportar planilhas (após qualificação manual)
python run.py --export

# Modo contínuo (roda todo dia às 6h via cron/systemd)
python run.py --continuous --interval 24 --max-runs 7

# --- EMAIL OUTREACH (NOVO) ---
# Preparar contatos para email (exporta CSV)
python run.py --email-prepare --classifications A B --min-score 70

# Dry run - ver quem seria contatado
python run.py --email-campaign --campaign-name "Q1_2024" --classifications A B --min-score 75

# Execução real - enviar emails
python run.py --email-campaign --execute --campaign-name "Q1_2024"

# Teste unitário - email para um lead específico
python run.py --email-test --lead-id LEAD_123 --email-template initial_outreach

# Estatísticas de campanhas
python run.py --email-stats
```

---

## ⚙️ Personalização Rápida

### Querer mais/menos leads?

```yaml
# config/settings.yaml
scraper:
  limits:
    max_queries_per_run: 200    # Aumentar para mais cobertura
    max_results_per_query: 500  # Resultados por query
```

### Querer thresholds mais brandos?

```yaml
# config/settings.yaml
qualification:
  thresholds:
    A_min: 80   # Era 85
    B_min: 65   # Era 70
    C_min: 45   # Era 50
```

### Querer só certos estados?

```bash
# Via CLI (usa priorities do config)
python run.py --full --priorities 1      # SP, RJ, MG, RS, PR, SC
python run.py --full --priorities 1 2    # + BA, PE, CE, GO, DF, ES
python run.py --full --priorities 1 2 3  # Todos 27 estados
```

---

## 🐛 Problemas Comuns

| Problema | Solução |
|----------|---------|
| `google-maps-scraper binary not found` | Rode `python download_scraper.py` |
| `Permission denied` (Linux/Mac) | `chmod +x google-maps-scraper` |
| Scraper travando / timeout | Aumente `exit_on_inactivity: "10m"` no settings.yaml |
| Poucos leads A/B | Reduza thresholds ou aumente `max_queries_per_run` |
| Memória alta | Reduza `batch_size_scrape: 50` e `max_workers_scraper: 2` |
| Erro import módulo | Use `PYTHONPATH=src python run.py ...` |

---

## 📱 Próximos Passos (WhatsApp)

Quando quiser ativar envio de mensagens:

### WhatsApp Business API
1. **Configure credenciais Meta** em `config/settings.yaml`:
```yaml
whatsapp:
  enabled: true
  cloud_api:
    business_account_id: "SEU_ID"
    phone_number_id: "SEU_ID"
    access_token: "SEU_TOKEN"
```

2. **Teste dry-run** (não envia, só mostra quem seria contatado):
```bash
python run.py --whatsapp-campaign --campaign-name "Teste" --classifications A B --min-score 75
```

3. **Execute real** (quando aprovado):
```bash
python run.py --whatsapp-campaign --execute --campaign-name "Campanha_Q1"
```

### Email Outreach (Zoho SMTP) - JÁ CONFIGURADO ✅
O email já está configurado com `contato@avertabrasil.com.br` via Zoho SMTP (credenciais no `.env`).

**Templates atualizados**: Foco em **Auditoria de Fretes (CT-e/NF-e)** - identificação de divergências, cobranças indevidas e recuperação de valores.

1. **Verifique configuração** em `config/settings.yaml`:
```yaml
email:
  enabled: true
  smtp:
    host: "smtppro.zoho.com"
    port: 465
    from_email: "contato@avertabrasil.com.br"
    from_name: "Equipe Averta"
```

2. **Prepare contatos** (exporta CSV para revisão):
```bash
python run.py --email-prepare --classifications A B --min-score 70
```

3. **Teste dry-run** (não envia, só mostra quem seria contatado):
```bash
python run.py --email-campaign --campaign-name "Q1_2024" --classifications A B --min-score 75
```

4. **Execute real** (envia emails via Zoho SMTP):
```bash
python run.py --email-campaign --execute --campaign-name "Q1_2024"
```

5. **Teste unitário** (envia email de teste):
```bash
python run.py --email-test --lead-id LEAD_123 --email-template initial_outreach
```

**Sequência automática** (7 emails ao longo de 45 dias) - **NOVO FOCO: Auditoria de Fretes**:
- Dia 0: `initial_outreach` - Oportunidade: divergências/cobranças indevidas em faturas de frete (CT-e/NF-e)
- Dia 3: `follow_up_1` - Reforço + case similar (implementação 30 dias, ROI 1º mês)
- Dia 7: `follow_up_2` - Case study completo do segmento
- Dia 14: `value_proposition` - 5 benefícios (cobranças > contratado, divergências fiscais, auditoria auto, contestações, valores recuperados)
- Dia 21: `case_study` - Case detalhado com métricas de recuperação financeira
- Dia 30: `meeting_request` - CTA direto agendar 15 min
- Dia 45: `breakup` - Opt-out respeitoso LGPD

---

## 📞 Suporte Rápido

- **Logs**: `logs/automation.log` (nível INFO)
- **Debug**: `python run.py --full --verbose` (nível DEBUG)
- **Banco**: `data/master.db` (SQLite - pode abrir com DB Browser)
- **Issues**: Reporte para equipe-dados@averta.com.br

---

## ✅ Checklist Primeira Execução

- [ ] Python 3.10+ instalado
- [ ] `venv` criado e ativado
- [ ] `pip install -r requirements.txt` OK
- [ ] `python download_scraper.py` OK (binário em `./google-maps-scraper`)
- [ ] `python run.py --generate-queries --max-queries 5` OK
- [ ] `python run.py --full --max-queries 50 --max-leads 200` OK
- [ ] `output/leads_A_B.xlsx` aberto e validado
- [ ] `output/whatsapp_ready/leads_whatsapp_*.xlsx` verificado
- [ ] `output/email_ready/leads_email_*.csv` verificado (NOVO)
- [ ] Leads A/B com WhatsApp válido identificados
- [ ] Leads A/B com Email corporativo válido identificados (NOVO)

---

**Pronto!** 🎉 Sua primeira prospecção está rodando. Os leads A e B em `output/leads_A_B.xlsx` estão prontos para contato manual, automação WhatsApp ou **Email Outreach via Zoho SMTP (contato@avertabrasil.com.br)**.