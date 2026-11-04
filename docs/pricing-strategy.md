# Estratégia de Precificação Competitiva - AvertaSaaS MVP (Revisão Agressiva)

**Versão:** 2.0  
**Data:** 2026-11-03  
**Responsável:** PO/Scrum Master  
**Status:** Para aprovação final - **Modo Guerra (Bootstrapped)**  

---

## 🎯 Princípios Norteadores (Startup Mode)

| Princípio | Decisão |
|-----------|---------|
| **Barreira zero** | Setup fee = **ZERO** para todos |
| **Risco compartilhado** | Success-fee **menor que concorrentes** |
| **Compromisso flexível** | **Mês a mês** (sem fidelidade 12 meses) |
| **API first** | API incluída **desde o Starter** |
| **Volume = desconto** | Escala automática, sem negociação |
| **Time-to-value** | Onboarding **< 7 dias** ou não cobramos o mês |

---

## 💰 Nova Tabela - Modo Agressivo (MVP)

### Planos Principais

| Plano | Frete/Mês | Success-Fee | Minimum/Mês | Platform Fee | API | Contrato |
|-------|-----------|-------------|-------------|--------------|-----|----------|
| **Free Trial** | Até R$ 100k | **12%** | **R$ 0** | **R$ 0** | ✅ Básica | 30 dias |
| **Starter** | R$ 100k-500k | **14%** | **R$ 1.500** | **R$ 300** | ✅ Completa | Mês a mês |
| **Growth** | R$ 500k-2M | **16%** | **R$ 3.000** | **R$ 500** | ✅ + Webhooks | Mês a mês |
| **Scale** | R$ 2M-10M | **14%** | **R$ 6.000** | **R$ 800** | ✅ + SSO + Dedicado | Mês a mês |
| **Enterprise** | > R$ 10M | **12%** | **R$ 12.000** | Custom | ✅ White-label | Anual (negociado) |

> **Nota:** API **própria** incluída em todos os planos. **Não há conectores ERP/TMS nativos** — o cliente integra via nossa REST API + Webhooks. Documentação OpenAPI/Swagger + Sandbox disponíveis desde o Free Trial.

> **Regra:** Fatura = `max(Success-Fee real, Minimum)` — **sem surpresas**

### Comparativo Direto vs Concorrentes (Cenário R$ 1M frete/mês)

| Custo Mensal | Datafrete | FreteControl | YLIP | **AvertaSaaS Growth** |
|--------------|-----------|--------------|------|----------------------|
| Fee Fixo | R$ 3.500 | R$ 2.500 | R$ 1.800 | **R$ 3.500** (min + platform) |
| Success-Fee (15%) | R$ 37.500 | - | R$ 25.000 | **R$ 40.000** (16%) |
| **Total/Mês** | **R$ 41.000** | **R$ 2.500** | **R$ 26.800** | **R$ 40.000** |
| **Recuperação Estimada** | 12% (R$ 120k) | 10% (R$ 100k) | 12% (R$ 120k) | **25% (R$ 250k)** |
| **Líquido Cliente** | **R$ 79k** | **R$ 97.5k** | **R$ 93.2k** | **R$ 210k** |
| **ROI Cliente** | **2.9x** | **39x** | **3.5x** | **6.0x** |

> **Nosso pitch:** *"Cobramos success-fee parecido, mas entregamos **2.5x mais recuperação** porque auditamos NF-e + CT-e juntos. No fim, seu bolso recebe **R$ 210k vs R$ 80-100k** deles."*

---

## 🚀 Programa "Primeiros 50" - Condições Fundadores

