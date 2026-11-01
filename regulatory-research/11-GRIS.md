# GRIS (Gerenciamento de Risco) - Regra GRIS

**Rule Code:** `GRIS`  
**Tipo:** `GRIS`  
**Severidade:** `MEDIUM`  
**Tags:** `gris`  
**Arquivo de Dados:** `backend/app/data/gris_taxas.json`  
**Teste:** `tests/test_rules_critical.py::test_gris`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 11.442/2007** (Art. 13, §2º) | Gerenciamento de risco no transporte | Vigente |
| **Res. ANTT 5.839/2021** | GRIS como componente do frete | 2021+ |
| **Normas ABNT NBR 15848** | Gestão de riscos no transporte | Vigente |
| **Contrato de Transporte** | Taxa GRIS pactuada | Por contrato |

---

## 🎯 Quando Aplica

**GRIS** = Taxa de Gerenciamento de Risco (prevenção de roubo, monitoramento):
- Contrato prevê taxa GRIS (fixa ou % sobre frete/valor)
- Comum em: cargas de alto valor, rotas de risco, operações noturnas
- CT-e pode informar em `vOutro` ou campo específico do contrato

---

## 🧮 Fórmula de Cálculo

```python
# GRIS = Base × Taxa GRIS

# Base pode ser:
# 1. Valor do Frete (vFrete) × %  → Mais comum
# 2. Valor da Carga (vNF) × %     → Cargas alto valor
# 3. Valor Fixo por viagem        → Rotas específicas
# 4. Por km rodado                → Longas distâncias

# Taxas típicas 2024:
# - % sobre frete: 1% a 5%
# - % sobre valor carga: 0,05% a 0,20%
# - Fixo: R$ 50 a R$ 500 por viagem
# - Por km: R$ 0,05 a R$ 0,20/km
```

### Taxas de Referência por Região/Risco (2024)

| Região/Rota | Risco | Taxa sobre Frete | Taxa sobre Valor Carga | Fixo/Viagem |
|-------------|-------|------------------|------------------------|-------------|
| **SP Capital/RMSP** | Alto | 3-5% | 0,10-0,20% | R$ 150-300 |
| **RJ Capital/Região** | Alto | 3-5% | 0,10-0,20% | R$ 150-300 |
| **Capitais NE (Salvador, Fortaleza, Recife)** | Alto | 3-4% | 0,08-0,15% | R$ 100-250 |
| **Interior SP/Sul/MG** | Médio | 2-3% | 0,05-0,10% | R$ 80-150 |
| **Centro-Oeste (GO, MT, MS, DF)** | Médio | 2-3% | 0,05-0,10% | R$ 80-150 |
| **Norte (AM, PA, TO)** | Médio/Baixo | 1-2% | 0,03-0,08% | R$ 50-100 |
| **Rotas Críticas (BR-116, BR-101, BR-381)** | Muito Alto | +1-2% | +0,05% | +R$ 50-100 |

---

## 🔍 Lógica de Detecção no Engine

```python
class GRISRule(BaseRule):
    code = "GRIS"
    relevance_tags = {"gris"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        if not context.contrato_tem_gris:
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        tipo_base = context.contrato_gris_tipo_base  # "frete", "carga", "fixo", "km"
        taxa = context.contrato_gris_taxa
        
        if tipo_base == "frete":
            base = context.vFrete
            gris_esperado = base * taxa
        elif tipo_base == "carga":
            base = context.vNF
            gris_esperado = base * taxa
        elif tipo_base == "fixo":
            gris_esperado = taxa  # taxa = valor fixo
        elif tipo_base == "km":
            base = context.distancia_km
            gris_esperado = base * taxa
        else:
            return []
        
        gris_informado = context.vGRIS or context.vOutro or 0
        
        diferenca = abs(gris_esperado - gris_informado)
        diferenca_pct = diferenca / gris_esperado if gris_esperado > 0 else 0
        
        if diferenca_pct > 0.05:  # 5% tolerância
            return [Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                expected_value=round(gris_esperado, 2),
                actual_value=round(gris_informado, 2),
                difference=round(diferenca, 2),
                details={
                    "tipo_base": tipo_base,
                    "base_calculo": round(base, 2) if tipo_base != "fixo" else "N/A",
                    "taxa_gris": taxa,
                    "gris_esperado": round(gris_esperado, 2),
                    "gris_informado": round(gris_informado, 2),
                    "rota": f"{context.uf_origem}→{context.uf_destino}",
                    "regiao_risco": self.get_regiao_risco(context.uf_origem, context.uf_destino)
                }
            )]
        return []
```

---

## 🧪 Casos de Teste

```python
# test_gris
# SP → RJ, frete R$ 10.000, taxa 4% sobre frete
# GRIS esperado = R$ 400,00
# Informado = R$ 300,00 → DIVERGÊNCIA 25%

# test_gris_valor_carga
# Eletrônicos SP → RJ, vNF R$ 5.000.000, taxa 0,15%
# GRIS esperado = R$ 7.500,00

# test_gris_rota_critica
# BR-381 (Minas Gerais) - risco muito alto
# Taxa base 3% + adicional 1,5% = 4,5%
```

---

## ⚠️ Pontos de Atenção

1. **GRIS ≠ Seguro:** GRIS é prevenção/monitoramento; Seguro é indenização
2. **Dupla Cobrança:** Verificar se contrato não cobra GRIS + Ad Valorem sobre mesma base
3. **Rotas de Risco:** Adicional para BR-116, BR-101, BR-381, BR-262, BR-364
4. **Monitoramento:** GRIS deve incluir rastreamento (rastreador, bloqueador, torre de controle)
5. **ANTT:** GRIS compõe o frete para fins de piso mínimo

---

## 📦 JSON para backend/app/data/gris_taxas.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Mercado transportador, ANTT, contratos típicos",
  "taxas_por_regiao": {
    "SP_RMSP": {"frete_pct": 0.04, "carga_pct": 0.0015, "fixo": 250, "risco": "ALTO"},
    "RJ_RMRJ": {"frete_pct": 0.04, "carga_pct": 0.0015, "fixo": 250, "risco": "ALTO"},
    "NE_CAPITAIS": {"frete_pct": 0.035, "carga_pct": 0.0012, "fixo": 200, "risco": "ALTO"},
    "SUL_CAPITAIS": {"frete_pct": 0.025, "carga_pct": 0.0008, "fixo": 120, "risco": "MEDIO"},
    "CO_CAPITAIS": {"frete_pct": 0.025, "carga_pct": 0.0008, "fixo": 120, "risco": "MEDIO"},
    "INTERIOR_SP_SUL_MG": {"frete_pct": 0.02, "carga_pct": 0.0006, "fixo": 100, "risco": "MEDIO"},
    "NORTE": {"frete_pct": 0.015, "carga_pct": 0.0005, "fixo": 80, "risco": "BAIXO"}
  },
  "adicional_rotas_criticas": {
    "BR-116": 0.015,
    "BR-101": 0.010,
    "BR-381": 0.020,
    "BR-262": 0.010,
    "BR-364": 0.010,
    "BR-163": 0.015
  },
  "tipos_base": ["frete", "carga", "fixo", "km"]
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Anual