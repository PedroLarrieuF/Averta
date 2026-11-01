# Kanban Cards - AvertaSaaS

## Como usar

Este é um quadro Kanban baseado em arquivos markdown. Cada card é um arquivo `.md` nas colunas:

```
cards/
├── 00-README.md           # Este arquivo
├── backlog/               # Futuras tarefas, ideias, tech debt
├── ready/                 # Prontas para serem pegas (bem definidas)
├── in-progress/           # Sendo trabalhadas agora
├── review/                # Aguardando review/approval
└── done/                  # Concluídas
```

## Fluxo de Trabalho

1. **Tech Lead** cria cards em `backlog/` baseados no review
2. **Tech Lead** move para `ready/` quando bem definidas (Definition of Ready)
3. **Agente** (Frontend/Backend/QA) move para `in-progress/` ao começar
4. **Agente** move para `review/` ao terminar (PR aberto)
5. **Tech Lead** revisa e move para `done/` ou devolve para `in-progress/`

## Convenção de Nomes

```
{numero}-{agente}-{titulo-breve}.md
```

Exemplos:
- `01-frontend-setup-vitest-rtl.md`
- `02-backend-rate-limiter-redis.md`
- `03-techlead-decide-nestjs.md`

## Agentes Disponíveis

| Agente | Arquivo | Foco |
|--------|---------|------|
| Frontend | `frontend-agent.md` | Features, páginas, componentes |
| Backend | `backend-agent.md` | API, rules engine, tasks |
| Tech Lead | `techlead-agent.md` | Review, arquitetura, decisões |
| Frontend QA | `frontend-qa-agent.md` | Testes, cobertura, a11y |
| Backend QA | `backend-qa-agent.md` | Testes integração, rules |

## Labels (usar no frontmatter)

- `priority`: critical, high, medium, low
- `type`: feature, bug, tech-debt, chore, decision
- `agent`: frontend, backend, techlead, frontend-qa, backend-qa
- `sprint`: 1, 2, 3, ...
- `estimate`: XS, S, M, L, XL