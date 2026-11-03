# Frete na Base de Cálculo do ICMS - Regra NFE_FRETE_NA_BASE

**Rule Code:** `NFE_FRETE_NA_BASE`  
**Tipo:** `FREIGHT_IN_BASE`  
**Severidade:** `CRITICAL`  
**Tags:** `freight, icms_base, nfe, lei_8884`  
**Arquivo de Dados:** `backend/app/data/nfe/frete_base_icms.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_frete_na_base_cst00`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 8.884/1994** (Art. 37) | Frete integra base cálculo ICMS | Vigente |
| **LC 87/1996** (Art. 2º, §2º) | Base cálculo inclui frete interestadual | Vigente |
| **RICMS/SP** (Art. 66) | Base cálculo ICMS - frete incluso | Vigente |
| **STF - RE 593.849** | Frete na base cálculo - constitucionalidade | Julgado |
| **Ajuste SINIEF 19/2016** | Campo vFrete na NF-e 4.00 | Vigente |
| **Manual NF-e 4.00** | vFrete destacado compõe vBC | 2024+ |

---

## 🎯 Regra Fundamental

> **Art. 37, Lei 8.884/94**: "A base de cálculo do ICMS é o valor da operação, **entendido este como o valor total da nota fiscal**, compreendendo o valor das mercadorias, **o frete, o seguro e demais despesas acessórias** cobradas ou debitadas ao adquirente."

**Em resumo:** Se o frete é **destacado na NF-e** (campo `<vFrete>` preenchido), ele **DEVE** integrar a base de cálculo do ICMS (vBC).

---

## 📊 CSTs que EXIGEM Frete na Base

| CST | Descrição | Frete na Base? | Base Legal |
|-----|-----------|----------------|------------|
| **00** | Tributada integralmente | **SIM** | Lei 8.884/94 Art. 37 |
| **10** | Tributada c/ ST | **SIM** | Lei 8.884/94 Art. 37 |
| **20** | Redução base | **SIM** | Lei 8.884/94 Art. 37 |
| **30** | Isenta/não trib c/ ST | **SIM** | Lei 8.884/94 Art. 37 |
| **40** | Isenta | **NÃO** | Isenção total |
| **41** | Não tributada | **NÃO** | Não incidência |
| **50** | Suspensão | **NÃO** | Suspensão (ex: exportação) |
| **51** | Diferimento | **NÃO** | Diferimento |
| **60** | ICMS ant. por ST | **SIM** | ST recolhido na origem |
| **70** | Redução base + ST | **SIM** | Lei 8.884/94 Art. 37 |
| **90** | Outras | **CONFORME** | Legislação específica |

### CSOSN (Simples Nacional)
| CSOSN | Frete na Base? |
|-------|----------------|
| 101, 102, 201, 202 | **SIM** (tributada pelo Simples) |
| 103, 300, 400 | **NÃO** (isenta/imune/não trib) |
| 500, 900 | **CONFORME** legislação |

---

## 🧮 Fórmula da Base de Cálculo (vBC)

```
vBC = vNF + vFrete + vSeg + vOutro - vDesc

ONDE:
- vNF = Valor total dos produtos (vProd)
- vFrete = Valor do frete destacado na NF-e
- vSeg = Valor do seguro destacado na NF-e
- vOutro = Outras despesas acessórias destacadas
- vDesc = Desconto incondicionado destacado
```

> **IMPORTANTE**: vNF **JÁ INCLUI** vFrete, vSeg, vOutro, vDesc!
> 
> Na NF-e: `vNF = vProd + vFrete + vSeg + vDesc + vOutro + impostos...`
> 
> Mas para **Base ICMS**: usa-se a fórmula acima (sem impostos)

---

## 🚨 Cenários de Frete

### 1. Frete por Conta do Emitente (modFrete = 0)
```
- Emitente contrata e paga frete
- vFrete DEVE ser destacado na NF-e
- vFrete INTEGRA base ICMS (vBC)
- CST 00/10/20/30/60/70/90: SIM
```

### 2. Frete por Conta do Destinatário (modFrete = 1)
```
- Destinatário contrata e paga frete
- Se frete DESTACADO na NF-e (vFrete > 0): INTEGRA base ICMS
- Se frete NÃO destacado (vFrete = 0): NÃO integra base ICMS
- CST 00/10/20/30/60/70/90: SIM se destacado
```

