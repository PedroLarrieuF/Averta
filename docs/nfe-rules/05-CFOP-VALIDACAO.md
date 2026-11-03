# CFOP Validação para Operações com Frete - Regras NFE_CFOP_FRETE, NFE_CFOP_INTERSTADUAL

**Rule Codes:** `NFE_CFOP_FRETE`, `NFE_CFOP_INTERSTADUAL`  
**Tipo:** `CFOP_VALIDATION`  
**Severidade:** `HIGH` / `HIGH`  
**Tags:** `cfop, freight, interstate, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/cfop_tabela.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_cfop_frete_valido`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Convênio ICMS 52/2017** | Tabela CFOP atualizada | Vigente |
| **Ajuste SINIEF 07/2005** | CFOP na NF-e | Vigente |
| **RICMS/UF** | CFOP por operação estadual | Vigente |
| **Manual NF-e 4.00** | Campo CFOP no XML | Vigente |

---

## 🎯 CFOP (Código Fiscal de Operações e Prestações)

O CFOP identifica a **natureza da operação** e determina:
- Tipo de tributação (ICMS, IPI, PIS/COFINS)
- Se há frete envolvido
- Se é interestadual/intermunicipal
- Se gera CT-e obrigatório

---

## 📋 CFOP Principais para Frete (Entrada/Saída)

### Vendas com Frete (Gera CT-e Obrigatório)

| CFOP | Descrição | Frete | modFrete | Gera CT-e? | Interestadual? |
|------|-----------|-------|----------|------------|----------------|
| **5.352** | Venda produção estabelecimento c/ frete por conta emitente | Conta emitente | 0 | **SIM** | Não (interna) |
| **5.353** | Venda produção estabelecimento c/ frete por conta destinatário | Conta destinatário | 1 | **SIM** | Não (interna) |
| **5.354** | Venda produção estabelecimento c/ frete por conta terceiros | Conta terceiros | 2/3/9 | **SIM** | Não (interna) |
| **6.352** | Venda produção estabelecimento c/ frete por conta emitente | Conta emitente | 0 | **SIM** | **SIM** |
| **6.353** | Venda produção estabelecimento c/ frete por conta destinatário | Conta destinatário | 1 | **SIM** | **SIM** |
| **6.354** | Venda produção estabelecimento c/ frete por conta terceiros | Conta terceiros | 2/3/9 | **SIM** | **SIM** |

### Vendas SEM Frete (NÃO Gera CT-e)

| CFOP | Descrição | Frete | Gera CT-e? |
|------|-----------|-------|------------|
| **5.355** | Venda produção estabelecimento sem frete | Sem frete | **NÃO** |
| **6.355** | Venda produção estabelecimento sem frete | Sem frete | **NÃO** |

### Devoluções (Podem Gerar CT-e)

| CFOP | Descrição | Gera CT-e? |
|------|-----------|------------|
| **1.202** | Devolução venda produção (interna) | Se houver frete |
| **2.202** | Devolução venda produção (interestadual) | Se houver frete |
| **1.411** | Devolução compra p/ industrialização (interna) | Se houver frete |
| **2.411** | Devolução compra p/ industrialização (interestadual) | Se houver frete |
| **5.202** | Devolução venda mercadoria adquirida (interna) | Se houver frete |
| **6.202** | Devolução venda mercadoria adquirida (interestadual) | Se houver frete |

### Simples Nacional (CFOP Específicos)

| CFOP | Descrição | Regime |
|------|-----------|--------|
| **5.101 a 5.119** | Operações internas Simples | Simples Nacional |
| **6.101 a 6.119** | Operações interestaduais Simples | Simples Nacional |

### Transferências/Bonificações

| CFOP | Descrição | Gera CT-e? |
|------|-----------|------------|
| **5.152** | Transferência estabelecimento mesmo titular (interna) | Se houver frete |
| **6.152** | Transferência estabelecimento mesmo titular (interestadual) | Se houver frete |
| **5.910** | Bonificação (interna) | Se houver frete |
| **6.910** | Bonificação (interestadual) | Se houver frete |

---

## 🔍 Estrutura CFOP (4 Dígitos)

```
C F O P
│ │ └─┬─ Prestação (00-99)
│ └───┬─── Operação (0-9)
└──────── Tipo (1-7)
```

