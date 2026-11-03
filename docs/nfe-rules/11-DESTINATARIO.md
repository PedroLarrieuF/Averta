# Dados Destinatário (IE, CNPJ/CPF) - Regra NFE_DESTINATARIO_VALIDACAO

**Rule Code:** `NFE_DESTINATARIO_VALIDACAO`  
**Tipo:** `DESTINATARY`  
**Severidade:** `HIGH`  
**Tags:** `destinatario, ie, cnpj, cpf, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/destinatario_validacao.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_destinatario_validacao`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Ajuste SINIEF 19/2016** | Grupo `<dest>` NF-e 4.00 | Vigente |
| **LC 87/1996** | ICMS interestadual - destinatário | Vigente |
| **LC 190/2022** | DIFAL - indIEDest | Vigente |
| **Manual NF-e 4.00** | Campos destinatário | Vigente |

---

## 🎯 Campos NF-e (Grupo Destinatário)

```xml
<dest>
  <CNPJ>12345678000199</CNPJ>         <!-- CNPJ (se PJ) -->
  <CPF>12345678901</CPF>              <!-- CPF (se PF) -->
  <idEstrangeiro>ABC123</idEstrangeiro> <!-- Se exterior -->
  <xNome>Empresa Destino Ltda</xNome>  <!-- Razão Social / Nome -->
  <indIEDest>1</indIEDest>             <!-- 1=Contrib, 2=Isento, 9=Não Contrib -->
  <IE>123456789</IE>                   <!-- IE (se contrib ou isento) -->
  <ISUF>...</ISUF>                     <!-- Inscrição SUFRAMA (ZFM) -->
  <IM>123456</IM>                      <!-- Inscrição Municipal (serviços) -->
  <email>destino@email.com</email>
  <enderDest>
    <xLgr>Rua Destino</xLgr>
    <nro>456</nro>
    <xBairro>Centro</xBairro>
    <cMun>3550308</cMun>               <!-- Código IBGE município -->
    <xMun>São Paulo</xMun>
    <UF>SP</UF>
    <CEP>01000000</CEP>
    <cPais>1058</cPais>
    <xPais>BRASIL</xPais>
    <fone>1133334444</fone>
  </enderDest>
</dest>
```

---

## 🎯 indIEDest (Indicador IE Destinatário)