### 3. Frete por Conta de Terceiros (modFrete = 2/3/9)
```
- Terceiro paga frete
- Mesmo critério: se destacado na NF-e, integra base
```

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEFreteNaBaseRule(BaseRule):
    code = "NFE_FRETE_NA_BASE"
    relevance_tags = {"freight", "icms_base", "nfe", "lei_8884"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        # Só se há frete destacado
        if context.vFrete <= 0:
            return False
        # Só CSTs que exigem frete na base
        csts_com_frete = {"00", "10", "20", "30", "60", "70", "90"}
        csosns_com_frete = {"101", "102", "201", "202"}
        return (context.cst_icms in csts_com_frete or 
                context.csosn_icms in csosns_com_frete)
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # Calcular base ESPERADA com frete
        vBC_esperada = (context.vNF + context.vFrete + context.vSeg + 
                       context.vOutro - context.vDesc)
        
        # Aplicar redução se CST 20/70
        if context.cst_icms in ["20", "70"]:
            pRedBC = self.get_percentual_reducao(context.ncm, context.uf_emitente)
            vBC_esperada = vBC_esperada * (1 - pRedBC)
        
        # Comparar com vBC informado na NF-e
        diferenca = abs(context.vBC - vBC_esperada)
        tolerancia = context.vNF * 0.001  # 0.1%
        
        if diferenca > tolerancia:
            # Verificar se a diferença é exatamente o frete (erro comum)
            diff_frete = abs(diferenca - context.vFrete)
            if diff_frete < tolerancia:
                erro_tipo = "FRETE_NAO_INCLUIDO_NA_BASE"
                severidade = "CRITICAL"
                detalhe = "Frete destacado na NF-e NÃO incluído na base de cálculo ICMS (vBC)"
            else:
                erro_tipo = "BASE_CALCULO_INCORRETA"
                severidade = "HIGH"
                detalhe = "Base cálculo ICMS (vBC) não confere com fórmula legal"
            
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity=severidade,
                expected_value=round(vBC_esperada, 2),
                actual_value=round(context.vBC, 2),
                difference=round(diferenca, 2),
                details={
                    "erro_tipo": erro_tipo,
                    "campo": "vBC",
                    "cst": context.cst_icms,
                    "csosn": context.csosn_icms,
                    "vFrete": context.vFrete,
                    "vSeg": context.vSeg,
                    "vOutro": context.vOutro,
                    "vDesc": context.vDesc,
                    "formula_esperada": "vNF + vFrete + vSeg + vOutro - vDesc" + 
                                      (" * (1 - pRedBC)" if context.cst_icms in ["20", "70"] else ""),
                    "base_legal": "Lei 8.884/94 Art. 37, LC 87/96 Art. 2º §2º",
                    "detalhe": detalhe
                }
            ))
        
        return discrepancies
```

---

## 🧮 Exemplos Práticos

### Exemplo 1: CST 00, Frete Emitente (modFrete=0)
```
NF-e:
- vProd: 10.000,00
- vFrete: 500,00 (destacado)
- vSeg: 100,00
- vOutro: 50,00
- vDesc: 0,00
- vNF: 10.650,00 (já inclui frete+seguro+outros)
- CST: 00
- vBC informado: 10.150,00  ❌ ERRO! (esqueceu frete)
- vBC correto: 10.650,00
- Diferença: 500,00 = exatamente o frete!
```

### Exemplo 2: CST 00, Frete Destinatário (modFrete=1) COM destaque
```
- vFrete: 500,00 (destacado na NF-e pelo emitente)
- Mesmo tratamento: INTEGRA base
- vBC = 10.650,00
```

### Exemplo 3: CST 00, Frete Destinatário (modFrete=1) SEM destaque
```
- vFrete: 0,00 (não destacado na NF-e)
- Frete pago direto pelo destinatário ao transportador
- NÃO integra base ICMS
- vBC = vNF + vSeg + vOutro - vDesc = 10.150,00
- ✓ CORRETO
```

### Exemplo 4: CST 20 (Redução 40%), com Frete
```
- vNF: 10.000,00
- vFrete: 500,00
- vSeg: 100,00
- vOutro: 50,00
- vDesc: 0,00
- CST: 20 (Redução 40% - ex: leite)
- pRedBC: 40% = 0,40

vBC sem redução = 10.650,00
vBC com redução = 10.650 × (1 - 0,40) = 6.390,00
```

### Exemplo 5: CST 40 (Isenta) - Frete NÃO integra base
```
- vNF: 10.000,00
- vFrete: 500,00 (destacado)
- CST: 40 (Isenta)
- vBC: 0,00
- vICMS: 0,00
- ✓ CORRETO - Isenção total, base zero
```

---

## 🧪 Casos de Teste

```python
# test_nfe_frete_na_base_cst00
# CST 00, vFrete=500, vBC informado=10150 (sem frete) → CRITICAL

# test_nfe_frete_na_base_cst10
# CST 10, vFrete=500, vBC sem frete → CRITICAL

# test_nfe_frete_na_base_cst20_reducao
# CST 20, redução 40%, vFrete=500 → vBC = (vNF+frete+...)*(1-0.4)

# test_nfe_frete_na_base_cst40_isenta
# CST 40, vFrete=500, vBC=0 → OK (isenta)

# test_nfe_frete_na_base_modfrete1_com_destaque
# modFrete=1, vFrete>0 destacado → INTEGRA base

# test_nfe_frete_na_base_modfrete1_sem_destaque
# modFrete=1, vFrete=0 → NÃO integra base (OK)

# test_nfe_frete_na_base_cst60_st_retido
# CST 60, vFrete=500 → INTEGRA base ST também

# test_nfe_frete_na_base_csosn101_simples
# Simples CSOSN 101, vFrete=500 → INTEGRA base

# test_nfe_frete_na_base_seguro_outros
# vSeg=100, vOutro=50 também devem integrar base
```

---

## ⚠️ Pontos Críticos para Auditoria de Frete

1. **Erro #1 mais comum**: Emitente destaca vFrete na NF-e mas **NÃO inclui no vBC**
   - Diferença = exatamente o valor do frete
   - Recuperação = alíquota ICMS × vFrete

2. **modFrete ≠ Integração na Base**
   - modFrete=0 (emitente): SEMPRE integra se destacado
   - modFrete=1 (destinatário): INTEGRA **SE DESTACADO** na NF-e
   - modFrete=2/3/9 (terceiros): INTEGRA **SE DESTACADO**

3. **Seguro e Outras Despesas**: Mesmo tratamento do frete (vSeg, vOutro)

4. **Desconto (vDesc)**: **REDUZ** a base (subtraído)

5. **CST 40/41/50/51**: Base = 0 (isenção/suspensão) - frete não integra

6. **ST (CST 10/30/60/70)**: Frete integra **TANTO** base ICMS próprio **QUANTO** base ST

7. **Simples Nacional**: CSOSN 101/102/201/202 - frete integra base

---

## 📦 JSON para backend/app/data/nfe/frete_base_icms.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Lei 8.884/94 Art. 37, LC 87/96, RICMS/UF, STF RE 593.849",
  "csts_frete_integra_base": [
    "00", "10", "20", "30", "60", "70", "90"
  ],
  "csts_frete_NAO_integra_base": [
    "40", "41", "50", "51"
  ],
  "csosns_frete_integra_base": [
    "101", "102", "201", "202"
  ],
  "csosns_frete_NAO_integra_base": [
    "103", "300", "400"
  ],
  "modfrete_regras": {
    "0": {"descricao": "Por conta emitente", "integra_se_destacado": true, "sempre_destaca": true},
    "1": {"descricao": "Por conta destinatário", "integra_se_destacado": true, "sempre_destaca": false},
    "2": {"descricao": "Por conta terceiros", "integra_se_destacado": true, "sempre_destaca": false},
    "3": {"descricao": "Próprio por conta remetente", "integra_se_destacado": true, "sempre_destaca": false},
    "9": {"descricao": "Sem frete", "integra_se_destacado": false, "sempre_destaca": false}
  },
  "campos_que_integram_base": [
    "vFrete",
    "vSeg",
    "vOutro"
  ],
  "campos_que_reduzem_base": [
    "vDesc"
  ],
  "formula_base": "vNF + vFrete + vSeg + vOutro - vDesc",
  "observacoes": "Frete destacado na NF-e (vFrete > 0) SEMPRE integra base ICMS para CSTs tributados. Lei 8.884/94 Art. 37 é federal e vale para todos os estados."
}
```

---

## 🔗 Referências

- [Lei 8.884/1994 Art. 37 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/L8884.htm)
- [LC 87/1996 - Planalto](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm)
- [STF RE 593.849 - Frete na base](https://portal.stf.jus.br/processos/detalhe.asp?incidente=3821071)
- [Manual NF-e 4.00 - vFrete](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Conforme jurisprudência STF/STJ