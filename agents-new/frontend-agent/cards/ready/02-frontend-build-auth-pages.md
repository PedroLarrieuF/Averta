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
Páginas de autenticação são a porta de entrada do sistema. Devem seguir o design system e integrar com o backend.

## Definition of Ready
- [x] API: POST /auth/login, POST /auth/register, POST /auth/refresh, POST /auth/logout, POST /auth/forgot-password, POST /auth/reset-password
- [x] Design system components (Button, Input, Card) - Card 07 dependency
- [x] Auth context + storage hooks prontos

## Tasks
- [ ] `src/pages/LoginPage.tsx` - Form com email/senha, validação Zod, "Lembrar-me", link "Esqueci senha"
- [ ] `src/pages/RegisterPage.tsx` - Multi-step: Company info → Admin user → Confirmation
- [ ] `src/pages/ForgotPasswordPage.tsx` - Email input → envia reset link
- [ ] `src/pages/ResetPasswordPage.tsx` - Token da URL + nova senha + confirmação
- [ ] Hooks:
  - `src/hooks/useAuth.ts` - login, register, logout, forgotPassword, resetPassword
- [ ] Validação client-side com React Hook Form + Zod
- [ ] Tratamento de erros: 401, 422, 429, 500 com toasts
- [ ] Redirecionamento pós-login baseado em role (Dashboard default)
- [ ] Testes: login success, login fail, register flow, password reset flow

## API Contract
```typescript
// POST /auth/login
interface LoginRequest { email: string; password: string; remember_me?: boolean }
interface LoginResponse { access_token: string; refresh_token: string; user: User; expires_in: number }

// POST /auth/register
interface RegisterRequest { 
  company: { name: string; cnpj: string; email: string };
  admin: { name: string; email: string; password: string }
}

// POST /auth/forgot-password { email: string }
// POST /auth/reset-password { token: string; password: string; password_confirm: string }
```

## Acceptance Criteria
- [ ] Login funcional com JWT + refresh token
- [ ] Registro multi-step cria company + admin user
- [ ] Esqueci senha envia email (Mailhog local)
- [ ] Reset senha com token expira em 1h
- [ ] Validação Zod em todos os campos
- [ ] Toasts para sucesso/erro
- [ ] Testes integração com MSW
- [ ] Acessibilidade: labels, aria, focus management

## Referências
- `frontend/src/store/auth-context.tsx` - useAuth() hook
- `frontend/src/services/api.ts` - axios interceptors
- `frontend/src/utils/helpers.ts` - formatters, cn()
- `backend/README.md` - seção "Auth"