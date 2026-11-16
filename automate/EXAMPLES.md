# Exemplos de Uso - Averta Lead Generation Automation

## Instalação Rápida

```bash
# 1. Entrar no diretório
cd automate

# 2. Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Baixar ou construir o binário do scraper
# Opção A: Download automático (recomendado)
python download_scraper.py

# Opção B: Build from source (requer Go 1.21+)
./build_scraper.sh  # Linux/Mac
# ou
.\build_scraper.ps1  # Windows PowerShell
# ou
build_scraper.bat  # Windows CMD

# 5. Verificar instalação
python run.py --generate-queries --max-queries 5
```

## Execução Básica

### Pipeline Completo (Recomendado)
```bash
# Execução completa com configurações padrão
python run.py --full

# Apenas estados prioritários (1 e 2)
python run.py --full --priorities 1 2

# Limitar para teste rápido
python run.py --full --max-queries 50 --max-leads 100
```

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
# Executar a cada 24 horas indefinidamente
python run.py --continuous --interval 24

# Executar 7 vezes (uma semana) a cada 24h
python run.py --continuous --interval 24 --max-runs 7

# Executar a cada 12 horas apenas nos prioritários
python run.py --continuous --interval 12 --priorities 1
```

## Configuração Personalizada

### Arquivo de Configuração Customizado
```bash
# Usar configuração personalizada
python run.py --full --config /caminho/para/meu_config.yaml
```

### Variáveis de Ambiente
```bash
# Configurar nível de log
export LOG_LEVEL=DEBUG
python run.py --full

# Configurar diretório de saída
export OUTPUT_DIR=/data/leads
python run.py --full
```

## Exemplos de Uso Programático

### Pipeline Completo
```python
from src.main import LeadGenerationAutomation

# Inicializar
automation = LeadGenerationAutomation()

# Executar pipeline completo
result = automation.run_full_pipeline(
    priorities=[1, 2],      # Apenas prioridades 1 e 2
    max_queries=200,        # Máximo 200 queries
    max_leads=5000,         # Processar até 5000 leads
)

if result['success']:
    print(f"Sucesso! Leads A: {result['steps']['qualification']['classified_a']}")
    print(f"Leads B: {result['steps']['qualification']['classified_b']}")
    print(f"Arquivos: {result['steps']['export']['files']}")
else:
    print(f"Falha: {result['errors']}")
```

### WhatsApp Business API - Campanhas Inteligentes
```python
from src.main import LeadGenerationAutomation
from src.whatsapp.client import CampaignBuilder, LeadClassification

automation = LeadGenerationAutomation()

# 1. Criar campanha personalizada com CampaignBuilder
campaign = (CampaignBuilder("Campanha_Personalizada_Q1")
    .with_description("Prospecção ativa para distribuidoras no Sudeste")
    .targeting_classifications(LeadClassification.A, LeadClassification.B)
    .targeting_min_score(80)
    .targeting_segments("distribuidoras", "atacadistas", "industrias")
    .targeting_states("SP", "RJ", "MG", "ES")
    .with_templates(
        initial="initial_contact",
        follow_ups=["follow_up_1", "follow_up_2", "value_proposition", "case_study"],
        intervals_hours=[24, 72, 168, 336]  # 1d, 3d, 7d, 14d
    )
    .with_schedule(
        business_hours_only=True,
        start_hour=8,
        end_hour=18,
        timezone="America/Sao_Paulo",
        rate_per_minute=20,
        rate_per_hour=500,
        rate_per_day=2000
    )
    .max_messages_per_lead(4)
    .with_opt_out_keywords("não quero", "parar", "cancelar", "descadastrar")
    .build())

# Registrar e executar
from src.whatsapp.client import create_messaging_engine, WhatsAppProvider
import asyncio

