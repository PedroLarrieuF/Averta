# Índice das Regras NF-e - AvertaSaaS Auditoria de Frete

**Versão:** 1.0  
**Data:** 2026-11-03  
**Responsável:** PO/Scrum Master  
**Status:** Em pesquisa - Base para Rules Engine v2 (NF-e)  

---

## 📋 Visão Geral

Este diretório contém a pesquisa regulatória completa para **regras de NF-e (Nota Fiscal Eletrônica)** que fundamentam a auditoria de frete no AvertaSaaS. Diferente do CT-e (documento de transporte), a NF-e é o documento fiscal da mercadoria e contém os valores, impostos e classificações que devem ser cruzados com o CT-e para auditoria completa.

**Objetivo:** Validar se a NF-e está correta para fins de auditoria de frete - valores, impostos, classificação fiscal, dados de transporte e consistência com CT-e.

---

## 📁 Estrutura dos Arquivos

| Arquivo | Área | Rules Relacionadas | Prioridade |
|---------|------|-------------------|------------|
| `01-ICMS-CALCULO.md` | ICMS - Cálculo e Validação (CST/CSOSN) | `NFE_ICMS_CALCULO`, `NFE_ICMS_CST_VALIDACAO` | CRITICAL |
| `02-ICMS-ST.md` | ICMS Substituição Tributária (MVA/IVA) | `NFE_ICMS_ST_VALIDACAO` | CRITICAL |
| `03-ICMS-DIFAL.md` | DIFAL NF-e (Destino não contribuinte) | `NFE_DIFAL` | CRITICAL |
| `04-FCP.md` | FCP - Fundo Combate à Pobreza | `NFE_FCP` | HIGH |
| `05-CFOP-VALIDACAO.md` | CFOP - Validação para Operações c/ Frete | `NFE_CFOP_FRETE`, `NFE_CFOP_INTERSTADUAL` | HIGH |
| `06-NCM-CEST.md` | NCM/CEST - Classificação e ST | `NFE_NCM_CEST_VALIDACAO` | HIGH |
| `07-FRETE-BASE-CALCULO.md` | Frete na Base de Cálculo do ICMS | `NFE_FRETE_NA_BASE` | CRITICAL |
| `08-VALOR-TOTAL.md` | Consistência Valor Total (vNF) | `NFE_VALOR_TOTAL_CONSISTENCIA` | HIGH |
| `09-PESO-VOLUME.md` | Peso/Volume da Carga na NF-e | `NFE_PESO_VOLUME_VALIDACAO` | MEDIUM |
| `10-DADOS-TRANSPORTE.md` | Dados Transportadora/Veículo/Motorista | `NFE_TRANSPORTADORA_DADOS` | HIGH |
| `11-DESTINATARIO.md` | Dados Destinatário (IE, CNPJ/CPF) | `NFE_DESTINATARIO_VALIDACAO` | HIGH |
| `12-NFE-COMPLEMENTAR.md` | NF-e Complementar / Carta de Correção | `NFE_COMPLEMENTAR`, `NFE_CARTA_CORRECAO` | MEDIUM |
| `13-CANCELAMENTO-INUTILIZACAO.md` | Cancelamento e Inutilização | `NFE_CANCELAMENTO`, `NFE_INUTILIZACAO` | MEDIUM |
| `14-CROSS-CTE-NFE.md` | Cruzamento CT-e × NF-e (Auditoria Core) | `NFE_CTE_CROSS_VALIDATION` | CRITICAL |
| `15-ALIQUOTAS-UF.md` | Tabela Consolidada Alíquotas por UF | Referência para ICMS | CRITICAL |
| `16-REGRAS-ESPECIAIS.md` | Regimes Especiais (Simples, ZFM, etc.) | `NFE_REGIME_ESPECIAL` | MEDIUM |
| `17-PARAMETROS-NFE.md` | Parâmetros Consolidados para Engine | Configuração rules NF-e | CRITICAL |

---

## 🔄 Mapeamento Rules Engine v2 (NF-e)

| Rule Code | Nome | Tipo | Severidade | Tags | Arquivo Principal |
|-----------|------|------|------------|------|-------------------|
| `NFE_ICMS_CALCULO` | ICMS Cálculo/Validação CST | ICMS_CALC | CRITICAL | icms, cst, csosn | 01-ICMS-CALCULO.md |
| `NFE_ICMS_CST_VALIDACAO` | CST/CSOSN x Operação | ICMS_CST | HIGH | icms, cst | 01-ICMS-CALCULO.md |
| `NFE_ICMS_ST_VALIDACAO` | ICMS ST (MVA/IVA) | ICMS_ST | CRITICAL | icms_st, mva | 02-ICMS-ST.md |
| `NFE_DIFAL` | DIFAL NF-e | ICMS_DIFFERENTIAL | CRITICAL | icms, difal | 03-ICMS-DIFAL.md |
| `NFE_FCP` | FCP na NF-e | ICMS_FCP | HIGH | fcp | 04-FCP.md |
| `NFE_CFOP_FRETE` | CFOP Operações c/ Frete | CFOP_VALIDATION | HIGH | cfop, freight | 05-CFOP-VALIDACAO.md |
| `NFE_CFOP_INTERSTADUAL` | CFOP Interestadual | CFOP_VALIDATION | HIGH | cfop, interstate | 05-CFOP-VALIDACAO.md |
| `NFE_NCM_CEST_VALIDACAO` | NCM/CEST Validação | NCM_CEST | HIGH | ncm, cest, st | 06-NCM-CEST.md |
| `NFE_FRETE_NA_BASE` | Frete na Base ICMS | FREIGHT_IN_BASE | CRITICAL | freight, icms_base | 07-FRETE-BASE-CALCULO.md |
| `NFE_VALOR_TOTAL_CONSISTENCIA` | vNF Consistência | TOTAL_VALIDATION | HIGH | total, vNF | 08-VALOR-TOTAL.md |
| `NFE_PESO_VOLUME_VALIDACAO` | Peso/Volume Carga | WEIGHT_VOLUME | MEDIUM | weight, volume | 09-PESO-VOLUME.md |
| `NFE_TRANSPORTADORA_DADOS` | Dados Transportadora | TRANSPORT_DATA | HIGH | transport, carrier | 10-DADOS-TRANSPORTE.md |
| `NFE_DESTINATARIO_VALIDACAO` | Destinatário IE/CNPJ | DESTINATARY | HIGH | destinatario, ie | 11-DESTINATARIO.md |
| `NFE_COMPLEMENTAR` | NF-e Complementar | COMPLEMENTARY | MEDIUM | complementar | 12-NFE-COMPLEMENTAR.md |
| `NFE_CARTA_CORRECAO` | Carta de Correção | CORRECTION | MEDIUM | carta_correcao | 12-NFE-COMPLEMENTAR.md |
| `NFE_CANCELAMENTO` | Cancelamento NF-e | CANCELLATION | MEDIUM | cancelamento | 13-CANCELAMENTO-INUTILIZACAO.md |
| `NFE_INUTILIZACAO` | Inutilização Numeração | INUTILIZATION | MEDIUM | inutilizacao | 13-CANCELAMENTO-INUTILIZACAO.md |
| `NFE_CTE_CROSS_VALIDATION` | Cruzamento CT-e × NF-e | CROSS_VALIDATION | CRITICAL | cross, cte, nfe | 14-CROSS-CTE-NFE.md |
| `NFE_REGIME_ESPECIAL` | Regimes Especiais | SPECIAL_REGIME | MEDIUM | simples, zfm | 16-REGRAS-ESPECIAIS.md |

---

## ⚖️ Legislação Base NF-e (Referência Rápida)

### Federal
| Lei/Decreto/Ato | Assunto | Status |
|-----------------|---------|--------|
| **Lei 8.884/1994** (Art. 37) | Base cálculo ICMS (inclui frete) | Vigente |
| **LC 87/1996** (Lei Kandir) | ICMS interestadual | Vigente |
| **LC 190/2022** | DIFAL regulamentado | Vigente |
| **Convênio ICMS 174/2023** | FCP alíquotas por UF | Vigente |
| **Convênio ICMS 142/2018** | ICMS ST protocolo | Vigente |
| **Ajuste SINIEF 07/2005** | Leiaute NF-e 4.00 | Vigente |
| **Ajuste SINIEF 19/2016** | NF-e 4.00 (atual) | Vigente |
| **Decreto 6.022/2006** | Regulamento ICMS federal | Vigente |
| **Convênio ICMS 38/2001** | CEST - Substituição Tributária | Vigente |
| **Convênio ICMS 52/2017** | CFOP atualizado | Vigente |

### Estadual (27 UFs + DF)
Cada UF possui legislação própria:
- **RICMS** - Regulamento do ICMS estadual
- **Decreto ST** - Produtos sujeitos, MVA/IVA ajustado
- **Decreto FCP** - Alíquotas FCP (desde 2023)
- **Decreto Simples Nacional** - Regras de ICMS para optantes

---

## 📊 Dados de Referência no Backend (NF-e)

```
backend/app/data/nfe/
├── icms_cst_csosn.json       # CST/CSOSN x operação x regime
├── icms_st_mva_iva.json      # MVA/IVA por NCM × UF × CEST
├── icms_difal.json           # Alíquotas interestaduais + internas
├── fcp_aliquotas.json        # FCP por UF (2024/2025)
├── cfop_tabela.json          # CFOP válidos por tipo operação
├── ncm_cest_st.json          # NCM → CEST → ST por UF
├── frete_base_icms.json      # Regras frete na base por UF/CST
├── transportadora_validacao.json  # Validação dados transportadora
├── nfe_complementar_regras.json   # Regras NF-e complementar/CC
├── cross_cte_nfe_regras.json      # Regras cruzamento CT-e × NF-e
└── regimes_especiais.json         # Simples, ZFM, isenções
```

---

## ✅ Checklist de Validação NF-e (PO + Tech Lead + Contador)

Antes de considerar a pesquisa NF-e completa:

### ICMS Básico
- [ ] **CST/CSOSN**: Tabela completa 00-90 + 101-500 (Simples) por operação
- [ ] **Base Cálculo**: vBC = vNF + vFrete + vSeg + vOutro - vDesc (por CST)
- [ ] **Alíquotas Internas**: 27 UFs + DF confirmadas 2024/2025
- [ ] **Alíquotas Interestaduais**: 4%, 7%, 12% por região origem/destino

### ICMS ST
- [ ] **MVA/IVA Original**: Por NCM (Convênio 38/2001 + atualizações)
- [ ] **MVA/IVA Ajustado**: Por UF destino (cada estado altera)
- [ ] **CEST Mapeado**: NCM → CEST → % ST por UF
- [ ] **Base ST**: (vNF + vFrete + vSeg + vOutro - vDesc) × (1 + MVA)

### DIFAL/FCP
- [ ] **DIFAL**: LC 190/2022 - destinatário não contribuinte (indIEDest=9)
- [ ] **FCP**: Convênio 174/2023 - alíquotas 2024/2025 por UF
- [ ] **Ordem Cálculo**: ICMS → FCP → DIFAL (ou ST → FCP → DIFAL)

### CFOP
- [ ] **CFOP Frete**: 5.352, 6.352, 5.353, 6.353, 5.354, 6.354, 5.355, 6.355
- [ ] **CFOP Interestadual**: 6.1xx, 6.2xx, 6.3xx, 6.4xx, 6.5xx
- [ ] **CFOP Devolução**: 1.202, 2.202, 1.411, 2.411
- [ ] **CFOP Simples Nacional**: 5.101 a 5.119, 6.101 a 6.119

### NCM/CEST
- [ ] **NCM 8 dígitos**: Tabela TIPI vigente
- [ ] **CEST**: Convênio 38/2001 + Convênio 52/2017 + atualizações
- [ ] **NCM x CEST x ST**: Mapeamento completo por UF

### Frete na Base
- [ ] **vFrete em vBC**: Obrigatório para CST 00, 10, 20, 30, 40, 41, 50, 51, 60, 70, 90
- [ ] **Exceções**: CST 40 (isenção), 41 (não tributada), 50 (suspensão), 51 (diferimento)
- [ ] **Frete por conta emitente**: Sempre na base
- [ ] **Frete por conta destinatário**: Na base se destacado na NF-e

### Cruzamento CT-e × NF-e (CORE)
- [ ] **Chave Acesso**: NF-e referenciada no CT-e (refNFe)
- [ ] **Valores**: vNF (NF-e) vs vTPrest (CT-e) - tolerância
- [ ] **Peso**: vPeso (NF-e) vs proPred/peso (CT-e) - tolerância 5-20%
- [ ] **Destinatário**: CNPJ/CPF/IE idênticos
- [ ] **Transportadora**: CNJT/CPF idênticos
- [ ] **UF Origem/Destino**: Coerentes entre documentos
- [ ] **CFOP x tpCTe**: Coerência operação

### Documentos Complementares
- [ ] **NF-e Complementar**: tpEmis=4 (complemento valor/ICMS)
- [ ] **Carta Correção**: Até 20 campos, não altera valores
- [ ] **Cancelamento**: Prazo 24h (alguns estados 168h), sem circulação
- [ ] **Inutilização**: Numeração não usada, justificativa

---

## 🚀 Próximos Passos NF-e

1. **Completar arquivos 01-17** com dados atuais (2024/2025)
2. **Validar com contador/especialista tributário** - agendar revisão NF-e específica
3. **Gerar JSONs** para `backend/app/data/nfe/` a partir desta pesquisa
4. **Criar testes automatizados** (`test_nfe_rules_critical.py`) baseados nos casos documentados
5. **Integrar com Rules Engine v2** - adicionar tags `nfe`, `cross_validation`
6. **Configurar alertas** para mudanças legislativas NF-e (Diário Oficial + SINIEF)

---

## 📝 Controle de Versão

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 2026-11-03 | PO Agent | Estrutura inicial NF-e, mapeamento 19 rules |

---

> **⚠️ IMPORTANTE**: Esta pesquisa NF-e complementa a pesquisa CT-e existente em `../regulatory-research/`. Ambas são **fontes da verdade** para o Rules Engine. Qualquer alteração deve:
> 1. Atualizar o arquivo `.md` correspondente
> 2. Atualizar o JSON em `backend/app/data/nfe/` ou `backend/app/data/`
> 3. Rodar testes de regressão (`poetry run pytest tests/test_nfe_rules_critical.py -v`)
> 4. Registrar no CHANGELOG com referência à legislação
> 5. **Sincronizar com regras CT-e** quando houver sobreposição (ex: DIFAL, FCP, ST)