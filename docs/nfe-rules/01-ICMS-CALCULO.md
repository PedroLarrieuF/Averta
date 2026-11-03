# ICMS Cálculo e Validação CST/CSOSN - Regras NFE_ICMS_CALCULO, NFE_ICMS_CST_VALIDACAO

**Rule Codes:** `NFE_ICMS_CALCULO`, `NFE_ICMS_CST_VALIDACAO`  
**Tipo:** `ICMS_CALC` / `ICMS_CST`  
**Severidade:** `CRITICAL` / `HIGH`  
**Tags:** `icms, cst, csosn, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/icms_cst_csosn.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_icms_calculo_cst00`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 8.884/1994** (Art. 37) | Base cálculo ICMS inclui frete, seguro, outras despesas | Vigente |
| **LC 87/1996** (Art. 2º, §2º) | ICMS nas operações interestaduais | Vigente |
| **RICMS/SP** (Art. 66-70) | Base cálculo, CST, alíquotas (exemplo SP) | Vigente |
| **Convênio ICMS 142/2018** | ICMS ST - protocolo | Vigente |
| **Ajuste SINIEF 19/2016** | Leiaute NF-e 4.00 - campos ICMS | Vigente |
| **Manual NF-e 4.00** | Especificação técnica - grupo ICMS | 2024+ |

---

## 🎯 CST (Código Situação Tributária) - ICMS Normal

### Tabela CST ICMS (00 a 90) - Regime Normal

| CST | Descrição | Base Cálculo (vBC) | Alíquota | ICMS Devido | Quando Usa |
|-----|-----------|-------------------|----------|-------------|------------|
| **00** | **Tributada integralmente** | vNF + vFrete + vSeg + vOutro - vDesc | Interna/Interestadual | vBC × alíq | Operação normal |
| **10** | Tributada com cobrança por ST | vNF + vFrete + vSeg + vOutro - vDesc | Interna | vBC × alíq | ST - remetente recolhe |
| **20** | Com redução de base | (vNF + vFrete + vSeg + vOutro - vDesc) × % red | Interna | vBC_red × alíq | Redução base (ex: leite) |
| **30** | Isenta ou não tributada c/ cobrança ST | vNF + vFrete + vSeg + vOutro - vDesc | - | 0 (ST recolhe) | Isenta mas ST |
| **40** | Isenta | - | - | 0 | Isenção total |
| **41** | Não tributada | - | - | 0 | Não incidência |
| **50** | Suspensão | - | - | 0 | Suspensão (ex: exportação) |
| **51** | Diferimento | - | - | 0 | Diferimento (posterior) |
| **60** | ICMS cobrado anterior por ST | vNF + vFrete + vSeg + vOutro - vDesc | Interna | vBC × alíq | Substituição tributária |
| **70** | Com redução base + ST | (vNF + ...) × % red | Interna | vBC_red × alíq | Redução + ST |
| **90** | Outras | Conforme legislação | Conforme legislação | Conforme | Casos especiais |

---

## 🎯 CSOSN (CST Simples Nacional) - 101 a 500

### Tabela CSOSN ICMS - Simples Nacional

| CSOSN | Descrição | Base Cálculo | ICMS Devido | Observação |
|-------|-----------|--------------|-------------|------------|
| **101** | Tributada pelo Simples c/ permissão de crédito | - | Pelo Simples (DAS) | Crédito para destinatário |
| **102** | Tributada pelo Simples s/ permissão de crédito | - | Pelo Simples (DAS) | Sem crédito |
| **103** | Isenção ICMS c/ faixa receita | - | 0 | Faixa de receita |
| **201** | Tributada pelo Simples c/ permissão crédito + ST | vBC_ST | ST recolhido | ST dentro Simples |
| **202** | Tributada pelo Simples s/ permissão crédito + ST | vBC_ST | ST recolhido | ST sem crédito |
| **203** | Isenção ICMS + ST | vBC_ST | ST recolhido | Isento mas ST |
| **300** | Imune | - | 0 | Imunidade constitucional |
| **400** | Não tributada pelo Simples | - | 0 | Fora Simples |
| **500** | ICMS cobrado anterior por ST (Simples) | vBC_ST | ST recolhido | Substituição |
| **900** | Outras | Conforme legislação | Conforme | Casos especiais |

---

## 🧮 Fórmulas de Cálculo por CST

### CST 00 - Tributada Integral (Mais Comum)
```python
# Base Cálculo ICMS
vBC = vNF + vFrete + vSeg + vOutro - vDesc

# ICMS Devido
vICMS = vBC * aliquota_interna  # Operação interna
vICMS = vBC * aliquota_interestadual  # Operação interestadual

# Valor Total Nota
vNF = vProd + vFrete + vSeg + vDesc + vOutro + vII + vIPI + vPIS + vCOFINS + vICMS + vICMSDeson + vFCP + vFCPST + vFCPSTRet
```

### CST 10 - Tributada com ST
```python
# ICMS Próprio (antecipado)
vBC = vNF + vFrete + vSeg + vOutro - vDesc
vICMS = vBC * aliquota_interna

# ICMS ST (ver regra NFE_ICMS_ST_VALIDACAO)
vBCST = (vNF + vFrete + vSeg + vOutro - vDesc) * (1 + MVA)
vICMSST = vBCST * aliquota_interna_destino - vICMS_próprio
```

### CST 20 - Redução de Base
```python
# % Redução varia por produto/UF (ex: leite 60%, medicamentos 40%)
pRedBC = get_percentual_reducao(ncm, uf)  # Ex: 0.60 = 60%
vBC = (vNF + vFrete + vSeg + vOutro - vDesc) * (1 - pRedBC)
vICMS = vBC * aliquota_interna
```

### CST 40/41 - Isenta/Não Tributada
```python
vBC = 0
vICMS = 0
# Mas vFrete, vSeg, vOutro AINDA compõem vNF!
```

### CST 60 - ICMS Cobrado Anterior por ST
```python
# Remetente já recolheu ST
# Destinatário NÃO recolhe ICMS próprio
vBC = vNF + vFrete + vSeg + vOutro - vDesc
vICMS = 0  # Já recolhido na origem
vICMSST = valor_recolhido_origem  # Informativo
```

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEICMSCalculoRule(BaseRule):
    code = "NFE_ICMS_CALCULO"
    relevance_tags = {"icms", "cst", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        # Aplica para todas NF-e com ICMS
        return context.cst_icms is not None
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        cst = context.cst_icms
        discrepancies = []
        
        # Obter regra do CST
        cst_rule = self.get_cst_rule(cst, context.regime_tributario)
        if not cst_rule:
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": f"CST {cst} não encontrado na tabela", "cst": cst}
            )]
        
        # Calcular base esperada
        vBC_esperada = self.calcular_base_icms(context, cst_rule)
        vICMS_esperado = self.calcular_icms_esperado(vBC_esperada, context, cst_rule)
        
        # Comparar com XML
        if abs(context.vBC - vBC_esperada) > context.vNF * 0.001:  # Tolerância 0.1%
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(vBC_esperada, 2),
                actual_value=round(context.vBC, 2),
                difference=round(abs(context.vBC - vBC_esperada), 2),
                details={
                    "campo": "vBC",
                    "cst": cst,
                    "formula_usada": cst_rule.formula_base,
                    "componentes": {
                        "vNF": context.vNF,
                        "vFrete": context.vFrete,
                        "vSeg": context.vSeg,
                        "vOutro": context.vOutro,
                        "vDesc": context.vDesc
                    }
                }
            ))
        
        if abs(context.vICMS - vICMS_esperado) > context.vNF * 0.001:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="CRITICAL",
                expected_value=round(vICMS_esperado, 2),
                actual_value=round(context.vICMS, 2),
                difference=round(abs(context.vICMS - vICMS_esperado), 2),
                details={
                    "campo": "vICMS",
                    "cst": cst,
                    "aliquota_aplicada": context.aliquota_icms,
                    "aliquota_esperada": cst_rule.aliquota
                }
            ))
        
        return discrepancies
    
    def calcular_base_icms(self, context, cst_rule):
        """Calcula vBC conforme CST"""
        base = context.vNF + context.vFrete + context.vSeg + context.vOutro - context.vDesc
        
        if cst_rule.tem_reducao_base:
            pRedBC = self.get_percentual_reducao(context.ncm, context.uf_emitente)
            base = base * (1 - pRedBC)
        
        return base
    
    def calcular_icms_esperado(self, vBC, context, cst_rule):
        if cst_rule.cst in ["40", "41", "50", "51", "103", "300", "400"]:
            return 0
        
        if context.operacao_interestadual:
            aliquota = self.get_aliquota_interestadual(context.uf_emitente, context.uf_destino)
        else:
            aliquota = self.get_aliquota_interna(context.uf_destino if cst_rule.cobrar_destino else context.uf_emitente)
        
        return vBC * aliquota