async def run_custom_campaign():
    engine = await create_messaging_engine(WhatsAppProvider.CLOUD_API)
    engine.register_campaign(campaign)
    
    # Buscar leads do banco
    leads = automation._get_leads_for_campaign(campaign)
    
    # Obter decisores
    decision_makers = {}
    for lead in leads:
        if lead.decision_makers:
            decision_makers[lead.id] = lead.decision_makers[0]
    
    # Executar
    results = await engine.run_campaign(campaign, leads, decision_makers)
    print(f"Resultados: {results}")

asyncio.run(run_custom_campaign())
```

### Personalização Avançada de Mensagens
```python
from src.whatsapp.client import (
    IntelligentMessagingEngine,
    PersonalizationContext,
    WhatsAppProvider,
    create_messaging_engine,
)
from src.storage.master_db import get_master_db
from src.storage.models import QualifiedLead, DecisionMaker
import asyncio

async def personalized_messaging():
    # Inicializar engine
    engine = await create_messaging_engine(WhatsAppProvider.CLOUD_API)
    
    # Buscar lead do banco
    db = get_master_db()
    lead = db.get_qualified_lead("lead_id_aqui")
    
    # Obter decisor (se houver)
    dm = lead.decision_makers[0] if lead.decision_makers else None
    
    # Criar mensagem personalizada com template
    message = engine.create_personalized_message(
        lead=lead,
        template_name="initial_contact",
        decision_maker=dm,
        custom_variables={
            "custom_field_1": "valor personalizado",
            "header_custom": "Header personalizado",
        }
    )
    
    # Ou criar mensagem totalmente customizada
    custom_message = engine.create_custom_message(
        lead=lead,
        text="""Olá {{contact_name}}!
        
        Vi que a {{company_name}} em {{city}} está crescendo.
        A {{our_company}} ajuda empresas de {{segment}} a {{value_prop_1}}.
        
        {{case_study}}
        
        Topa conversar 15 min?""",
        decision_maker=dm,
        custom_variables={
            "meeting_link": "https://calendly.com/averta/15min",
        }
    )
    
    # Enviar
    result = await engine.send_message(message)
    print(f"Enviado: {result}")

asyncio.run(personalized_messaging())
```

### Processamento de Respostas (Webhook)
```python
from src.whatsapp.client import IntelligentMessagingEngine, WhatsAppProvider
import asyncio

# Simular recebimento de webhook do Meta
webhook_data = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": "5511999999999",
                    "id": "wamid.xxx",
                    "timestamp": "1234567890",
                    "type": "text",
                    "text": {"body": "Tenho interesse, me manda mais info"}
                }]
            }
        }]
    }]
}

async def process_incoming():
    engine = await create_messaging_engine(WhatsAppProvider.CLOUD_API)
    
    # Processar mensagem recebida
    result = await engine.process_incoming_message(webhook_data)
    
    if result:
        print(f"Lead: {result['lead_id']}")
        print(f"Mensagem: {result['message']}")
        print(f"Ação: {result['action']}")
        
        # Se lead respondeu, pode criar follow-up personalizado
        if result['action'] == 'reply_received':
            # Lógica para responder automaticamente ou notificar vendedor
            pass

asyncio.run(process_incoming())
```

### Apenas Geração de Queries
```python
from src.scraper.queries import QueryGenerator

gen = QueryGenerator()

# Gerar queries para estados específicos
queries = gen.generate_focused_queries(
    state_codes=['SP', 'RJ', 'MG', 'RS', 'PR', 'SC'],
    segments=['distribuidoras', 'atacadistas', 'industrias'],
    max_per_state=30
)

# Salvar
query_file = gen.save_queries(queries, "minhas_queries.txt")
print(f"Geradas {len(queries)} queries em {query_file}")
```

### Qualificação de Leads Existentes
```python
from src.qualification.scorer import LeadQualificationPipeline
from src.storage.master_db import get_master_db

db = get_master_db()
pipeline = LeadQualificationPipeline()

