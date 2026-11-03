# FCP - Fundo de Combate à Pobreza - Regra NFE_FCP

**Rule Code:** `NFE_FCP`  
**Tipo:** `ICMS_FCP`  
**Severidade:** `HIGH`  
**Tags:** `fcp, icms, interstate, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/fcp_aliquotas.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_fcp_calculo`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **LC 190/2022** (Art. 3º) | Institui FCP nas operações interestaduais | 01/01/2023 |
| **Convênio ICMS 174/2023** | Alíquotas FCP por UF | Vigente |
| **STF - ADI 7066/2024** | Constitucionalidade FCP | Julgada |
| **Ajuste SINIEF 19/2016** | Campos FCP na NF-e 4.00 (vFCP, vFCPST, vFCPSTRet) | Vigente |

---

## 🎯 O que é FCP

> **Fundo de Combate à Pobreza** - Adicional ao ICMS nas operações interestaduais destinadas a consumidor final não contribuinte, para financiar programas de combate à pobreza.

**Aplica-se quando:**
- Operação **interestadual** (UF Origem ≠ UF Destino)
- Destinatário **NÃO contribuinte** (`indIEDest = 9`)
- **Além do DIFAL** - FCP é calculado **APÓS** o ICMS/DIFAL

---

## 🧮 Fórmula de Cálculo

### FCP Próprio (Operação Própria)
```
vFCP = vBC × aliquota_FCP_destino
```

### FCP sobre ST (Substituição Tributária)
```
vFCPST = vBCST × aliquota_FCP_destino
```

### FCP Retido (ST Retido Anterior)
```
vFCPSTRet = vBCSTRet × aliquota_FCP_destino
```

---

## 📊 Alíquotas FCP por UF (Convênio ICMS 174/2023 - 2024/2025)

| UF | FCP (%) | Observação |
|----|---------|------------|
| **AC** | 2% | |
| **AL** | 2% | |
| **AP** | 2% | |
| **AM** | 2% | ZFM: isento |
| **BA** | 2.5% | FECOP estadual |
| **CE** | 2% | |
| **DF** | 2% | |
| **ES** | 2% | |
| **GO** | 2% | |
| **MA** | 2% | |
| **MT** | 2% | |
| **MS** | 2% | |
| **MG** | 2% | |
| **PA** | 2% | |
| **PB** | 2% | |
| **PR** | 2% | |
| **PE** | 2% | |
| **PI** | 2% | |
| **RJ** | 2% | FECP estadual |
| **RN** | 2% | |
| **RS** | 2% | |
| **RO** | 2% | |
| **RR** | 2% | |
| **SC** | 2% | |
| **SP** | 2% | |
| **SE** | 2% | |
| **TO** | 2% | |

> ⚠️ **MAIORIA 2%**. BA e RJ têm adicionais estaduais (FECOP/FECP). ZFM (AM) isento.

---

## 💰 Campos NF-e 4.00 (Grupo ICMS)

