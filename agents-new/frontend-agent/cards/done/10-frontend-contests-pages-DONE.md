---
id: 10
title: "Build Contests Workflow Pages (Create, Detail, Negotiate, Payments)"
priority: critical
type: feature
agent: frontend
sprint: 2
estimate: XL
status: done
created: 2026-11-01
reviewed_by: techlead
---

# Card 10: Build Contests Workflow Pages

## Contexto
Fluxo completo de contestação: seleção discrepâncias → criar contestação → PDF → enviar → negociar → pagamentos → success fee.

## Definition of Ready
- [x] API: POST /contests, GET /contests, GET /contests/{id}, POST /contests/{id}/send, PATCH /contests/{id}/negotiate, POST /contests/{id}/payments
- [x] Discrepancies page (Card 09) - origem da seleção
- [x] Design system + PDF viewer

## Tasks
- [ ] `src/pages/ContestCreatePage.tsx` - stepper: select discrepancies → review → create
- [ ] `src/pages/ContestsPage.tsx` - lista com status workflow (DRAFT→SENT→NEGOTIATING→ACCEPTED/PARTIAL/REJECTED)
- [ ] `src/pages/ContestDetailPage.tsx` - timeline, items, communications, payments
- [ ] `src/pages/ContestNegotiatePage.tsx` - atualizar status, registrar comunicação
- [ ] Hooks:
  - `src/hooks/useContests.ts` - CRUD + workflow actions
  - `src/hooks/useContestWorkflow.ts` - send, negotiate, payment
- [ ] Componentes:
  - `src/components/contests/ContestTable.tsx` - status badge, progress indicator
  - `src/components/contests/ContestCreateStepper.tsx` - 3 steps
  - `src/components/contests/ContestTimeline.tsx` - vertical timeline
  - `src/components/contests/ContestItemTable.tsx` - discrepâncias na contestação
  - `src/components/contests/CommunicationThread.tsx` - mensagens + anexos
  - `src/components/contests/PaymentForm.tsx` - registrar pagamento
  - `src/components/contests/SuccessFeeCalculator.tsx` - mostra cálculo em tempo real
  - `src/components/contests/ContestPDFViewer.tsx` - iframe/blob para PDF gerado
- [ ] PDF Generation:
  - Botão "Gerar PDF" → POST /contests/{id}/send → polling status
  - Preview PDF antes de enviar
  - Download PDF
- [ ] Success Fee Display:
  - `success_fee = total_recovered * (contract.success_fee_pct / 100)`
  - `net_recovery = total_recovered - success_fee`
  - Mostrar breakdown visual

## Acceptance Criteria
- [ ] Criar contestação a partir de discrepâncias selecionadas
- [ ] PDF gerado corretamente (visualizar + download)
- [ ] Workflow status transitions funcionam
- [ ] Comunicações registradas (inbound/outbound)
- [ ] Pagamentos registrados → success fee calculado
- [ ] Notificações toast em cada ação
- [ ] Testes integração fluxo completo

## Referências
- `backend/README.md` - seção "Contestação & Success-Fee", "Fluxo de Auditoria"
- `frontend/utils/helpers.ts` - CONTEST_STATUS, formatCurrency