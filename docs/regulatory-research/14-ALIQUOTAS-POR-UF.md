# Alíquotas Consolidadas ICMS/FCP/ST por UF (2024/2025)

**Arquivo:** Referência consolidada para `backend/app/data/icms_rules.json`  
**Fonte:** LC 87/1996, LC 190/2022, Convênio ICMS 174/2023, Convênio ICMS 142/2018, Decretos Estaduais  
**Atualização:** Janeiro 2025

---

## 📊 Tabela Mestra por UF

| UF | Região | ICMS Interno | FCP | ICMS ST (MVA/IVA) | Observações |
|----|--------|--------------|-----|-------------------|-------------|
| **AC** | Norte | 17% | 0% | Conforme Conv. 142 | |
| **AL** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **AP** | Norte | 18% | 2% | Conforme Conv. 142 | |
| **AM** | Norte | 18% | 2% | Conforme Conv. 142 | ZFM: regimes especiais |
| **BA** | Nordeste | **20,5%** | **2%** | Conforme Conv. 142 | **Interna inclui FECOP 2,5%** |
| **CE** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **DF** | Centro-Oeste | 18% | 0% | Conforme Conv. 142 | |
| **ES** | Sudeste | 17% | 2% | Conforme Conv. 142 | |
| **GO** | Centro-Oeste | 19% | 0% | Conforme Conv. 142 | |
| **MA** | Nordeste | 20% | 2% | Conforme Conv. 142 | |
| **MT** | Centro-Oeste | 17% | 0% | Conforme Conv. 142 | |
| **MS** | Centro-Oeste | 17% | 0% | Conforme Conv. 142 | |
| **MG** | Sudeste | 18% | 2% | Conforme Conv. 142 | |
| **PA** | Norte | 17% | 2% | Conforme Conv. 142 | |
| **PB** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **PR** | Sul | 18% | 2% | Conforme Conv. 142 | |
| **PE** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **PI** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **RJ** | Sudeste | **20%** | **2%** | Conforme Conv. 142 | **Interna inclui FECP 2%** |
| **RN** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **RS** | Sul | 18% | 2% | Conforme Conv. 142 | |
| **RO** | Norte | 17,5% | 0% | Conforme Conv. 142 | |
| **RR** | Norte | 17% | 2% | Conforme Conv. 142 | |
| **SC** | Sul | 17% | 2% | Conforme Conv. 142 | |
| **SP** | Sudeste | **18%** | **2%** | Conforme Conv. 142 | **Interna inclui FECOP 2%** |
| **SE** | Nordeste | 18% | 2% | Conforme Conv. 142 | |
| **TO** | Norte | 18% | 0% | Conforme Conv. 142 | |

---

## ⚠️ ALÍQUOTAS INTERNAS QUE JÁ INCLUEM FCP

| UF | Alíquota Informada | ICMS Puro | FCP Incluso | Como Tratar no DIFAL |
|----|-------------------|-----------|-------------|---------------------|
| **BA** | 20,5% | 18% | 2,5% (FECOP) | Usar 18% no DIFAL + FCP 2% separado |
| **RJ** | 20% | 18% | 2% (FECP) | Usar 18% no DIFAL + FCP 2% separado |
| **SP** | 18% | 16% | 2% (FECOP) | Usar 16% no DIFAL + FCP 2% separado |
| **Outras** | 17-18% | 17-18% | 0-2% | Verificar decreto estadual |

> **REGRA DE OURO:** Se alíquota interna já inclui FCP, **não somar FCP novamente** no cálculo do DIFAL. O DIFAL usa a alíquota **líquida de FCP**.

---

## 📊 Alíquotas Interestaduais (Convênio ICMS 236/2021)

| Origem → Destino | Alíquota |
|------------------|----------|
| Sul/Sudeste/CO → Norte/NE | 12% |
| Norte/NE → Sul/Sudeste/CO | 7% |
| Entre Sul/Sudeste/CO | 12% |
| Entre Norte/NE | 7% |
| Importação → Qualquer | 4% |

### Regiões por UF
- **Norte:** AC, AP, AM, PA, RO, RR, TO
- **Nordeste:** AL, BA, CE, MA, PB, PE, PI, RN, SE
- **Centro-Oeste:** DF, GO, MT, MS
- **Sudeste:** ES, MG, RJ, SP
- **Sul:** PR, RS, SC

