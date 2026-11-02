# Parâmetros Consolidados para Rules Engine v2 - Configuração Backend

**Arquivo:** Fonte única de verdade para `backend/app/data/*.json`  
**Uso:** Configuração do Rules Engine v2, testes, validação  
**Versão:** 2025.1  
**Atualização:** Janeiro 2025

---

## 📦 Estrutura de Arquivos JSON no Backend

```
backend/app/data/
├── icms_rules.json           # ICMS DIFAL, FCP, ST, alíquotas por UF
├── sicoban_table.json        # Tabela SICOBAN 22 faixas CEP
├── antt_faixas_peso_valor.json    # Faixas Peso × Valor (10 faixas × 5 tipos)
├── antt_faixas_cubagem.json     # Faixas Cubagem (10 faixas × 5 tipos)
├── antt_piso_minimo.json        # Pisos por eixos × distância
├── pedagio_tarifas.json         # Tarifas pedágio por concessionária/praça
├── ad_valorem_taxas.json        # Taxas Ad Valorem por tipo carga
├── gris_taxas.json              # Taxas GRIS por região/risco
├── cte_complementar_regras.json # Regras validação CT-e complementar
├── redespacho_regras.json       # Regras validação redespacho
├── pesos_tolerancia.json        # Tolerâncias peso real vs faturado
├── ncm_st_params.json           # Parâmetros ST por NCM × UF (MVA/IVA)
└── referencia_cep_faixa.json    # Mapeamento CEP → Faixa SICOBAN
```

---

## ⚙️ Parâmetros por Regra (Engine Config)

### 1. ICMS_DIFAL
```json
{
  "rule_code": "ICMS_DIFAL",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["icms", "interstate"],
  "parameters": {
    "min_difference_pct_bc": 0.01,
    "use_aliquota_interna_liquida_fcp": true,
    "considerar_ind_ie_dest": true
  },
  "data_source": "icms_rules.json"
}
```

### 2. ICMS_FCP
```json
{
  "rule_code": "ICMS_FCP",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["icms", "interstate"],
  "parameters": {
    "min_difference_pct_bc": 0.001,
    "base_fcp_igual_base_difal": true,
    "nao_somar_se_incluso_na_interna": true
  },
  "data_source": "icms_rules.json"
}
```

### 3. ICMS_ST
```json
{
  "rule_code": "ICMS_ST",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["icms", "icms_st"],
  "parameters": {
    "min_difference_pct_bc": 0.01,
    "incluir_fcp_st": true,
    "validar_cst_csosn": true,
    "validar_ncm_cest": true
  },
  "data_source": "icms_rules.json (seção icms_st)"
}
```

### 4. FRETE_PESO_VALOR
```json
{
  "rule_code": "FRETE_PESO_VALOR",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["freight", "weight"],
  "parameters": {
    "tolerancia_pct": 0.01,
    "peso_em_toneladas": true,
    "aplicar_fator_tipo_carga": true,
    "considerar_cte_complementar": true
  },
  "data_source": "antt_faixas_peso_valor.json"
}
```

### 5. FRETE_CUBAGEM
```json
{
  "rule_code": "FRETE_CUBAGEM",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["freight", "cubage"],
  "parameters": {
    "tolerancia_pct": 0.01,
    "cubagem_em_m3": true,
    "aplicar_fator_tipo_carga": true
  },
  "data_source": "antt_faixas_cubagem.json"
}
```

### 6. PESO_REAL_VS_FATURADO
```json
{
  "rule_code": "PESO_REAL_VS_FATURADO",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["weight"],
  "parameters": {
    "tolerancias_por_tipo_carga": {
      "01": 0.05, "02": 0.03, "03": 0.05, "04": 0.20,
      "05": 0.20, "06": 0.05, "07": 0.05, "08": 0.05,
      "09": 0.03, "10": 0.10
    },
    "exigir_fonte_peso_real": true,
    "fontes_validas": ["balança_fiscal", "balança_transportador", "nota_pesagem"]
  },
  "data_source": "pesos_tolerancia.json"
}
```

