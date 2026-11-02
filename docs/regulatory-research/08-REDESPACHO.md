# Redespacho (CT-e Complementar) - Regra REDESPACHO_VALIDACAO

**Rule Code:** `REDESPACHO_VALIDACAO`  
**Tipo:** `REDESPACHO`  
**Severidade:** `HIGH`  
**Tags:** `redespacho`  
**Arquivo de Dados:** `backend/app/data/redespacho_regras.json`  
**Teste:** `tests/test_rules_critical.py::test_redespacho_validacao`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Decreto 9.209/2017** (Art. 28-30) | Redespacho e subcontratação | Vigente |
| **Manual CT-e 3.00** | CT-e de redespacho (tpCTe=3) | Vigente |
| **Lei 11.442/2007** (Art. 3º, §2º) | Subcontratação de transporte | Vigente |
| **Res. ANTT 5.839/2021** | Piso mínimo aplica a redespacho | 2021+ |

---

## 🎯 Quando Aplica

**Redespacho** = Transportador principal (contratante) subcontrata outro transportador (redespachante) para executar **todo ou parte** do percurso.

**CT-e de Redespacho:** `tpCTe = 3` (Redespacho)

### Cadeia Documental
```
CT-e Normal (tpCTe=0) - Transportador Principal (Emissor)
    ↓
CT-e Redespacho (tpCTe=3) - Transportador Redespachante (Emissor)
    ↓ (opcional)
CT-e Redespacho Intermediário (tpCTe=3) - Outro redespachante
```

---

## 🧮 Regras de Validação

### 1. **CT-e Principal deve existir**
- Chave do CT-e normal referenciada no redespacho (`refCTe`)

### 2. **Transportadores Diferentes**
- CNPJ emitente do redespacho ≠ CNPJ emitente do principal

### 3. **Piso Mínimo Aplica-se a CADA Trecho**
- Principal: piso pelo trecho que executou
- Redespachante: piso pelo trecho que executou
- **Soma dos fretes** ≥ Piso total origem→destino

### 4. **ICMS - Responsabilidade**
- **Principal:** Recolhe ICMS total (origem→destino)
- **Redespachante:** Emite CT-e com ICMS próprio (se contribuinte) ou isento

---

## 🔍 Lógica de Detecção no Engine

```python
class RedespachoValidacaoRule(BaseRule):
    code = "REDESPACHO_VALIDACAO"
    relevance_tags = {"redespacho"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        return context.tpCTe == "3"  # CT-e de redespacho
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        discrepancias = []
        
        # 1. Deve ter refCTe (CT-e principal)
        if not context.refCTe:
            discrepancias.append(Discrepancy(
                rule_code=self.code, severity="HIGH",
                details={"erro": "CT-e redespacho sem refCTe ao CT-e principal"}
            ))
            return discrepancias
        
        cte_principal = self.get_cte_by_chave(context.refCTe)
        if not cte_principal:
            discrepancias.append(Discrepancy(
                rule_code=self.code, severity="HIGH",
                details={"erro": "CT-e principal referenciado não encontrado"}
            ))
            return discrepancias
        
        # 2. Transportadores diferentes
        if cte_principal.emit_cnpj == context.emit_cnpj:
            discrepancias.append(Discrepancy(
                rule_code=self.code, severity="HIGH",
                details={"erro": "Transportador redespachante igual ao principal"}
            ))
        
        # 3. Piso mínimo por trecho
        # Trecho principal: origem → ponto redespacho
        # Trecho redespacho: ponto redespacho → destino
        piso_principal = self.calcular_piso_trecho(
            cte_principal.uf_origem, cte_principal.uf_redespacho,
            cte_principal.peso_carga, cte_principal.tpCarga
        )
        piso_redespacho = self.calcular_piso_trecho(
            context.uf_origem, context.uf_destino,
            context.peso_carga, context.tpCarga
        )
        
        # Verificar cada frete
        if cte_principal.vFrete < piso_principal * 0.99:
            discrepancias.append(Discrepancy(
                rule_code=self.code, severity="CRITICAL",
                expected_value=round(piso_principal, 2),
                actual_value=round(cte_principal.vFrete, 2),
                details={"trecho": "principal", "erro": "Piso mínimo não atingido"}
            ))
        
        if context.vFrete < piso_redespacho * 0.99:
            discrepancias.append(Discrepancy(
                rule_code=self.code, severity="CRITICAL",
                expected_value=round(piso_redespacho, 2),
                actual_value=round(context.vFrete, 2),
                details={"trecho": "redespacho", "erro": "Piso mínimo não atingido"}
            ))
        
        # 4. Soma dos fretes não pode ser < piso total direto
        piso_total_direto = self.calcular_piso_trecho(
            cte_principal.uf_origem, cte_principal.uf_destino,
            cte_principal.peso_carga, cte_principal.tpCarga
        )
        soma_fretes = cte_principal.vFrete + context.vFrete
        
        if soma_fretes < piso_total_direto * 0.99:
            discrepancias.append(Discrepancy(
                rule_code=self.code, severity="HIGH",
                expected_value=round(piso_total_direto, 2),
                actual_value=round(soma_fretes, 2),
                details={"erro": "Soma dos fretes (principal + redespacho) abaixo do piso direto origem→destino"}
            ))
        
        return discrepancias
```

---

## 🧪 Casos de Teste

```python
# test_redespacho_validacao
# Principal: SP → Campinas (100 km), 10 ton, R$ 2.000
# Redespacho: Campinas → RJ (400 km), 10 ton, R$ 1.500
# Piso Principal: 100 × 4,90 (3 eixos) = 490 / 100km × 100 = R$ 490 (peso×valor maior)
# Piso Redespacho: 400 × 4,90 = R$ 1.960
# Redespacho R$ 1.500 < R$ 1.960 → DIVERGÊNCIA

# test_redespacho_soma_abaixo_piso_total
# Principal R$ 1.000 + Redespacho R$ 1.000 = R$ 2.000
# Piso SP→RJ direto = R$ 3.000 → DIVERGÊNCIA

# test_redespacho_mesmo_transportador
# CNPJ principal = CNPJ redespacho → DIVERGÊNCIA
```

---

## ⚠️ Pontos de Atenção

1. **Subcontratação ≠ Redespacho:** Subcontratação é mais ampla; redespacho é tipo específico
2. **CT-e Principal:** Deve ter `infCte/infCTeNorm/infRespTec` com responsável técnico
3. **ICMS:** Principal recolhe total; redespachante emite com CST 90 (outros) ou isento
4. **Seguro:** Responsabilidade civil - principal responde perante embarcador
5. **ANTT:** Ambos transportadores devem ter RNTR-C válido

---

## 📦 JSON para backend/app/data/redespacho_regras.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Decreto 9.209/2017, Lei 11.442/2007, Res. ANTT 5.839/2021",
  "regras": {
    "refCTe_obrigatorio": true,
    "transportadores_diferentes": true,
    "piso_minimo_por_trecho": true,
    "soma_fretes_maior_ou_igual_piso_direto": true,
    "icms_principal_recolhe_total": true,
    "redespachante_pode_ser_isento": true
  }
}
```

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Anual