class NFEICMSCSTValidacaoRule(BaseRule):
    code = "NFE_ICMS_CST_VALIDACAO"
    relevance_tags = {"icms", "cst", "nfe", "validation"}
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        """Valida se CST/CSOSN é compatível com operação"""
        discrepancies = []
        cst = context.cst_icms
        csosn = context.csosn_icms
        regime = context.regime_tributario  # "NORMAL" ou "SIMPLES"
        
        # Regime Normal não pode usar CSOSN
        if regime == "NORMAL" and csosn:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "erro": "Regime Normal não deve usar CSOSN",
                    "cst": cst,
                    "csosn": csosn,
                    "regime": regime
                }
            ))
        
        # Simples Nacional não pode usar CST (exceto 900)
        if regime == "SIMPLES" and cst and cst != "90":
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "erro": "Simples Nacional deve usar CSOSN, não CST",
                    "cst": cst,
                    "csosn": csosn,
                    "regime": regime
                }
            ))
        
        # Validar CST x CFOP
        if not self.cst_cfop_compativel(cst, context.cfop, context.operacao_interestadual):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "erro": "CST incompatível com CFOP",
                    "cst": cst,
                    "cfop": context.cfop,
                    "interstadual": context.operacao_interestadual
                }
            ))
        
        # CST 10/30/60/70 exigem ST
        if cst in ["10", "30", "60", "70"] and not context.tem_icms_st:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "erro": f"CST {cst} exige ICMS ST (vBCST/vICMSST)",
                    "cst": cst,
                    "tem_st": context.tem_icms_st
                }
            ))
        
        return discrepancies
```

---

## 🧪 Casos de Teste

```python
# test_nfe_icms_calculo_cst00
# CST 00, operação interna SP, vNF=10000, vFrete=500, vSeg=100, vOutro=50, vDesc=0
# vBC = 10000+500+100+50 = 10650
# vICMS = 10650 * 18% = 1917.00

# test_nfe_icms_calculo_cst00_interstadual
# CST 00, SP→RJ, vNF=10000, vFrete=500
# vBC = 10650
# vICMS = 10650 * 12% = 1278.00 (interestadual)

# test_nfe_icms_calculo_cst20_reducao
# CST 20, redução 40%, vNF=10000, vFrete=500
# vBC = 10650 * 0.60 = 6390
# vICMS = 6390 * 18% = 1150.20

# test_nfe_icms_calculo_cst40_isenta
# CST 40, vNF=10000, vFrete=500
# vBC = 0, vICMS = 0
# MAS vNF deve incluir frete!

# test_nfe_icms_calculo_cst10_com_st
# CST 10, vNF=10000, vFrete=500, MVA=40%
# vBC = 10650
# vICMS_próprio = 10650 * 18% = 1917
# vBCST = 10650 * 1.40 = 14910
# vICMSST = 14910 * 18% - 1917 = 2683.80 - 1917 = 766.80

# test_nfe_icms_cst_validacao_simples_usando_cst
# Simples Nacional com CST 00 → ERRO

# test_nfe_icms_cst_validacao_cst10_sem_st
# CST 10 mas vBCST=0 → ERRO