| Código | Descrição | ICMS | DIFAL | FCP | IE Obrigatório? |
|--------|-----------|------|-------|-----|-----------------|
| **1** | **Contribuinte ICMS** | Sim (destino) | Sim (diferencial) | Não | **SIM** |
| **2** | **Isento ICMS** | Não (isento) | Ver legislação | Não | **SIM** |
| **9** | **Não Contribuinte** | Não (destino recolhe) | **SIM (integral)** | **SIM** | NÃO |

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEDestinatarioValidacaoRule(BaseRule):
    code = "NFE_DESTINATARIO_VALIDACAO"
    relevance_tags = {"destinatario", "ie", "cnpj", "cpf", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return True  # Sempre validar destinatário
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. CNPJ ou CPF obrigatório (exclusivo)
        tem_cnpj = bool(context.dest_cnpj)
        tem_cpf = bool(context.dest_cpf)
        tem_estrangeiro = bool(context.dest_id_estrangeiro)
        
        if not (tem_cnpj ^ tem_cpf ^ tem_estrangeiro):  # XOR - exatamente um
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "validacao": "DESTINATARIO_DOC_OBRIGATORIO_EXCLUSIVO",
                    "tem_cnpj": tem_cnpj,
                    "tem_cpf": tem_cpf,
                    "tem_estrangeiro": tem_estrangeiro,
                    "regra": "Informar exatamente um: CNPJ, CPF ou idEstrangeiro"
                }
            ))
        
        # 2. Validar CNPJ
        if tem_cnpj and not self.validar_cnpj(context.dest_cnpj):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"validacao": "DESTINATARIO_CNPJ_INVALIDO", "cnpj": context.dest_cnpj}
            ))
        
        # 3. Validar CPF
        if tem_cpf and not self.validar_cpf(context.dest_cpf):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"validacao": "DESTINATARIO_CPF_INVALIDO", "cpf": context.dest_cpf}
            ))
        
        # 4. indIEDest obrigatório
        if not context.indIEDest:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"validacao": "DESTINATARIO_INDIEDEST_OBRIGATORIO"}
            ))
        
        # 5. IE obrigatório se indIEDest = 1 ou 2
        if context.indIEDest in ["1", "2"]:
            if not context.dest_ie:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "DESTINATARIO_IE_OBRIGATORIO_CONTRIBUINTE_ISENTO",
                        "indIEDest": context.indIEDest
                    }
                ))
            elif not self.validar_ie(context.dest_ie, context.dest_uf):
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "DESTINATARIO_IE_INVALIDO_UF",
                        "ie": context.dest_ie,
                        "uf": context.dest_uf
                    }
                ))
        
        # 6. IE NÃO deve ser informado se indIEDest = 9
        if context.indIEDest == "9" and context.dest_ie:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "validacao": "DESTINATARIO_IE_NAO_DEVE_SER_INFORMADO_NAO_CONTRIBUINTE",
                    "indIEDest": "9",
                    "ie_informada": context.dest_ie
                }
            ))
        
        # 7. UF Destino obrigatória
        if not context.dest_uf:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"validacao": "DESTINATARIO_UF_OBRIGATORIA"}
            ))
        
        # 8. Código IBGE Município (cMun) válido
        if context.dest_cmun and not self.validar_cmun(context.dest_cmun, context.dest_uf):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "validacao": "DESTINATARIO_CMUN_INVALIDO_UF",
                    "cMun": context.dest_cmun,
                    "uf": context.dest_uf
                }
            ))
        
        # 9. Cross-validation CT-e (ver 14-CROSS-CTE-NFE.md)
        if context.cte:
            self.validar_cross_cte(context, discrepancies)
        
        return discrepancies
    
    def validar_cross_cte(self, context, discrepancies):
        """Valida destinatário NF-e vs CT-e"""
        cte = context.cte
        
        # CNPJ/CPF
        if cte.dest_cnpj_cpf and (context.dest_cnpj or context.dest_cpf):
            doc_nfe = context.dest_cnpj or context.dest_cpf
            if cte.dest_cnpj_cpf != doc_nfe:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="CRITICAL",
                    details={
                        "validacao": "DESTINATARIO_CNPJ_CPF_DIVERGENTE",
                        "cte": cte.dest_cnpj_cpf,
                        "nfe": doc_nfe
                    }
                ))
        
        # IE
        if cte.dest_ie and context.dest_ie:
            if cte.dest_ie != context.dest_ie:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="HIGH",
                    details={
                        "validacao": "DESTINATARIO_IE_DIVERGENTE",
                        "cte": cte.dest_ie,
                        "nfe": context.dest_ie
                    }
                ))
        
        # UF
        if cte.dest_uf and context.dest_uf:
            if cte.dest_uf != context.dest_uf:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="CRITICAL",
                    details={
                        "validacao": "DESTINATARIO_UF_DIVERGENTE",
                        "cte": cte.dest_uf,
                        "nfe": context.dest_uf,
                        "impacto": "DIFAL/FCP/ICMS calculados errado"
                    }
                ))
        
        # Município
        if cte.dest_cmun and context.dest_cmun:
            if cte.dest_cmun != context.dest_cmun:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="MEDIUM",
                    details={
                        "validacao": "DESTINATARIO_MUNICIPIO_DIVERGENTE",
                        "cte": cte.dest_cmun,
                        "nfe": context.dest_cmun
                    }
                ))
    
    def validar_cnpj(self, cnpj):
        cnpj = ''.join(filter(str.isdigit, cnpj))
        if len(cnpj) != 14:
            return False
        # Validar dígitos verificadores
        return self.validar_dv_cnpj(cnpj)
    
    def validar_cpf(self, cpf):
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) != 11:
            return False
        return self.validar_dv_cpf(cpf)
    
    def validar_dv_cnpj(self, cnpj):
        # Implementar validação DV CNPJ
        return True  # Simplificado
    
    def validar_dv_cpf(self, cpf):
        # Implementar validação DV CPF
        return True  # Simplificado
    
    def validar_ie(self, ie, uf):
        # Validação IE por UF (cada estado tem formato próprio)
        return len(ie) >= 6
    
    def validar_cmun(self, cmun, uf):
        # Validar se cMun pertence à UF (tabela IBGE)
        return len(str(cmun)) == 7