# Buscar leads não qualificados
leads = db.get_unqualified_leads(limit=1000)
leads_data = [lead.to_dict() for lead in leads]

# Qualificar
qualified = pipeline.qualify_batch(leads_data)

# Salvar
for lead in qualified:
    db.upsert_qualified_lead(lead)

stats = pipeline.get_stats()
print(f"Processados: {stats['total']}")
print(f"A: {stats['classified_a']}, B: {stats['classified_b']}")
```

### Preparação para WhatsApp
```python
from src.whatsapp.prepare import WhatsAppPreparator
from src.storage.master_db import get_master_db
from src.storage.models import LeadClassification

db = get_master_db()
preparator = WhatsAppPreparator()

# Buscar leads A e B prontos para WhatsApp
leads_ab = db.get_leads_for_export()  # A e B
wa_leads = [l for l in leads_ab if l.whatsapp_ready]

# Preparar contatos
contacts = preparator.prepare_leads(wa_leads)

# Agendar envios (respeita horário comercial)
contacts = preparator.get_sending_schedule(
    contacts,
    business_hours_only=True,
    rate_limit_per_minute=20
)

# Exportar para API do WhatsApp
api_file = preparator.export_for_whatsapp_api(contacts)
print(f"Exportado para API: {api_file}")
```

### WhatsApp Business API - Envio de Mensagens
```python
from src.main import LeadGenerationAutomation

automation = LeadGenerationAutomation()

# 1. Dry run - ver quais leads seriam contatados
result = automation.run_whatsapp_campaign(
    campaign_name="Q1_2024_Distribuidoras_SP",
    classifications=["A", "B"],
    min_score=75,
    segments=["distribuidoras", "atacadistas"],
    states=["SP", "RJ", "MG"],
    dry_run=True
)

print(f"Leads que seriam contatados: {result['leads_found']}")
for lead in result['leads_preview'][:5]:
    print(f"  {lead['name']} - {lead['city']}/{lead['state']} - Score: {lead['score']}")

# 2. Executar campanha real (envia mensagens)
result = automation.run_whatsapp_campaign(
    campaign_name="Q1_2024_Distribuidoras_SP",
    classifications=["A", "B"],
    min_score=75,
    segments=["distribuidoras"],
    states=["SP"],
    dry_run=False  # ATENÇÃO: envia mensagens reais!
)

print(f"Enviadas: {result['results']['sent']}")
print(f"Falhas: {result['results']['failed']}")

# 3. Enviar mensagem de teste para um lead específico
result = automation.send_whatsapp_test(
    lead_id="lead_abc123",
    template_name="initial_contact"
)
print(f"Mensagem de teste enviada: {result['success']}")

# 4. Ver estatísticas das campanhas
stats = automation.get_whatsapp_campaign_stats()
for camp_id, camp_stats in stats.items():
    print(f"{camp_stats['name']}: Enviadas={camp_stats['stats']['messages_sent']}, Lidas={camp_stats['stats']['messages_read']}")
```

### WhatsAPI via CLI
```bash
# Dry run da campanha
python run.py --whatsapp-campaign --campaign-name "Minha Campanha" --classifications A B --min-score 75 --segments distribuidoras --states SP RJ

# Executar campanha real
python run.py --whatsapp-campaign --execute --campaign-name "Minha Campanha" --classifications A B --min-score 75

# Enviar mensagem de teste
python run.py --whatsapp-test --lead-id lead_abc123 --template initial_contact

# Ver estatísticas
python run.py --whatsapp-stats
```

### Relatórios Personalizados
```python
from src.export.report_generator import ReportGenerator
from datetime import date, timedelta

report_gen = ReportGenerator()

# Relatório diário
report = report_gen.generate_daily_report(
    report_date=date.today()
)

# Relatório semanal
weekly = report_gen.generate_weekly_report(
    end_date=date.today(),
    weeks_back=1
)

