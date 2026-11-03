# Regimes Especiais (Simples, ZFM, Isenções) - Regra NFE_REGIME_ESPECIAL

**Rule Code:** `NFE_REGIME_ESPECIAL`  
**Tipo:** `SPECIAL_REGIME`  
**Severidade:** `MEDIUM`  
**Tags:** `simples, zfm, special_regime, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/regimes_especiais.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_simples_nacional_csosn`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **LC 123/2006** | Simples Nacional | Vigente |
| **LC 147/2014** | Alterações Simples Nacional | Vigente |
| **Decreto 6.759/2009** | ZFM - Zona Franca Manaus | Vigente |
| **Convênio ICMS 38/2001** | Isenções/Imunidades | Vigente |
| **RICMS/UF** | Regimes especiais estaduais | Vigente |

---

## 🎯 Simples Nacional (LC 123/2006)

### Características
- **Regime unificado** de tributação federal + estadual + municipal
- **DAS** (Documento de Arrecadação do Simples) - guia única
- **Alíquotas progressivas** por faixa de receita bruta (12 meses)
- **ICMS incluso** no DAS - **NÃO** destaca ICMS na NF-e

### CSOSN (CST Simples Nacional) - Obrigatório

| CSOSN | Descrição | Crédito ICMS | ST | Quando Usa |
|-------|-----------|--------------|----|------------|
| **101** | Tributada pelo Simples c/ permissão crédito | **SIM** | Não | Regra geral |
| **102** | Tributada pelo Simples s/ permissão crédito | **NÃO** | Não | Atividades vedadas crédito |
| **103** | Isenção ICMS faixa receita | NÃO | Não | Receita até limite |
| **201** | Tributada Simples c/ crédito + ST | **SIM** | **SIM** | Produto com ST |
| **202** | Tributada Simples s/ crédito + ST | **NÃO** | **SIM** | Produto com ST |
| **203** | Isenção ICMS + ST | NÃO | **SIM** | Isento mas ST |
| **300** | Imune | NÃO | Não | Imunidade constitucional |
| **400** | Não tributada pelo Simples | NÃO | Não | Fora Simples |
| **500** | ICMS cobrado anterior por ST (Simples) | NÃO | **SIM** | Substituição |
| **900** | Outras | Conforme | Conforme | Casos especiais |

### Regras NF-e Simples Nacional

```python
class NFESimplesNacionalRule(BaseRule):
    code = "NFE_REGIME_ESPECIAL"
    relevance_tags = {"simples", "special_regime", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.regime_tributario == "SIMPLES_NACIONAL"
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. Deve usar CSOSN, NÃO CST
        if context.cst_icms and context.cst_icms != "90":
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "erro": "Simples Nacional deve usar CSOSN, não CST",
                    "cst": context.cst_icms,
                    "csosn": context.csosn_icms
                }
            ))
        
        # 2. CSOSN obrigatório
        if not context.csosn_icms:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "CSOSN obrigatório para Simples Nacional"}
            ))
        
        # 3. CSOSN válido
        csosns_validos = {"101", "102", "103", "201", "202", "203", "300", "400", "500", "900"}
        if context.csosn_icms not in csosns_validos:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": f"CSOSN {context.csosn_icms} inválido para Simples"}
            ))
        
        # 4. ICMS NÃO destacado na NF-e (exceto ST)
        if context.csosn_icms in ["101", "102", "103", "300", "400"]:
            if context.vICMS > 0:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "erro": "Simples Nacional (sem ST) não deve destacar vICMS",
                        "csosn": context.csosn_icms,
                        "vICMS": context.vICMS
                    }
                ))
            if context.vBC > 0:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "erro": "Simples Nacional (sem ST) não deve ter vBC",
                        "csosn": context.csosn_icms,
                        "vBC": context.vBC
                    }
                ))
        
        # 5. Se CSOSN com ST (201,202,203,500) - validar ST
        if context.csosn_icms in ["201", "202", "203", "500"]:
            if context.vBCST <= 0 or context.vICMSST <= 0:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "erro": f"CSOSN {context.csosn_icms} exige ST (vBCST/vICMSST)",
                        "csosn": context.csosn_icms,
                        "vBCST": context.vBCST,
                        "vICMSST": context.vICMSST
                    }
                ))
        
        # 6. DIFAL pode NÃO aplicar para Simples (verificar UF)
        if context.operacao_interestadual and context.indIEDest == "9":
            # Algumas UFs não cobram DIFAL de Simples
            if self.uf_nao_cobra_difal_simples(context.uf_destino):
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "info": f"UF {context.uf_destino} pode não cobrar DIFAL de Simples Nacional",
                        "uf": context.uf_destino
                    }
                ))
        
        # 7. FCP pode NÃO aplicar para Simples
        if context.operacao_interestadual and context.indIEDest == "9":
            if self.uf_nao_cobra_fcp_simples(context.uf_destino):
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "info": f"UF {context.uf_destino} pode não cobrar FCP de Simples Nacional",
                        "uf": context.uf_destino
                    }
                ))
        
        return discrepancies
```

