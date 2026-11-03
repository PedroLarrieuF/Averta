# Parâmetros Consolidados para Engine NF-e - Configuração Rules

**Rule Code:** Configuração (não é rule executável)  
**Tipo:** `CONFIGURATION`  
**Prioridade:** `CRITICAL`  
**Arquivos de Dados:** Todos `backend/app/data/nfe/*.json`  
**Uso:** Source of Truth para implementação Rules Engine v2 (NF-e)

---

## 📜 Objetivo

Este documento consolida **todos os parâmetros** necessários para configurar o Rules Engine v2 para validação de NF-e. Serve como **fonte única** para geração dos arquivos JSON em `backend/app/data/nfe/`.

---

## 📁 Arquivos JSON a Gerar

```
backend/app/data/nfe/
├── icms_cst_csosn.json          # 01-ICMS-CALCULO.md
├── icms_st_mva_iva.json         # 02-ICMS-ST.md
├── icms_difal.json              # 03-ICMS-DIFAL.md
├── fcp_aliquotas.json           # 04-FCP.md
├── cfop_tabela.json             # 05-CFOP-VALIDACAO.md
├── ncm_cest_st.json             # 06-NCM-CEST.md
├── frete_base_icms.json         # 07-FRETE-BASE-CALCULO.md
├── valor_total_consistencia.json # 08-VALOR-TOTAL.md
├── peso_volume_validacao.json   # 09-PESO-VOLUME.md
├── transportadora_validacao.json # 10-DADOS-TRANSPORTE.md
├── destinatario_validacao.json  # 11-DESTINATARIO.md
├── nfe_complementar_regras.json # 12-NFE-COMPLEMENTAR.md
├── cancelamento_inutilizacao.json # 13-CANCELAMENTO-INUTILIZACAO.md
├── cross_cte_nfe_regras.json    # 14-CROSS-CTE-NFE.md
├── aliquotas_uf.json            # 15-ALIQUOTAS-UF.md
├── regimes_especiais.json       # 16-REGRAS-ESPECIAIS.md
└── parametros_engine.json       # ESTE ARQUIVO (consolidado)
```

---

