---
id: 02
title: "Build Authentication Pages (Login, Register, Forgot Password)"
priority: critical
type: feature
agent: frontend
sprint: 1
estimate: M
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 02: Build Authentication Pages

## Contexto
Frontend tem apenas setup (main.tsx, auth-context, api.ts). Precisa das páginas de autenticação funcionais.

## Definition of Ready
- [x] Design system pronto (index.css tem btn, input, card, form classes)
- [x] Auth context + storage implementados
- [x] API client com interceptors pronto
- [x] Rotas definidas no App.tsx (precisa criar)

## Tasks
- [ ] Criar `src/pages/LoginPage.tsx`
  - Form com React Hook Form + Zod schema
  - Validação email/senha
  - Loading state, error handling
  - Link para "Esqueci senha" e "Registrar"
- [ ] Criar `src/pages/RegisterPage.tsx`
  - Form multi-step: Company info → User info
  - Validação CNPJ (máscara + validação)
  - Password strength indicator
- [ ] Criar `src/pages/ForgotPasswordPage.tsx`
  - Email input → envia reset token
- [ ] Criar `src/pages/ResetPasswordPage.tsx`
  - Token da URL + nova senha + confirmação
- [ ] Atualizar `App.tsx` com rotas públicas/protegidas
- [ ] Criar `PrivateRoute` e `PublicRoute` wrappers
- [ ] Testes de integração para fluxo de login

## Acceptance Criteria
- [ ] Login com credenciais válidas → redireciona para Dashboard
- [ ] Login inválido → mostra erro amigável
- [ ] Registro cria empresa + usuário → loga automaticamente
- [ ] Fluxo forgot/reset password funciona end-to-end
- [ ] Tokens salvos no localStorage, refresh automático
- [ ] Logout limpa tudo e redireciona para /login

## Componentes Reutilizáveis a Criar
- `src/components/forms/LoginForm.tsx`
- `src/components/forms/RegisterForm.tsx`
- `src/components/forms/PasswordForm.tsx`
- `src/components/ui/Input.tsx` (wrapper do design system)
- `src/components/ui/Button.tsx`

## Referências
- `frontend-agent.md` - seção "Common Tasks"
- `frontend-qa-agent.md` - seção "Integration Tests"
- `TECHLEAD_REVIEW.md` - TD-007