# DIFAL NF-e (Diferencial de Alíquota) - Regra NFE_DIFAL

**Rule Code:** `NFE_DIFAL`  
**Tipo:** `ICMS_DIFFERENTIAL`  
**Severidade:** `CRITICAL`  
**Tags:** `icms, difal, interstate, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/icms_difal.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_difal_nao_contribuinte`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **LC 87/1996** (Art. 2º, §2º) | ICMS nas operações interestaduais | Vigente |
| **LC 190/2022** | Regulamenta DIFAL para destinatário não contribuinte | 01/01/2023 |
| **Convênio ICMS 236/2021** | Alíquotas interestaduais (4%, 7%, 12%) | Vigente |
| **STF - ADI 7066/2024** | Constitucionalidade DIFAL não contribuintes | Julgada procedente |
| **Ajuste SINIEF 19/2016** | Campos indIEDest, UF destino na NF-e 4.00 | Vigente |

---

## 🎯 Quando Aplica (NF-e)

**Operação Interestadual** onde:
- UF Emitente ≠ UF Destinatário (`<enderEmit><UF>` ≠ `<enderDest><UF>`)
- **Destinatário NÃO é contribuinte do ICMS** (`indIEDest = 9`)
- Ou destinatário É contribuinte mas opera com diferencial (`indIEDest = 1`)

**NF-e:** `tpEmis = 1` (normal) ou `tpEmis = 4` (EPEC) ou `tpEmis = 5` (FS-DA)

---

## 🧮 Fórmula de Cálculo NF-e

### Cenário 1: Destinatário NÃO Contribuinte (`indIEDest = 9`) - MAIS COMUM
```
# ICMS que DEVERIA ser recolhido no destino
ICMS_Destino = vBC × aliquota_interna_destino

# ICMS efetivamente recolhido na origem (informado na NF-e)
ICMS_Origem = vICMS

# DIFAL = Diferença a recolher no destino
DIFAL = ICMS_Destino - ICMS_Origem
```

### Cenário 2: Destinatário Contribuinte (`indIEDest = 1`)
```
# DIFAL = Diferença entre alíquota interna destino e interestadual
DIFAL = (aliquota_interna_destino - aliquota_interestadual) × vBC
```

### Cenário 3: Isento/Imune (`indIEDest = 2`)
```
# Verificar legislação estadual - geralmente DIFAL = 0
DIFAL = 0
```

---

## 📊 Alíquotas Interestaduais (Convênio ICMS 236/2021)

| Origem → Destino | Alíquota |
|------------------|----------|
| **Sul/Sudeste/Centro-Oeste** → **Norte/Nordeste** | **12%** |
| **Norte/Nordeste** → **Sul/Sudeste/Centro-Oeste** | **7%** |
| **Entre Sul/Sudeste/Centro-Oeste** | **12%** |
| **Entre Norte/Nordeste** | **7%** |
| **Importação** → Qualquer UF | **4%** |

### Regiões por UF
| Região | UFs |
|--------|-----|
| **Norte** | AC, AP, AM, PA, RO, RR, TO |
| **Nordeste** | AL, BA, CE, MA, PB, PE, PI, RN, SE |
| **Centro-Oeste** | DF, GO, MT, MS |
| **Sudeste** | ES, MG, RJ, SP |
| **Sul** | PR, RS, SC |

---

## 📋 Alíquotas Internas por UF (2024/2025)

| UF | Alíquota Interna | Observação |
|----|------------------|------------|
| **AC** | 17% | |
| **AL** | 18% | |
| **AP** | 18% | |
| **AM** | 18% | ZFM: regimes especiais |
| **BA** | 20.5% | 18% + 2.5% FECOP |
| **CE** | 18% | |
| **DF** | 18% | |
| **ES** | 17% | |
| **GO** | 19% | |
| **MA** | 20% | |
| **MT** | 17% | |
| **MS** | 17% | |
| **MG** | 18% | |
| **PA** | 17% | |
| **PB** | 18% | |
| **PR** | 18% | |
| **PE** | 18% | |
| **PI** | 18% | |
| **RJ** | 20% | 18% + 2% FECP |
| **RN** | 18% | |
| **RS** | 18% | |
| **RO** | 17.5% | |
| **RR** | 17% | |
| **SC** | 17% | |
| **SP** | 18% | |
| **SE** | 18% | |
| **TO** | 18% | |

---

## 💰 Base de Cálculo (vBC) - Campos NF-e

| Campo XML | Descrição | Tag NF-e 4.00 |
|-----------|-----------|---------------|
| `vBC` | Base Cálculo ICMS | `<ICMS><ICMS00><vBC>` |
| `vICMS` | Valor ICMS | `<ICMS><ICMS00><vICMS>` |
| `vNF` | Valor Total NF-e | `<total><ICMSTot><vNF>` |
| `vFrete` | Valor Frete | `<total><ICMSTot><vFrete>` |
| `vSeg` | Valor Seguro | `<total><ICMSTot><vSeg>` |
| `vOutro` | Outras Despesas | `<total><ICMSTot><vOutro>` |
| `vDesc` | Desconto | `<total><ICMSTot><vDesc>` |
| `UF Emitente` | UF do Emitente | `<enderEmit><UF>` |
| `UF Destino` | UF do Destinatário | `<enderDest><UF>` |
| `indIEDest` | Indicador IE Destino | `<indIEDest>` (1=Contrib, 2=Isento, 9=Não Contrib) |
| `IE Destino` | Inscrição Estadual | `<enderDest><IE>` (se contrib) |

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEDifalRule(BaseRule):
    code = "NFE_DIFAL"
    relevance_tags = {"icms", "difal", "interstate", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        # Só interestadual
        if context.uf_emitente == context.uf_destino:
            return False
        # Só se há ICMS na nota
        if context.vICMS <= 0 and context.vICMSST <= 0:
            return False
        # Só se destinatário não contribuinte OU contribuinte com diferencial
        return context.indIEDest in [1, 9]
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # Obter alíquotas
        aliquota_interestadual = self.get_aliquota_interestadual(
            context.uf_emitente, context.uf_destino
        )
        aliquota_interna_destino = self.get_aliquota_interna(context.uf_destino)
        
        # Base cálculo (vBC da NF-e)
        vBC = context.vBC
        
        if context.indIEDest == 9:  # Não Contribuinte
            # ICMS devido no destino = alíquota interna × BC
            icms_devido_destino = vBC * aliquota_interna_destino
            # ICMS recolhido na origem
            icms_recolhido_origem = context.vICMS
            
            # DIFAL = diferença
            difal = icms_devido_destino - icms_recolhido_origem
            
            # Se há ST, ICMS próprio já foi antecipado
            if context.cst_icms in ["10", "30", "70"]:
                # vICMS já inclui ICMS próprio antecipado
                # DIFAL = ICMS_destino - ICMS_próprio_antecipado
                pass  # Lógica já coberta acima
            
        elif context.indIEDest == 1:  # Contribuinte
            # DIFAL = (interna_destino - interestadual) × BC
            difal = (aliquota_interna_destino - aliquota_interestadual) * vBC
        
        else:  # Isento (2) - verificar legislação
            difal = 0
        
        # Só dispara se DIFAL significativo (> 1% da BC)
        if difal > vBC * 0.01:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="CRITICAL",
                expected_value=round(icms_devido_destino if context.indIEDest == 9 else vBC * aliquota_interna_destino, 2),
                actual_value=round(context.vICMS, 2),
                difference=round(difal, 2),
                details={
                    "uf_emitente": context.uf_emitente,
                    "uf_destino": context.uf_destino,
                    "indIEDest": context.indIEDest,
                    "aliquota_interstadual": aliquota_interestadual,
                    "aliquota_interna_destino": aliquota_interna_destino,
                    "base_calculo": vBC,
                    "icms_origem": context.vICMS,
                    "icms_devido_destino": round(icms_devido_destino if context.indIEDest == 9 else vBC * aliquota_interna_destino, 2),
                    "difal_calculado": round(difal, 2),
                    "cenario": "Nao_Contribuinte" if context.indIEDest == 9 else "Contribuinte"
                }
            ))
        
        return discrepancies
```

---

## 🧮 Exemplos Práticos

### Exemplo 1: SP → RJ, Não Contribuinte (`indIEDest=9`)
```
NF-e:
- UF Emitente: SP (18%)
- UF Destino: RJ (20%)  
- indIEDest: 9 (Não Contribuinte)
- vNF: 10.000,00
- vFrete: 500,00
- vSeg: 100,00
- vOutro: 50,00
- vDesc: 0,00
- CST: 00
- vBC: 10.650,00 (vNF + vFrete + vSeg + vOutro - vDesc)
- vICMS: 1.278,00 (12% interestadual SP→RJ)

Cálculo:
- Alíquota Interestadual SP→RJ: 12% (Sudeste→Sudeste)
- Alíquota Interna RJ: 20%
- ICMS Devido Destino: 10.650 × 20% = 2.130,00
- ICMS Recolhido Origem: 1.278,00
- DIFAL: 2.130,00 - 1.278,00 = 852,00

⚠️ DIVERGÊNCIA: DIFAL de R$ 852,00 não recolhido!
```

### Exemplo 2: SP → RJ, Contribuinte (`indIEDest=1`)
```
Mesmos dados, mas indIEDest = 1

Cálculo:
- DIFAL = (20% - 12%) × 10.650 = 8% × 10.650 = 852,00
- Mesmo valor, mas base legal diferente (LC 87/96 vs LC 190/2022)
```

### Exemplo 3: BA (Nordeste) → SP (Sudeste), Não Contribuinte
```
- UF Origem: BA (Nordeste) - alíquota interna 20.5%
- UF Destino: SP (Sudeste) - alíquota interna 18%
- Alíquota Interestadual: 7% (Nordeste→Sudeste)
- vBC: 10.650,00
- vICMS: 745,50 (7%)

Cálculo:
- ICMS Devido SP: 10.650 × 18% = 1.917,00
- ICMS Recolhido BA: 745,50
- DIFAL: 1.917,00 - 745,50 = 1.171,50
```

### Exemplo 4: Com ST (CST 10)
```
- CST: 10 (Tributada com ST)
- vBC: 10.650,00
- vICMS (próprio antecipado): 2.130,00 (20% interna RJ)
- vBCST: 17.998,50
- vICMSST: 1.469,70

DIFAL para não contribuinte:
- ICMS Devido Destino: 10.650 × 20% = 2.130,00
- ICMS Recolhido Origem (vICMS próprio): 2.130,00
- DIFAL: 2.130,00 - 2.130,00 = 0,00 ✓

⚠️ ATENÇÃO: Se CST 10 usa alíquota interna destino no vICMS, DIFAL = 0
```

---

## 🧪 Casos de Teste

```python
# test_nfe_difal_nao_contribuinte
# SP→RJ, indIEDest=9, vBC=10650, vICMS=1278 (12%)
# DIFAL = 10650*20% - 1278 = 2130 - 1278 = 852

# test_nfe_difal_contribuinte
# SP→RJ, indIEDest=1, vBC=10650
# DIFAL = (20% - 12%) * 10650 = 852

# test_nfe_difal_mesma_uf
# SP→SP, indIEDest=9 → NÃO APLICA (não interestadual)

# test_nfe_difal_isento
# SP→RJ, indIEDest=2 → DIFAL = 0 (verificar lei estadual)

# test_nfe_difal_com_st_cst10
# CST 10, vICMS usa alíquota interna destino → DIFAL = 0

# test_nfe_difal_com_st_cst60
# CST 60, vICMS=0, vICMSST=valor_retido
# DIFAL calculado sobre vBC normal

# test_nfe_difal_regiao_nordeste_para_sudeste
# BA→SP, interestadual 7%, interna SP 18%
# DIFAL = (18% - 7%) * BC = 11% * BC

# test_nfe_difal_importacao
# Importação→SP, interestadual 4%, interna SP 18%
# DIFAL = (18% - 4%) * BC = 14% * BC
```

---

## ⚠️ Pontos de Atenção NF-e

1. **indIEDest = 9 (Não Contribuinte)**: DIFAL integral = alíquota interna destino × BC
2. **indIEDest = 2 (Isento)**: Verificar legislação estadual - pode não haver DIFAL
3. **Regimes Especiais**: ZFM (AM), Simples Nacional - regras diferenciadas
4. **FCP**: Se UF destino tem FCP, calcular **APÓS** DIFAL (ver 04-FCP.md)
5. **Crédito Presumido**: Alguns estados dão crédito presumido que reduz DIFAL
6. **CST 10/30/70**: Se vICMS já calculado com alíquota interna destino, DIFAL ≈ 0
7. **CST 60**: ICMS retido anterior - vICMS=0, DIFAL calculado normal
8. **Simples Nacional**: Optante Simples (CSOSN) - DIFAL pode não aplicar (ver 16-REGRAS-ESPECIAIS.md)

---

## 📦 JSON para backend/app/data/nfe/icms_difal.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "LC 87/1996, LC 190/2022, Convênio ICMS 236/2021, STF ADI 7066",
  "aliquotas_interestaduais": {
    "sul_sudeste_centrooeste_para_norte_nordeste": 0.12,
    "norte_nordeste_para_sul_sudeste_centrooeste": 0.07,
    "entre_sul_sudeste_centrooeste": 0.12,
    "entre_norte_nordeste": 0.07,
    "importacao_para_qualquer_uf": 0.04
  },
  "aliquotas_internas": {
    "AC": 0.17, "AL": 0.18, "AP": 0.18, "AM": 0.18,
    "BA": 0.205, "CE": 0.18, "DF": 0.18, "ES": 0.17,
    "GO": 0.19, "MA": 0.20, "MT": 0.17, "MS": 0.17,
    "MG": 0.18, "PA": 0.17, "PB": 0.18, "PR": 0.18,
    "PE": 0.18, "PI": 0.18, "RJ": 0.20, "RN": 0.18,
    "RS": 0.18, "RO": 0.175, "RR": 0.17, "SC": 0.17,
    "SP": 0.18, "SE": 0.18, "TO": 0.18
  },
  "regioes": {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "CentroOeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"]
  },
  "indIEDest": {
    "1": "Contribuinte ICMS",
    "2": "Isento ICMS",
    "9": "Nao Contribuinte ICMS"
  },
  "regras_difal": {
    "nao_contribuinte": "DIFAL = aliquota_interna_destino * vBC - vICMS_origem",
    "contribuinte": "DIFAL = (aliquota_interna_destino - aliquota_interestadual) * vBC",
    "isento": "Verificar legislacao estadual - geralmente 0",
    "minimo_disparo": "1% da BC"
  }
}
```

---

## 🔗 Referências

- [LC 87/1996 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm)
- [LC 190/2022 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm)
- [Convênio ICMS 236/2021 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2021/convenio-icms-236-2021)
- [STF ADI 7066 - Supremo](https://portal.stf.jus.br/processos/detalhe.asp?incidente=5633265)
- [Manual NF-e 4.00 - indIEDest](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar alíquotas estaduais)