## ⚙️ Parâmetros do Engine (parametros_engine.json)

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "engine": "RulesEngineV2",
  "rules_nfe": {
    "NFE_ICMS_CALCULO": {
      "enabled": true,
      "severity": "CRITICAL",
      "tags": ["icms", "cst", "csosn", "nfe"],
      "relevance_tags": ["icms", "cst", "nfe"],
      "tolerancia_base_calculo_pct": 0.001,
      "tolerancia_icms_pct": 0.001,
      "csts_com_frete_base": ["00", "10", "20", "30", "60", "70", "90"],
      "csts_sem_frete_base": ["40", "41", "50", "51"],
      "csosns_com_frete_base": ["101", "102", "201", "202"]
    },
    "NFE_ICMS_CST_VALIDACAO": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["icms", "cst", "validation", "nfe"],
      "validar_cst_cfop": true,
      "validar_cst_st": true,
      "validar_regime_cst": true
    },
    "NFE_ICMS_ST_VALIDACAO": {
      "enabled": true,
      "severity": "CRITICAL",
      "tags": ["icms_st", "mva", "iva", "cest", "nfe"],
      "tolerancia_bcst_pct": 0.005,
      "tolerancia_icmsst_pct": 0.005,
      "usar_mva_ajustada_uf_destino": true,
      "frete_integra_base_st": true
    },
    "NFE_DIFAL": {
      "enabled": true,
      "severity": "CRITICAL",
      "tags": ["icms", "difal", "interstate", "nfe"],
      "tolerancia_minima_pct_bc": 0.01,
      "aplica_nao_contribuinte": true,
      "aplica_contribuinte": true,
      "ordem_calculo": ["ICMS", "DIFAL", "FCP"]
    },
    "NFE_FCP": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["fcp", "icms", "interstate", "nfe"],
      "aplica_apenas_nao_contribuinte": true,
      "aplica_apenas_interestadual": true,
      "campos": ["vFCP", "vFCPST", "vFCPSTRet", "pFCP", "pFCPST"]
    },
    "NFE_CFOP_FRETE": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["cfop", "freight", "nfe"],
      "validar_modfrete": true,
      "validar_cte_obrigatorio": true,
      "cfops_frete_obrigatorio": ["5352", "5353", "5354", "6352", "6353", "6354"],
      "cfops_sem_frete": ["5355", "6355"]
    },
    "NFE_CFOP_INTERSTADUAL": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["cfop", "interstate", "nfe"],
      "validar_uf_origem_destino": true
    },
    "NFE_NCM_CEST_VALIDACAO": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["ncm", "cest", "st", "classification", "nfe"],
      "validar_cest_obrigatorio": true,
      "validar_cst_st_consistencia": true,
      "validar_mva_uf": true,
      "validar_ncm_tipi": true
    },
    "NFE_FRETE_NA_BASE": {
      "enabled": true,
      "severity": "CRITICAL",
      "tags": ["freight", "icms_base", "nfe", "lei_8884"],
      "tolerancia_pct": 0.001,
      "detectar_frete_nao_incluido": true,
      "base_legal": "Lei 8.884/94 Art. 37"
    },
    "NFE_VALOR_TOTAL_CONSISTENCIA": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["total", "vNF", "nfe"],
      "tolerancia_pct": 0.005,
      "validar_soma_itens": true,
      "validar_impostos": true
    },
    "NFE_PESO_VOLUME_VALIDACAO": {
      "enabled": true,
      "severity": "MEDIUM",
      "tags": ["weight", "volume", "nfe"],
      "tolerancia_carga_geral_pct": 0.05,
      "tolerancia_granel_pct": 0.20,
      "tipos_granel": ["GRANEL_LIQUIDO", "GRANEL_SOLIDO", "GRANEL_GASOSO"]
    },
    "NFE_TRANSPORTADORA_DADOS": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["transport", "carrier", "nfe"],
      "validar_cnpj_emitente_cte": true,
      "validar_veiculo": true,
      "validar_motorista": true
    },
    "NFE_DESTINATARIO_VALIDACAO": {
      "enabled": true,
      "severity": "HIGH",
      "tags": ["destinatary", "ie", "cnpj", "nfe"],
      "validar_ie_formato": true,
      "validar_cnpj_cpf": true,
      "validar_uf_coerencia": true
    },
    "NFE_COMPLEMENTAR": {
      "enabled": true,
      "severity": "MEDIUM",
      "tags": ["complementar", "carta_correcao", "nfe"],
      "max_cartas_correcao": 20,
      "cartas_nao_alteram_valores": true
    },
    "NFE_CARTA_CORRECAO": {
      "enabled": true,
      "severity": "MEDIUM",
      "tags": ["carta_correcao", "nfe"],
      "campos_permitidos": 20,
      "nao_pode_alterar": ["vNF", "vICMS", "vBC", "vFrete", "CFOP", "NCM"]
    },
    "NFE_CANCELAMENTO": {
      "enabled": true,
      "severity": "MEDIUM",
      "tags": ["cancellation", "nfe"],
      "prazo_horas_padrao": 24,
      "prazo_horas_estendido": 168,
      "requisitos": ["sem_circulacao", "sem_uso", "autorizado_sefaz"]
    },
    "NFE_INUTILIZACAO": {
      "enabled": true,
      "severity": "MEDIUM",
      "tags": ["inutilizacao", "nfe"],
      "justificativa_obrigatoria": true,
      "numeracao_nao_usada": true
    },
    "NFE_CTE_CROSS_VALIDATION": {
      "enabled": true,
      "severity": "CRITICAL",
      "tags": ["cross", "cte", "nfe", "freight_audit", "core"],
      "tolerancias": {
        "valor_total_pct": 0.02,
        "valor_total_minimo": 10.0,
        "peso_carga_geral_pct": 0.05,
        "peso_granel_pct": 0.20,
        "frete_valor_pct": 0.05,
        "frete_valor_minimo": 5.0,
        "cubagem_pct": 0.10
      },
      "validacoes_critical": [
        "VALOR_TOTAL_vTPrest_vs_vNF",
        "DESTINATARIO_CNPJ_CPF",
        "TRANSPORTADORA_CNPJ",
        "UF_DESTINO",
        "FRETE_NA_BASE_ICMS"
      ],
      "validacoes_high": [
        "PESO",
        "DESTINATARIO_IE",
        "UF_ORIGEM",
        "CFOP_TPCTE",
        "ICMS_OPERACAO"
      ],
      "validacoes_medium": [
        "DESTINATARIO_CIDADE",
        "VOLUMES_QUANTIDADE",
        "REDESPACHO_SEM_COMPLEMENTAR",
        "FRETE_VALOR_DIVERGENTE"
      ],
      "success_fee": {
        "base_calculo": "ICMS_sonegado + multa + juros",
        "percentual_padrao": 0.15,
        "prescricao_anos": 5
      }
    },
    "NFE_REGIME_ESPECIAL": {
      "enabled": true,
      "severity": "MEDIUM",
      "tags": ["simples", "zfm", "special_regime", "nfe"],
      "simples_nacional": {
        "csosn_validos": ["101", "102", "103", "201", "202", "203", "300", "400", "500", "900"],
        "icms_diferenciado": true,
        "difal_pode_nao_aplicar": true,
        "fcp_pode_nao_aplicar": true
      },
      "zfm": {
        "uf": "AM",
        "isento_fcp": true,
        "icms_diferenciado": true,
        "regimes_especiais": true
      }
    }
  },
  "dados_referencia": {
    "icms_cst_csosn": "icms_cst_csosn.json",
    "icms_st_mva_iva": "icms_st_mva_iva.json",
    "icms_difal": "icms_difal.json",
    "fcp_aliquotas": "fcp_aliquotas.json",
    "cfop_tabela": "cfop_tabela.json",
    "ncm_cest_st": "ncm_cest_st.json",
    "frete_base_icms": "frete_base_icms.json",
    "aliquotas_uf": "aliquotas_uf.json",
    "cross_cte_nfe": "cross_cte_nfe_regras.json",
    "regimes_especiais": "regimes_especiais.json"
  },
  "atualizacao": {
    "frequencia": "mensal",
    "fontes": [
      "Diário Oficial da União",
      "Diários Oficiais Estaduais (27 + DF)",
      "CONFAZ - Convênios ICMS",
      "SINIEF - Ajustes",
      "Portal NF-e / CT-e",
      "TIPI - Decreto 6.759/2009"
    ],
    "alertas": [
      "Alíquotas internas estaduais (janeiro)",
      "FCP Convênio 174 (janeiro)",
      "MVA/IVA ajustada por UF",
      "CEST Convênio 52 (anual)",
      "TIPI/NCM atualizações",
      "CFOP Convênio 52",
      "Piso Mínimo Frete ANTT"
    ]
  }
}
```

---

## 🔧 Configuração por Ambiente

### Development
```json
{
  "rules_nfe": {
    "NFE_ICMS_CALCULO": { "tolerancia_base_calculo_pct": 0.01 },
    "NFE_CTE_CROSS_VALIDATION": { "tolerancias": { "valor_total_pct": 0.05 } }
  }
}
```

### Staging
```json
{
  "rules_nfe": {
    "NFE_ICMS_CALCULO": { "tolerancia_base_calculo_pct": 0.001 },
    "NFE_CTE_CROSS_VALIDATION": { "tolerancias": { "valor_total_pct": 0.02 } }
  }
}
```

### Production
```json
{
  "rules_nfe": {
    "NFE_ICMS_CALCULO": { "tolerancia_base_calculo_pct": 0.001 },
    "NFE_CTE_CROSS_VALIDATION": { "tolerancias": { "valor_total_pct": 0.02 } }
  }
}
```

---

## 🏷️ Tags do Engine (para Filtros)

```json
{
  "tags_disponiveis": [
    "icms", "cst", "csosn", "icms_st", "mva", "iva", "cest",
    "difal", "interstate", "fcp", "freight", "icms_base",
    "cfop", "ncm", "classification", "total", "weight", "volume",
    "transport", "carrier", "destinatary", "ie", "cnpj",
    "complementar", "carta_correcao", "cancellation", "inutilizacao",
    "cross", "cte", "nfe", "freight_audit", "core",
    "simples", "zfm", "special_regime", "validation",
    "lei_8884"
  ],
  "tags_por_regra": {
    "NFE_ICMS_CALCULO": ["icms", "cst", "nfe"],
    "NFE_ICMS_CST_VALIDACAO": ["icms", "cst", "validation", "nfe"],
    "NFE_ICMS_ST_VALIDACAO": ["icms_st", "mva", "nfe"],
    "NFE_DIFAL": ["icms", "difal", "interstate", "nfe"],
    "NFE_FCP": ["fcp", "icms", "interstate", "nfe"],
    "NFE_CFOP_FRETE": ["cfop", "freight", "nfe"],
    "NFE_CFOP_INTERSTADUAL": ["cfop", "interstate", "nfe"],
    "NFE_NCM_CEST_VALIDACAO": ["ncm", "cest", "st", "nfe"],
    "NFE_FRETE_NA_BASE": ["freight", "icms_base", "nfe", "lei_8884"],
    "NFE_VALOR_TOTAL_CONSISTENCIA": ["total", "vNF", "nfe"],
    "NFE_PESO_VOLUME_VALIDACAO": ["weight", "volume", "nfe"],
    "NFE_TRANSPORTADORA_DADOS": ["transport", "carrier", "nfe"],
    "NFE_DESTINATARIO_VALIDACAO": ["destinatary", "ie", "cnpj", "nfe"],
    "NFE_COMPLEMENTAR": ["complementar", "carta_correcao", "nfe"],
    "NFE_CARTA_CORRECAO": ["carta_correcao", "nfe"],
    "NFE_CANCELAMENTO": ["cancellation", "nfe"],
    "NFE_INUTILIZACAO": ["inutilizacao", "nfe"],
    "NFE_CTE_CROSS_VALIDATION": ["cross", "cte", "nfe", "freight_audit", "core"],
    "NFE_REGIME_ESPECIAL": ["simples", "zfm", "special_regime", "nfe"]
  }
}
```

---

## 🔄 Ordem de Execução das Rules (Prioridade)

```json
{
  "ordem_execucao": [
    1,  // NFE_ICMS_CALCULO (base para todas)
    2,  // NFE_ICMS_CST_VALIDACAO (valida CST antes de calcular)
    3,  // NFE_FRETE_NA_BASE (afeta base ICMS e ST)
    4,  // NFE_ICMS_ST_VALIDACAO (depende de base correta)
    5,  // NFE_DIFAL (depende de ICMS correto)
    6,  // NFE_FCP (calculado após ICMS/DIFAL/ST)
    7,  // NFE_NCM_CEST_VALIDACAO (valida classificação)
    8,  // NFE_CFOP_FRETE (valida operação)
    9,  // NFE_CFOP_INTERSTADUAL (valida UF x CFOP)
    10, // NFE_VALOR_TOTAL_CONSISTENCIA (valida totais)
    11, // NFE_PESO_VOLUME_VALIDACAO (valida peso)
    12, // NFE_TRANSPORTADORA_DADOS (valida transportadora)
    13, // NFE_DESTINATARIO_VALIDACAO (valida destinatário)
    14, // NFE_COMPLEMENTAR / NFE_CARTA_CORRECAO
    15, // NFE_CANCELAMENTO / NFE_INUTILIZACAO
    16  // NFE_CTE_CROSS_VALIDATION (core - roda por último, cross-valida tudo)
  ],
  "observacao": "NFE_CTE_CROSS_VALIDATION roda por último pois precisa de TODOS os dados validados individualmente"
}
```

---

## 📊 Métricas e Thresholds

```json
{
  "metricas": {
    "cobertura_rules_nfe": 19,
    "rules_critical": 5,
    "rules_high": 7,
    "rules_medium": 7,
    "tempo_maximo_avaliacao_ms": 500,
    "cache_ttl_segundos": 3600,
    "reprocessar_apos_atualizacao_dados": true
  },
  "thresholds_alerta": {
    "divergencias_por_nfe_media": 2,
    "divergencias_por_nfe_p95": 5,
    "taxa_falsos_positivos_max": 0.05,
    "tempo_resposta_p99_ms": 1000
  }
}
```

---

## 🚀 Checklist Implementação Backend

### Fase 1: Dados Base (Semana 1)
- [ ] `icms_cst_csosn.json` - Tabela CST/CSOSN completa
- [ ] `aliquotas_uf.json` - Alíquotas internas + FCP + Interestaduais
- [ ] `cfop_tabela.json` - CFOP válidos + modFrete + gera CT-e

### Fase 2: Rules Core ICMS (Semana 2)
- [ ] `icms_difal.json` - DIFAL parâmetros
- [ ] `fcp_aliquotas.json` - FCP por UF
- [ ] `icms_st_mva_iva.json` - MVA Original + Ajustada por UF
- [ ] `ncm_cest_st.json` - NCM → CEST → MVA + ST
- [ ] `frete_base_icms.json` - Regras frete na base

### Fase 3: Rules Validação (Semana 3)
- [ ] `valor_total_consistencia.json`
- [ ] `peso_volume_validacao.json`
- [ ] `transportadora_validacao.json`
- [ ] `destinatario_validacao.json`
- [ ] `cfop_tabela.json` (completo)

### Fase 4: Rules Documentos (Semana 4)
- [ ] `nfe_complementar_regras.json`
- [ ] `cancelamento_inutilizacao.json`
- [ ] `regimes_especiais.json`

### Fase 5: Cross-Validation CORE (Semana 5)
- [ ] `cross_cte_nfe_regras.json` - **MAIS IMPORTANTE**
- [ ] Integração RulesEngineV2 com tags `cross`, `freight_audit`, `core`
- [ ] Testes end-to-end CT-e × NF-e

### Fase 6: Configuração Engine (Semana 6)
- [ ] `parametros_engine.json` (este arquivo)
- [ ] Tags, ordem execução, thresholds
- [ ] Cache, performance, métricas
- [ ] Deploy staging → production

---

## 📝 Controle de Versão

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 2026-11-03 | PO Agent | Estrutura inicial, 19 rules NF-e mapeadas, JSONs definidos |

---

## 🔗 Referências Cruzadas

| Arquivo NF-e | Arquivo CT-e (regulatory-research) | Sincronização |
|--------------|-----------------------------------|---------------|
| 01-ICMS-CALCULO.md | 01-ICMS-DIFAL.md, 02-ICMS-FCP.md, 03-ICMS-ST.md | Alíquotas, CST, base cálculo |
| 02-ICMS-ST.md | 03-ICMS-ST.md, 15-NCM-ST.md | MVA/IVA, CEST |
| 03-ICMS-DIFAL.md | 01-ICMS-DIFAL.md | Mesma legislação (LC 190/2022) |
| 04-FCP.md | 02-ICMS-FCP.md | Mesma legislação (Convênio 174/2023) |
| 07-FRETE-BASE-CALCULO.md | 04-FRETE-PESO-VALOR.md, 05-FRETE-CUBAGEM.md | Frete na base, pisos ANTT |
| 14-CROSS-CTE-NFE.md | 13-CTE-COMPLEMENTAR.md, 08-REDESPACHO.md | **CORE BUSINESS** - Cruzamento |

---

> **⚠️ IMPORTANTE**: Este arquivo (`17-PARAMETROS-NFE.md`) é o **guia mestre** para implementação. Todos os arquivos JSON em `backend/app/data/nfe/` devem ser gerados a partir da documentação em `docs/nfe-rules/` e mantidos **sincronizados** com `docs/regulatory-research/` (CT-e) quando houver sobreposição legislativa.