# Piso Mínimo de Frete ANTT (Res. 5.839/2021) - Regra VALOR_MINIMO_FRETE

**Rule Code:** `VALOR_MINIMO_FRETE`  
**Tipo:** `VALOR_MINIMO_FRETE`  
**Severidade:** `CRITICAL`  
**Tags:** `freight, weight`  
**Arquivo de Dados:** `backend/app/data/antt_piso_minimo.json` (consolida peso×valor + cubagem + eixos)  
**Teste:** `tests/test_rules_critical.py::test_valor_minimo_frete`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Res. ANTT 5.839/2021** | Piso Mínimo de Frete - Tabelas completas | 2021+ |
| **Res. ANTT 5.868/2022** | Atualização 2023 (IPCA + óleo diesel) | 2023+ |
| **Res. ANTT 5.933/2023** | Atualização 2024 | 2024+ |
| **Lei 11.442/2007** (Art. 6º, §5º) | Obrigatoriedade do piso mínimo | Vigente |
| **Lei 13.103/2015** (Lei dos Caminhoneiros) | Jornada, piso, fiscalização | Vigente |
| **MP 1.153/2022** → **Lei 14.445/2022** | Regras de contratação, multas | Vigente |

---

## 🎯 Quando Aplica

**TODAS** as operações de transporte rodoviário de cargas:
- Modal = Rodoviário (01)
- **Qualquer tipo de cálculo** (Peso×Valor, Cubagem, Por viagem)
- **Qualquer tipo de carga**
- **Regra "guarda-chuva"**: garante que **nenhum frete** fique abaixo do piso absoluto

---

## 🧮 Três Métodos de Cálculo do Piso

### 1. **Piso por Peso × Valor** (já em `04-FRETE-PESO-VALOR.md`)
- Frete Mínimo = Peso (ton) × Valor/ton (faixa ANTT por tipo carga)

### 2. **Piso por Cubagem** (já em `05-FRETE-CUBAGEM.md`)
- Frete Mínimo = Cubagem (m³) × Valor/m³ (faixa ANTT)

### 3. **Piso por Eixos × Distância** (NOVO - Regra Crítica)

```python
# Piso Mínimo = Distância (km) × Valor por km (por configuração de eixos)

# Tabela ANTT - Valor por km por Configuração de Eixos (2024/2025)
# Res. ANTT 5.933/2023 - Anexo I, Tabela 3

| Configuração | Descrição | Eixos | Valor R$/km (2024) |
|--------------|-----------|-------|-------------------|
| **3 eixos** | Truck (2+1) ou Cavalo 2 eixos + Carreta 1 eixo | 3 | 4,90 |
| **4 eixos** | Truck 3 eixos + Carreta 1 eixo / Cavalo 2+2 | 4 | 5,85 |
| **5 eixos** | Cavalo 2 eixos + Carreta 3 eixos (Bitrem) | 5 | 6,75 |
| **6 eixos** | Cavalo 3 eixos + Carreta 3 eixos (Rodotrem) | 6 | 7,60 |
| **7 eixos** | Bitrem 7 eixos / Rodotrem 7 eixos | 7 | 8,40 |
| **9 eixos** | Rodotrem 9 eixos | 9 | 9,80 |

# Fórmula: Piso_Eixos = Distancia_km × Valor_km(eixos)
```

---

## 🎯 Regra Consolidada (Engine)

```python
class MinimumFreightValueRule(BaseRule):
    code = "VALOR_MINIMO_FRETE"
    relevance_tags = {"freight", "weight"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        if context.modal != "01":
            return False
        if not context.vFrete or context.vFrete <= 0:
            return False
        return True  # SEMPRE verifica piso mínimo
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        pisos = []
        
        # 1. Piso por Peso × Valor
        if context.peso_carga and context.peso_carga > 0:
            piso_peso = self.calcular_piso_peso_valor(context)
            if piso_peso:
                pisos.append(("PESO_VALOR", piso_peso))
        
        # 2. Piso por Cubagem
        if context.cubagem and context.cubagem > 0:
            piso_cub = self.calcular_piso_cubagem(context)
            if piso_cub:
                pisos.append(("CUBAGEM", piso_cub))
        
        # 3. Piso por Eixos × Distância (SEMPRE se tem distância e eixos)
        if context.distancia_km and context.distancia_km > 0 and context.qtd_eixos:
            piso_eixos = self.calcular_piso_eixos(context)
            if piso_eixos:
                pisos.append(("EIXOS_DISTANCIA", piso_eixos))
        
        # Piso Mínimo = MAIOR dos pisos aplicáveis
        if not pisos:
            return []
        
        piso_minimo = max(pisos, key=lambda x: x[1])[1]
        metodo_usado = max(pisos, key=lambda x: x[1])[0]
        
        if context.vFrete < piso_minimo * 0.99:  # 1% tolerância
            diferenca = piso_minimo - context.vFrete
            return [Discrepancy(
                rule_code=self.code,
                severity="CRITICAL",
                expected_value=round(piso_minimo, 2),
                actual_value=round(context.vFrete, 2),
                difference=round(diferenca, 2),
                details={
                    "piso_minimo_aplicavel": round(piso_minimo, 2),
                    "metodo_calculo": metodo_usado,
                    "pisos_calculados": {k: round(v, 2) for k, v in pisos},
                    "distancia_km": context.distancia_km,
                    "qtd_eixos": context.qtd_eixos,
                    "peso_toneladas": context.peso_carga / 1000 if context.peso_carga else None,
                    "cubagem_m3": context.cubagem,
                    "tipo_carga": context.tpCarga
                }
            )]
        return []
```

---

## 📊 Tabela Pisos por Eixos × Distância (2024/2025)

| Eixos | R$/km | Exemplo 500 km | Exemplo 1.000 km | Exemplo 2.000 km |
|-------|-------|----------------|------------------|------------------|
| **3** | 4,90 | R$ 2.450,00 | R$ 4.900,00 | R$ 9.800,00 |
| **4** | 5,85 | R$ 2.925,00 | R$ 5.850,00 | R$ 11.700,00 |
| **5** | 6,75 | R$ 3.375,00 | R$ 6.750,00 | R$ 13.500,00 |
| **6** | 7,60 | R$ 3.800,00 | R$ 7.600,00 | R$ 15.200,00 |
| **7** | 8,40 | R$ 4.200,00 | R$ 8.400,00 | R$ 16.800,00 |
| **9** | 9,80 | R$ 4.900,00 | R$ 9.800,00 | R$ 19.600,00 |

> **Fator atualização anual:** IPCA + variação preço óleo diesel (ANTT publica todo julho)

---

## 🧪 Casos de Teste

```python
# test_valor_minimo_frete
# 3 eixos, 500 km, carga geral 12 ton
# Piso Eixos = 500 × 4,90 = R$ 2.450,00
# Peso × Valor = 12 × 252,19 = R$ 3.026,28
# Piso Mínimo = MAX(2.450, 3.026) = R$ 3.026,28
# Frete Cobrado = R$ 2.500,00 → DIVERGÊNCIA R$ 526,28

# test_valor_minimo_frete_eixos_maior
# 6 eixos, 1000 km, carga leve 5 ton (cubagem)
# Piso Eixos = 1000 × 7,60 = R$ 7.600,00
# Peso × Valor = 5 × 322,47 = R$ 1.612,35
# Piso Mínimo = R$ 7.600,00 (eixos vence)

# test_valor_minimo_frete_cubagem_maior
# Móveis 60 m³, 300 km, 4 eixos
# Piso Eixos = 300 × 5,85 = R$ 1.755,00
# Cubagem = 60 × 66,55 = R$ 3.993,00
# Piso Mínimo = R$ 3.993,00
```

---

## ⚠️ Pontos Críticos

1. **SEMPRE calcular os 3 pisos** e pegar o maior
2. **Distância:** Usar menor percurso (Google Maps / ANTT) ou percurso contratado
3. **Eixos:** Informado no CT-e (`veicNovos` / `veicReboque` / `qtdEixos`)
4. **Multas:** Art. 6º Lei 11.442 - Multa de 2x a diferença + proibição de contratar
5. **Fiscalização:** ANTT + PRF + SEFAZ - Balanças + Documentação

---

## 📦 JSON para backend/app/data/antt_piso_minimo.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Resolução ANTT 5.933/2023",
  "piso_eixos_distancia": {
    "3": 4.90,
    "4": 5.85,
    "5": 6.75,
    "6": 7.60,
    "7": 8.40,
    "9": 9.80
  },
  "configuracoes_eixos": {
    "3": "Truck (2+1) ou Cavalo 2+Carreta 1",
    "4": "Truck 3+Carreta 1 / Cavalo 2+2",
    "5": "Cavalo 2+Carreta 3 (Bitrem)",
    "6": "Cavalo 3+Carreta 3 (Rodotrem)",
    "7": "Bitrem 7 eixos / Rodotrem 7",
    "9": "Rodotrem 9 eixos"
  },
  "fator_atualizacao_anual": "IPCA + variação óleo diesel",
  "proxima_atualizacao": "2025-07-01"
}
```

---

## 🔗 Referências

- [Res. ANTT 5.839/2021](https://www.antt.gov.br/archives/legislacao/resolucoes/2021/resolucao-5839-2021.pdf)
- [Res. ANTT 5.933/2023](https://www.antt.gov.br/archives/legislacao/resolucoes/2023/resolucao-5933-2023.pdf)
- [Calculadora Piso Mínimo ANTT](https://www.antt.gov.br/piso-minimo-de-frete/calculadora)
- [Lei 11.442/2007 Art. 6º](http://www.planalto.gov.br/ccivil_03/_ato2004-2006/2007/lei/l11442.htm)

---

**Última Atualização:** 2026-11-01 | **Severidade: CRITICAL** | **Próxima Revisão:** Julho 2025