| Benefício | Detalhe | Expira |
|-----------|---------|--------|
| **Success-Fee vitalício** | **13% fixo** (vs 14-16% tabela) | 50 primeiros |
| **Minimum vitalício** | **25% desconto** na minimum | 50 primeiros |
| **Platform Fee** | **50% desconto** vitalício | 50 primeiros |
| **API** | Inclusa desde dia 1 (sem platform fee) | 50 primeiros |
| **Onboarding** | **< 10 dias ou 50% desconto mês 1** | 50 primeiros |
| **Suporte** | Canal Slack direto com founders | 50 primeiros |
| **Contrato** | **Mês a mês, cancela quando quiser** | 50 primeiros |
| **Roadmap vote** | Peso 2x em features | 50 primeiros |

> **Meta:** Fechar 50 "Founding Customers" em **90 dias** pós-launch

---

## 🆓 Free Trial Real (Não "Demo")

| Item | Detalhe |
|------|---------|
| **Duração** | 30 dias corridos |
| **Volume** | Até R$ 100k frete auditado |
| **Success-Fee** | **12%** (mesmo do Enterprise) |
| **Minimum** | **R$ 0** |
| **API** | Acesso completo (sandbox + prod) |
| **Setup** | Auto-service via portal (XML/API) |
| **Conversão** | Auto-upgrade para Starter se quiser continuar |
| **Sem cartão** | Só CNPJ + acesso SEFAZ/XML |

**Por que funciona:** Cliente vê **dinheiro real recuperado** em 30 dias → decisão óbvia.

---

## 📈 Escada de Valor (Land & Expand Automático)

```
Mês 1: Free Trial (R$ 100k frete) → Recupera R$ 25k → Paga R$ 3k (12%)
Mês 2: Starter (R$ 300k frete)   → Recupera R$ 75k → Paga R$ 10.5k (14%)
Mês 4: Growth (R$ 800k frete)    → Recupera R$ 200k → Paga R$ 32k (16%)
Mês 8: Scale (R$ 3M frete)       → Recupera R$ 750k → Paga R$ 105k (14%)
Mês 12: Enterprise (R$ 15M)      → Recupera R$ 3.75M → Paga R$ 450k (12%)
```

**Expansion Revenue:** +20% ao ano por cliente (upsell volume + módulos)

---

## 🔌 API Própria - Incluída Desde Free Trial

| Feature | Free Trial | Starter | Growth | Scale | Enterprise |
|---------|------------|---------|--------|-------|------------|
| REST API | ✅ | ✅ | ✅ | ✅ | ✅ |
| Webhooks | ❌ | ✅ | ✅ | ✅ | ✅ |
| Sandbox | ✅ | ✅ | ✅ | ✅ | ✅ |
| Rate Limit | 100 req/min | 500 req/min | 2.000 req/min | 10k req/min | Custom |
| SSO (SAML/OIDC) | ❌ | ❌ | ❌ | ✅ | ✅ |
| SLA API | 99% | 99.5% | 99.9% | 99.95% | 99.99% |

> **Modelo:** Plataforma **API-first** — cedemos endpoints REST + Webhooks + documentação OpenAPI + Sandbox. **O cliente é responsável pela sua integração** (seu time, seu TMS, seu ERP). Não desenvolvemos nem mantemos conectores nativos para ERPs/TMSs de terceiros.

---

## 💳 Faturamento Simples & Transparente

```
Ciclo Mensal:
1. Dia 1-5: Processa lote anterior (NF-e + CT-e via API/XML)
2. Dia 5: Dashboard mostra discrepâncias + valor recuperável
3. Dia 10: Auto-aprovação (cliente não faz nada = aprova)
4. Dia 12: Fatura gerada = max(Success-Fee, Minimum)
5. Dia 15: Vencimento (PIX 2% off / Boleto / Cartão)
6. Dia 30: Suspensão se > 15 dias atraso (recupera ao pagar)
```

**Zero burocracia:** Nota fiscal emitida automaticamente, integração contábil nativa.

---

## 🛡️ Garantias que Removem Risco do Cliente

| Garantia | Detalhe |
|----------|---------|
| **ROI Mínimo 3x** | Se em 90 dias não recuperar 3x o que pagou, **devolvemos a diferença** |
| **Onboarding < 7 dias** | Se não estiver rodando em 7 dias úteis, **mês 1 grátis** |
| **Sem fidelidade** | Cancela no portal, **sem multa, sem aviso prévio** |
| **Dados seus** | Exporta tudo (JSON/CSV/PDF) a qualquer momento |
| **Auditoria aberta** | Metodologia documentada, cliente pode auditar quando quiser |

---

## 🎯 Battle Cards Atualizados (Modo Guerra)

### vs Datafrete (R$ 3-5k fixo + 10-15%)
> **"Vocês pagam R$ 3.500/mês ANTES de recuperar 1 real. Com a gente, primeiro recupera, depois paga 14% do que achou. E a gente acha 2.5x mais porque olha NF-e + CT-e juntos."**

### vs FreteControl (R$ 1.5-3k fixo, sem success-fee)
> **"Preço fixo parece barato... até você perceber que eles não têm incentivo para achar mais. Nós só ganhamos se você ganha mais. Alinhamento total."**

### vs YLIP (R$ 1-2.5k + 10% só e-comm)
> **"Só comparam tabelas. A gente audita o que **realmente foi cobrado** vs contrato + impostos na NF-e. Frete não é só tabela."**

### vs Renota/Agente Tributário (R$ 297/mês, só fiscal)
> **"Barato que não olha frete = caro. ICMS/ST/DIFAL/FCP no frete representam 40-60% da recuperação. Separar perde dinheiro."**

### vs Audfrete (TMS + auditoria R$ 3-8k)
> **"TMS preso + auditoria presa. A gente é best-of-breed: API aberta para seu time integrar no SEU TMS/ERP. Você não troca o que funciona, nem depende de conector nosso."**

---

## 📊 Projeção Agressiva - Primeiros 12 Meses

| Mês | Free Trials | Pagantes | MRR | ARR | CAC | LTV | Caixa |
|-----|-------------|----------|-----|-----|-----|-----|-------|
| 1 | 20 | 0 | R$ 0 | - | R$ 5k | - | R$ 200k |
| 2 | 35 | 5 | R$ 12k | R$ 144k | R$ 4k | R$ 120k | R$ 150k |
| 3 | 50 | 15 | R$ 45k | R$ 540k | R$ 3k | R$ 180k | R$ 100k |
| 4 | 40 | 30 | R$ 110k | R$ 1.3M | R$ 2.5k | R$ 220k | R$ 50k |
| 5 | 30 | 50 | R$ 220k | R$ 2.6M | R$ 2k | R$ 280k | **Break-even** |
| 6 | 25 | 75 | R$ 380k | R$ 4.6M | R$ 1.8k | R$ 320k | R$ 100k |
| 9 | 20 | 150 | R$ 850k | R$ 10M | R$ 1.5k | R$ 400k | R$ 500k |
| 12 | 15 | 250 | R$ 1.5M | **R$ 18M** | R$ 1.2k | R$ 500k | **R$ 1.2M** |

**Assunções conservadoras:**
- Conversão Trial → Pago: **40%** (indústria 15-25%)
- Churn mensal: **3%** (indústria 5-7%)
- Expansão conta: **+15%/ano**
- CAC: **R$ 1-5k** (inbound + outbound founder-led)

---

## 🎪 Go-to-Market Tático (Próximos 90 Dias)

### Semana 1-2: Fundação
- [ ] Landing page com calculadora ROI pública
- [ ] Portal auto-service trial (CNPJ + XML → resultado em 24h)
- [ ] Deck 1-pager + caso estudo template
- [ ] Contrato mestre mês-a-mês (3 páginas)

### Semana 3-4: Primeiros 10 (Founders)
- [ ] Lista 200 ICP (industrial, atacado, agro, e-comm > R$ 200k frete/mês)
- [ ] 50 warm intros via network (investidores, advisors, ex-colegas)
- [ ] 20 discovery calls → 10 trials → **5 pagantes**

### Mês 2: Escala Inicial
- [ ] Content: "Como recuperei R$ 50k em frete no mês 1" (case anônimo)
- [ ] LinkedIn outbound automatizado (fundador + SDR jr)
- [ ] Parcerias: Contadores, consultorias tributárias (revshare 20%)
- [ ] Meta: **20 pagantes**

### Mês 3: Traction
- [ ] Webinar mensal "Auditoria frete na prática"
- [ ] Programa indicação: cliente indica = 1 mês grátis para ambos
- [ ] Primeiro case study nominal (com autorização)
- [ ] Meta: **50 pagantes** (encerra "Primeiros 50")

---

## 📋 Checklist Aprovação Final (Esta Semana)

| Área | Decisão Necessária | Responsável |
|------|-------------------|-------------|
| **Pricing** | Aprovar tabela agressiva + "Primeiros 50" | Founders |
| **Financeiro** | Validar unit economics (LTV/CAC > 3, payback < 4 meses) | CFO/Founder |
| **Jurídico** | Contrato mês-a-mês 3 páginas + termos API | Legal/Founder |
| **Produto** | Onboarding < 7 dias validado (3 beta users) | Tech Lead |
| **Tech** | API sandbox + webhooks + documentação OpenAPI | Tech Lead |
| **Vendas** | Deck, 1-pager, calculadora ROI, email sequences | Founder/Sales |
| **Marketing** | Landing page, trial flow, case study template | Founder/Marketing |

---

## 🔗 Referências (Atualizadas)

1. **Mercgroup** - [Faixas Preço Auditoria 2026](https://www.mercgroup.com.br/insights/quanto-custa-uma-auditoria)
2. **Datafrete** - [Auditoria Fretes](https://www.datafrete.com/auditoria-de-fretes/)
3. **FreteControl Pro** - [Site](https://www.fretecontrolpro.com.br/)
4. **YLIP** - [Comparação Tabelas](https://www.ylip.com.br/)
5. **Audfrete** - [TMS](https://www.audfrete.com.br/)
6. **Renota** - [IA Fiscal](https://renota.com.br/)
7. **Agente Tributário** - [Planos R$ 297](https://agentetributarioapp.com.br/planos)
8. **Fiscal Monitor** - [Planos](https://fiscal.io/monitor/planos)
9. **Certa Fiscal** - [Preços](https://certafiscal.com.br/precos)

---

## 📝 Controle de Versão

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 2026-11-03 | PO Agent | Versão inicial (conservadora) |
| 2.0 | 2026-11-03 | PO Agent | Modo Guerra: Setup=0, Mês-a-mês, API inclusa, Free Trial real, Primeiros 50 vitalício |
| **2.1** | **2026-11-03** | **PO Agent** | **API-first (sem conectores ERP/TMS), Primeiros 50 ajustado: 13% success-fee, 25% min, 50% platform fee** |

---

## 🎯 Decisão Final Requerida

> **Aprovar modelo agressivo v2.0 para execução imediata.**
>
> - **Setup fee = ZERO** (todos planos)
> - **Contrato = Mês a mês** (sem fidelidade)
> - **API = Inclusa desde Free Trial** (plataforma API-first, sem conectores ERP/TMS nativos)
> - **Free Trial real** (30 dias, 12% success-fee, R$ 0 minimum)
> - **Primeiros 50** = 13% success-fee vitalício + 25% minimum + 50% platform fee
> - **Garantia ROI 3x em 90 dias** ou devolve diferença
>
> **Objetivo:** 50 clientes pagantes em 90 dias, break-even mês 5, ARR R$ 18M mês 12.
>
> **Risco:** Baixo (receita success-fee = alinhada, churn controlado por valor entregue).
> **Upside:** Market share rápido, social proof, network effects via API aberta.

---

**Próximo passo:** Call 30 min founders para bater martelo → execução imediata.