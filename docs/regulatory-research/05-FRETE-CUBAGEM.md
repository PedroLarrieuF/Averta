# Frete por Cubagem (m³) - Regra FRETE_CUBAGE

**Rule Code:** `FRETE_CUBAGEM`  
**Tipo:** `FREIGHT_CUBAGE`  
**Severidade:** `HIGH`  
**Tags:** `freight, cubage`  
**Arquivo de Dados:** `backend/app/data/antt_faixas_cubagem.json`  
**Teste:** `tests/test_rules_critical.py::test_freight_cubage`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Res. ANTT 5.839/2021** (Anexo II) | Tabelas de frete por cubagem | 2021+ |
| **Res. ANTT 5.868/2022** | Atualização 2023 | 2023+ |
| **Res. ANTT 5.933/2023** | Atualização 2024 | 2024+ |
| **Lei 11.442/2007** | Contratação de transporte rodoviário | Vigente |

---

## 🎯 Quando Aplica

**Transporte Rodoviário** onde o frete é calculado por **volume (m³)**:
- Cargas leves e volumosas (ex: móveis, eletrodomésticos, embalagens)
- `tipo_calculo_frete = "CUBAGEM"` no contrato/frete
- CT-e com informações de cubagem (`qCub`, `vCub`)

**Identificação no CT-e:**
```xml
<infCarga>
  <qCub>50.000</qCub>          <!-- Cubagem em m³ -->
  <vCub>150.00</vCub>          <!-- Valor por m³ -->
  <proPred>
    <tpCarga>01</tpCarga>
  </proPred>
</infCarga>
```

---

## 🧮 Fórmula de Cálculo

```python
# Frete Mínimo = Cubagem (m³) × Valor por m³ (faixa ANTT)

# Onde:
# - Cubagem = Comprimento × Largura × Altura (m³) OU valor informado no CT-e
# - Valor por m³ = Tabela ANTT por faixa de cubagem e tipo de carga

# Se frete cobrado < Frete Mínimo → DIVERGÊNCIA
```

### Tabela ANTT 2024/2025 - Faixas Cubagem (R$/m³)

| Faixa | Cubagem (m³) | Carga Geral | Carga Perigosa | Carga Frigorífica | Granel Líquido | Granel Sólido |
|-------|--------------|-------------|----------------|-------------------|----------------|---------------|
| **1** | Até 10 | 102,45 | 122,94 | 112,70 | 92,21 | 87,08 |
| **2** | 10,01 a 20 | 88,67 | 106,40 | 97,54 | 79,80 | 75,37 |
| **3** | 20,01 a 30 | 80,45 | 96,54 | 88,50 | 72,41 | 68,38 |
| **4** | 30,01 a 40 | 74,52 | 89,42 | 81,97 | 67,07 | 63,34 |
| **5** | 40,01 a 50 | 70,05 | 84,06 | 77,06 | 63,05 | 59,54 |
| **6** | 50,01 a 60 | 66,55 | 79,86 | 73,21 | 59,90 | 56,57 |
| **7** | 60,01 a 70 | 63,71 | 76,45 | 70,08 | 57,34 | 54,15 |
| **8** | 70,01 a 80 | 61,35 | 73,62 | 67,49 | 55,22 | 52,15 |
| **9** | 80,01 a 90 | 59,35 | 71,22 | 65,29 | 53,42 | 50,45 |
| **10** | 90,01 a 100 | 57,61 | 69,13 | 63,37 | 51,85 | 48,97 |

> **Fatores por tipo de carga:** Igual ao Peso × Valor (ver `04-FRETE-PESO-VALOR.md`)

---

## 🔍 Lógica de Detecção no Engine

```python
class FreightCubageRule(BaseRule):
    code = "FRETE_CUBAGEM"
    relevance_tags = {"freight", "cubage"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        if context.modal != "01":
            return False
        # Verifica se frete é por cubagem
        if context.tipo_calculo_frete != "CUBAGEM":
            return False
        if not context.cubagem or context.cubagem <= 0:
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        cubagem = context.cubagem  # m³
        tipo_carga = context.tpCarga or "01"
        
        valor_m3 = self.get_valor_m3(cubagem, tipo_carga)
        if not valor_m3:
            return []
        
        frete_minimo = cubagem * valor_m3
        frete_cobrado = context.vFrete
        
        diferenca = frete_minimo - frete_cobrado
        
        if diferenca > frete_cobrado * 0.01:
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(frete_minimo, 2),
                actual_value=round(frete_cobrado, 2),
                difference=round(diferenca, 2),
                details={
                    "cubagem_m3": round(cubagem, 3),
                    "tipo_carga": tipo_carga,
                    "faixa_cubagem": self.get_faixa_cubagem(cubagem),
                    "valor_m3_antt": valor_m3,
                    "frete_minimo_calculado": round(frete_minimo, 2)
                }
            )]
        return []
```

---

## 🧪 Casos de Teste

```python
# test_freight_cubage
# Móveis, 45 m³, Carga Geral
# Faixa 5 (40,01 a 50): R$ 70,05/m³
# Frete Mínimo = 45 × 70,05 = R$ 3.152,25

# test_freight_cubage_frigorifica
# Carga Frigorífica, 25 m³
# Faixa 3: R$ 80,45 × 1,10 = R$ 88,50/m³
```

---

## 📦 JSON para backend/app/data/antt_faixas_cubagem.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Resolução ANTT 5.933/2023",
  "faixas_cubagem": [
    {"faixa": 1, "cub_min": 0, "cub_max": 10, "carga_geral": 102.45, "perigosa": 122.94, "frigorifica": 112.70, "granel_liquido": 92.21, "granel_solido": 87.08},
    {"faixa": 2, "cub_min": 10.01, "cub_max": 20, "carga_geral": 88.67, "perigosa": 106.40, "frigorifica": 97.54, "granel_liquido": 79.80, "granel_solido": 75.37},
    {"faixa": 3, "cub_min": 20.01, "cub_max": 30, "carga_geral": 80.45, "perigosa": 96.54, "frigorifica": 88.50, "granel_liquido": 72.41, "granel_solido": 68.38},
    {"faixa": 4, "cub_min": 30.01, "cub_max": 40, "carga_geral": 74.52, "perigosa": 89.42, "frigorifica": 81.97, "granel_liquido": 67.07, "granel_solido": 63.34},
    {"faixa": 5, "cub_min": 40.01, "cub_max": 50, "carga_geral": 70.05, "perigosa": 84.06, "frigorifica": 77.06, "granel_liquido": 63.05, "granel_solido": 59.54},
    {"faixa": 6, "cub_min": 50.01, "cub_max": 60, "carga_geral": 66.55, "perigosa": 79.86, "frigorifica": 73.21, "granel_liquido": 59.90, "granel_solido": 56.57},
    {"faixa": 7, "cub_min": 60.01, "cub_max": 70, "carga_geral": 63.71, "perigosa": 76.45, "frigorifica": 70.08, "granel_liquido": 57.34, "granel_solido": 54.15},
    {"faixa": 8, "cub_min": 70.01, "cub_max": 80, "carga_geral": 61.35, "perigosa": 73.62, "frigorifica": 67.49, "granel_liquido": 55.22, "granel_solido": 52.15},
    {"faixa": 9, "cub_min": 80.01, "cub_max": 90, "carga_geral": 59.35, "perigosa": 71.22, "frigorifica": 65.29, "granel_liquido": 53.42, "granel_solido": 50.45},
    {"faixa": 10, "cub_min": 90.01, "cub_max": 100, "carga_geral": 57.61, "perigosa": 69.13, "frigorifica": 63.37, "granel_liquido": 51.85, "granel_solido": 48.97}
  ]
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Julho 2025 (Res. ANTT anual)