---

## 🔢 Cálculo DIFAL por Cenário

### Cenário A: Destino NÃO Contribuinte (indIEDest = 9)
```
ICMS_Destino = Alíquota_Interna_Destino_Líquida × BC
ICMS_Origem  = Alíquota_Interestadual × BC
DIFAL = ICMS_Destino - ICMS_Origem
FCP   = Alíquota_FCP_Destino × BC  (se UF tem FCP)
Total = DIFAL + FCP
```

### Cenário B: Destino Contribuinte (indIEDest = 1)
```
DIFAL = (Alíquota_Interna_Destino_Líquida - Alíquota_Interestadual) × BC
FCP   = Alíquota_FCP_Destino × Base_DIFAL
Total = DIFAL + FCP
```

---

## 📦 JSON Consolidado para backend/app/data/icms_rules.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "LC 87/1996, LC 190/2022, Conv. ICMS 174/2023, Conv. ICMS 142/2018",
  "uf_data": {
    "AC": {"regiao": "Norte", "icms_interno": 0.17, "fcp": 0.00, "icms_interno_liquido_fcp": 0.17},
    "AL": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "AP": {"regiao": "Norte", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "AM": {"regiao": "Norte", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16, "obs": "ZFM especial"},
    "BA": {"regiao": "Nordeste", "icms_interno": 0.205, "fcp": 0.02, "icms_interno_liquido_fcp": 0.18, "obs": "Inclui FECOP 2.5%"},
    "CE": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "DF": {"regiao": "CentroOeste", "icms_interno": 0.18, "fcp": 0.00, "icms_interno_liquido_fcp": 0.18},
    "ES": {"regiao": "Sudeste", "icms_interno": 0.17, "fcp": 0.02, "icms_interno_liquido_fcp": 0.15},
    "GO": {"regiao": "CentroOeste", "icms_interno": 0.19, "fcp": 0.00, "icms_interno_liquido_fcp": 0.19},
    "MA": {"regiao": "Nordeste", "icms_interno": 0.20, "fcp": 0.02, "icms_interno_liquido_fcp": 0.18},
    "MT": {"regiao": "CentroOeste", "icms_interno": 0.17, "fcp": 0.00, "icms_interno_liquido_fcp": 0.17},
    "MS": {"regiao": "CentroOeste", "icms_interno": 0.17, "fcp": 0.00, "icms_interno_liquido_fcp": 0.17},
    "MG": {"regiao": "Sudeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "PA": {"regiao": "Norte", "icms_interno": 0.17, "fcp": 0.02, "icms_interno_liquido_fcp": 0.15},
    "PB": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "PR": {"regiao": "Sul", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "PE": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "PI": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "RJ": {"regiao": "Sudeste", "icms_interno": 0.20, "fcp": 0.02, "icms_interno_liquido_fcp": 0.18, "obs": "Inclui FECP 2%"},
    "RN": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "RS": {"regiao": "Sul", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "RO": {"regiao": "Norte", "icms_interno": 0.175, "fcp": 0.00, "icms_interno_liquido_fcp": 0.175},
    "RR": {"regiao": "Norte", "icms_interno": 0.17, "fcp": 0.02, "icms_interno_liquido_fcp": 0.15},
    "SC": {"regiao": "Sul", "icms_interno": 0.17, "fcp": 0.02, "icms_interno_liquido_fcp": 0.15},
    "SP": {"regiao": "Sudeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16, "obs": "Inclui FECOP 2%"},
    "SE": {"regiao": "Nordeste", "icms_interno": 0.18, "fcp": 0.02, "icms_interno_liquido_fcp": 0.16},
    "TO": {"regiao": "Norte", "icms_interno": 0.18, "fcp": 0.00, "icms_interno_liquido_fcp": 0.18}
  },
  "aliquotas_interestaduais": {
    "sul_sudeste_co_para_norte_ne": 0.12,
    "norte_ne_para_sul_sudeste_co": 0.07,
    "entre_sul_sudeste_co": 0.12,
    "entre_norte_ne": 0.07,
    "importacao_para_qualquer": 0.04
  },
  "regioes": {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "CentroOeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"]
  }
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Janeiro 2026 (verificar decretos estaduais)