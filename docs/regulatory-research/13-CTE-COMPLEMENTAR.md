# CT-e Complementar (Anulação, Substituição, Complemento) - Regras CTE_ANULACAO, CTE_SUBSTITUICAO, CTE_COMPLEMENTO_VALOR

**Rule Codes:** `CTE_ANULACAO`, `CTE_SUBSTITUICAO`, `CTE_COMPLEMENTO_VALOR`  
**Tipo:** `COMPLEMENTARY_CTE`  
**Severidade:** `HIGH` / `HIGH` / `MEDIUM`  
**Tags:** `cte_complementar`  
**Arquivo de Dados:** `backend/app/data/cte_complementar_regras.json`  
**Teste:** `tests/test_rules_critical.py::test_cte_anulacao_without_ref`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Decreto 9.209/2017** (Art. 33-35) | CT-e complementar - anulação, substituição, complemento | Vigente |
| **Manual CT-e 3.00** (Receita Federal) | Especificação técnica XML | 2024+ |
| **Convênio ICMS 188/2017** | Padronização CT-e complementar | Vigente |
| **Ajuste SINIEF 09/2017** | Leiaute CT-e 3.00 | Vigente |

---

## 🎯 Tipos de CT-e Complementar (tpEmis)

| tpEmis | Tipo | Descrição | Quando Usa |
|--------|------|-----------|------------|
| **2** | **Substituição** | Substitui CT-e anterior com erro | Erro de dados (peso, valor, destinatário) |
| **3** | **Anulação** | Anula CT-e anterior | Operação não realizada, cancelamento |
| **4** | **Complemento** | Complementa valor (frete, ICMS) | Diferença de frete, ICMS complementar |

---

## 🔍 Regra CTE_ANULACAO (tpEmis=3) - CRITICAL

### Quando Dispara
- CT-e de anulação **SEM referência** ao CT-e original (`refCTe` vazio)
- CT-e original **já anulado** (dupla anulação)
- Anulação fora do prazo (não há prazo legal, mas fiscalização questiona > 30 dias)

### Validação Obrigatória
```xml
<!-- CT-e Anulação deve ter: -->
<infCte>
  <ide>
    <tpEmis>3</tpEmis>                    <!-- Anulação -->
    <refCTe>35250101234567890123550010000000011234567890</refCTe>  <!-- CHAVE CT-e original -->
  </ide>
</infCte>
```

### Lógica no Engine
```python
class CteAnulacaoRule(BaseRule):
    code = "CTE_ANULACAO"
    relevance_tags = {"cte_complementar"}
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        if context.tpEmis != "3":
            return []
        
        # CRÍTICO: Deve ter refCTe
        if not context.refCTe:
            return [Discrepancy(
                rule_code=self.code,
                severity="CRITICAL",
                expected_value="CHAVE_CTE_ORIGINAL",
                actual_value="VAZIO",
                difference=0,
                details={"erro": "CT-e anulação sem referência ao CT-e original (refCTe obrigatório)"}
            )]
        
        # Verificar se CT-e original existe e não está anulado
        cte_original = self.get_cte_by_chave(context.refCTe)
        if not cte_original:
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value="CTE_EXISTENTE",
                actual_value="CTE_NAO_ENCONTRADO",
                difference=0,
                details={"refCTe": context.refCTe, "erro": "CT-e original não encontrado na base"}
            )]
        
        if cte_original.status == "ANULADO":
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value="CTE_ATIVO",
                actual_value="CTE_JA_ANULADO",
                difference=0,
                details={"refCTe": context.refCTe, "erro": "Dupla anulação detectada"}
            )]
        
        return []
```

---

## 🔍 Regra CTE_SUBSTITUICAO (tpEmis=2) - HIGH

### Quando Dispara
- CT-e substituição **SEM refCTe**
- CT-e original **já substituído** (não pode substituir substituição)
- Valores do substituto **não conferem** com correção alegada
- Substituição para **aumentar ICMS** sem justificativa

### Validação Obrigatória
```xml
<infCte>
  <ide>
    <tpEmis>2</tpEmis>                    <!-- Substituição -->
    <refCTe>35250101234567890123550010000000011234567890</refCTe>
  </ide>
  <!-- Dados corrigidos -->
  <infCTeNorm>
    <vPrest><vTPrest>5500.00</vTPrest></vPrest>  <!-- Valor corrigido -->
    <infCarga><proPred><peso>11000.000</peso></proPred></infCarga>  <!-- Peso corrigido -->
  </infCTeNorm>
</infCte>
```

### Lógica no Engine
```python
class CteSubstituicaoRule(BaseRule):
    code = "CTE_SUBSTITUICAO"
    relevance_tags = {"cte_complementar"}
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        if context.tpEmis != "2":
            return []
        
        if not context.refCTe:
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value="CHAVE_CTE_ORIGINAL",
                actual_value="VAZIO",
                difference=0,
                details={"erro": "CT-e substituição sem refCTe"}
            )]
        
        cte_original = self.get_cte_by_chave(context.refCTe)
        if not cte_original:
            return [Discrepancy(...)]  # CTe original não existe
        
        if cte_original.status == "SUBSTITUIDO":
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "CT-e original já foi substituído anteriormente"}
            )]
        
        # Verificar se substituição faz sentido (valor/peso corrigido)
        # Não pode ser usado para "esconder" erro original
        return []
```

---

## 🔍 Regra CTE_COMPLEMENTO_VALOR (tpEmis=4) - MEDIUM

### Quando Dispara
- CT-e complemento **SEM refCTe**
- Valor complementar **negativo** (não permitido)
- Complemento de ICMS sem base legal (diferença alíquota)
- Complemento de frete **acima do contratado** sem aditivo

### Validação Obrigatória
```xml
<infCte>
  <ide>
    <tpEmis>4</tpEmis>                    <!-- Complemento -->
    <refCTe>35250101234567890123550010000000011234567890</refCTe>
  </ide>
  <infCTeComp>
    <vCarga>500.00</vCarga>               <!-- Valor complementar frete -->
    <vICMS>50.00</vICMS>                  <!-- ICMS complementar -->
  </infCTeComp>
</infCte>
```

### Lógica no Engine
```python
class CteComplementoValorRule(BaseRule):
    code = "CTE_COMPLEMENTO_VALOR"
    relevance_tags = {"cte_complementar"}
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        if context.tpEmis != "4":
            return []
        
        if not context.refCTe:
            return [Discrepancy(...)]
        
        cte_original = self.get_cte_by_chave(context.refCTe)
        if not cte_original:
            return [Discrepancy(...)]
        
        # Complemento não pode ser negativo
        if (context.vCargaComp or 0) < 0 or (context.vICMSComp or 0) < 0:
            return [Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={"erro": "Valor complementar não pode ser negativo"}
            )]
        
        # Verificar se complemento de frete tem aditivo contratual
        if context.vCargaComp and context.vCargaComp > 0:
            if not context.tem_aditivo_contratual:
                return [Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={"erro": "Complemento de frete sem aditivo contratual", 
                             "valor_complemento": context.vCargaComp}
                )]
        
        return []
```

---

## 🧪 Casos de Teste

```python
# test_cte_anulacao_without_ref (CRÍTICO)
# CT-e tpEmis=3 sem refCTe → DIVERGÊNCIA CRITICAL

# test_cte_anulacao_dupla
# Anular CT-e já anulado → DIVERGÊNCIA HIGH

# test_cte_substituicao_sem_ref
# CT-e tpEmis=2 sem refCTe → DIVERGÊNCIA HIGH

# test_cte_substituicao_ja_substituido
# Substituir CT-e já substituído → DIVERGÊNCIA HIGH

# test_cte_complemento_valor_negativo
# Complemento com valor negativo → DIVERGÊNCIA MEDIUM

# test_cte_complemento_sem_aditivo
# Complemento frete > 0 sem aditivo → DIVERGÊNCIA MEDIUM
```

---

## ⚠️ Pontos Críticos

1. **refCTe é OBRIGATÓRIO** para todos os 3 tipos (2, 3, 4)
2. **Cadeia:** Original → Substituição (tpEmis=2) → **NÃO PODE** ter outra substituição
3. **Anulação (3)** finaliza o ciclo - não pode ter complemento após anulação
4. **Complemento (4)** só soma - não substitui nem anula
5. **Chave de acesso:** 44 dígitos, validar dígito verificador (mod 11)
6. **Prazo:** Não há prazo legal fixo, mas recomenda-se < 30 dias

---

## 📦 JSON para backend/app/data/cte_complementar_regras.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Decreto 9.209/2017, Manual CT-e 3.00",
  "tipos_complementar": {
    "2": {"nome": "Substituição", "severidade": "HIGH", "permite_multiplos": false},
    "3": {"nome": "Anulação", "severidade": "CRITICAL", "permite_multiplos": false},
    "4": {"nome": "Complemento de Valor", "severidade": "MEDIUM", "permite_multiplos": true}
  },
  "validacoes_obrigatorias": {
    "refCTe_obrigatorio": true,
    "refCTe_deve_existir": true,
    "refCTe_nao_pode_estar_anulado": true,
    "substituicao_apenas_uma_vez": true,
    "complemento_valor_nao_negativo": true,
    "complemento_frete_requer_aditivo": true
  }
}
```

---

## 🔗 Referências

- [Manual CT-e 3.00 - Receita Federal](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Decreto 9.209/2017](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/decreto/D9209.htm)
- [Convênio ICMS 188/2017](https://www.confaz.fazenda.gov.br/legislacao/convenios/2017/convenio-icms-188-2017)

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Conforme atualização Manual CT-e