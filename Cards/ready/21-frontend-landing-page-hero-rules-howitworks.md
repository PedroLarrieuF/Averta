---
id: 21
title: "Landing Page — Hero, Problem/Solution, 17 Rules Grid, How It Works"
priority: high
type: feature
agent: frontend
sprint: 1
estimate: L
status: ready
created: 2026-11-10
reviewed_by: techlead
---

## Description

Build the main landing page for AvertaSaaS targeting Brazilian shippers. This is the primary conversion surface for inbound/outbound prospects.

## Acceptance Criteria

### Hero Section (Above Fold)
- [ ] Headline: "Auditoria de Frete que se Paga Sozinha"
- [ ] Subheadline: "Só cobramos % do que recuperamos. Zero setup. Zero risco. Piloto em 48h."
- [ ] Primary CTA: "Iniciar Piloto Grátis" (green, sticky on scroll)
- [ ] Secondary CTA: "Calcular Minha Economia" (outline)
- [ ] Trust bar: 3-5 client logos + "R$12M+ recuperados em 2024"
- [ ] Responsive: mobile-first, sticky CTA bottom bar on mobile

### Problem/Solution Section
- [ ] Left column: 3 pain points (planilhas, equipe manual, 5-15% perdido)
- [ ] Right column: 3 solutions (XML→IA→Divergências→Contestação→$$$)
- [ ] Visual: simple 4-step flow diagram with icons

### 17 Regras Grid (Key Differentiator)
- [ ] 4x4 grid cards (16 visible, 17th in "ver todas" modal)
- [ ] Each card: icon, rule name, 1-line value prop, hover tooltip with avg recovery
- [ ] Categories: ICMS (ST/DIFAL/FCP), Frete (peso/cubagem/valor mínimo), Adicionais (pedágio/ad-valorem/GRIS/SICOBAN), CT-e (complementar/anulação/substituição), NF-e (cross-check), ML Anomaly
- [ ] Tag badges: "Alto impacto", "Obrigatório", "Automatizado"

### How It Works (4 Steps)
- [ ] Step 1: Conecta — API/TMS/ERP ou upload XML
- [ ] Step 2: Audita — 17 regras rodam em segundos
- [ ] Step 3: Contesta — PDF jurídico auto-gerado + workflow
- [ ] Step 4: Recupera — Dinheiro na conta. Fee % do ganho
- [ ] 30s Loom-style video embed (placeholder for now)

### Technical Requirements
- [ ] Framer Motion for scroll animations (fade-up, stagger)
- [ ] Counter animation for "R$ recuperados" stat
- [ ] IntersectionObserver for lazy animations
- [ ] SEO meta tags: title, description, OG image, JSON-LD Product schema
- [ ] Performance: <100KB JS gzipped, LCP <2.5s
- [ ] Accessibility: WCAG AA, semantic HTML, focus states

## Design References

- Color palette: CSS variables from `packages/frontend/src/index.css`
- Components: Use design system (Button, Card, Badge, Tooltip from Radix)
- Icons: Lucide React (consistent with app)
- Typography: Inter (already configured)

## API Integration

- [ ] POST `/api/v1/leads` for CTA clicks (source: landing_page, section: hero/rules/calculator)
- [ ] Event tracking: `landing_cta_click`, `landing_scroll_depth`, `calculator_open`

## Dependencies

- Design system components (Card 07) — must be done first
- Lead capture API endpoint (backend card needed)

## Notes

This card covers the "marketing site" — not the authenticated app. Deploy to separate subdomain (app.averta.com.br vs a.verta.com.br) or path (/landing) with separate build config.