### 7. VALOR_MINIMO_FRETE
```json
{
  "rule_code": "VALOR_MINIMO_FRETE",
  "enabled": true,
  "severity": "CRITICAL",
  "relevance_tags": ["freight", "weight"],
  "parameters": {
    "tolerancia_pct": 0.01,
    "calcular_tres_metodos": true,
    "pegar_maior_piso": true,
    "metodos": ["peso_valor", "cubagem", "eixos_distancia"]
  },
  "data_sources": [
    "antt_faixas_peso_valor.json",
    "antt_faixas_cubagem.json",
    "antt_piso_minimo.json"
  ]
}
```

### 8. REDESPACHO_VALIDACAO
```json
{
  "rule_code": "REDESPACHO_VALIDACAO",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["redespacho"],
  "parameters": {
    "exigir_refCTe": true,
    "transportadores_diferentes": true,
    "piso_minimo_por_trecho": true,
    "soma_fretes_maior_piso_direto": true
  },
  "data_source": "redespacho_regras.json"
}
```

### 9. PEDAGIO_CONFERENCIA
```json
{
  "rule_code": "PEDAGIO_CONFERENCIA",
  "enabled": true,
  "severity": "MEDIUM",
  "relevance_tags": ["toll"],
  "parameters": {
    "tolerancia_pct": 0.10,
    "exigir_percurso_rodovias": true,
    "categoria_por_eixos": {
      "2": 2, "3": 3, "4": 4, "5": 4, "6": 5, "7": 5, "9": 5
    }
  },
  "data_source": "pedagio_tarifas.json"
}
```

### 10. AD_VALOREM
```json
{
  "rule_code": "AD_VALOREM",
  "enabled": true,
  "severity": "MEDIUM",
  "relevance_tags": ["advalorem"],
  "parameters": {
    "tolerancia_pct": 0.05,
    "base_calculo": "vNF",
    "taxa_por_contrato": true,
    "taxas_referencia_por_tipo": "ad_valorem_taxas.json"
  },
  "data_source": "ad_valorem_taxas.json"
}
```

### 11. GRIS
```json
{
  "rule_code": "GRIS",
  "enabled": true,
  "severity": "MEDIUM",
  "relevance_tags": ["gris"],
  "parameters": {
    "tolerancia_pct": 0.05,
    "tipos_base_validos": ["frete", "carga", "fixo", "km"],
    "adicional_rotas_criticas": true,
    "taxas_por_regiao": "gris_taxas.json"
  },
  "data_source": "gris_taxas.json"
}
```

### 12. SICOBAN_TABLE_REAL
```json
{
  "rule_code": "SICOBAN_TABLE_REAL",
  "enabled": true,
  "severity": "HIGH",
  "relevance_tags": ["freight", "sicoban"],
  "parameters": {
    "tolerancia_pct": 0.05,
    "exigir_contrato_com_sicoban": true,
    "mapear_cep_para_faixa": true
  },
  "data_sources": ["sicoban_table.json", "referencia_cep_faixa.json"]
}
```

### 13. CTE_COMPLEMENTAR (Anulação/Substituição/Complemento)
```json
{
  "CTE_ANULACAO": {
    "rule_code": "CTE_ANULACAO",
    "enabled": true,
    "severity": "CRITICAL",
    "relevance_tags": ["cte_complementar"],
    "parameters": {
      "exigir_refCTe": true,
      "validar_cte_original_existe": true,
      "validar_nao_dupla_anulacao": true
    }
  },
  "CTE_SUBSTITUICAO": {
    "rule_code": "CTE_SUBSTITUICAO",
    "enabled": true,
    "severity": "HIGH",
    "relevance_tags": ["cte_complementar"],
    "parameters": {
      "exigir_refCTe": true,
      "validar_cte_original_existe": true,
      "validar_nao_ja_substituido": true
    }
  },
  "CTE_COMPLEMENTO_VALOR": {
    "rule_code": "CTE_COMPLEMENTO_VALOR",
    "enabled": true,
    "severity": "MEDIUM",
    "relevance_tags": ["cte_complementar"],
    "parameters": {
      "exigir_refCTe": true,
      "validar_cte_original_existe": true,
      "valor_nao_negativo": true,
      "complemento_frete_exige_aditivo": true
    }
  },
  "data_source": "cte_complementar_regras.json"
}
```

