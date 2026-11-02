# Card: Configuração de Alertas de Mudanças Regulatórias

**ID**: XX-TECHLEAD-ALERT-CONFIG  
**Coluna**: READY  
**Prioridade**: HIGH  
**Estimativa**: 5 SP  
**Sprint**: Próxima  

---

## 🎯 Objetivo
Implementar sistema de monitoramento automatizado de mudanças na legislação brasileira de transporte/frete (ICMS, ANTT, CT-e, Pedágio, Seguros) para manter o Rules Engine v2 sempre atualizado.

---

## 📋 Escopo

### Fontes a Monitorar
| Fonte | Tipo | Frequência | Método |
|-------|------|------------|--------|
| **Diário Oficial da União (DOU)** | Federal | Diária | Web scraping / API IN.gov.br |
| **Diários Oficiais Estaduais (27 UFs)** | Estadual | Diária | Web scraping / APIs estaduais |
| **CONFAZ - Convênios ICMS** | Tributário | Semanal | Site CONFAZ + RSS |
| **ANTT - Resoluções/Portarias** | Transporte | Semanal | Site ANTT + Diário Oficial |
| **SUSEP - Circulares Seguros** | Seguros | Mensal | Site SUSEP |
| **DNIT - Portarias Trânsito** | Rodoviário | Mensal | Site DNIT |
| **CNPJ/IE - Mudanças cadastrais** | Cadastro | Eventual | ReceitaWeb / Sefaz |

### Eventos Críticos que Disparam Alerta
- [ ] Nova Resolução ANTT (piso mínimo, faixas, cubagem)
- [ ] Novo Convênio ICMS (alíquotas, DIFAL, FCP, ST, MVA)
- [ ] Alteração CT-e (layout, tpEmis, campos obrigatórios)
- [ ] Nova tarifa pedágio (concessionárias: CCR, EcoRodovias, Arteris, etc.)
- [ ] Atualização SICOBAN (faixas CEP, valores)
- [ ] Mudança alíquotas Ad Valorem / GRIS (SUSEP)
- [ ] Nova tolerância peso (ANTT)
- [ ] Legislação carga especial (perigosa, frigorífica, projeto, viva)

---

## 🏗️ Arquitetura Proposta

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Coletores      │────▶│  Processador     │────▶│  Notificadores  │
│  (Scrapers/API) │     │  (NLP/Regex)     │     │  (Slack/Email/  │
└─────────────────┘     └──────────────────┘     │   Webhook)      │
                            │                    └─────────────────┘
                            ▼
                   ┌──────────────────┐
                   │  Validador       │
                   │  (Tax Specialist)│
                   └──────────────────┘
                            │
                            ▼
                   ┌──────────────────┐     ┌─────────────────┐
                   │  Atualizador     │────▶│  Rules Engine   │
                   │  JSONs + DB      │     │  (Hot Reload)   │
                   └──────────────────┘     └─────────────────┘
```

### Componentes
1. **Collectors** (Python/Playwright): Um por fonte, agendados via Celery Beat
2. **Processor**: Extrai número, data, ementa, texto relevante; classifica por tag (icms, antt, cte, pedagio, etc.)
3. **Validator**: Fila para revisão humana (Tax Specialist/Contador) antes de aplicar
4. **Updater**: Atualiza JSONs em `backend/app/data/` + tabela `freight_table.rules` no PostgreSQL
5. **Hot Reload**: Sinal para `RulesEngineV2` recarregar regras sem restart

---

## 📦 Entregáveis

### 1. Coleta Automatizada
- [ ] `dou_collector.py` - DOU (IN.gov.br API)
- [ ] `confaz_collector.py` - Convênios ICMS
- [ ] `antt_collector.py` - Resoluções ANTT
- [ ] `concessionarias_collector.py` - CCR, EcoRodovias, Arteris (APIs/Scraping)
- [ ] `susep_collector.py` - Circulares seguros
- [ ] `sefaz_collectors.py` - 27 UFs (priorizar SP, RJ, MG, RS, PR, BA)

### 2. Processamento & Classificação
- [ ] `regulatory_processor.py` - NLP/Regex para extrair: tipo, UF, alíquotas, vigência
- [ ] Schema `RegulatoryChange` (Pydantic) com campos obrigatórios
- [ ] Deduplicação (mesmo ato normativo coletado de múltiplas fontes)

### 3. Workflow de Aprovação
- [ ] Tabela `regulatory_changes_pending` (PostgreSQL/Prisma)
- [ ] Endpoint `/api/v1/regulatory/pending` para revisão
- [ ] Ação: `APPROVE` → aplica em JSONs/DB + notifica; `REJECT` → arquiva

### 4. Notificações
- [ ] Slack webhook (canal #regulatory-alerts)
- [ ] Email para Tax Specialist + Tech Lead
- [ ] Webhook genérico para integrações futuras

### 5. Atualização Automática (Pós-Aprovação)
- [ ] `json_updater.py` - Atualiza os 12 JSONs em `backend/app/data/`
- [ ] `db_updater.py` - Atualiza `freight_table.rules` por empresa
- [ ] Sinal `SIGHUP` ou Redis pub/sub para `RulesEngineV2` recarregar

---

## ✅ Critérios de Aceite

1. **Cobertura**: 100% das fontes críticas (DOU, CONFAZ, ANTT, 5 maiores concessionárias)
2. **Latência**: Alerta em < 4h após publicação oficial
3. **Falsos Positivos**: < 10% (validado por humano antes de aplicar)
4. **Auditoria**: Log completo de coleta → processamento → aprovação → aplicação
5. **Rollback**: Capacidade de reverter JSON/DB se atualização causar regressão
6. **Testes**: Unitários para collectors + processor; integração para fluxo completo

---

## 🔗 Dependências

- **Bloqueia**: Validação dos JSONs com Contador/Tax Specialist (task paralela)
- **Requer**: Redis configurado (para cache + pub/sub hot reload)
- **Requer**: Celery Beat para agendamento collectors
- **Relacionado**: Card "Hot Reload Rules Engine v2" (técnico)

---

## 📝 Notas Técnicas

- **Rate Limiting**: Respeitar `robots.txt` e limites APIs oficiais
- **Idempotência**: Mesmo ato processado 2x não duplica alerta
- **Versionamento**: JSONs com `version` + `updated` (já implementado)
- **Diff**: Mostrar diff JSON anterior vs novo na aprovação
- **Fallback**: Se collector falhar, alerta em log + retry exponencial

---

## 👥 Responsáveis

| Papel | Pessoa | Responsabilidade |
|-------|--------|------------------|
| **Tech Lead** | [A definir] | Arquitetura, code review, deploy |
| **Backend Dev** | [A definir] | Collectors, processor, API |
| **Tax Specialist** | [A definir] | Validação semanal pendências |
| **Contador** | [A definir] | Validação final antes produção |
| **DevOps** | [A definir] | Infra, monitoramento, alertas infra |

---

## 📅 Cronograma Sugerido

| Semana | Foco |
|--------|------|
| 1 | Collectors DOU + CONFAZ + ANTT + Processor básico |
| 2 | Collectors Concessionárias + SUSEP + Sefaz (SP/RJ/MG) |
| 3 | Workflow aprovação + Notificações Slack/Email |
| 4 | Updaters JSON/DB + Hot Reload + Testes + Documentação |

---

**Criado por**: PO/Scrum Master Agent  
**Base**: Pesquisa regulatória completa (18 arquivos .md)  
**Relacionado**: `REVISAO_REGRAS_REGULATORIAS.md` (mesma pasta)