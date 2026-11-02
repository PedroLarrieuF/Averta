# Frete Peso × Valor (Faixas ANTT) - Regra FRETE_PESO_VALOR

**Rule Code:** `FRETE_PESO_VALOR`  
**Tipo:** `FREIGHT_WEIGHT_VALUE`  
**Severidade:** `HIGH`  
**Tags:** `freight, weight`  
**Arquivo de Dados:** `backend/app/data/antt_faixas_peso_valor.json`  
**Teste:** `tests/test_rules_critical.py::test_freight_weight_value`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Res. ANTT 5.839/2021** | Piso Mínimo de Frete - Tabelas Peso × Valor | 2021+ |
| **Res. ANTT 5.868/2022** | Atualização dos pisos para 2023 | 2023+ |
| **Res. ANTT 5.933/2023** | Atualização dos pisos para 2024 | 2024+ |
| **Lei 11.442/2007** (Art. 6º, §5º) | Obrigatoriedade do piso mínimo | Vigente |
| **MP 1.153/2022** (convertida em Lei 14.445/2022) | Regras de contratação de frete | Vigente |

---

## 🎯 Quando Aplica

**Transporte Rodoviário de Cargas** onde:
- Modal = Rodoviário (CT-e modal = 01)
- Tipo de operação: Carga Lotação (FTL) ou Fracionada (LTL)
- Frete calculado por **Peso × Valor** (não cubagem)
- **Qualquer UF** - Tabela nacional ANTT

**Identificação no CT-e:**
- `modal = 01` (Rodoviário)
- `tpCTe = 0` (Normal) ou `1` (Complementar)
- Peso informado em `vCarga` / `peso` / `pesoBC`
- Valor do frete em `vFrete` / `vTPrest`

---

## 🧮 Fórmula de Cálculo

```python
# Frete Mínimo = Peso (toneladas) × Valor por Tonelada (faixa)

# Onde:
# - Peso = Peso bruto total da carga (toneladas)
# - Valor por Tonelada = Tabela ANTT por faixa de peso e tipo de carga

# Se frete cobrado < Frete Mínimo → DIVERGÊNCIA
diferenca = frete_minimo_antt - frete_cobrado
```

### Tabela ANTT 2024/2025 - Faixas Peso × Valor (R$/tonelada)

| Faixa | Peso (ton) | Carga Geral | Carga Perigosa | Carga Frigorífica | Carga Granel Líquido | Carga Granel Sólido |
|-------|------------|-------------|----------------|-------------------|----------------------|---------------------|
| **1** | Até 5,0 | 322,47 | 386,96 | 354,72 | 290,22 | 274,71 |
| **2** | 5,01 a 10,0 | 278,15 | 333,78 | 305,97 | 250,34 | 237,02 |
| **3** | 10,01 a 15,0 | 252,19 | 302,63 | 277,41 | 226,97 | 214,87 |
| **4** | 15,01 a 20,0 | 233,77 | 280,52 | 257,15 | 210,39 | 199,17 |
| **5** | 20,01 a 25,0 | 219,85 | 263,82 | 241,84 | 197,87 | 187,31 |
| **6** | 25,01 a 30,0 | 208,65 | 250,38 | 229,52 | 187,79 | 177,76 |
| **7** | 30,01 a 35,0 | 199,32 | 239,18 | 219,25 | 179,39 | 169,81 |
| **8** | 35,01 a 40,0 | 191,39 | 229,67 | 210,53 | 172,25 | 163,06 |
| **9** | 40,01 a 45,0 | 184,55 | 221,46 | 203,01 | 166,10 | 157,24 |
| **10** | 45,01 a 50,0 | 178,59 | 214,31 | 196,45 | 160,73 | 152,15 |

> ⚠️ **Valores atualizados pela Res. ANTT 5.933/2023** (vigentes 2024)
> **Fator de atualização anual:** INPC/IBGE + variação óleo diesel (ANTT)

---

## 📊 Cálculo por Tipo de Carga

| Tipo Carga (CT-e: `tpCarga`) | Descrição | Fator sobre Carga Geral |
|------------------------------|-----------|-------------------------|
| **01** | Carga Geral | 1,0000 (base) |
| **02** | Carga Perigosa | 1,2000 (+20%) |
| **03** | Carga Frigorífica | 1,1000 (+10%) |
| **04** | Carga Granel Líquido | 0,9000 (-10%) |
| **05** | Carga Granel Sólido | 0,8500 (-15%) |
| **06** | Carga Neogranel | 1,0000 (igual geral) |
| **07** | Container | 1,0000 (igual geral) |
| **08** | Carga Projeto | 1,3000 (+30%) |
| **09** | Veículos | 1,0000 (igual geral) |
| **10** | Carga Viva | 1,1500 (+15%) |

---

## 🔍 Lógica de Detecção no Engine

```python
class FreightWeightValueRule(BaseRule):
    code = "FRETE_PESO_VALOR"
    relevance_tags = {"freight", "weight"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        # Só rodoviário
        if context.modal != "01":
            return False
        # Precisa ter peso e valor frete
        if not context.peso_carga or context.peso_carga <= 0:
            return False
        if not context.vFrete or context.vFrete <= 0:
            return False
        # Só se frete calculado por peso (não cubagem)
        if context.tipo_calculo_frete == "CUBAGEM":
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        peso_ton = context.peso_carga / 1000  # kg para ton
        tipo_carga = context.tpCarga or "01"  # default: carga geral
        
        # Buscar valor por tonelada na faixa de peso
        valor_ton = self.get_valor_tonelada(peso_ton, tipo_carga)
        if not valor_ton:
            return []
        
        frete_minimo = peso_ton * valor_ton
        frete_cobrado = context.vFrete
        
        diferenca = frete_minimo - frete_cobrado
        
        # Tolerância 1% (arredondamento)
        if diferenca > frete_cobrado * 0.01:
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(frete_minimo, 2),
                actual_value=round(frete_cobrado, 2),
                difference=round(diferenca, 2),
                details={
                    "peso_toneladas": round(peso_ton, 3),
                    "tipo_carga": tipo_carga,
                    "faixa_peso": self.get_faixa_peso(peso_ton),
                    "valor_tonelada_antt": valor_ton,
                    "frete_minimo_calculado": round(frete_minimo, 2),
                    "modal": context.modal
                }
            )]
        return []
```

---

## 🧪 Casos de Teste (test_rules_critical.py)

```python
# test_freight_weight_value
# Carga Geral, 12 toneladas, SP → RJ
# Faixa 3 (10,01 a 15,0): R$ 252,19/ton
# Frete Mínimo = 12 × 252,19 = R$ 3.026,28
# Frete Cobrado = R$ 2.500,00
# Diferença = R$ 526,28

# test_freight_weight_value_perigosa
# Carga Perigosa (tpCarga=02), 8 toneladas
# Faixa 2: R$ 278,15 × 1,20 = R$ 333,78/ton
# Frete Mínimo = 8 × 333,78 = R$ 2.670,24

# test_freight_weight_value_granel_liquido
# Granel Líquido (tpCarga=04), 30 toneladas
# Faixa 6: R$ 208,65 × 0,90 = R$ 187,79/ton
# Frete Mínimo = 30 × 187,79 = R$ 5.633,70

# test_freight_weight_value_not_applicable
# Modal aéreo (02) - rule não dispara
# Frete por cubagem - rule não dispara
```

---

## ⚠️ Pontos de Atenção

### 1. **Peso Informado no CT-e**
```xml
<!-- Campos relevantes -->
<infCte>
  <infCTeNorm>
    <vPrest>
      <vTPrest>5000.00</vTPrest>      <!-- Valor total frete -->
      <vRec>5000.00</vRec>
    </vPrest>
    <infCarga>
      <vCarga>12000.00</vCarga>        <!-- Valor da carga -->
      <proPred>
        <tpCarga>01</tpCarga>          <!-- Tipo carga -->
        <peso>12000.000</peso>         <!-- Peso em KG -->
      </proPred>
    </infCarga>
  </infCTeNorm>
</infCte>
```

### 2. **CT-e Complementar (tpEmis=4)**
- Complemento de valor **SOMA** ao frete original
- Regra deve considerar `vFrete` total (original + complementares)

### 3. **Redespacho (tpCTe=3)**
- Cada trecho tem frete próprio
- Aplicar regra por trecho (CT-e de redespacho)

### 4. **Subcontratação**
- Transportador principal (CT-e normal)
- Subcontratado (CT-e redespacho)
- **Ambos** sujeitos ao piso mínimo

---

## 📦 JSON para backend/app/data/antt_faixas_peso_valor.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Resolução ANTT 5.933/2023",
  "vigencia": "2024-01-01",
  "faixas_peso_valor": [
    {"faixa": 1, "peso_min": 0, "peso_max": 5.0, "carga_geral": 322.47, "perigosa": 386.96, "frigorifica": 354.72, "granel_liquido": 290.22, "granel_solido": 274.71},
    {"faixa": 2, "peso_min": 5.01, "peso_max": 10.0, "carga_geral": 278.15, "perigosa": 333.78, "frigorifica": 305.97, "granel_liquido": 250.34, "granel_solido": 237.02},
    {"faixa": 3, "peso_min": 10.01, "peso_max": 15.0, "carga_geral": 252.19, "perigosa": 302.63, "frigorifica": 277.41, "granel_liquido": 226.97, "granel_solido": 214.87},
    {"faixa": 4, "peso_min": 15.01, "peso_max": 20.0, "carga_geral": 233.77, "perigosa": 280.52, "frigorifica": 257.15, "granel_liquido": 210.39, "granel_solido": 199.17},
    {"faixa": 5, "peso_min": 20.01, "peso_max": 25.0, "carga_geral": 219.85, "perigosa": 263.82, "frigorifica": 241.84, "granel_liquido": 197.87, "granel_solido": 187.31},
    {"faixa": 6, "peso_min": 25.01, "peso_max": 30.0, "carga_geral": 208.65, "perigosa": 250.38, "frigorifica": 229.52, "granel_liquido": 187.79, "granel_solido": 177.76},
    {"faixa": 7, "peso_min": 30.01, "peso_max": 35.0, "carga_geral": 199.32, "perigosa": 239.18, "frigorifica": 219.25, "granel_liquido": 179.39, "granel_solido": 169.81},
    {"faixa": 8, "peso_min": 35.01, "peso_max": 40.0, "carga_geral": 191.39, "perigosa": 229.67, "frigorifica": 210.53, "granel_liquido": 172.25, "granel_solido": 163.06},
    {"faixa": 9, "peso_min": 40.01, "peso_max": 45.0, "carga_geral": 184.55, "perigosa": 221.46, "frigorifica": 203.01, "granel_liquido": 166.10, "granel_solido": 157.24},
    {"faixa": 10, "peso_min": 45.01, "peso_max": 50.0, "carga_geral": 178.59, "perigosa": 214.31, "frigorifica": 196.45, "granel_liquido": 160.73, "granel_solido": 152.15}
  ],
  "fatores_tipo_carga": {
    "01": 1.0000, "02": 1.2000, "03": 1.1000, "04": 0.9000,
    "05": 0.8500, "06": 1.0000, "07": 1.0000, "08": 1.3000,
    "09": 1.0000, "10": 1.1500
  },
  "tipos_carga": {
    "01": "Carga Geral", "02": "Carga Perigosa", "03": "Carga Frigorífica",
    "04": "Granel Líquido", "05": "Granel Sólido", "06": "Neogranel",
    "07": "Container", "08": "Carga Projeto", "09": "Veículos", "10": "Carga Viva"
  }
}
```

---

## 🔗 Referências

- [Res. ANTT 5.839/2021 - Original](https://www.antt.gov.br/archives/legislacao/resolucoes/2021/resolucao-5839-2021.pdf)
- [Res. ANTT 5.868/2022 - Atualização 2023](https://www.antt.gov.br/archives/legislacao/resolucoes/2022/resolucao-5868-2022.pdf)
- [Res. ANTT 5.933/2023 - Atualização 2024](https://www.antt.gov.br/archives/legislacao/resolucoes/2023/resolucao-5933-2023.pdf)
- [Tabela Piso Mínimo ANTT - Portal](https://www.antt.gov.br/piso-minimo-de-frete)

---

**Última Atualização:** 2026-11-01  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2025 (Res. ANTT anual - geralmente julho)