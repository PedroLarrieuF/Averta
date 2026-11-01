# Ad Valorem (Seguro Valor da Carga) - Regra AD_VALOREM

**Rule Code:** `AD_VALOREM`  
**Tipo:** `AD_VALOREM`  
**Severidade:** `MEDIUM`  
**Tags:** `advalorem`  
**Arquivo de Dados:** `backend/app/data/ad_valorem_taxas.json`  
**Teste:** `tests/test_rules_critical.py::test_ad_valorem`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 11.442/2007** (Art. 13) | Seguro de responsabilidade civil | Vigente |
| **Res. CNSP 381/2020** (SUSEP) | Condições gerais seguro RCTR-C | Vigente |
| **Código Civil** (Art. 734-742) | Transporte - responsabilidade | Vigente |
| **Contrato de Transporte** | Cláusula de ad valorem pactuada | Por contrato |

---

## 🎯 Quando Aplica

**Ad Valorem** = Seguro baseado no **valor da mercadoria** (não no frete):
- Contrato prevê taxa ad valorem (% sobre valor da nota fiscal)
- CT-e informa `vSeg` (valor do seguro) ou `vAdValorem`
- **Diferente do RCTR-C** (seguro obrigatório do transportador)

---

## 🧮 Fórmula de Cálculo

```python
# Ad Valorem = Valor da Carga (vNF) × Taxa Ad Valorem (%)

# Taxa típica: 0,05% a 0,30% ao mês (ou por viagem)
# Depende: tipo de carga, rota, valor, seguradora

# Exemplo:
# vNF = R$ 500.000,00
# Taxa = 0,10% (0,001)
# Ad Valorem = 500.000 × 0,001 = R$ 500,00
```

### Taxas de Referência por Tipo de Carga (2024)

| Tipo Carga | Taxa Mínima | Taxa Média | Taxa Máxima | Observação |
|------------|-------------|------------|-------------|------------|
| **Carga Geral** | 0,03% | 0,08% | 0,15% | Por viagem |
| **Carga Perigosa** | 0,10% | 0,25% | 0,50% | Risco elevado |
| **Carga Frigorífica** | 0,05% | 0,12% | 0,20% | Risco perecível |
| **Eletrônicos/Alto Valor** | 0,15% | 0,30% | 0,60% | Celulares, informática |
| **Joias/Metais Preciosos** | 0,50% | 1,00% | 2,00% | Seguro especial |
| **Veículos** | 0,05% | 0,10% | 0,20% | Por unidade |
| **Granel (líq/sól)** | 0,02% | 0,05% | 0,10% | Baixo valor unitário |

---

## 🔍 Lógica de Detecção no Engine

```python
class AdValoremRule(BaseRule):
    code = "AD_VALOREM"
    relevance_tags = {"advalorem"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        # Só se contrato prevê ad valorem
        if not context.contrato_tem_ad_valorem:
            return False
        if not context.vNF or context.vNF <= 0:
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        taxa_contratada = context.contrato_taxa_ad_valorem  # ex: 0.001 = 0,1%
        vNF = context.vNF
        
        ad_valorem_esperado = vNF * taxa_contratada
        ad_valorem_informado = context.vAdValorem or context.vSeg or 0
        
        diferenca = abs(ad_valorem_esperado - ad_valorem_informado)
        diferenca_pct = diferenca / ad_valorem_esperado if ad_valorem_esperado > 0 else 0
        
        # Tolerância 5% (arredondamentos)
        if diferenca_pct > 0.05:
            return [Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                expected_value=round(ad_valorem_esperado, 2),
                actual_value=round(ad_valorem_informado, 2),
                difference=round(diferenca, 2),
                details={
                    "vNF": vNF,
                    "taxa_contratada": taxa_contratada,
                    "taxa_contratada_pct": taxa_contratada * 100,
                    "ad_valorem_esperado": round(ad_valorem_esperado, 2),
                    "ad_valorem_informado": round(ad_valorem_informado, 2),
                    "tipo_carga": context.tpCarga
                }
            )]
        return []
```

---

## 🧪 Casos de Teste

```python
# test_ad_valorem
# vNF = R$ 1.000.000, Taxa contratada 0,10%
# Esperado = R$ 1.000,00
# Informado = R$ 800,00 → DIVERGÊNCIA 20%

# test_ad_valorem_eletronicos
# Celulares, taxa 0,30%
# vNF = R$ 2.000.000
# Esperado = R$ 6.000,00

# test_ad_valorem_sem_contrato
# Contrato não prevê ad valorem → Rule não dispara
```

---

## ⚠️ Pontos de Atenção

1. **Ad Valorem ≠ RCTR-C:** RCTR-C é obrigatório (transportador), Ad Valorem é opcional (contratual)
2. **Base de Cálculo:** Valor da NF-e (`vNF`) ou valor declarado no CT-e (`vCarga`)
3. **Taxa por Viagem vs Mensal:** Verificar contrato - a maioria é por viagem
4. **Limite de Cobertura:** Alguns contratos têm teto máximo (ex: R$ 500.000)
5. **Seguradora:** Taxa varia por seguradora - usar taxa do contrato

---

## 📦 JSON para backend/app/data/ad_valorem_taxas.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Mercado segurador, SUSEP, contratos típicos",
  "taxas_referencia_por_tipo_carga": {
    "01": {"min": 0.0003, "media": 0.0008, "max": 0.0015, "desc": "Carga Geral"},
    "02": {"min": 0.0010, "media": 0.0025, "max": 0.0050, "desc": "Carga Perigosa"},
    "03": {"min": 0.0005, "media": 0.0012, "max": 0.0020, "desc": "Carga Frigorífica"},
    "04": {"min": 0.0002, "media": 0.0005, "max": 0.0010, "desc": "Granel Líquido"},
    "05": {"min": 0.0002, "media": 0.0005, "max": 0.0010, "desc": "Granel Sólido"},
    "06": {"min": 0.0003, "media": 0.0008, "max": 0.0015, "desc": "Neogranel"},
    "07": {"min": 0.0005, "media": 0.0010, "max": 0.0020, "desc": "Container"},
    "08": {"min": 0.0010, "media": 0.0030, "max": 0.0060, "desc": "Carga Projeto/Alto Valor"},
    "09": {"min": 0.0005, "media": 0.0010, "max": 0.0020, "desc": "Veículos"},
    "10": {"min": 0.0008, "media": 0.0020, "max": 0.0040, "desc": "Carga Viva"}
  },
  "taxas_especiais": {
    "eletronicos": 0.0030,
    "joias": 0.0100,
    "medicamentos_controlados": 0.0020
  }
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Anual