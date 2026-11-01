# ICMS Diferencial (DIFAL) - Regra ICMS_DIFAL

**Rule Code:** `ICMS_DIFAL`  
**Tipo:** `ICMS_DIFFERENTIAL`  
**Severidade:** `HIGH`  
**Tags:** `icms, interstate`  
**Arquivo de Dados:** `backend/app/data/icms_rules.json`  
**Teste:** `tests/test_rules_critical.py::test_icms_diferential_triggered`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **LC 87/1996** (Art. 2º, §2º) | ICMS nas operações interestaduais | Vigente |
| **LC 190/2022** | Regulamenta a cobrança do DIFAL (destino) | 01/01/2023 |
| **Convênio ICMS 236/2021** | Alíquotas interestaduais (4%, 7%, 12%) | Vigente |
| **STF - ADI 7066/2024** | Constitucionalidade do DIFAL para não contribuintes | Julgada procedente |

---

## 🎯 Quando Aplica

**Operação Interestadual** onde:
- UF Origem ≠ UF Destino
- Destinatário **NÃO** é contribuinte do ICMS (consumidor final, não inscrito)
- Ou destinatário É contribuinte mas opera com diferencial de alíquota

**CT-e/NF-e:** `tpEmis = 1` (normal) ou `tpEmis = 4` (EPEC)

---

## 🧮 Fórmula de Cálculo

```python
# DIFAL = (Alíquota Interestadual - Alíquota Interna Origem) × Base Cálculo
# OU (para destino não contribuinte):
# DIFAL = Alíquota Interna Destino × Base Cálculo - ICMS Recolhido Origem

# Base de Cálculo = Valor Total da NF-e (vNF) + Frete (vFrete) + Seguro (vSeg) + Outras Despesas (vOutro) - Desconto (vDesc)
# Base ICMS = vBC (campo da NF-e)

difal = (aliquota_interna_destino - aliquota_interestadual) * base_calculo
```

### Cenários

| Cenário | Fórmula | Exemplo |
|---------|---------|---------|
| **Destino NÃO contribuinte** | `ICMS_Destino = aliquota_interna_destino * BC`<br>`DIFAL = ICMS_Destino - ICMS_Origem` | SP→RJ (não contrib): 18% × BC - 12% × BC = 6% × BC |
| **Destino Contribuinte** | `DIFAL = (aliquota_interna_destino - aliquota_interestadual) * BC` | SP→RJ (contrib): (18% - 12%) × BC = 6% × BC |
| **Isento/Imune** | DIFAL = 0 | Operações com isenção |

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

| UF | Alíquota Interna Geral | Observação |
|----|------------------------|------------|
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

> ⚠️ **Verificar anualmente** - Estados alteram alíquotas via lei estadual (ex: RJ 20%, BA 20.5%)

---

## 💰 Base de Cálculo (BC) - Campos NF-e/CT-e

| Campo XML | Descrição | Tag |
|-----------|-----------|-----|
| `vBC` | Base de Cálculo do ICMS | `<ICMS><ICMS00><vBC>` |
| `vICMS` | Valor do ICMS | `<ICMS><ICMS00><vICMS>` |
| `vNF` | Valor Total da NF-e | `<total><ICMSTot><vNF>` |
| `vFrete` | Valor do Frete | `<total><ICMSTot><vFrete>` |
| `vSeg` | Valor do Seguro | `<total><ICMSTot><vSeg>` |
| `vOutro` | Outras Despesas | `<total><ICMSTot><vOutro>` |
| `vDesc` | Desconto | `<total><ICMSTot><vDesc>` |
| `UF` (emit/dest) | UF Emitente/Destinatário | `<enderEmit><UF>` / `<enderDest><UF>` |
| `indIEDest` | Indicador IE Destino (1=Contrib, 2=Isento, 9=Não Contrib) | `<indIEDest>` |

---

## 🔍 Lógica de Detecção no Engine

```python
class ICMSDiferencialRule(BaseRule):
    code = "ICMS_DIFAL"
    relevance_tags = {"icms", "interstate"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        # Só aplica se interestadual
        if context.uf_origem == context.uf_destino:
            return False
        # Só aplica se há ICMS na nota
        if context.vICMS <= 0:
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        aliquota_interestadual = self.get_aliquota_interestadual(
            context.uf_origem, context.uf_destino
        )
        aliquota_interna_destino = self.get_aliquota_interna(context.uf_destino)
        
        # ICMS que deveria ter sido recolhido no destino
        icms_devido_destino = context.vBC * aliquota_interna_destino
        # ICMS efetivamente recolhido na origem
        icms_recolhido_origem = context.vICMS
        
        # DIFAL = diferença
        difal = icms_devido_destino - icms_recolhido_origem
        
        if difal > context.vBC * 0.01:  # Mínimo 1% da BC
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(icms_devido_destino, 2),
                actual_value=round(icms_recolhido_origem, 2),
                difference=round(difal, 2),
                details={
                    "uf_origem": context.uf_origem,
                    "uf_destino": context.uf_destino,
                    "aliquota_interstadual": aliquota_interestadual,
                    "aliquota_interna_destino": aliquota_interna_destino,
                    "base_calculo": context.vBC,
                    "ind_ie_dest": context.indIEDest
                }
            )]
        return []
```

---

## 🧪 Casos de Teste (test_rules_critical.py)

```python
# test_icms_diferential_triggered
# SP (18%) → RJ (20%), destinatário não contribuinte
# BC = 10.000, ICMS Origem (12%) = 1.200
# ICMS Devido RJ = 10.000 × 20% = 2.000
# DIFAL = 2.000 - 1.200 = 800

# test_icms_diferential_not_triggered
# SP → SP (mesma UF) - não é interestadual

# test_icms_diferential_same_uf
# Operação interna - rule não deve disparar

# test_icms_diferential_contribuinte_destino
# SP → RJ, destinatário contribuinte
# DIFAL = (20% - 12%) × BC = 8% × BC

# test_icms_diferential_regiao_nordeste
# BA (Nordeste) → SP (Sudeste) = 7% interestadual
# DIFAL = (18% - 7%) × BC = 11% × BC
```

---

## ⚠️ Pontos de Atenção

1. **indIEDest = 9 (Não Contribuinte)**: DIFAL integral = alíquota interna destino × BC
2. **indIEDest = 2 (Isento)**: Verificar legislação estadual - pode não haver DIFAL
3. **Regimes Especiais**: ZFM (AM), Simples Nacional - regras diferenciadas
4. **FCP**: Se UF destino tem FCP, calcular **APÓS** DIFAL (ver `02-ICMS-FCP.md`)
5. **Crédito Presumido**: Alguns estados dão crédito presumido que reduz DIFAL

---

## 📦 JSON para backend/app/data/icms_rules.json

```json
{
  "icms_difal": {
    "version": "2025.1",
    "updated": "2025-01-15",
    "source": "LC 87/1996, LC 190/2022, Convênio ICMS 236/2021",
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
    }
  }
}
```

---

## 🔗 Referências

- [LC 87/1996 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm)
- [LC 190/2022 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm)
- [Convênio ICMS 236/2021 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2021/convenio-icms-236-2021)
- [Manual CT-e 3.00 - Receita Federal](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Portal ICMS por Estado](https://www.icms.ind.br/)

---

**Última Atualização:** 2026-11-01  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar atualizações alíquotas estaduais)