| 1º Dígito (Tipo) | Significado |
|------------------|-------------|
| **1** | Entrada interestadual |
| **2** | Saída interestadual |
| **3** | Entrada intermunicipal |
| **4** | Saída intermunicipal |
| **5** | Entrada interna (mesmo estado) |
| **6** | Saída interna (mesmo estado) |
| **7** | Operações com exterior |

| 2º Dígito (Operação) | Significado |
|---------------------|-------------|
| **1** | Venda de produção do estabelecimento |
| **2** | Venda de mercadoria adquirida de terceiros |
| **3** | Entrada de mercadoria (compra) |
| **4** | Entrada p/ industrialização |
| **5** | Transferência |
| **9** | Outras operações |

---

## 🔍 Lógica de Detecção no Engine

```python
class NFECFOPFreteRule(BaseRule):
    code = "NFE_CFOP_FRETE"
    relevance_tags = {"cfop", "freight", "nfe"}
    
    # CFOP que OBRIGATORIAMENTE têm frete (devem ter CT-e)
    CFOPS_COM_FRETE_OBRIGATORIO = {
        "5352", "5353", "5354",  # Internas
        "6352", "6353", "6354",  # Interestaduais
        "1202", "2202", "1411", "2411", "5202", "6202",  # Devoluções c/ frete
        "5152", "6152", "5910", "6910"  # Transferências/Bonificações c/ frete
    }
    
    # CFOP que NÃO têm frete (não devem ter CT-e)
    CFOPS_SEM_FRETE = {
        "5355", "6355",  # Vendas sem frete
        "5101", "5102", "5103", "5104", "5105", "5106", "5107", "5108", "5109",
        "5110", "5111", "5112", "5113", "5114", "5115", "5116", "5117", "5118", "5119",
        "6101", "6102", "6103", "6104", "6105", "6106", "6107", "6108", "6109",
        "6110", "6111", "6112", "6113", "6114", "6115", "6116", "6117", "6118", "6119"
    }
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.cfop is not None
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        cfop = str(context.cfop).zfill(4)
        
        # 1. CFOP com frete obrigatório mas vFrete = 0
        if cfop in self.CFOPS_COM_FRETE_OBRIGATORIO:
            if context.vFrete <= 0:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CFOP_COM_FRETE_SEM_VFRETE",
                        "cfop": cfop,
                        "descricao": self.get_cfop_descricao(cfop),
                        "vFrete": context.vFrete,
                        "modFrete": context.modFrete,
                        "risco": "CFOP indica frete mas vFrete não destacado na NF-e"
                    }
                ))
            
            # Verificar se tem CT-e correspondente (cross-validation)
            if not context.tem_cte_correspondente:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CFOP_FRETE_SEM_CTE",
                        "cfop": cfop,
                        "risco": "Operação com frete sem CT-e emitido"
                    }
                ))
        
        # 2. CFOP sem frete mas vFrete > 0
        if cfop in self.CFOPS_SEM_FRETE:
            if context.vFrete > 0:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "CFOP_SEM_FRETE_COM_VFRETE",
                        "cfop": cfop,
                        "vFrete": context.vFrete,
                        "risco": "CFOP não prevê frete mas vFrete destacado"
                    }
                ))
        
        # 3. Validar CFOP x modFrete
        if not self.cfop_modfrete_compativel(cfop, context.modFrete):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "validacao": "CFOP_MODFRETE_INCOMPATIVEL",
                    "cfop": cfop,
                    "modFrete": context.modFrete,
                    "esperado": self.get_modfrete_esperado(cfop)
                }
            ))
        
        # 4. Validar CFOP x UF (interno vs interestadual)
        if not self.cfop_uf_compativel(cfop, context.uf_emitente, context.uf_destino):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "validacao": "CFOP_UF_INCOMPATIVEL",
                    "cfop": cfop,
                    "uf_emitente": context.uf_emitente,
                    "uf_destino": context.uf_destino,
                    "tipo_esperado": "interestadual" if cfop.startswith(("1","2","6")) else "interna"
                }
            ))
        
        return discrepancies
    
    def cfop_modfrete_compativel(self, cfop, modfrete):
        """Valida compatibilidade CFOP x modFrete"""
        if cfop in ["5352", "6352"]:  # Frete conta emitente
            return modfrete == "0"
        elif cfop in ["5353", "6353"]:  # Frete conta destinatário
            return modfrete == "1"
        elif cfop in ["5354", "6354"]:  # Frete conta terceiros
            return modfrete in ["2", "3", "9"]
        elif cfop in ["5355", "6355"]:  # Sem frete
            return modfrete == "9"
        return True  # Outros CFOP - não validar modFrete
    
    def get_modfrete_esperado(self, cfop):
        mapa = {
            "5352": "0", "6352": "0",
            "5353": "1", "6353": "1",
            "5354": "2/3/9", "6354": "2/3/9",
            "5355": "9", "6355": "9"
        }
        return mapa.get(cfop, "Não definido")
    
    def cfop_uf_compativel(self, cfop, uf_emit, uf_dest):
        """Valida se CFOP condiz com UF origem/destino"""
        primeiro_digito = cfop[0]
        
        if primeiro_digito in ["1", "2", "6"]:  # Interestadual
            return uf_emit != uf_dest
        elif primeiro_digito in ["5"]:  # Interna (saída)
            return uf_emit == uf_dest
        return True


class NFECFOPInterestadualRule(BaseRule):
    code = "NFE_CFOP_INTERSTADUAL"
    relevance_tags = {"cfop", "interstate", "nfe"}
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        cfop = str(context.cfop).zfill(4)
        
        # Verificar se CFOP interestadual bate com UF diferentes
        if cfop.startswith(("1", "2", "6")):  # Interestadual
            if context.uf_emitente == context.uf_destino:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CFOP_INTERESTADUAL_MESMA_UF",
                        "cfop": cfop,
                        "uf_emitente": context.uf_emitente,
                        "uf_destino": context.uf_destino,
                        "risco": "CFOP interestadual mas UF origem = UF destino"
                    }
                ))
        
        # Verificar se CFOP interno bate com UF iguais
        if cfop.startswith("5"):  # Saída interna
            if context.uf_emitente != context.uf_destino:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CFOP_INTERNO_UF_DIFERENTES",
                        "cfop": cfop,
                        "uf_emitente": context.uf_emitente,
                        "uf_destino": context.uf_destino,
                        "risco": "CFOP interno mas UF origem ≠ UF destino"
                    }
                ))
        
        return discrepancies
```