---

## 🎯 ZFM - Zona Franca de Manaus (AM)

### Características
- **Incentivos fiscais** federais, estaduais, municipais
- **ICMS diferenciado** - isenção/redução
- **IPI isento** para produtos fabricados na ZFM
- **Importação facilitada** - isenção II, IPI, PIS/COFINS

### Regras NF-e ZFM

```python
class NFEZFMRule(BaseRule):
    code = "NFE_REGIME_ESPECIAL"
    relevance_tags = {"zfm", "special_regime", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.uf_emitente == "AM" and context.eh_zfm
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. ICMS isento/reduzido
        if context.cst_icms not in ["40", "41", "50", "51", "60"]:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "aviso": "ZFM - verificar CST ICMS correto (isento/suspensão)",
                    "cst": context.cst_icms,
                    "uf": "AM"
                }
            ))
        
        # 2. FCP ISENTO para ZFM
        if context.vFCP > 0:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "erro": "ZFM isenta FCP (vFCP deve ser 0)",
                    "vFCP": context.vFCP
                }
            ))
        
        # 3. DIFAL não aplica para ZFM (geralmente)
        if context.operacao_interestadual and context.indIEDest == "9":
            if context.vICMS > 0:  # DIFAL calculado
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "aviso": "ZFM - DIFAL pode não aplicar, verificar legislação",
                        "uf_origem": "AM"
                    }
                ))
        
        # 4. ISUF (SUFRAMA) obrigatório se destinatário ZFM
        if context.dest_uf == "AM" and context.dest_eh_zfm:
            if not context.dest_isuf:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "erro": "Destinatário ZFM deve informar ISUF (Inscrição SUFRAMA)"
                    }
                ))
        
        return discrepancies
```

---

## 🎯 Outras Isenções/Imunidades

### Imunidades Constitucionais (Art. 150, CF/88)
| Situação | Base Legal | CST/CSOSN |
|----------|------------|-----------|
| Livros, jornais, papel | Art. 150, VI, d | 40/41 / 300 |
| Templos religiosos | Art. 150, VI, b | 40/41 / 300 |
| Partidos políticos | Art. 150, VI, c | 40/41 / 300 |
| Sindicatos | Art. 150, VI, c | 40/41 / 300 |
| Entidades filantrópicas | Art. 150, VI, c | 40/41 / 300 |

### Isenções Convênio ICMS 38/2001
| Produto | Isenção | CST |
|---------|---------|-----|
| Hortifrutigranjeiros in natura | Convênio 38 | 40/41 |
| Medicamentos genéricos | Convênio 38 | 40/41 |
| Produtos cesta básica | Convênio 38 | 40/41 |

---

## 🔍 Lógica Unificada Regimes Especiais

```python
class NFERegimeEspecialRule(BaseRule):
    code = "NFE_REGIME_ESPECIAL"
    relevance_tags = {"simples", "zfm", "special_regime", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return (context.regime_tributario == "SIMPLES_NACIONAL" or
                context.uf_emitente == "AM" or
                context.uf_destino == "AM" or
                context.tem_isencao_imunidade)
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # Delegar para rules específicas
        if context.regime_tributario == "SIMPLES_NACIONAL":
            discrepancies.extend(self.validar_simples(context))
        
        if context.uf_emitente == "AM" and context.eh_zfm:
            discrepancies.extend(self.validar_zfm_emitente(context))
        
        if context.uf_destino == "AM" and context.dest_eh_zfm:
            discrepancies.extend(self.validar_zfm_destinatario(context))
        
        if context.tem_isencao_imunidade:
            discrepancies.extend(self.validar_isencao_imunidade(context))
        
        return discrepancies
```

---