---

## 🔧 Configuração Global do Engine

```json
{
  "engine_config": {
    "version": "2025.1",
    "cache_redis": {
      "enabled": true,
      "ttl_seconds": 3600,
      "key_prefix": "averta:rules:"
    },
    "tag_filtering": {
      "enabled": true,
      "performance_mode": "O_tag"
    },
    "default_tolerances": {
      "monetary_pct": 0.01,
      "percentage_pct": 0.001,
      "weight_pct": 0.05
    },
    "severity_levels": {
      "CRITICAL": 0,
      "HIGH": 1,
      "MEDIUM": 2,
      "LOW": 3
    },
    "money_handling": {
      "decimal_places": 2,
      "rounding": "HALF_UP",
      "currency": "BRL"
    },
    "datetime_handling": {
      "timezone": "UTC",
      "format": "ISO8601"
    }
  }
}
```

---

## 🧪 Parâmetros de Teste (test_rules_critical.py)

### Casos de Teste Obrigatórios por Regra

| Rule | Testes Mínimos | Cenários |
|------|----------------|----------|
| ICMS_DIFAL | 4 | triggered, not_triggered, same_uf, contribuinte_destino |
| ICMS_FCP | 3 | BA (2%), SP (2%), sem_FCP (GO) |
| ICMS_ST | 3 | MVA (cerveja), IVA (cigarro), com_FCP |
| FRETE_PESO_VALOR | 3 | carga_geral, perigosa, granel_liquido |
| FRETE_CUBAGEM | 2 | carga_geral, frigorifica |
| PESO_REAL_VS_FATURADO | 4 | dentro_tolerancia, fora_tolerancia, granel, perigosa |
| VALOR_MINIMO_FRETE | 4 | peso_vence, eixos_vence, cubagem_vence, redespacho |
| REDESPACHO | 3 | valido, mesmo_transportador, soma_abaixo_piso |
| PEDAGIO | 2 | confere, nao_confere (10%) |
| AD_VALOREM | 2 | confere, nao_confere (5%) |
| GRIS | 2 | confere, rota_critica |
| SICOBAN | 2 | confere, nao_confere (5%) |
| CTE_ANULACAO | 2 | sem_refCTe, dupla_anulacao |
| CTE_SUBSTITUICAO | 2 | sem_refCTe, ja_substituido |
| CTE_COMPLEMENTO | 2 | valor_negativo, sem_aditivo |

### Dados de Teste Padrão (Fixtures)

```python
# tests/fixtures/test_data.py

CENÁRIO_ICMS_DIFAL_SP_RJ_NAO_CONTRIBUINTE = {
    "uf_origem": "SP", "uf_destino": "RJ",
    "indIEDest": 9,  # Não contribuinte
    "vBC": 10000.00, "vICMS": 1200.00,  # ICMS 12% interestadual
    "expected_difal": 800.00,  # (20% - 12%) * 10000
    "expected_fcp": 200.00     # 2% * 10000
}

CENÁRIO_FRETE_PESO_12TON_CARGA_GERAL = {
    "peso_carga": 12000,  # kg
    "tpCarga": "01",      # Carga Geral
    "modal": "01",        # Rodoviário
    "vFrete": 2500.00,
    "expected_piso": 3026.28,  # 12 * 252.19 (faixa 3)
    "expected_diff": 526.28
}

CENÁRIO_PISO_MINIMO_3EIXOS_500KM = {
    "qtd_eixos": 3,
    "distancia_km": 500,
    "peso_carga": 12000,
    "tpCarga": "01",
    "vFrete": 2500.00,
    "expected_piso_eixos": 2450.00,  # 500 * 4.90
    "expected_piso_peso": 3026.28,
    "expected_piso_final": 3026.28  # MAX dos dois
}
```

---

## 📊 Validação de Dados (Data Quality Checks)

```json
{
  "data_quality_checks": {
    "icms_rules.json": {
      "required_fields": ["aliquotas_internas", "aliquotas_interestaduais", "fcp", "regioes"],
      "validations": [
        "Todas 27 UFs + DF presentes",
        "Alíquotas entre 0 e 1",
        "FCP >= 0",
        "Regiões cobrem todas UFs"
      ]
    },
    "antt_faixas_peso_valor.json": {
      "required_fields": ["faixas_peso_valor", "fatores_tipo_carga"],
      "validations": [
        "10 faixas com peso_min < peso_max",
        "Valores > 0",
        "5 tipos de carga com fatores > 0"
      ]
    },
    "sicoban_table.json": {
      "required_fields": ["faixas_cep", "fatores_tipo_carga", "valores_base_exemplos"],
      "validations": [
        "22 faixas",
        "CEPs não sobrepostos",
        "10 tipos de carga"
      ]
    }
  }
}
```

---

## 🚀 Checklist de Deploy (Configuração Produção)

- [ ] `icms_rules.json` validado com 27 UFs + DF
- [ ] `antt_faixas_peso_valor.json` com Res. 5.933/2023
- [ ] `antt_faixas_cubagem.json` com Res. 5.933/2023
- [ ] `antt_piso_minimo.json` com valores por eixos 2024
- [ ] `sicoban_table.json` com 22 faixas atuais
- [ ] `pedagio_tarifas.json` com concessionárias operantes
- [ ] `ad_valorem_taxas.json` com taxas de referência
- [ ] `gris_taxas.json` com regiões de risco
- [ ] `cte_complementar_regras.json` validações obrigatórias
- [ ] `redespacho_regras.json` regras de validação
- [ ] `pesos_tolerancia.json` tolerâncias por tipo carga
- [ ] `ncm_st_params.json` NCMs principais por UF
- [ ] Cache Redis configurado e testado
- [ ] Testes automatizados passando (50+ testes)
- [ ] Monitoramento de alertas configurado (regras CRITICAL)

---

## 📝 Controle de Versão de Dados

| Arquivo | Versão | Atualização | Próxima | Responsável |
|---------|--------|-------------|---------|-------------|
| icms_rules.json | 2025.1 | Jan/2025 | Jan/2026 | PO + Tax |
| antt_faixas_peso_valor.json | 2024.1 | Jul/2024 | Jul/2025 | PO + Ops |
| antt_faixas_cubagem.json | 2024.1 | Jul/2024 | Jul/2025 | PO + Ops |
| antt_piso_minimo.json | 2024.1 | Jul/2024 | Jul/2025 | PO + Ops |
| sicoban_table.json | 2024.1 | Jul/2024 | Jul/2025 | PO + Ops |
| pedagio_tarifas.json | 2024.2 | Jan/2025 | Jul/2025 | PO + Ops |
| ad_valorem_taxas.json | 2024.1 | Jan/2025 | Jan/2026 | PO + Comercial |
| gris_taxas.json | 2024.1 | Jan/2025 | Jan/2026 | PO + Comercial |
| ncm_st_params.json | 2025.1 | Jan/2025 | Jan/2026 | PO + Tax |

---

**Última Atualização:** 2026-11-01  
**Versão Engine:** v2.0  
**Próxima Revisão Completa:** Janeiro 2026