---

## 🧮 Exemplos Práticos

### Exemplo 1: Venda Interna SP, Frete Emitente
```
CFOP: 5352
modFrete: 0 (conta emitente)
UF Emitente: SP
UF Destino: SP
vFrete: 500,00
CT-e: OBRIGATÓRIO
✓ VÁLIDO
```

### Exemplo 2: Venda Interestadual SP→RJ, Frete Destinatário
```
CFOP: 6353
modFrete: 1 (conta destinatário)
UF Emitente: SP
UF Destino: RJ
vFrete: 500,00
CT-e: OBRIGATÓRIO
✓ VÁLIDO
```

### Exemplo 3: CFOP 5352 mas modFrete=1 (INCOMPATÍVEL)
```
CFOP: 5352 (frete emitente)
modFrete: 1 (frete destinatário)
→ DIVERGÊNCIA MEDIUM: CFOP_MODFRETE_INCOMPATIVEL
```

### Exemplo 4: CFOP 6352 mas UF iguais (INCOMPATÍVEL)
```
CFOP: 6352 (interestadual)
UF Emitente: SP
UF Destino: SP
→ DIVERGÊNCIA HIGH: CFOP_INTERESTADUAL_MESMA_UF
```

### Exemplo 5: CFOP 5355 (sem frete) mas vFrete > 0
```
CFOP: 5355
vFrete: 300,00
→ DIVERGÊNCIA MEDIUM: CFOP_SEM_FRETE_COM_VFRETE
```

---

## 🧪 Casos de Teste

```python
# test_nfe_cfop_frete_valido_5352
# CFOP 5352, modFrete=0, vFrete=500, UF iguais → OK

# test_nfe_cfop_frete_valido_6353
# CFOP 6353, modFrete=1, vFrete=500, UF diferentes → OK

# test_nfe_cfop_frete_sem_vfrete
# CFOP 5352, vFrete=0 → HIGH

# test_nfe_cfop_sem_frete_com_vfrete
# CFOP 5355, vFrete=300 → MEDIUM

# test_nfe_cfop_modfrete_incompativel
# CFOP 5352, modFrete=1 → MEDIUM

# test_nfe_cfop_interstadual_mesma_uf
# CFOP 6352, UF SP→SP → HIGH

# test_nfe_cfop_interno_uf_diferentes
# CFOP 5352, UF SP→RJ → HIGH

# test_nfe_cfop_devolucao_com_frete
# CFOP 2202, vFrete>0, tem CT-e → OK

# test_nfe_cfop_simples_nacional
# CFOP 5101, regime Simples → validar CSOSN não CST
```

---

## ⚠️ Pontos de Atenção

1. **CFOP 5.352/3/4 e 6.352/3/4** = **SEMPRE** geram CT-e obrigatório
2. **CFOP 5.355/6.355** = **NUNCA** geram CT-e (sem frete)
3. **modFrete DEVE coincidir** com CFOP de frete
4. **CFOP interestadual (1,2,6)** ↔ **UF Origem ≠ UF Destino**
5. **CFOP interno (5)** ↔ **UF Origem = UF Destino**
6. **Devoluções (1202, 2202, etc.)** podem ter frete e CT-e
7. **Simples Nacional** usa CFOP 5.101-5.119 / 6.101-6.119
8. **Cross-validation**: CFOP com frete → deve ter CT-e (ver 14-CROSS-CTE-NFE.md)

---

## 📦 JSON para backend/app/data/nfe/cfop_tabela.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Convênio ICMS 52/2017, Ajuste SINIEF 07/2005",
  "cfops_com_frete_obrigatorio": {
    "5352": {"desc": "Venda prod. estab. c/ frete emitente (interna)", "modfrete": "0", "interestadual": false, "gera_cte": true},
    "5353": {"desc": "Venda prod. estab. c/ frete destinatário (interna)", "modfrete": "1", "interestadual": false, "gera_cte": true},
    "5354": {"desc": "Venda prod. estab. c/ frete terceiros (interna)", "modfrete": "2/3/9", "interestadual": false, "gera_cte": true},
    "6352": {"desc": "Venda prod. estab. c/ frete emitente (interstadual)", "modfrete": "0", "interestadual": true, "gera_cte": true},
    "6353": {"desc": "Venda prod. estab. c/ frete destinatário (interstadual)", "modfrete": "1", "interestadual": true, "gera_cte": true},
    "6354": {"desc": "Venda prod. estab. c/ frete terceiros (interstadual)", "modfrete": "2/3/9", "interestadual": true, "gera_cte": true},
    "1202": {"desc": "Devolução venda prod. (interstadual)", "modfrete": "variavel", "interestadual": true, "gera_cte": "se_tiver_frete"},
    "2202": {"desc": "Devolução venda prod. (interna)", "modfrete": "variavel", "interestadual": false, "gera_cte": "se_tiver_frete"},
    "5152": {"desc": "Transferência mesmo titular (interna)", "modfrete": "variavel", "interestadual": false, "gera_cte": "se_tiver_frete"},
    "6152": {"desc": "Transferência mesmo titular (interstadual)", "modfrete": "variavel", "interestadual": true, "gera_cte": "se_tiver_frete"},
    "5910": {"desc": "Bonificação (interna)", "modfrete": "variavel", "interestadual": false, "gera_cte": "se_tiver_frete"},
    "6910": {"desc": "Bonificação (interstadual)", "modfrete": "variavel", "interestadual": true, "gera_cte": "se_tiver_frete"}
  },
  "cfops_sem_frete": {
    "5355": {"desc": "Venda prod. estab. sem frete (interna)", "modfrete": "9", "interestadual": false, "gera_cte": false},
    "6355": {"desc": "Venda prod. estab. sem frete (interstadual)", "modfrete": "9", "interestadual": true, "gera_cte": false}
  },
  "cfops_simples_nacional": {
    "prefixos": ["510", "511", "610", "611"],
    "faixa": "5101-5119, 6101-6119",
    "regime": "SIMPLES_NACIONAL"
  },
  "estrutura_cfop": {
    "digito_1_tipo": {"1": "entrada_interstadual", "2": "saida_interstadual", "5": "saida_interna", "6": "saida_interna_interstadual"},
    "digito_2_operacao": {"1": "venda_producao", "2": "venda_adquirida", "3": "entrada_compra", "5": "transferencia", "9": "outras"}
  }
}
```

---

## 🔗 Referências

- [Convênio ICMS 52/2017 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2017/convenio-icms-52-2017)
- [Tabela CFOP Completa - Portal NF-e](https://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=P2V5c0lHVnliRzlJYjI1MWMyVnlkRzl5)
- [Manual NF-e 4.00 - CFOP](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Conforme atualização Convênio ICMS 52