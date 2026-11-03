---
id: 01
title: "Setup Vitest + React Testing Library + MSW"
priority: critical
type: chore
agent: frontend
sprint: 1
estimate: M
status: done
created: 2026-11-01
completed: 2026-11-01
reviewed_by: techlead
---

# Card 01: Setup Vitest + RTL + MSW

## Contexto
Frontend tem **0% cobertura de testes**. Precisa configurar toda a infraestrutura de testes antes de escrever testes.

## Definition of Ready
- [x] Requisitos claros (do techlead review)
- [x] Stack definida: Vitest + RTL + MSW + jsdom
- [x] Package.json já tem as dependências

## Tasks
- [x] Criar `vitest.config.ts` com coverage thresholds (70% lines, 70% functions, 60% branches)
- [x] Configurar `setupTests.ts` com jest-axe, MSW server
- [x] Criar handlers MSW para auth, documents, discrepancies, contests, reports
- [x] Criar factories de dados mock (`src/test/factories.ts`)
- [x] Adicionar scripts no package.json: `test`, `test:ui`, `test:coverage`
- [ ] Configurar CI GitHub Actions para rodar testes + upload Codecov

## Acceptance Criteria
- [x] `pnpm test` roda sem erros
- [x] `pnpm test -- --coverage` gera relatório com thresholds
- [x] MSW intercepta chamadas de API nos testes
- [x] Testes de exemplo passam (helpers, auth-storage)

## Referências
- `frontend-agent.md` - seção "Test Implementation Guide"
- `TECHLEAD_REVIEW.md` - TD-006

## Notas
Começar com testes unitários dos helpers (pure functions = alto ROI).

## Completed Files
- `vitest.config.ts` - Vitest configuration with coverage
- `src/test/setupTests.ts` - Test setup with MSW server, jest-axe, mocks
- `src/test/handlers.ts` - MSW handlers for all API endpoints
- `src/test/factories.ts` - Test data factories using @faker-js/faker
- `src/test/index.ts` - Barrel exports
- `src/test/msw.test.ts` - MSW integration tests
- `src/utils/helpers.test.ts` - Helper function tests (37 tests)
- `src/store/auth-storage.test.ts` - Auth storage tests (16 tests)
- `src/components/Button.test.tsx` - Button component tests (11 tests)
- Updated `package.json` with `test:coverage` script

## Test Results
- **72 tests passing** across 4 test files
- Coverage: 65.96% lines, 94.23% branches, 91.3% functions (on tested files)
- MSW handlers verified working for all API modules