# Relatório de qualidade
quality = report_gen.generate_lead_quality_report()
print(f"Top empresas: {quality['top_companies'][:5]}")
```

## Estrutura de Saída

Após execução, os arquivos são gerados em `output/`:

```
output/
├── leads_A_B.xlsx           # Leads classificados A e B (principais)
├── leads_C.xlsx             # Leads C (precisam enriquecimento)
├── whatsapp_ready/
│   └── leads_whatsapp_YYYYMMDD.xlsx  # Prontos para WhatsApp
├── reports/
│   ├── daily_YYYYMMDD.xlsx  # Relatório diário completo
│   ├── coverage_YYYYMMDD.xlsx        # Cobertura por estado/segmento
│   └── decision_makers_YYYYMMDD.xlsx # Decisores identificados
```

## Colunas Principais (leads_A_B.xlsx)

| Coluna | Descrição |
|--------|-----------|
| id | ID único do lead |
| classification | A ou B |
| score | Score 0-100 |
| company_name | Nome da empresa |
| trade_name | Nome fantasia |
| segment | Segmento ICP |
| city / state | Localização |
| phone / whatsapp | Telefones |
| email | E-mail corporativo |
| website / linkedin | Canais digitais |
| operational_fit_score | Score fit operacional (0-100) |
| commercial_fit_score | Score fit comercial (0-100) |
| data_confidence_score | Score confiança dados (0-100) |
| decision_makers | JSON com decisores |
| institutional_contacts | JSON com contatos institucionais |
| whatsapp_ready | Pronto para WhatsApp |
| whatsapp_template_suggested | Template sugerido |

## KPIs Monitorados

O relatório diário inclui:

- **Queries executadas**
- **Empresas encontradas / únicas**
- **Leads por classificação (A, B, C, D)**
- **Decisores identificados**
- **Contatos válidos (tel, email, WhatsApp, LinkedIn)**
- **Cobertura por estado / segmento**
- **Custo por lead qualificado com contato verificável** (KPI principal)
- **Taxa de qualificação**

## Solução de Problemas

### Binário não encontrado
```bash
# Baixar automaticamente
python download_scraper.py

# Ou construir
./build_scraper.sh
```

### Erro de permissão no binário (Linux/Mac)
```bash
chmod +x google-maps-scraper
```

### Timeout do scraper
Aumente o timeout no `config/settings.yaml`:
```yaml
scraper:
  params:
    exit_on_inactivity: "10m"  # Aumentar de 5m para 10m
```

### Poucos leads qualificados
1. Verifique se as queries estão muito restritivas
2. Aumente `max_queries_per_run`
3. Reduza thresholds em `config/settings.yaml`:
```yaml
qualification:
  thresholds:
    A_min: 80  # Era 85
    B_min: 65  # Era 70
    C_min: 45  # Era 50
```

### Memória insuficiente
Reduza batch sizes:
```yaml
performance:
  batch_size_scrape: 50    # Era 100
  batch_size_qualify: 200  # Era 500
  max_workers_scraper: 2   # Era 4
```

## Agendamento Automático (systemd/cron)

### systemd service
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
# Editar crontab
crontab -e

# Adicionar linha
0 6 * * * cd /opt/averta/automate && /opt/averta/automate/venv/bin/python run.py --full >> /var/log/averta-leads.log 2>&1
```

## Próximos Passos (Roadmap)

1. **Integração WhatsApp Business API** - Envio automático de templates aprovados
2. **Enriquecimento externo** - Hunter.io, Apollo, Clearbit para emails/telefones
3. **Dashboard Web** - Visualização de leads, funil, KPIs em tempo real
4. **API REST** - Expor leads qualificados para CRM/ERP
5. **ML Scoring** - Modelo de ML para melhorar qualificação
6. **Deduplicação avançada** - Fuzzy matching entre execuções
7. **Alertas** - Notificação quando novos leads A aparecem