## 🧪 Casos de Teste

```python
# test_nfe_simples_nacional_csosn_obrigatorio
# Simples sem CSOSN → HIGH

# test_nfe_simples_nacional_cst_invalido
# Simples com CST 00 → HIGH

# test_nfe_simples_sem_st_sem_icms
# CSOSN 101, vICMS>0 → HIGH

# test_nfe_simples_com_st_valido
# CSOSN 201, vBCST>0, vICMSST>0 → OK

# test_nfe_simples_difal_pode_nao_aplicar
# Simples interestadual não contribuinte → MEDIUM info

# test_nfe_zfm_fcp_isento
# AM ZFM, vFCP>0 → MEDIUM

# test_nfe_zfm_isuf_obrigatorio
# Destino AM ZFM, sem ISUF → HIGH

# test_nfe_isencao_constitucional
# Livros, CST 40, vICMS=0 → OK

# test_nfe_imunidade_sem_icms
# Entidade filantrópica, CSOSN 300 → OK
```

---

## ⚠️ Pontos de Atenção

### Simples Nacional
1. **SEMPRE CSOSN** (nunca CST, exceto 900)
2. **ICMS NÃO destacado** (exceto ST - CSOSN 201,202,203,500)
3. **DIFAL/FCP** podem não aplicar - verificar UF destino
4. **Crédito ICMS** só se CSOSN 101/201 (permite crédito)
5. **CFOP próprios**: 5.101-5.119 / 6.101-6.119

### ZFM (AM)
1. **FCP ISENTO** (Convênio 174/2023)
2. **DIFAL** pode não aplicar
3. **ISUF** obrigatório para destinatário ZFM
4. **CST isenção/suspensão** (40,41,50,51,60)
5. **IPI isento** para produtos fabricados na ZFM

### Isenções/Imunidades
1. **CST 40/41** (isento/não tributado) - vICMS=0, vBC=0
2. **CSOSN 300** (imune)
3. **Não confundir** isenção (CST 40) com não incidência (CST 41)

---

## 📦 JSON para backend/app/data/nfe/regimes_especiais.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "simples_nacional": {
    "csosns_validos": ["101", "102", "103", "201", "202", "203", "300", "400", "500", "900"],
    "csosns_com_credito": ["101", "201"],
    "csosns_sem_credito": ["102", "103", "202", "203", "300", "400", "500", "900"],
    "csosns_com_st": ["201", "202", "203", "500"],
    "csosns_sem_st": ["101", "102", "103", "300", "400"],
    "csosns_isencao": ["103"],
    "csosns_imune": ["300"],
    "icms_nao_destacado_sem_st": true,
    "cfop_faixa": "5101-5119, 6101-6119",
    "difal_pode_nao_aplicar": true,
    "fcp_pode_nao_aplicar": true,
    "ufs_nao_cobram_difal_simples": [],
    "ufs_nao_cobram_fcp_simples": []
  },
  "zfm": {
    "uf": "AM",
    "fcp_isento": true,
    "difal_pode_nao_aplicar": true,
    "csts_permitidos": ["40", "41", "50", "51", "60"],
    "isuf_obrigatorio_destinatario": true,
    "ipi_isento_fabricacao_zfm": true,
    "importacao_facilitada": true
  },
  "isencoes_constitucionais": {
    "livros_jornais_papel": {"cst": "40", "base": "Art. 150 VI d CF/88"},
    "templos_religiosos": {"cst": "40", "base": "Art. 150 VI b CF/88"},
    "partidos_politicos": {"cst": "40", "base": "Art. 150 VI c CF/88"},
    "sindicatos": {"cst": "40", "base": "Art. 150 VI c CF/88"},
    "entidades_filantropicas": {"cst": "40", "base": "Art. 150 VI c CF/88"}
  },
  "isencoes_convenio_38": {
    "hortifrutigranjeiros_in_natura": {"cst": "40"},
    "medicamentos_genericos": {"cst": "40"},
    "cesta_basica": {"cst": "40"}
  }
}
```

---

## 🔗 Referências

- [LC 123/2006 - Simples Nacional](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm)
- [LC 147/2014](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp147.htm)
- [Decreto 6.759/2009 - ZFM](http://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/decreto/d6759.htm)
- [Convênio ICMS 38/2001](https://www.confaz.fazenda.gov.br/legislacao/convenios/2001/convenio-icms-38-2001)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent