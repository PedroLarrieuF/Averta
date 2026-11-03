# Peso/Volume da Carga na NF-e - Regra NFE_PESO_VOLUME_VALIDACAO

**Rule Code:** `NFE_PESO_VOLUME_VALIDACAO`  
**Tipo:** `WEIGHT_VOLUME`  
**Severidade:** `MEDIUM`  
**Tags:** `weight, volume, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/peso_volume_validacao.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_peso_volume_validacao`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Ajuste SINIEF 19/2016** | Campos peso/volume NF-e 4.00 | Vigente |
| **Manual NF-e 4.00** | Grupo `<infCarga>` / `<vol>` | Vigente |
| **Lei 11.442/2007** | Peso no transporte rodoviário | Vigente |
| **ANTT Res. 5.839/2021** | Peso para piso mínimo frete | Vigente |

---

## 🎯 Campos NF-e (Grupo Carga/Volumes)

### Peso
```xml
<infNFe>
  <infCarga>
    <vCarga>5000.000</vCarga>        <!-- Peso Líquido Total (kg) -->
    <proPred>                        <!-- Produto Predominante -->
      <cProd>123</cProd>
      <xProd>Mercadoria</xProd>
      <NCM>30049000</NCM>
      <qCarga>1000.000</qCarga>      <!-- Quantidade carga -->
      <peso>5000.000</peso>          <!-- Peso Bruto Total (kg) -->
    </proPred>
  </infCarga>
</infNFe>
```

### Volumes
```xml
<vol>
  <qVol>10</qVol>                    <!-- Quantidade volumes -->
  <esp>CAIXA</esp>                   <!-- Espécie -->
  <marca>MARCA</marca>               <!-- Marca -->
  <nVol>1</nVol>                     <!-- Numeração volumes -->
  <pesoL>500.000</pesoL>             <!-- Peso Líquido (kg) -->
  <pesoB>520.000</pesoB>             <!-- Peso Bruto (kg) -->
</vol>
```

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEPesoVolumeValidacaoRule(BaseRule):
    code = "NFE_PESO_VOLUME_VALIDACAO"
    relevance_tags = {"weight", "volume", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.vPeso is not None or context.volumes
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. Peso Líquido vs Soma Itens
        if context.itens and context.vPeso:
            peso_soma_itens = sum(item.qCom * item.peso_liquido_unitario for item in context.itens if item.peso_liquido_unitario)
            if peso_soma_itens > 0:
                tolerancia = context.vPeso * 0.05  # 5%
                if abs(context.vPeso - peso_soma_itens) > tolerancia:
                    discrepancies.append(Discrepancy(
                        rule_code=self.code,
                        severity="MEDIUM",
                        expected_value=round(peso_soma_itens, 3),
                        actual_value=round(context.vPeso, 3),
                        difference=round(abs(context.vPeso - peso_soma_itens), 3),
                        details={
                            "validacao": "PESO_LIQUIDO_SOMA_ITENS",
                            "vPeso_nfe": context.vPeso,
                            "soma_itens": peso_soma_itens
                        }
                    ))
        
        # 2. Peso Bruto (proPred/peso) vs Peso Líquido
        if context.peso_bruto and context.vPeso:
            if context.peso_bruto < context.vPeso:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "PESO_BRUTO_MENOR_LIQUIDO",
                        "peso_bruto": context.peso_bruto,
                        "peso_liquido": context.vPeso
                    }
                ))
        
        # 3. Volumes - Peso total volumes vs Peso NF-e
        if context.volumes:
            peso_bruto_volumes = sum(v.pesoB for v in context.volumes)
            peso_liquido_volumes = sum(v.pesoL for v in context.volumes)
            
            if context.peso_bruto and abs(context.peso_bruto - peso_bruto_volumes) > 0.01:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="LOW",
                    details={
                        "validacao": "PESO_BRUTO_VOLUMES_DIVERGENTE",
                        "peso_bruto_nfe": context.peso_bruto,
                        "soma_volumes": peso_bruto_volumes
                    }
                ))
            
            if context.vPeso and abs(context.vPeso - peso_liquido_volumes) > 0.01:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="LOW",
                    details={
                        "validacao": "PESO_LIQUIDO_VOLUMES_DIVERGENTE",
                        "peso_liquido_nfe": context.vPeso,
                        "soma_volumes": peso_liquido_volumes
                    }
                ))
        
        # 4. Quantidade volumes coerente
        if context.volumes and context.qVol:
            if len(context.volumes) != context.qVol:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="LOW",
                    details={
                        "validacao": "QTD_VOLUMES_DIVERGENTE",
                        "qVol_informado": context.qVol,
                        "volumes_xml": len(context.volumes)
                    }
                ))
        
        return discrepancies
```

---

## 🧪 Casos de Teste

```python
# test_nfe_peso_volume_validacao_peso_liquido_soma_itens
# vPeso=5000, soma itens=5100 (5% diff) → OK (tolerância 5%)
# vPeso=5000, soma itens=5500 (10% diff) → MEDIUM

# test_nfe_peso_volume_peso_bruto_menor_liquido
# peso_bruto=4000, vPeso=5000 → MEDIUM

# test_nfe_peso_volume_volumes_soma_peso
# soma pesoB volumes ≠ peso_bruto NF-e → LOW

# test_nfe_peso_volume_qtd_volumes
# qVol=10 mas 12 volumes no XML → LOW
```

---

## ⚠️ Pontos de Atenção

1. **vPeso = Peso Líquido Total** (sem embalagem)
2. **proPred/peso = Peso Bruto Total** (com embalagem) → deve ser ≥ vPeso
3. **Volumes**: Soma pesoL ≈ vPeso, soma pesoB ≈ proPred/peso
4. **Tolerância 5%** para arredondamentos por item
5. **Cross CT-e**: Peso NF-e vs proPred/peso CT-e (ver 14-CROSS-CTE-NFE.md)
6. **Piso Mínimo Frete**: Peso NF-e usado para validar frete mínimo ANTT

---

## 📦 JSON para backend/app/data/nfe/peso_volume_validacao.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "tolerancias": {
    "peso_liquido_soma_itens_pct": 0.05,
    "peso_bruto_volumes_pct": 0.02,
    "peso_liquido_volumes_pct": 0.02
  },
  "regras": {
    "peso_bruto_ge_liquido": true,
    "validar_soma_itens": true,
    "validar_volumes": true
  },
  "campos_nfe": {
    "vPeso": "Peso líquido total",
    "proPred_peso": "Peso bruto total (produto predominante)",
    "vol_pesoL": "Peso líquido por volume",
    "vol_pesoB": "Peso bruto por volume",
    "qVol": "Quantidade volumes"
  }
}
```

---

## 🔗 Referências

- [Manual NF-e 4.00 - Grupo Carga](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Lei 11.442/2007](http://www.planalto.gov.br/ccivil_03/_ato2004-2006/2007/lei/l11442.htm)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent