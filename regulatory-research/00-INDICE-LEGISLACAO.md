# Índice da Legislação - AvertaSaaS Auditoria de Frete

**Versão:** 1.0  
**Data:** 2026-11-01  
**Responsável:** PO/Scrum Master  
**Status:** Em pesquisa - Base para Rules Engine v2

---

## 📋 Visão Geral

Este diretório contém a pesquisa regulatória completa que fundamenta as **17 rules do Rules Engine v2**. Cada arquivo detalha a legislação, alíquotas vigentes, fórmulas de cálculo e parâmetros para implementação no backend.

---

## 📁 Estrutura dos Arquivos

| Arquivo | Área | Rules Relacionadas | Prioridade |
|---------|------|-------------------|------------|
| `01-ICMS-DIFAL.md` | ICMS Diferencial (Interestadual) | `ICMS_DIFAL` | CRITICAL |
| `02-ICMS-FCP.md` | FCP - Fundo Combate à Pobreza | `ICMS_FCP` | CRITICAL |
| `03-ICMS-ST.md` | ICMS Substituição Tributária | `ICMS_ST` | CRITICAL |
| `04-FRETE-PESO-VALOR.md` | Frete Peso × Valor (Faixas ANTT) | `FRETE_PESO_VALOR` | CRITICAL |
| `05-FRETE-CUBAGEM.md` | Frete por Cubagem (m³) | `FRETE_CUBAGE` | HIGH |
| `06-PESO-REAL-FATURADO.md` | Peso Real vs Faturado | `PESO_REAL_VS_FATURADO` | HIGH |
| `07-VALOR-MINIMO-FRETE.md` | Piso Mínimo ANTT 5.839/2021 | `VALOR_MINIMO_FRETE` | CRITICAL |
| `08-REDESPACHO.md` | Redespacho (CT-e Complementar) | `REDESPACHO_VALIDACAO` | HIGH |
| `09-PEDAGIO.md` | Conferência de Pedágio | `PEDAGIO_CONFERENCIA` | MEDIUM |
| `10-AD-VALOREM.md` | Ad Valorem (Seguro Valor) | `AD_VALOREM` | MEDIUM |
| `11-GRIS.md` | Gerenciamento de Risco | `GRIS` | MEDIUM |
| `12-SICOBAN.md` | Tabela SICOBAN/ANTT (CEP × Tipo × Modal) | `SICOBAN_TABLE_REAL` | HIGH |
| `13-CTE-COMPLEMENTAR.md` | CT-e Complementares (Anulação/Substituição/Complemento) | `CTE_ANULACAO`, `CTE_SUBSTITUICAO`, `CTE_COMPLEMENTO_VALOR` | HIGH |
| `14-ALIQUOTAS-POR-UF.md` | Tabela consolidada ICMS/FCP/ST por UF | Todas ICMS | CRITICAL |
| `15-NCM-ST.md` | NCMs sujeitos a ST por UF | `ICMS_ST` | HIGH |
| `16-LEIS-BASE.md` | Legislação federal e estadual base | Referência geral | REFERENCE |
| `17-PARAMETROS-CALCULO.md` | Parâmetros consolidados para engine | Configuração rules | CRITICAL |

---

## ⚖️ Legislação Base (Referência Rápida)

### Federal
| Lei/Decreto | Assunto | Status |
|-------------|---------|--------|
| **LC 87/1996** (Lei Kandir) | ICMS interestadual | Vigente |
| **LC 190/2022** | Regulamenta DIFAL (LC 87) | Vigente |
| **Convênio ICMS 174/2023** | FCP - Alíquotas por UF | Vigente |
| **Convênio ICMS 142/2018** | ICMS ST - Protocolo | Vigente |
| **Res. ANTT 5.839/2021** | Piso Mínimo de Frete | Vigente |
| **Res. ANTT 5.868/2022** | Atualização pisos 2023 | Vigente |
| **Lei 11.442/2007** | Transporte rodoviário de cargas | Vigente |
| **Decreto 9.209/2017** | Regulamento CT-e | Vigente |

### Estadual (Exemplos - 27 UFs + DF)
Cada UF possui:
- Decreto estadual do ICMS (RICMS)
- Decreto de ST (produtos sujeitos, MVA, IVA)
- Legislação FCP (desde 2023)

---

## 🔄 Regras do Engine v2 Mapeadas

| Rule Code | Nome | Tipo | Severidade | Tags | Arquivo Principal |
|-----------|------|------|------------|------|-------------------|
| `ICMS_DIFAL` | ICMS Diferencial (DIFAL) | ICMS_DIFFERENTIAL | HIGH | icms, interstate | 01-ICMS-DIFAL.md |
| `ICMS_FCP` | FCP - Fundo Combate Pobreza | ICMS_FCP | HIGH | icms, interstate | 02-ICMS-FCP.md |
| `ICMS_ST` | ICMS Substituição Tributária | ICMS_ST | HIGH | icms, icms_st | 03-ICMS-ST.md |
| `FRETE_PESO_VALOR` | Frete Peso × Valor (faixas) | FREIGHT_WEIGHT_VALUE | HIGH | freight, weight | 04-FRETE-PESO-VALOR.md |
| `FRETE_CUBAGEM` | Frete Cubagem (m³) | FREIGHT_CUBAGE | HIGH | freight, cubage | 05-FRETE-CUBAGEM.md |
| `PESO_REAL_VS_FATURADO` | Peso Real vs Faturado | PESO_REAL_VS_FATURADO | HIGH | weight | 06-PESO-REAL-FATURADO.md |
| `VALOR_MINIMO_FRETE` | Piso Mínimo ANTT 5.839/2021 | VALOR_MINIMO_FRETE | CRITICAL | freight, weight | 07-VALOR-MINIMO-FRETE.md |
| `REDESPACHO_VALIDACAO` | Redespacho (CT-e comp.) | REDESPACHO | HIGH | redespacho | 08-REDESPACHO.md |
| `PEDAGIO_CONFERENCIA` | Conferência Pedágio | TOLL_PLAZA | MEDIUM | toll | 09-PEDAGIO.md |
| `AD_VALOREM` | Ad Valorem (seguro valor) | AD_VALOREM | MEDIUM | advalorem | 10-AD-VALOREM.md |
| `GRIS` | Gerenciamento Risco | GRIS | MEDIUM | gris | 11-GRIS.md |
| `SICOBAN_TABLE_REAL` | Tabela Sicoban/ANTT (CEP) | SICOBAN_TABLE | HIGH | freight, sicoban | 12-SICOBAN.md |
| `CTE_ANULACAO` | CT-e Anulação (tpEmis=3) | COMPLEMENTARY_CTE | HIGH | cte_complementar | 13-CTE-COMPLEMENTAR.md |
| `CTE_SUBSTITUICAO` | CT-e Substituição (tpEmis=2) | COMPLEMENTARY_CTE | HIGH | cte_complementar | 13-CTE-COMPLEMENTAR.md |
| `CTE_COMPLEMENTO_VALOR` | CT-e Complemento (tpEmis=4) | COMPLEMENTARY_CTE | MEDIUM | cte_complementar | 13-CTE-COMPLEMENTAR.md |

---

## 📊 Dados de Referência no Backend

```
backend/app/data/
├── icms_rules.json       # 27 UFs × alíquotas ICMS + FCP + ST por NCM/UF
├── sicoban_table.json    # 22 faixas CEP × tipo × modal + pisos ANTT
└── (novos arquivos a criar)
    ├── antt_faixas_peso_valor.json    # Faixas peso × valor Res. 5.839
    ├── antt_faixas_cubagem.json       # Faixas cubagem
    ├── pedagio_tarifas.json           # Tarifas pedágio por praça/rodovia
    ├── ad_valorem_taxas.json          # Taxas seguro por tipo carga
    ├── gris_taxas.json                # Taxas GRIS por região/risco
    ├── cte_complementar_regras.json   # Regras validação complementares
    └── pesos_tolerancia.json          # Tolerâncias peso real vs faturado
```

---

## ✅ Checklist de Validação (PO + Tech Lead)

Antes de considerar a pesquisa completa:

- [ ] **ICMS DIFAL**: Alíquotas interestaduais 4%, 7%, 12% confirmadas por UF origem/destino
- [ ] **FCP**: Alíquotas 2024/2025 por UF destino (Convênio 174/2023)
- [ ] **ICMS ST**: MVA/IVA por NCM × UF, CEST mapeado
- [ ] **Piso Mínimo ANTT**: Tabelas 2024/2025 (Res. 5.868/2022 + atualizações)
- [ ] **SICOBAN**: 22 faixas CEP × 5 tipos carga × 2 modais confirmadas
- [ ] **Tolerâncias peso**: 5% (carga geral) / 20% (granel) - legislação
- [ ] **CT-e complementar**: Regras tpEmis 2,3,4 validadas contra Manual CT-e 3.00
- [ ] **Pedágio**: Fontes de tarifas (CCR, EcoRodovias, etc.) identificadas
- [ ] **Ad Valorem/GRIS**: Taxas praticadas por seguradoras/transportadoras

---

## 🚀 Próximos Passos

1. **Completar arquivos 01-17** com dados atuais (2024/2025)
2. **Validar com contador/especialista tributário** - agendar revisão
3. **Gerar JSONs** para `backend/app/data/` a partir desta pesquisa
4. **Criar testes automatizados** (`test_rules_critical.py`) baseados nos casos aqui documentados
5. **Configurar alertas** para mudanças legislativas (monitoramento Diário Oficial)

---

## 📝 Controle de Versão

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 2026-11-01 | PO Agent | Estrutura inicial, mapeamento rules → legislação |

---

> **⚠️ IMPORTANTE**: Esta pesquisa serve como **fonte da verdade** para o Rules Engine. Qualquer alteração nas alíquotas/parâmetros deve:
> 1. Atualizar o arquivo `.md` correspondente
> 2. Atualizar o JSON em `backend/app/data/`
> 3. Rodar testes de regressão (`poetry run pytest tests/test_rules_critical.py -v`)
> 4. Registrar no CHANGELOG com referência à legislação