| Campo | Descrição | Tag XML |
|-------|-----------|---------|
| `vFCP` | Valor FCP operação própria | `<ICMS><ICMS00><vFCP>` |
| `vFCPST` | Valor FCP retido por ST | `<ICMS><ICMS10><vFCPST>` |
| `vFCPSTRet` | Valor FCP retido ST anterior | `<ICMS><ICMS60><vFCPSTRet>` |
| `pFCP` | Percentual FCP | `<ICMS><ICMS00><pFCP>` |
| `pFCPST` | Percentual FCP ST | `<ICMS><ICMS10><pFCPST>` |

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEFCPRule(BaseRule):
    code = "NFE_FCP"
    relevance_tags = {"fcp", "icms", "interstate", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        # Só interestadual
        if context.uf_emitente == context.uf_destino:
            return False
        # Só não contribuinte (FCP só para não contribuinte)
        if context.indIEDest != 9:
            return False
        # Só se UF destino tem FCP
        return self.uf_tem_fcp(context.uf_destino)
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        aliquota_fcp = self.get_aliquota_fcp(context.uf_destino)
        if aliquota_fcp == 0:
            return []
        
        # 1. FCP Próprio (vFCP)
        vFCP_esperado = context.vBC * aliquota_fcp
        if abs(context.vFCP - vFCP_esperado) > context.vNF * 0.001:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(vFCP_esperado, 2),
                actual_value=round(context.vFCP, 2),
                difference=round(abs(context.vFCP - vFCP_esperado), 2),
                details={
                    "tipo": "FCP_PROPRIO",
                    "campo": "vFCP",
                    "uf_destino": context.uf_destino,
                    "aliquota_fcp": aliquota_fcp,
                    "base_calculo": context.vBC
                }
            ))
        
        # 2. FCP ST (vFCPST) - se CST 10/30/70
        if context.cst_icms in ["10", "30", "70"] and context.vBCST > 0:
            vFCPST_esperado = context.vBCST * aliquota_fcp
            if abs(context.vFCPST - vFCPST_esperado) > context.vNF * 0.001:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    expected_value=round(vFCPST_esperado, 2),
                    actual_value=round(context.vFCPST, 2),
                    difference=round(abs(context.vFCPST - vFCPST_esperado), 2),
                    details={
                        "tipo": "FCP_ST",
                        "campo": "vFCPST",
                        "uf_destino": context.uf_destino,
                        "aliquota_fcp": aliquota_fcp,
                        "base_calculo": context.vBCST
                    }
                ))
        
        # 3. FCP ST Retido (vFCPSTRet) - se CST 60
        if context.cst_icms == "60" and context.vBCSTRet > 0:
            vFCPSTRet_esperado = context.vBCSTRet * aliquota_fcp
            if abs(context.vFCPSTRet - vFCPSTRet_esperado) > context.vNF * 0.001:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    expected_value=round(vFCPSTRet_esperado, 2),
                    actual_value=round(context.vFCPSTRet, 2),
                    difference=round(abs(context.vFCPSTRet - vFCPSTRet_esperado), 2),
                    details={
                        "tipo": "FCP_ST_RETIDO",
                        "campo": "vFCPSTRet",
                        "uf_destino": context.uf_destino,
                        "aliquota_fcp": aliquota_fcp
                    }
                ))
        
        return discrepancies
```

---

## 🧮 Exemplos Práticos

### Exemplo 1: SP → RJ, Não Contribuinte, CST 00
```
NF-e:
- UF Origem: SP
- UF Destino: RJ (FCP 2%)
- indIEDest: 9
- vBC: 10.650,00
- CST: 00

Cálculo:
- DIFAL (ver 03-ICMS-DIFAL): (20% - 12%) × 10.650 = 852,00
- FCP: 10.650 × 2% = 213,00
- Total recolher destino: 852,00 + 213,00 = 1.065,00

Campos NF-e:
- vICMS: 1.278,00 (12% interestadual)
- vFCP: 213,00
- pFCP: 2.00
```

### Exemplo 2: SP → RJ, Não Contribuinte, CST 10 (com ST)
```
- vBC: 10.650,00
- vBCST: 17.998,50
- CST: 10
- UF Destino: RJ (FCP 2%, ICMS 20%)

Cálculo:
- ICMS próprio: 10.650 × 20% = 2.130,00 (vICMS)
- ICMS ST: 17.998,50 × 20% - 2.130,00 = 1.469,70 (vICMSST)
- FCP próprio: 10.650 × 2% = 213,00 (vFCP)
- FCP ST: 17.998,50 × 2% = 359,97 (vFCPST)
- Total FCP: 213,00 + 359,97 = 572,97

Campos NF-e:
- vICMS: 2.130,00
- vICMSST: 1.469,70
- vFCP: 213,00
- vFCPST: 359,97
```

### Exemplo 3: SP → BA, Não Contribuinte (FCP 2.5%)
```
- UF Destino: BA (FCP 2.5%)
- vBC: 10.650,00
- FCP: 10.650 × 2.5% = 266,25
```

---

## 🧪 Casos de Teste

```python
# test_nfe_fcp_calculo_cst00
# SP→RJ, indIEDest=9, vBC=10650, CST=00
# vFCP = 10650 * 2% = 213.00

# test_nfe_fcp_calculo_cst10_com_st
# SP→RJ, indIEDest=9, vBC=10650, vBCST=17998.50, CST=10
# vFCP = 213.00, vFCPST = 359.97

# test_nfe_fcp_calculo_cst60_st_retido
# SP→RJ, indIEDest=9, CST=60, vBCSTRet=15000
# vFCPSTRet = 15000 * 2% = 300.00

# test_nfe_fcp_nao_se_aplica_mesma_uf
# SP→SP → FCP = 0

# test_nfe_fcp_nao_se_aplica_contribuinte
# indIEDest=1 → FCP = 0 (só para não contribuinte)

# test_nfe_fcp_uf_sem_fcp
# UF sem FCP (ex: antiga legislação) → FCP = 0

# test_nfe_fcp_zfm_am
# Destino AM (ZFM) → FCP = 0 (isento)

# test_nfe_fcp_ba_aliquota_diferenciada
# SP→BA, FCP 2.5% → vFCP = BC * 2.5%
```

---

## ⚠️ Pontos de Atenção

1. **FCP SÓ para não contribuinte** (`indIEDest = 9`)
2. **FCP SÓ interestadual** (UF origem ≠ UF destino)
3. **Ordem de cálculo**: ICMS → DIFAL → FCP (ou ST → FCP)
4. **Maioria UFs = 2%**, exceto BA (2.5%), RJ (2% + FECP), AM (isento ZFM)
5. **Três campos**: vFCP (próprio), vFCPST (ST), vFCPSTRet (ST retido)
6. **Base FCP ST** = vBCST (base ST), não vBC
7. **Não confunde com FECOP/FECP** - esses são fundos estaduais (BA, RJ)
8. **Simples Nacional**: FCP pode não aplicar (ver 16-REGRAS-ESPECIAIS.md)

---

## 📦 JSON para backend/app/data/nfe/fcp_aliquotas.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "LC 190/2022, Convênio ICMS 174/2023",
  "aliquotas_fcp": {
    "AC": 0.02, "AL": 0.02, "AP": 0.02, "AM": 0.00,
    "BA": 0.025, "CE": 0.02, "DF": 0.02, "ES": 0.02,
    "GO": 0.02, "MA": 0.02, "MT": 0.02, "MS": 0.02,
    "MG": 0.02, "PA": 0.02, "PB": 0.02, "PR": 0.02,
    "PE": 0.02, "PI": 0.02, "RJ": 0.02, "RN": 0.02,
    "RS": 0.02, "RO": 0.02, "RR": 0.02, "SC": 0.02,
    "SP": 0.02, "SE": 0.02, "TO": 0.02
  },
  "observacoes": {
    "AM": "ZFM - Isento FCP",
    "BA": "2.5% (inclui FECOP estadual)",
    "RJ": "2% + FECP estadual separado",
    "geral": "FCP só se aplica: interestadual + indIEDest=9 (não contribuinte)"
  },
  "campos_nfe": {
    "vFCP": "FCP operação própria",
    "vFCPST": "FCP retenção ST",
    "vFCPSTRet": "FCP retenção ST anterior",
    "pFCP": "Alíquota FCP própria",
    "pFCPST": "Alíquota FCP ST"
  },
  "ordem_calculo": [
    "ICMS_PROPRIO",
    "ICMS_ST",
    "DIFAL",
    "FCP_PROPRIO",
    "FCP_ST",
    "FCP_ST_RETIDO"
  ]
}
```

---

## 🔗 Referências

- [LC 190/2022 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm)
- [Convênio ICMS 174/2023 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2023/convenio-icms-174-2023)
- [Manual NF-e 4.00 - Campos FCP](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar Convênio ICMS 174 atualizações)