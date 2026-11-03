---
id: 33
title: "Epic: NF-e Audit Rules Implementation (17 rules)"
priority: critical
type: epic
agent: po-scrum
sprint: 3
estimate: XL
status: ready
created: 2026-11-03
reviewed_by: techlead
dependencies: ["32"]
---

# Epic #33: NF-e Audit Rules Implementation (17 rules)

## Contexto do Negócio

O PO identificou que **17 regras de auditoria específicas para NF-e** são necessárias para compliance fiscal brasileiro. Atualmente, o `RuleCode` enum em `rules_engine_v2.py` define essas 17 regras (5 CRITICAL, 7 HIGH, 6 MEDIUM) mas **NENHUMA está implementada** no `rules_critical.py`.

As 15 regras atualmente implementadas cobrem lógica geral de frete/ICMS/CT-e, mas **não são as regras NF-e específicas**.

## Breakdown das Regras por Prioridade

### 🔴 CRITICAL (5 regras) - Card #34 (Backend)
| Código | Nome | Descrição |
|--------|------|-----------|
| NFE_ICMS_CALCULO | Validação Cálculo ICMS NF-e | Verificar base, alíquota, valor ICMS por UF |
| NFE_ICMS_ST | Validação ICMS ST NF-e | Produtos sujeitos a ST |
| NFE_DIFAL | Diferencial de Alíquota | Interestadual para não-Simples |
| NFE_FRETE_NA_BASE | Frete na Base ICMS | Inclusão correta do frete |
| NFE_CTE_CROSS | Cross NF-e × CTE | Matching por chave, valores, pesos |

### 🟠 HIGH (7 regras) - Card #35 (Backend)
| Código | Nome | Descrição |
|--------|------|-----------|
| NFE_FCP | Fundo Combate à Pobreza | Interestadual com FCP |
| NFE_CFOP_FRETE | CFOP Operações de Frete | CIF/FOB, interestadual/intrastadual |
| NFE_CFOP_INTERSTADUAL | CFOP Interestadual | Deve iniciar com 6.xxx |
| NFE_NCM_CEST | NCM/CEST Pairing | Validação Convênio ICMS 142/2018 |
| NFE_VALOR_TOTAL | Valor Total NF-e | Soma itens + impostos + frete ≈ vNF |
| NFE_TRANSPORTADORA | Dados Transportadora | CNPJ/IE/UF/Placa/RNTRC |
| NFE_DESTINATARIO | Dados Destinatário | CNPJ/CPF/IE/Endereço/UF |

### 🟡 MEDIUM (6 regras) - Card #36 (Backend)
| Código | Nome | Descrição |
|--------|------|-----------|
| NFE_PESO_VOLUME | Peso/Volume Consistência | Líquido/bruto vs volumes, cubagem |
| NFE_COMPLEMENTAR | NF-e Complementar | Referencia NF-e, campos válidos, ≤720h |
| NFE_CARTA_CORRECAO | Carta de Correção | Campos, códigos motivo, autorização |
| NFE_CANCELAMENTO | Cancelamento NF-e | ≤24h, protocolo, justificativa, sem circulação |
| NFE_INUTILIZACAO | Inutilização Numeração | Faixa válida, justificativa, sem uso prévio |
| NFE_REGIME_ESPECIAL | Regime Especial | CRT compatível com regime da empresa |

## Dependências Técnicas

| Componente | Status | Necessário Para |
|------------|--------|-----------------|
| XML Parser NF-e 4.00 | ✅ Done (#12) | Extrair campos das regras |
| Rules Engine v2 + Cache Redis | ✅ Done (#05) | Executar regras com performance |
| Rate Limiting Redis | ✅ Done (#04) | API endpoints das regras |
| Testes de Regras (34 passing) | ✅ Done (#28) | Base para novos testes |
| Testes Rate Limit (15 passing) | ✅ Done (#30) | Base para novos testes |

## Entregas por Sprint

### Sprint 3 (Atual) - Foco: CRITICAL + HIGH
- [ ] **Card #34**: Implementar 5 regras CRITICAL + 15 testes
- [ ] **Card #35**: Implementar 7 regras HIGH + 21 testes
- [ ] **Card #38**: Frontend Dashboard NF-e (paralelo)

### Sprint 4 - Foco: MEDIUM + Frontend
- [ ] **Card #36**: Implementar 6 regras MEDIUM + 18 testes
- [ ] **Card #38**: Completar Frontend (detalhes, config admin)
- [ ] Integração completa end-to-end

## Critérios de Aceitação do Epic

### Backend
- [ ] 18 novas regras registradas no `_load_builtin_rules()`
- [ ] 54 novos testes unitários (3 por regra mínimo)
- [ ] Total: 88 testes passing (34 existing + 54 new)
- [ ] Cache TTL correto por prioridade (1800s/3600s/7200s)
- [ ] Tags de relevância para filtering O(tag)

### Frontend
- [ ] Dashboard NF-e com lista de 18 regras
- [ ] Filtro por prioridade (Critical/High/Medium)
- [ ] Visualização de discrepâncias com evidências
- [ ] Configuração admin (enable/disable, thresholds)

### Qualidade
- [ ] Zero ruff errors novo código
- [ ] Zero mypy errors
- [ ] Cobertura ≥80% nas novas regras
- [ ] Documentação atualizada (README, ADR se necessário)

## Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Complexidade cálculo ICMS/DIFAL/FCP | Alta | Alto | Pair programming, validação com contador |
| Dados de referência (NCM/CEST, UF, CFOP) | Média | Médio | Carregar de `app/data/` versionado |
| Performance 18 regras + cache | Baixa | Médio | Tags de relevância, TTL otimizado |
| Mudança legislação | Média | Alto | Regras DB-driven (Card #16) futuro |

## Stakeholders

- **PO**: Validação regras negócio, priorização
- **Tech Lead**: Arquitetura, code review, coordenação
- **Backend Agent**: Implementação regras + testes
- **Frontend Agent**: Dashboard + UI discrepâncias
- **QA Agent**: Testes integração, validação cenários

## Definition of Done (Epic)
- [ ] 3 backend cards (#34, #35, #36) Done
- [ ] 1 frontend card (#38) Done
- [ ] 88 testes backend passing
- [ ] Frontend E2E passing
- [ ] Demo para PO/Stakeholders
- [ ] Epic movido para `done/`