# test_nfe_icms_cst_validacao_cfop_incompativel
# CST 00 com CFOP 5.933 (simples) → ERRO
```

---

## ⚠️ Pontos de Atenção

1. **Frete SEMPRE na base** para CST 00, 10, 20, 30, 60, 70, 90 (Lei 8.884/94 Art. 37)
2. **vFrete destacado** na NF-e (tag `<vFrete>`) = incluído na base
3. **Frete por conta destinatário** (modFrete=1): se destacado na NF-e, entra na base
4. **Redução base (CST 20)**: % varia por NCM e UF - consultar tabela estadual
5. **MVA/IVA para ST**: Original (Convênio 38/2001) vs Ajustado (por UF destino)
6. **FCP**: Calcular APÓS ICMS próprio e ST (ver 04-FCP.md)
7. **DIFAL**: Para destinatário não contribuinte (indIEDest=9) - ver 03-ICMS-DIFAL.md
8. **Simples Nacional**: CSOSN 101/102 geram crédito; 102/202 não geram

---

## 📦 JSON para backend/app/data/nfe/icms_cst_csosn.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Lei 8.884/94, LC 87/96, RICMS/UF, Ajuste SINIEF 19/2016",
  "cst_normal": {
    "00": {"nome": "Tributada integralmente", "base_inclui_frete": true, "tem_reducao": false, "tem_st": false, "aliquota_tipo": "interna_ou_interstadual"},
    "10": {"nome": "Tributada c/ ST", "base_inclui_frete": true, "tem_reducao": false, "tem_st": true, "aliquota_tipo": "interna"},
    "20": {"nome": "Redução base", "base_inclui_frete": true, "tem_reducao": true, "tem_st": false, "aliquota_tipo": "interna"},
    "30": {"nome": "Isenta/não trib c/ ST", "base_inclui_frete": true, "tem_reducao": false, "tem_st": true, "aliquota_tipo": "interna"},
    "40": {"nome": "Isenta", "base_inclui_frete": false, "tem_reducao": false, "tem_st": false, "aliquota_tipo": "zero"},
    "41": {"nome": "Não tributada", "base_inclui_frete": false, "tem_reducao": false, "tem_st": false, "aliquota_tipo": "zero"},
    "50": {"nome": "Suspensão", "base_inclui_frete": false, "tem_reducao": false, "tem_st": false, "aliquota_tipo": "zero"},
    "51": {"nome": "Diferimento", "base_inclui_frete": false, "tem_reducao": false, "tem_st": false, "aliquota_tipo": "zero"},
    "60": {"nome": "ICMS cobrado ant. por ST", "base_inclui_frete": true, "tem_reducao": false, "tem_st": true, "aliquota_tipo": "interna"},
    "70": {"nome": "Redução base + ST", "base_inclui_frete": true, "tem_reducao": true, "tem_st": true, "aliquota_tipo": "interna"},
    "90": {"nome": "Outras", "base_inclui_frete": true, "tem_reducao": false, "tem_st": false, "aliquota_tipo": "conforme_leg"}
  },
  "csosn_simples": {
    "101": {"nome": "Simples c/ crédito", "gera_credito": true, "tem_st": false},
    "102": {"nome": "Simples s/ crédito", "gera_credito": false, "tem_st": false},
    "103": {"nome": "Isenção faixa receita", "gera_credito": false, "tem_st": false},
    "201": {"nome": "Simples c/ crédito + ST", "gera_credito": true, "tem_st": true},
    "202": {"nome": "Simples s/ crédito + ST", "gera_credito": false, "tem_st": true},
    "203": {"nome": "Isenção + ST", "gera_credito": false, "tem_st": true},
    "300": {"nome": "Imune", "gera_credito": false, "tem_st": false},
    "400": {"nome": "Não trib. Simples", "gera_credito": false, "tem_st": false},
    "500": {"nome": "ICMS ant. ST (Simples)", "gera_credito": false, "tem_st": true},
    "900": {"nome": "Outras", "gera_credito": false, "tem_st": false}
  },
  "regras_frete_base": {
    "csts_com_frete_na_base": ["00", "10", "20", "30", "60", "70", "90"],
    "csts_sem_frete_na_base": ["40", "41", "50", "51"],
    "observacao": "Lei 8.884/94 Art. 37 - frete integra base cálculo ICMS quando destacado na NF-e"
  }
}
```

---

## 🔗 Referências

- [Lei 8.884/1994 Art. 37 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/L8884.htm)
- [LC 87/1996 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm)
- [Manual NF-e 4.00 - Receita Federal](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Ajuste SINIEF 19/2016 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/ajustes/2016/ajuste-sinief-19-2016)
- [Tabela CST ICMS - Portal NF-e](https://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=P2V5c0lHVnliRzlJYjI1MWMyVnlkRzl5)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar atualizações CST/CSOSN)