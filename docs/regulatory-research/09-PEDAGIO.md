# Conferência de Pedágio - Regra PEDAGIO_CONFERENCIA

**Rule Code:** `PEDAGIO_CONFERENCIA`  
**Tipo:** `TOLL_PLAZA`  
**Severidade:** `MEDIUM`  
**Tags:** `toll`  
**Arquivo de Dados:** `backend/app/data/pedagio_tarifas.json`  
**Teste:** `tests/test_rules_critical.py::test_pedagio_conferencia`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 11.442/2007** (Art. 6º, §2º) | Pedágio como componente do frete | Vigente |
| **Res. ANTT 5.839/2021** | Pedágio incluído no piso mínimo | 2021+ |
| **Contratos de Concessão** | Tarifas por praça/rodovia/concessionária | Por concessão |
| **Decreto 9.209/2017** | CT-e deve informar pedágio (`vPed`) | Vigente |

---

## 🎯 Quando Aplica

**Toda operação rodoviária** que percorra rodovias pedagiadas:
- CT-e informa `vPed` (valor pedágio) no grupo `vPrest`
- Valor deve conferir com **tarifa vigente** da concessionária
- Percurso informado deve passar pelas praças de pedágio

---

## 🧮 Fórmula de Cálculo

```python
# Pedágio Total = Σ (Tarifa Praça × Fator Eixos × Qtd Passagens)

# Onde:
# - Tarifa Praça = Valor base por categoria de veículo
# - Fator Eixos = Multiplicador por número de eixos
# - Qtd Passagens = Quantas vezes passa na praça (ida/volta, trechos)

# Categorias de Veículo (ANTT):
# 1. Automóveis (2 eixos)
# 2. Caminhões leves (2 eixos, > 3,5t)
# 3. Caminhões médios (3 eixos)
# 4. Caminhões pesados (4-5 eixos)
# 5. Combinações (6+ eixos - bitrem, rodotrem)
```

### Exemplo: CCR AutoBAn (SP) - Tarifas 2024

| Praça | Cat 1 (Auto) | Cat 2 (Leve) | Cat 3 (3 eixos) | Cat 4 (4-5 eixos) | Cat 5 (6+ eixos) |
|-------|--------------|--------------|-----------------|-------------------|------------------|
| Jundiaí | 12,40 | 18,60 | 24,80 | 31,00 | 37,20 |
| Itupeva | 10,80 | 16,20 | 21,60 | 27,00 | 32,40 |
| Cabreúva | 9,20 | 13,80 | 18,40 | 23,00 | 27,60 |

---

## 🔍 Lógica de Detecção no Engine

```python
class TollConferenceRule(BaseRule):
    code = "PEDAGIO_CONFERENCIA"
    relevance_tags = {"toll"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        if context.modal != "01":
            return False
        if not context.vPed or context.vPed <= 0:
            return False  # Sem pedágio informado
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        # Calcular pedágio esperado baseado no percurso
        pedagio_esperado = self.calcular_pedagio_percurso(
            context.uf_origem, context.uf_destino,
            context.qtd_eixos, context.percurso_rodovias
        )
        
        if not pedagio_esperado:
            return []  # Sem dados de tarifa para o percurso
        
        pedagio_informado = context.vPed
        diferenca = abs(pedagio_esperado - pedagio_informado)
        diferenca_pct = diferenca / pedagio_esperado
        
        # Tolerância 10% (tarifas mudam, arredondamentos)
        if diferenca_pct > 0.10:
            return [Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                expected_value=round(pedagio_esperado, 2),
                actual_value=round(pedagio_informado, 2),
                difference=round(diferenca, 2),
                details={
                    "pedagio_esperado": round(pedagio_esperado, 2),
                    "pedagio_informado": round(pedagio_informado, 2),
                    "qtd_eixos": context.qtd_eixos,
                    "percurso": context.percurso_rodovias,
                    "praças_percurso": pedagio_esperado.detalhes_pracas
                }
            )]
        return []
```

---

## 🧪 Casos de Teste

```python
# test_pedagio_conferencia
# SP → RJ via Dutra (BR-116)
# Praças: Jacareí, Taubaté, Piraí
# 3 eixos: 24,80 + 24,80 + 24,80 = R$ 74,40
# CT-e informa vPed = R$ 50,00 → DIVERGÊNCIA 32%

# test_pedagio_sem_informar
# Percurso com pedágio mas vPed = 0 ou não informado
# → ALERT (não divergência, mas dado faltante)

# test_pedagio_isento
# Veículo isento (transporte público, etc.) - vPed = 0 válido
```

---

## ⚠️ Pontos de Atenção

1. **Fontes de Tarifa:** Sites concessionárias (CCR, EcoRodovias, Arteris, ViaOeste, etc.)
2. **Atualização:** Tarifas reajustadas anualmente (geralmente janeiro/julho)
3. **Isenções:** Transporte coletivo, ambulâncias, viaturas - verificar legislação
4. **Sem Parar / Tags:** Valor é o mesmo; CT-e deve informar valor nominal
5. **Percurso Alternativo:** Se transportador usa rota sem pedágio, vPed = 0 válido

---

## 📦 JSON para backend/app/data/pedagio_tarifas.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Concessionárias rodoviárias, ANTT",
  "concessionarias": {
    "CCR_AutoBAn": {
      "rodovias": ["SP-300", "SP-330", "SP-348"],
      "pracas": {
        "Jundiai": {"cat1": 12.40, "cat2": 18.60, "cat3": 24.80, "cat4": 31.00, "cat5": 37.20},
        "Itupeva": {"cat1": 10.80, "cat2": 16.20, "cat3": 21.60, "cat4": 27.00, "cat5": 32.40},
        "Cabreuva": {"cat1": 9.20, "cat2": 13.80, "cat3": 18.40, "cat4": 23.00, "cat5": 27.60}
      }
    },
    "EcoRodovias_Dutra": {
      "rodovias": ["BR-116"],
      "pracas": {
        "Jacarei": {"cat1": 13.50, "cat2": 20.20, "cat3": 27.00, "cat4": 33.70, "cat5": 40.50},
        "Taubate": {"cat1": 13.50, "cat2": 20.20, "cat3": 27.00, "cat4": 33.70, "cat5": 40.50},
        "Pirai": {"cat1": 14.20, "cat2": 21.30, "cat3": 28.40, "cat4": 35.50, "cat5": 42.60}
      }
    }
  },
  "categoria_por_eixos": {
    "2": 2,  // Caminhão leve
    "3": 3,  // 3 eixos
    "4": 4,  // 4-5 eixos
    "5": 4,
    "6": 5,  // 6+ eixos
    "7": 5,
    "9": 5
  }
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Semestral (tarifas mudam)