# FCP - Fundo de Combate à Pobreza - Regra ICMS_FCP

**Rule Code:** `ICMS_FCP`  
**Tipo:** `ICMS_FCP`  
**Severidade:** `HIGH`  
**Tags:** `icms, interstate`  
**Arquivo de Dados:** `backend/app/data/icms_rules.json` (seção `fcp`)  
**Teste:** `tests/test_rules_critical.py::test_fcp_rule`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **EC 42/2003** | Cria o FCP (art. 82 do ADCT) | 2003 |
| **LC 190/2022** (Art. 4º) | Regulamenta FCP nas operações interestaduais | 01/01/2023 |
| **Convênio ICMS 174/2023** | Alíquotas FCP por UF destino | 2023+ |
| **Convênio ICMS 236/2021** | Base de cálculo (inclui FCP no DIFAL) | Vigente |

---

## 🎯 Quando Aplica

**Operação Interestadual** com destino para UF que instituiu FCP:
- UF Origem ≠ UF Destino
- UF Destino possui FCP vigente
- **Incide sobre a mesma base do DIFAL** (operações para não contribuintes)
- **Ou sobre a diferença de alíquota** (operações para contribuintes)

---

## 🧮 Fórmula de Cálculo

```python
# FCP = Alíquota FCP (UF Destino) × Base de Cálculo do DIFAL

# Para não contribuinte (indIEDest = 9):
# Base FCP = Base Cálculo ICMS (vBC) da NF-e
# FCP = aliquota_fcp_destino * vBC

# Para contribuinte (indIEDest = 1):
# Base FCP = (aliquota_interna_destino - aliquota_interestadual) * vBC
# FCP = aliquota_fcp_destino * base_difal
```

### Importante: FCP **NÃO** compõe base de cálculo do ICMS
- FCP é **adicional** ao ICMS
- Calculado **APÓS** o DIFAL
- Não gera crédito para o destinatário

---

## 📊 Alíquotas FCP por UF (Convênio ICMS 174/2023 - Atualizado 2024/2025)

| UF | Alíquota FCP | Observação | Vigência |
|----|--------------|------------|----------|
| **AC** | 0% | Não instituiu | - |
| **AL** | 2% | Lei estadual | 2023+ |
| **AP** | 2% | Lei estadual | 2023+ |
| **AM** | 2% | Exceto ZFM | 2023+ |
| **BA** | 2% | FECOP integrado | 2023+ |
| **CE** | 2% | Lei estadual | 2023+ |
| **DF** | 0% | Não instituiu | - |
| **ES** | 2% | Lei estadual | 2023+ |
| **GO** | 0% | Não instituiu | - |
| **MA** | 2% | Lei estadual | 2023+ |
| **MT** | 0% | Não instituiu | - |
| **MS** | 0% | Não instituiu | - |
| **MG** | 2% | Lei estadual | 2023+ |
| **PA** | 2% | Lei estadual | 2023+ |
| **PB** | 2% | Lei estadual | 2023+ |
| **PR** | 2% | Lei estadual | 2023+ |
| **PE** | 2% | Lei estadual | 2023+ |
| **PI** | 2% | Lei estadual | 2023+ |
| **RJ** | 2% | FECP (2%) | 2023+ |
| **RN** | 2% | Lei estadual | 2023+ |
| **RS** | 2% | Lei estadual | 2023+ |
| **RO** | 0% | Não instituiu | - |
| **RR** | 2% | Lei estadual | 2023+ |
| **SC** | 2% | Lei estadual | 2023+ |
| **SP** | 2% | FECOP (2%) | 2023+ |
| **SE** | 2% | Lei estadual | 2023+ |
| **TO** | 0% | Não instituiu | - |

> **Total com FCP:** 18 UFs com 2% | 9 UFs sem FCP (0%)

---

## 🔍 Lógica de Detecção no Engine

```python
class ICMSFCPRule(BaseRule):
    code = "ICMS_FCP"
    relevance_tags = {"icms", "interstate"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        # Só se interestadual E UF destino tem FCP > 0
        if context.uf_origem == context.uf_destino:
            return False
        fcp_rate = self.get_fcp_rate(context.uf_destino)
        return fcp_rate > 0
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        fcp_rate = self.get_fcp_rate(context.uf_destino)
        
        if fcp_rate == 0:
            return []
        
        # Base do FCP = mesma base do DIFAL
        if context.indIEDest == 9:  # Não contribuinte
            base_fcp = context.vBC
        else:  # Contribuinte
            aliquota_interestadual = self.get_aliquota_interestadual(
                context.uf_origem, context.uf_destino
            )
            aliquota_interna_destino = self.get_aliquota_interna(context.uf_destino)
            base_fcp = context.vBC * (aliquota_interna_destino - aliquota_interestadual)
        
        fcp_devido = base_fcp * fcp_rate
        
        # Verificar se FCP foi destacado na NF-e (campo vFCP)
        fcp_recolhido = context.vFCP or 0
        
        diferenca = fcp_devido - fcp_recolhido
        
        if diferenca > context.vBC * 0.001:  # Mínimo 0.1% da BC
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(fcp_devido, 2),
                actual_value=round(fcp_recolhido, 2),
                difference=round(diferenca, 2),
                details={
                    "uf_destino": context.uf_destino,
                    "aliquota_fcp": fcp_rate,
                    "base_fcp": round(base_fcp, 2),
                    "ind_ie_dest": context.indIEDest,
                    "vfcp_xml": context.vFCP
                }
            )]
        return []
```

---

## 🧪 Casos de Teste (test_rules_critical.py)

```python
# test_fcp_rule
# BA (FCP 2%) ← SP, não contribuinte
# vBC = 10.000
# FCP = 10.000 × 2% = 200

# test_fcp_rule_sp_destino
# SP (FCP 2%) ← RJ, contribuinte
# DIFAL base = (18% - 12%) × 10.000 = 600
# FCP = 600 × 2% = 12

# test_fcp_rule_sem_fcp
# GO (sem FCP) ← SP
# FCP = 0 (rule não dispara)

# test_fcp_ba_fcp_2porcento
# BA tem FCP 2% (FECOP integrado na alíquota interna 20.5%)
# Verificar se alíquota interna já inclui FCP ou é adicional
```

---

## ⚠️ Pontos Críticos de Atenção

### 1. **Alíquota Interna JÁ INCLUI FCP em alguns estados**
| UF | Alíquota Interna | FCP | Composição |
|----|------------------|-----|------------|
| **BA** | 20.5% | 2% | 18% ICMS + 2.5% FECOP |
| **RJ** | 20% | 2% | 18% ICMS + 2% FECP |
| **SP** | 18% | 2% | 16% ICMS + 2% FECOP |
| **Outras** | 17-18% | 2% | Verificar lei estadual |

> **Regra:** Se alíquota interna já inclui FCP, **não somar** FCP novamente no DIFAL.
> O DIFAL usa alíquota interna **líquida de FCP**.

### 2. **Campo vFCP no XML (CT-e/NF-e 4.00)**
```xml
<ICMS>
  <ICMS00>
    <vBC>10000.00</vBC>
    <pICMS>12.00</pICMS>
    <vICMS>1200.00</vICMS>
    <vFCP>200.00</vFCP>      <!-- FCP destacado -->
    <pFCP>2.00</pFCP>        <!-- Alíquota FCP -->
  </ICMS00>
</ICMS>
```

### 3. **FCP em Operações com ST**
Se a operação também tem ICMS ST, o FCP incide sobre a **base do ICMS ST** (ver `03-ICMS-ST.md`)

---

## 📦 JSON para backend/app/data/icms_rules.json (seção FCP)

```json
{
  "fcp": {
    "version": "2025.1",
    "updated": "2025-01-15",
    "source": "Convênio ICMS 174/2023, LC 190/2022",
    "aliquotas": {
      "AC": 0.00, "AL": 0.02, "AP": 0.02, "AM": 0.02,
      "BA": 0.02, "CE": 0.02, "DF": 0.00, "ES": 0.02,
      "GO": 0.00, "MA": 0.02, "MT": 0.00, "MS": 0.00,
      "MG": 0.02, "PA": 0.02, "PB": 0.02, "PR": 0.02,
      "PE": 0.02, "PI": 0.02, "RJ": 0.02, "RN": 0.02,
      "RS": 0.02, "RO": 0.00, "RR": 0.02, "SC": 0.02,
      "SP": 0.02, "SE": 0.02, "TO": 0.00
    },
    "estados_com_fcp": ["AL", "AP", "AM", "BA", "CE", "ES", "MA", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RR", "SC", "SP", "SE"],
    "observacoes": {
      "BA": "Alíquota interna 20.5% inclui FECOP 2.5% - FCP adicional não incide sobre DIFAL",
      "RJ": "Alíquota interna 20% inclui FECP 2% - FCP adicional não incide sobre DIFAL", 
      "SP": "Alíquota interna 18% inclui FECOP 2% - FCP adicional não incide sobre DIFAL"
    }
  }
}
```

---

## 🔗 Referências

- [EC 42/2003 - Planalto](http://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc42.htm)
- [LC 190/2022 - Art. 4º](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm)
- [Convênio ICMS 174/2023 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2023/convenio-icms-174-2023)
- [Portal FCP por Estado](https://www.confaz.fazenda.gov.br/legislacao/convenios/2023)

---

**Última Atualização:** 2026-11-01  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (Convênio ICMS 174 renova anualmente)