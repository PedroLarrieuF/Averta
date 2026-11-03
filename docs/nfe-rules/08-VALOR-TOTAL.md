# Consistência Valor Total (vNF) - Regra NFE_VALOR_TOTAL_CONSISTENCIA

**Rule Code:** `NFE_VALOR_TOTAL_CONSISTENCIA`  
**Tipo:** `TOTAL_VALIDATION`  
**Severidade:** `HIGH`  
**Tags:** `total, vNF, consistency, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/valor_total_consistencia.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_valor_total_consistencia`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Ajuste SINIEF 19/2016** | Leiaute NF-e 4.00 - Grupo Total | Vigente |
| **Manual NF-e 4.00** | Cálculo vNF e validações | Vigente |
| **RICMS/UF** | Valor total da operação | Vigente |

---

## 🎯 Objetivo

Validar se o **Valor Total da NF-e (vNF)** está consistente com a soma dos componentes:
- Valor dos produtos (vProd)
- Frete (vFrete)
- Seguro (vSeg)
- Desconto (vDesc)
- Outras despesas (vOutro)
- Impostos (II, IPI, PIS, COFINS, ICMS, FCP, ST, etc.)

---

## 🧮 Fórmula Oficial vNF (NF-e 4.00)

```
vNF = vProd 
    + vFrete 
    + vSeg 
    + vDesc        (valor negativo/subtraído)
    + vOutro 
    + vII 
    + vIPI 
    + vPIS 
    + vCOFINS 
    + vICMS 
    + vICMSDeson   (ICMS desonerado - valor negativo)
    + vFCP 
    + vFCPST 
    + vFCPSTRet
```

> **Nota**: vDesc é **subtraído** (desconto incondicionado).
> vICMSDeson é **subtraído** (ICMS desonerado - ex: incentivos fiscais).

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEValorTotalConsistenciaRule(BaseRule):
    code = "NFE_VALOR_TOTAL_CONSISTENCIA"
    relevance_tags = {"total", "vNF", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.vNF is not None and context.vNF > 0
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # Calcular vNF esperado
        vNF_esperado = (
            (context.vProd or 0)
            + (context.vFrete or 0)
            + (context.vSeg or 0)
            - (context.vDesc or 0)           # Desconto subtrai
            + (context.vOutro or 0)
            + (context.vII or 0)
            + (context.vIPI or 0)
            + (context.vPIS or 0)
            + (context.vCOFINS or 0)
            + (context.vICMS or 0)
            - (context.vICMSDeson or 0)      # ICMS desonerado subtrai
            + (context.vFCP or 0)
            + (context.vFCPST or 0)
            + (context.vFCPSTRet or 0)
        )
        
        # Tolerância: 0.5% do vNF ou R$ 1,00
        tolerancia = max(context.vNF * 0.005, 1.0)
        diferenca = abs(context.vNF - vNF_esperado)
        
        if diferenca > tolerancia:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(vNF_esperado, 2),
                actual_value=round(context.vNF, 2),
                difference=round(diferenca, 2),
                details={
                    "validacao": "VF_TOTAL_INCONSISTENTE",
                    "formula": "vProd + vFrete + vSeg - vDesc + vOutro + vII + vIPI + vPIS + vCOFINS + vICMS - vICMSDeson + vFCP + vFCPST + vFCPSTRet",
                    "componentes": {
                        "vProd": context.vProd,
                        "vFrete": context.vFrete,
                        "vSeg": context.vSeg,
                        "vDesc": context.vDesc,
                        "vOutro": context.vOutro,
                        "vII": context.vII,
                        "vIPI": context.vIPI,
                        "vPIS": context.vPIS,
                        "vCOFINS": context.vCOFINS,
                        "vICMS": context.vICMS,
                        "vICMSDeson": context.vICMSDeson,
                        "vFCP": context.vFCP,
                        "vFCPST": context.vFCPST,
                        "vFCPSTRet": context.vFCPSTRet
                    },
                    "tolerancia_usada": tolerancia
                }
            ))
        
        # Validar também vProd = soma dos itens
        if context.itens:
            vProd_soma_itens = sum(item.vProd for item in context.itens)
            if abs(context.vProd - vProd_soma_itens) > tolerancia:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    expected_value=round(vProd_soma_itens, 2),
                    actual_value=round(context.vProd, 2),
                    difference=round(abs(context.vProd - vProd_soma_itens), 2),
                    details={
                        "validacao": "VPROD_SOMA_ITENS",
                        "qtd_itens": len(context.itens)
                    }
                ))
        
        return discrepancies
```

---

## 🧪 Casos de Teste

```python
# test_nfe_valor_total_consistencia_ok
# Todos componentes somam corretamente → OK

# test_nfe_valor_total_frete_nao_incluido
# vFrete=500 mas não somado no vNF → HIGH (diff=500)

# test_nfe_valor_total_desconto_sinal_errado
# vDesc somado em vez de subtraído → HIGH

# test_nfe_valor_total_icms_desonerado_sinal_errado
# vICMSDeson somado em vez de subtraído → HIGH

# test_nfe_valor_total_soma_itens_divergente
# vNF informado ≠ soma itens + impostos → HIGH

# test_nfe_valor_total_fcp_nao_incluido
# vFCP>0 mas não no vNF → HIGH
```

---

## ⚠️ Pontos de Atenção

1. **vDesc SUBTRAI** - Desconto incondicionado reduz vNF
2. **vICMSDeson SUBTRAI** - ICMS desonerado (incentivos) reduz vNF
3. **Todos impostos SOMAM** - II, IPI, PIS, COFINS, ICMS, FCP, ST
4. **vProd = Soma itens** - Validar consistência itens × total
5. **Tolerância 0.5%** - Arredondamentos de centavos por item
6. **Cross com CT-e**: vNF deve ≈ vTPrest (ver 14-CROSS-CTE-NFE.md)

---

## 📦 JSON para backend/app/data/nfe/valor_total_consistencia.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "formula_vNF": "vProd + vFrete + vSeg - vDesc + vOutro + vII + vIPI + vPIS + vCOFINS + vICMS - vICMSDeson + vFCP + vFCPST + vFCPSTRet",
  "campos_somam": [
    "vProd", "vFrete", "vSeg", "vOutro", "vII", "vIPI", 
    "vPIS", "vCOFINS", "vICMS", "vFCP", "vFCPST", "vFCPSTRet"
  ],
  "campos_subtraem": [
    "vDesc", "vICMSDeson"
  ],
  "tolerancia_pct": 0.005,
  "tolerancia_minima": 1.0,
  "validar_soma_itens": true
}
```

---

## 🔗 Referências

- [Manual NF-e 4.00 - Grupo Total](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Ajuste SINIEF 19/2016](https://www.confaz.fazenda.gov.br/legislacao/ajustes/2016/ajuste-sinief-19-2016)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent