# Peso Real vs Faturado - Regra PESO_REAL_VS_FATURADO

**Rule Code:** `PESO_REAL_VS_FATURADO`  
**Tipo:** `PESO_REAL_VS_FATURADO`  
**Severidade:** `HIGH`  
**Tags:** `weight`  
**Arquivo de Dados:** `backend/app/data/pesos_tolerancia.json`  
**Teste:** `tests/test_rules_critical.py::test_peso_real_vs_faturado`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 11.442/2007** (Art. 6º, §3º) | Peso declarado vs peso real | Vigente |
| **Res. ANTT 5.839/2021** (Art. 7º) | Tolerâncias de pesagem | 2021+ |
| **Decreto 9.209/2017** (Art. 33) | Pesagem obrigatória no CT-e | Vigente |
| **Portaria INMETRO 236/2022** | Balanças rodoviárias - verificações | Vigente |

---

## 🎯 Quando Aplica

**Toda operação rodoviária** onde:
- Peso informado no CT-e (`peso` / `vCarga`) ≠ Peso real aferido na balança
- Existem **balanças rodoviárias** no percurso (pesagem fiscal)
- Transportador **faturou** por peso diferente do real

**Identificação:**
- CT-e: `peso` (peso declarado)
- Documento de pesagem: `peso_real` (balança fiscal)
- Diferença = |peso_real - peso_declarado| / peso_declarado

---

## 🧮 Fórmula de Cálculo

```python
# Diferença % = |Peso Real - Peso Faturado| / Peso Faturado × 100

# Tolerâncias ANTT (Res. 5.839/2021, Art. 7º):
# - Carga Geral / Fracionada: **5%**
# - Granel (sólido/líquido): **20%**
# - Carga Perigosa: **3%** (mais rigoroso)
# - Carga Frigorífica: **5%**
# - Container: **5%**

# Se diferença > tolerância → DIVERGÊNCIA
# Valor divergência = (peso_real - peso_faturado) × valor_por_tonelada
```

### Tabela de Tolerâncias

| Tipo Carga | Tolerância | Base Legal |
|------------|------------|------------|
| **Carga Geral (01)** | 5% | ANTT 5.839 Art. 7º |
| **Carga Perigosa (02)** | 3% | ANTT + normas perigosos |
| **Carga Frigorífica (03)** | 5% | ANTT 5.839 Art. 7º |
| **Granel Líquido (04)** | 20% | ANTT 5.839 Art. 7º §2º |
| **Granel Sólido (05)** | 20% | ANTT 5.839 Art. 7º §2º |
| **Neogranel (06)** | 5% | ANTT 5.839 Art. 7º |
| **Container (07)** | 5% | ANTT 5.839 Art. 7º |
| **Carga Projeto (08)** | 5% | ANTT 5.839 Art. 7º |
| **Veículos (09)** | 3% | Específico veículos |
| **Carga Viva (10)** | 10% | Perdas naturais |

---

## 🔍 Lógica de Detecção no Engine

```python
class RealWeightVsBilledRule(BaseRule):
    code = "PESO_REAL_VS_FATURADO"
    relevance_tags = {"weight"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        if context.modal != "01":
            return False
        # Precisa ter peso real (de balança fiscal) E peso faturado
        if not context.peso_real or not context.peso_faturado:
            return False
        if context.peso_faturado <= 0:
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        peso_faturado = context.peso_faturado  # kg (do CT-e)
        peso_real = context.peso_real          # kg (balança fiscal)
        tipo_carga = context.tpCarga or "01"
        
        tolerancia = self.get_tolerancia(tipo_carga)
        
        diferenca_abs = abs(peso_real - peso_faturado)
        diferenca_pct = diferenca_abs / peso_faturado
        
        if diferenca_pct <= tolerancia:
            return []  # Dentro da tolerância
        
        # Calcular valor da divergência
        # Usar valor/tonelada do contrato ou tabela ANTT
        valor_ton = context.valor_por_tonelada or self.get_valor_tonelada_antt(
            peso_faturado / 1000, tipo_carga
        )
        
        peso_divergencia_ton = diferenca_abs / 1000
        valor_divergencia = peso_divergencia_ton * valor_ton
        
        return [Discrepancy(
            rule_code=self.code,
            severity="HIGH",
            expected_value=round(peso_real, 2),
            actual_value=round(peso_faturado, 2),
            difference=round(valor_divergencia, 2),
            difference_pct=round(diferenca_pct * 100, 2),
            details={
                "peso_faturado_kg": peso_faturado,
                "peso_real_kg": peso_real,
                "diferenca_kg": round(diferenca_abs, 2),
                "diferenca_pct": round(diferenca_pct * 100, 2),
                "tolerancia_permitida_pct": tolerancia * 100,
                "tipo_carga": tipo_carga,
                "valor_tonelada_usado": valor_ton,
                "fonte_peso_real": context.fonte_peso_real  # "balança fiscal", "nota fiscal", etc.
            }
        )]
```

---

## 🧪 Casos de Teste

```python
# test_peso_real_vs_faturado
# Carga Geral, faturado 10.000 kg, real 11.000 kg
# Diferença = 10% > 5% tolerância
# Valor tonelada = R$ 250,00
# Divergência = 1 ton × 250 = R$ 250,00

# test_peso_real_vs_faturado_dentro_tolerancia
# Carga Geral, faturado 10.000 kg, real 10.400 kg
# Diferença = 4% ≤ 5% → SEM divergência

# test_peso_real_vs_faturado_granel
# Granel Sólido, faturado 30.000 kg, real 35.000 kg
# Diferença = 16,67% ≤ 20% → SEM divergência

# test_peso_real_vs_faturado_perigosa
# Perigosa, faturado 5.000 kg, real 5.200 kg
# Diferença = 4% > 3% → DIVERGÊNCIA
```

---

## ⚠️ Pontos de Atenção

1. **Fonte do Peso Real:** Balança fiscal (ANTT), balança transportador, nota fiscal de pesagem
2. **Peso Bruto vs Líquido:** CT-e informa peso bruto; comparar com pesagem bruta
3. **Múltiplas Pesagens:** Usar a **primeira pesagem fiscal** no percurso
4. **CT-e Complementar:** Se houve complemento de peso (tpEmis=4), considerar peso final

---

## 📦 JSON para backend/app/data/pesos_tolerancia.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Resolução ANTT 5.839/2021 Art. 7º",
  "tolerancias_por_tipo_carga": {
    "01": 0.05, "02": 0.03, "03": 0.05, "04": 0.20,
    "05": 0.20, "06": 0.05, "07": 0.05, "08": 0.05,
    "09": 0.03, "10": 0.10
  },
  "tipos_carga": {
    "01": "Carga Geral", "02": "Carga Perigosa", "03": "Carga Frigorífica",
    "04": "Granel Líquido", "05": "Granel Sólido", "06": "Neogranel",
    "07": "Container", "08": "Carga Projeto", "09": "Veículos", "10": "Carga Viva"
  }
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Julho 2025