# Tabela Consolidada Alíquotas por UF - Referência NFE

**Arquivo:** `15-ALIQUOTAS-UF.md`  
**Tipo:** `REFERENCE`  
**Prioridade:** `CRITICAL`  
**Uso:** Consolidação para `backend/app/data/nfe/` e `backend/app/data/icms_rules.json`

---

## 📜 Base Legal Consolidada

| Norma | Alíquotas Definidas |
|-------|---------------------|
| **Convênio ICMS 236/2021** | Interestaduais (4%, 7%, 12%) |
| **Convênio ICMS 174/2023** | FCP por UF |
| **LC 190/2022** | DIFAL regulamentado |
| **RICMS/UF (27 + DF)** | Internas, ST, FECOP/FECP |

---

## 📊 Tabela Mestra Alíquotas 2024/2025

| UF | Região | ICMS Interna | FCP | FECOP/FECP | Total Efetiva | DIFAL Base | Observação |
|----|--------|--------------|-----|------------|---------------|------------|------------|
| **AC** | Norte | 17.0% | 2% | - | 19.0% | 17% | |
| **AL** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **AP** | Norte | 18.0% | 2% | - | 20.0% | 18% | |
| **AM** | Norte | 18.0% | 0% (ZFM) | - | 18.0% | 18% | ZFM isento FCP |
| **BA** | Nordeste | 18.0% | 2.5% | 2.5% FECOP | 23.0% | 20.5% | FECOP estadual |
| **CE** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **DF** | Centro-Oeste | 18.0% | 2% | - | 20.0% | 18% | |
| **ES** | Sudeste | 17.0% | 2% | - | 19.0% | 17% | |
| **GO** | Centro-Oeste | 19.0% | 2% | - | 21.0% | 19% | |
| **MA** | Nordeste | 20.0% | 2% | - | 22.0% | 20% | |
| **MT** | Centro-Oeste | 17.0% | 2% | - | 19.0% | 17% | |
| **MS** | Centro-Oeste | 17.0% | 2% | - | 19.0% | 17% | |
| **MG** | Sudeste | 18.0% | 2% | - | 20.0% | 18% | |
| **PA** | Norte | 17.0% | 2% | - | 19.0% | 17% | |
| **PB** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **PR** | Sul | 18.0% | 2% | - | 20.0% | 18% | |
| **PE** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **PI** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **RJ** | Sudeste | 18.0% | 2% | 2% FECP | 22.0% | 20% | FECP estadual |
| **RN** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **RS** | Sul | 18.0% | 2% | - | 20.0% | 18% | |
| **RO** | Norte | 17.5% | 2% | - | 19.5% | 17.5% | |
| **RR** | Norte | 17.0% | 2% | - | 19.0% | 17% | |
| **SC** | Sul | 17.0% | 2% | - | 19.0% | 17% | |
| **SP** | Sudeste | 18.0% | 2% | - | 20.0% | 18% | |
| **SE** | Nordeste | 18.0% | 2% | - | 20.0% | 18% | |
| **TO** | Norte | 18.0% | 2% | - | 20.0% | 18% | |

---

## 🌍 Regiões para Alíquotas Interestaduais

| Região | UFs |
|--------|-----|
| **Norte** | AC, AP, AM, PA, RO, RR, TO |
| **Nordeste** | AL, BA, CE, MA, PB, PE, PI, RN, SE |
| **Centro-Oeste** | DF, GO, MT, MS |
| **Sudeste** | ES, MG, RJ, SP |
| **Sul** | PR, RS, SC |

---

## 📈 Alíquotas Interestaduais (Convênio ICMS 236/2021)

| Origem → Destino | Alíquota |
|------------------|----------|
| **Sul/Sudeste/Centro-Oeste** → **Norte/Nordeste** | **12%** |
| **Norte/Nordeste** → **Sul/Sudeste/Centro-Oeste** | **7%** |
| **Entre Sul/Sudeste/Centro-Oeste** | **12%** |
| **Entre Norte/Nordeste** | **7%** |
| **Importação** → Qualquer UF | **4%** |

### Matriz Resumida

| Origem \ Destino | Norte/Nordeste | Sul/Sudeste/CO |
|------------------|----------------|----------------|
| **Norte/Nordeste** | 7% | 7% |
| **Sul/Sudeste/CO** | 12% | 12% |

---

## 🧮 Cálculos Combinados (DIFAL + FCP)

### Para Não Contribuinte (indIEDest=9) - Interestadual

```
ICMS Devido Destino = vBC × Alíquota Interna Destino
FCP Devido = vBC × Alíquota FCP Destino
ICMS Recolhido Origem = vBC × Alíquota Interestadual
DIFAL = ICMS Devido Destino - ICMS Recolhido Origem
TOTAL RECOLHER DESTINO = DIFAL + FCP
```

### Exemplo SP → RJ (Não Contribuinte)
```
vBC = 10.650,00
Alíquota Interestadual SP→RJ = 12%
Alíquota Interna RJ = 20% (18% + 2% FECP)
FCP RJ = 2%

ICMS Origem = 10.650 × 12% = 1.278,00
ICMS Devido RJ = 10.650 × 20% = 2.130,00
FCP Devido = 10.650 × 2% = 213,00
DIFAL = 2.130 - 1.278 = 852,00
TOTAL = 852 + 213 = 1.065,00
```

### Exemplo BA → SP (Não Contribuinte)
```
vBC = 10.650,00
Alíquota Interestadual BA→SP = 7% (Nordeste→Sudeste)
Alíquota Interna SP = 18%
FCP SP = 2%

ICMS Origem = 10.650 × 7% = 745,50
ICMS Devido SP = 10.650 × 18% = 1.917,00
FCP Devido = 10.650 × 2% = 213,00
DIFAL = 1.917 - 745,50 = 1.171,50
TOTAL = 1.171,50 + 213 = 1.384,50
```

---

## 📦 JSON Consolidado para Backend

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Convênio ICMS 236/2021, 174/2023, LC 190/2022, RICMS/UF 2024/2025",
  "aliquotas_internas": {
    "AC": 0.17, "AL": 0.18, "AP": 0.18, "AM": 0.18,
    "BA": 0.205, "CE": 0.18, "DF": 0.18, "ES": 0.17,
    "GO": 0.19, "MA": 0.20, "MT": 0.17, "MS": 0.17,
    "MG": 0.18, "PA": 0.17, "PB": 0.18, "PR": 0.18,
    "PE": 0.18, "PI": 0.18, "RJ": 0.20, "RN": 0.18,
    "RS": 0.18, "RO": 0.175, "RR": 0.17, "SC": 0.17,
    "SP": 0.18, "SE": 0.18, "TO": 0.18
  },
  "aliquotas_fcp": {
    "AC": 0.02, "AL": 0.02, "AP": 0.02, "AM": 0.00,
    "BA": 0.025, "CE": 0.02, "DF": 0.02, "ES": 0.02,
    "GO": 0.02, "MA": 0.02, "MT": 0.02, "MS": 0.02,
    "MG": 0.02, "PA": 0.02, "PB": 0.02, "PR": 0.02,
    "PE": 0.02, "PI": 0.02, "RJ": 0.02, "RN": 0.02,
    "RS": 0.02, "RO": 0.02, "RR": 0.02, "SC": 0.02,
    "SP": 0.02, "SE": 0.02, "TO": 0.02
  },
  "adicionais_estaduais": {
    "BA": {"nome": "FECOP", "aliquota": 0.025, "incluida_em_interna": true},
    "RJ": {"nome": "FECP", "aliquota": 0.02, "incluida_em_interna": true},
    "AM": {"nome": "ZFM", "isento_fcp": true, "regime_especial": true}
  },
  "regioes_interestaduais": {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "CentroOeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"]
  },
  "aliquotas_interestaduais": {
    "sul_sudeste_co_para_norte_ne": 0.12,
    "norte_ne_para_sul_sudeste_co": 0.07,
    "entre_sul_sudeste_co": 0.12,
    "entre_norte_ne": 0.07,
    "importacao_para_qualquer": 0.04
  },
  "calculo_difal_fcp": {
    "nao_contribuinte": {
      "icms_devido_destino": "vBC * aliquota_interna_destino",
      "fcp_devido": "vBC * aliquota_fcp_destino",
      "icms_recolhido_origem": "vBC * aliquota_interestadual",
      "difal": "icms_devido_destino - icms_recolhido_origem",
      "total_recolher": "difal + fcp_devido"
    },
    "contribuinte": {
      "difal": "vBC * (aliquota_interna_destino - aliquota_interestadual)",
      "fcp": 0
    },
    "isento": {
      "difal": 0,
      "fcp": 0,
      "observacao": "Verificar legislacao estadual"
    }
  }
}
```

---

## ⚠️ Alertas de Atualização

1. **Janeiro de cada ano**: Estados publicam novas alíquotas internas
2. **Convênio ICMS 174**: Atualiza FCP anualmente (geralmente janeiro)
3. **FECOP/FECP**: BA e RJ têm fundos estaduais próprios
4. **ZFM (AM)**: Regime especial - isenção FCP, alíquotas diferenciadas
5. **Simples Nacional**: Regras próprias de ICMS (ver 16-REGRAS-ESPECIAIS.md)

---

## 🔗 Referências

- [Convênio ICMS 236/2021](https://www.confaz.fazenda.gov.br/legislacao/convenios/2021/convenio-icms-236-2021)
- [Convênio ICMS 174/2023](https://www.confaz.fazenda.gov.br/legislacao/convenios/2023/convenio-icms-174-2023)
- [LC 190/2022](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm)
- [Portal ICMS por Estado](https://www.icms.ind.br/)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (obrigatório - alíquotas estaduais)