```

---

## 🧪 Casos de Teste

```python
# test_nfe_destinatario_cnpj_obrigatorio
# Sem CNPJ/CPF/idEstrangeiro → HIGH

# test_nfe_destinatario_cnpj_cpf_ambos
# CNPJ e CPF informados → HIGH (exclusivo)

# test_nfe_destinatario_indiedest_obrigatorio
# Sem indIEDest → HIGH

# test_nfe_destinatario_ie_obrigatorio_contribuinte
# indIEDest=1, sem IE → HIGH

# test_nfe_destinatario_ie_obrigatorio_isento
# indIEDest=2, sem IE → HIGH

# test_nfe_destinatario_ie_nao_informado_nao_contribuinte
# indIEDest=9, com IE → MEDIUM

# test_nfe_destinatario_ie_formato_invalido
# IE formato errado para UF → MEDIUM

# test_nfe_destinatario_uf_obrigatoria
# Sem UF → HIGH

# test_nfe_cross_destinatario_cnpj_divergente
# CT-e CNPJ=111, NF-e CNPJ=222 → CRITICAL

# test_nfe_cross_destinatario_uf_divergente
# CT-e UF=RJ, NF-e UF=SP → CRITICAL (impacta DIFAL/FCP)
```

---

## ⚠️ Pontos de Atenção

1. **Exatamente UM documento**: CNPJ **OU** CPF **OU** idEstrangeiro
2. **indIEDest OBRIGATÓRIO**: 1=Contribuinte, 2=Isento, 9=Não Contribuinte
3. **IE obrigatória** se indIEDest 1 ou 2; **PROIBIDA** se 9
4. **IE formato por UF** - cada estado tem máscara própria
4. **UF Destino CRÍTICA** - define ICMS interestadual, DIFAL, FCP
5. **cMun (IBGE)** deve pertencer à UF informada
6. **Cross CT-e**: CNPJ/CPF, IE, UF, Município **IDÊNTICOS**
7. **ISUF** (SUFRAMA) para ZFM (AM) - regime especial
8. **IM** (Municipal) para serviços

---

## 📦 JSON para backend/app/data/nfe/destinatario_validacao.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "indIEDest": {
    "1": {"desc": "Contribuinte ICMS", "ie_obrigatoria": true, "difal": "diferencial", "fcp": false},
    "2": {"desc": "Isento ICMS", "ie_obrigatoria": true, "difal": "ver_legislacao", "fcp": false},
    "9": {"desc": "Nao Contribuinte", "ie_obrigatoria": false, "difal": "integral", "fcp": true}
  },
  "documento_obrigatorio_exclusivo": ["CNPJ", "CPF", "idEstrangeiro"],
  "validacoes": {
    "cnpj": {"tamanho": 14, "dv": true},
    "cpf": {"tamanho": 11, "dv": true},
    "ie_por_uf": "validar_mascara_uf",
    "cmun": {"tamanho": 7, "pertence_uf": true}
  },
  "cross_cte_campos": [
    "dest_cnpj_cpf = cte_dest_cnpj_cpf",
    "dest_ie = cte_dest_ie",
    "dest_uf = cte_dest_uf",
    "dest_cmun = cte_dest_cmun"
  ]
}
```

---

## 🔗 Referências

- [Manual NF-e 4.00 - Grupo Destinatário](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [LC 190/2022 - DIFAL indIEDest](http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp190.htm)
- [Tabela IBGE Municípios](https://www.ibge.gov.br/)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent