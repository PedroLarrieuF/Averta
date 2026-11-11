---
id: 22
title: "Landing Page — ROI Calculator Widget + Lead Capture Form"
priority: high
type: feature
agent: frontend
sprint: 1
estimate: M
status: ready
created: 2026-11-10
reviewed_by: techlead
---

## Description

Build the interactive ROI calculator widget and lead capture form — the highest-conversion element on the landing page.

## Acceptance Criteria

### ROI Calculator Widget
- [ ] **Inputs** (all with validation + helpful defaults):
  - Gasto mensal com frete (R$) — required, number, min 10000
  - Volume de CT-es/mês — required, number, min 100
  - % estimado de erro/overcharge — select: 3% (conservador), 5% (mercado), 8% (alto), custom
  - Modelo de precificação — radio: Progressivo (5%→10%) / Fixo (25% default)

- [ ] **Real-time Calculations** (client-side, no API call):
  - Valor potencial de recuperação/mês = gasto × %erro
  - Fee mês 1 (5% progressivo ou % fixo)
  - Fee mês 2+ (10% progressivo ou % fixo)
  - **Seu líquido mês 1** = recuperação - fee
  - **Seu líquido mês 2+** = recuperação - fee
  - Projeção 12 meses (soma progressiva)

- [ ] **Visual Output**:
  - Large counter: "R$ XX.XXX/mês no seu bolso"
  - Progress bar: fee vs seu ganho
  - 12-month projection chart (simple bars, Recharts or CSS)
  - "Quero esse dinheiro" CTA button (triggers lead form)

- [ ] **Smart Defaults by Vertical** (optional v2):
  - Dropdown: "Meu setor" → pre-fills %erro based on benchmarks

### Lead Capture Form (Modal/Slide-over)
- [ ] Triggered by: Hero CTA, Calculator "Quero esse dinheiro", Rules grid "Ver caso"
- [ ] Fields:
  - Nome completo (required)
  - Email corporativo (required, validate domain)
  - Telefone/WhatsApp (required, mask BR)
  - Empresa (required)
  - Gasto mensal frete (pre-filled from calculator)
  - Volume CT-es (pre-filled)
  - Melhor horário para contato (select: manhã/tarde/qualquer)
  - Checkbox LGPD (required, link to policy)
- [ ] Submit → POST `/api/v1/leads` with:
  - All form fields + calculator inputs + source_section + utm_params
- [ ] Success state: "Agendaremos em 24h" + Calendly embed link
- [ ] Error handling: inline validation, toast notifications

### Analytics Events
- [ ] `calculator_opened` (when widget enters viewport)
- [ ] `calculator_input_change` (debounced, each field)
- [ ] `calculator_result_viewed` (when result visible >3s)
- [ ] `calculator_cta_click` (click "Quero esse dinheiro")
- [ ] `lead_form_opened`
- [ ] `lead_form_submitted` (success/failure)
- [ ] All events: send to GA4, Meta Pixel, HubSpot (via dataLayer)

### Technical Requirements
- [ ] React Hook Form + Zod schema (shared with app forms)
- [ ] Framer Motion for modal/slide-over animation
- [ ] No external deps for calculator logic (pure TS functions)
- [ ] Unit tests for calculation functions (Vitest)
- [ ] Accessible: labels, ARIA, focus trap in modal, keyboard nav
- [ ] Mobile: full-screen modal on <640px

## API Contract (Backend Card Needed)

```
POST /api/v1/leads
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "monthly_freight_spend": "number",
  "monthly_cte_volume": "number",
  "estimated_error_pct": "number",
  "pricing_model": "PROGRESSIVE|FIXED",
  "preferred_contact_time": "MORNING|AFTERNOON|ANY",
  "source": "landing_page",
  "source_section": "hero|calculator|rules|how_it_works|faq",
  "utm_source": "string?",
  "utm_medium": "string?",
  "utm_campaign": "string?",
  "utm_content": "string?",
  "calculator_projection": {
    "monthly_recovery": "number",
    "monthly_fee_m1": "number",
    "monthly_fee_m2": "number",
    "net_m1": "number",
    "net_m2": "number",
    "annual_projection": "number"
  }
}

Response: 201 { "lead_id": "uuid", "calendly_url": "string" }
```

## Dependencies

- Card 21 (landing page structure) — calculator embedded in that page
- Backend: Lead capture endpoint + email notification to sales
- Design system: Button, Input, Select, Checkbox, Modal, Toast (Card 07)

## Notes

- Calculator logic must match backend progressive pricing exactly (5% month 1, 10% month 2+)
- Consider adding "Salvar simulação" → email PDF with results (future)
- A/B test: calculator default %erro (3% vs 5%), CTA text variations