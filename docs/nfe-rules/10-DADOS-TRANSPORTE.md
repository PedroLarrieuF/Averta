# Dados Transportadora/Veículo/Motorista - Regra NFE_TRANSPORTADORA_DADOS

**Rule Code:** `NFE_TRANSPORTADORA_DADOS`  
**Tipo:** `TRANSPORT_DATA`  
**Severidade:** `HIGH`  
**Tags:** `transport, carrier, vehicle, driver, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/transportadora_validacao.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_transportadora_dados`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Ajuste SINIEF 19/2016** | Grupo `<transp>` NF-e 4.00 | Vigente |
| **Lei 11.442/2007** | Transporte rodoviário de cargas | Vigente |
| **ANTT Res. 5.839/2021** | Dados transportadora no CT-e | Vigente |
| **Decreto 9.209/2017** | CT-e - transportadora | Vigente |

---

## 🎯 Campos NF-e (Grupo Transportadora)

```xml
<transp>
  <modFrete>0</modFrete>              <!-- 0=Emitente, 1=Destinatário, 2=Terceiros, 3=Próprio remetente, 9=Sem -->
  <transporta>                        <!-- Dados da Transportadora -->
    <CNPJ>12345678000199</CNPJ>       <!-- CNPJ Transportadora -->
    <IE>123456789</IE>                <!-- IE Transportadora -->
    <xNome>Transportadora Ltda</xNome> <!-- Razão Social -->
    <xEnder>Rua X, 123</xEnder>       <!-- Endereço -->
    <xMun>São Paulo</xMun>            <!-- Município -->
    <UF>SP</UF>                       <!-- UF -->
  </transporta>
  <veicTransp>                        <!-- Veículo -->
    <placa>ABC1234</placa>            <!-- Placa (formato Mercosul: ABC1D23) -->
    <UF>SP</UF>                       <!-- UF veículo -->
    <RNTC>12345678</RNTC>             <!-- RNTC ANTT -->
  </veicTransp>
  <motorista>                         <!-- Motorista -->
    <xNome>João da Silva</xNome>
    <CPF>12345678901</CPF>
  </motorista>
  <reboque>                           <!-- Reboque (opcional) -->
    <placa>DEF5678</placa>
    <UF>SP</UF>
    <RNTC>87654321</RNTC>
  </reboque>
  <vagao>...</vagao>                  <!-- Vagão (ferroviário) -->
  <balsa>...</balsa>                  <!-- Balsa (aquaviário) -->
</transp>
```

---

## 🔍 Lógica de Detecção no Engine

```python
class NFETransportadoraDadosRule(BaseRule):
    code = "NFE_TRANSPORTADORA_DADOS"
    relevance_tags = {"transport", "carrier", "vehicle", "driver", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        # Só se há frete (modFrete != 9)
        return context.modFrete and context.modFrete != "9"
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. modFrete 0,2,3 = Transportadora OBRIGATÓRIA
        if context.modFrete in ["0", "2", "3"]:
            if not context.transporta_cnpj:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "TRANSPORTADORA_OBRIGATORIA",
                        "modFrete": context.modFrete,
                        "campo_faltando": "transporta/CNPJ"
                    }
                ))
            
            if not context.transporta_ie:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "TRANSPORTADORA_IE_OBRIGATORIA",
                        "modFrete": context.modFrete,
                        "campo_faltando": "transporta/IE"
                    }
                ))
        
        # 2. modFrete 1 (Destinatário) = Transportadora OPCIONAL
        # Mas se informou, validar
        
        # 3. Validar CNPJ formato
        if context.transporta_cnpj:
            if not self.validar_cnpj(context.transporta_cnpj):
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "TRANSPORTADORA_CNPJ_INVALIDO",
                        "cnpj": context.transporta_cnpj
                    }
                ))
        
        # 4. Validar IE formato (por UF)
        if context.transporta_ie and context.transporta_uf:
            if not self.validar_ie(context.transporta_ie, context.transporta_uf):
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "TRANSPORTADORA_IE_INVALIDO_UF",
                        "ie": context.transporta_ie,
                        "uf": context.transporta_uf
                    }
                ))
        
        # 5. Veículo - Obrigatório se modFrete 0,1,2,3
        if context.modFrete in ["0", "1", "2", "3"]:
            if not context.veic_placa:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "VEICULO_OBRIGATORIO",
                        "modFrete": context.modFrete
                    }
                ))
            else:
                # Validar formato placa (Mercosul: AAA1B23 ou antigo: AAA1234)
                if not self.validar_placa(context.veic_placa):
                    discrepancies.append(Discrepancy(
                        rule_code=self.code,
                        severity="MEDIUM",
                        details={
                            "validacao": "VEICULO_PLACA_INVALIDA",
                            "placa": context.veic_placa
                        }
                    ))
            
            # RNTC obrigatório para transporte interestadual
            if context.uf_emitente != context.uf_destino:
                if not context.veic_rntc:
                    discrepancies.append(Discrepancy(
                        rule_code=self.code,
                        severity="MEDIUM",
                        details={
                            "validacao": "VEICULO_RNTC_OBRIGATORIO_INTERESTADUAL",
                            "uf_origem": context.uf_emitente,
                            "uf_destino": context.uf_destino
                        }
                    ))
        
        # 6. Motorista - CPF obrigatório se veículo informado
        if context.veic_placa and not context.motorista_cpf:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "validacao": "MOTORISTA_CPF_OBRIGATORIO"
                }
            ))
        
        if context.motorista_cpf and not self.validar_cpf(context.motorista_cpf):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "validacao": "MOTORISTA_CPF_INVALIDO",
                    "cpf": context.motorista_cpf
                }
            ))
        
        # 7. Cross-validation com CT-e (ver 14-CROSS-CTE-NFE.md)
        if context.cte:
            self.validar_cross_cte(context, discrepancies)
        
        return discrepancies
    
    def validar_cross_cte(self, context, discrepancies):
        """Valida transportadora NF-e vs CT-e"""
        cte = context.cte
        
        # Transportadora CT-e (emitente) vs NF-e (transporta)
        if cte.emit_cnpj and context.transporta_cnpj:
            if cte.emit_cnpj != context.transporta_cnpj:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="CRITICAL",
                    details={
                        "validacao": "TRANSPORTADORA_CNPJ_DIVERGENTE",
                        "cte_emitente": cte.emit_cnpj,
                        "nfe_transporta": context.transporta_cnpj
                    }
                ))
        
        # Veículo
        if cte.veic_placa and context.veic_placa:
            if cte.veic_placa != context.veic_placa:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="HIGH",
                    details={
                        "validacao": "VEICULO_PLACA_DIVERGENTE",
                        "cte": cte.veic_placa,
                        "nfe": context.veic_placa
                    }
                ))
        
        # Motorista
        if cte.motorista_cpf and context.motorista_cpf:
            if cte.motorista_cpf != context.motorista_cpf:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="MEDIUM",
                    details={
                        "validacao": "MOTORISTA_CPF_DIVERGENTE",
                        "cte": cte.motorista_cpf,
                        "nfe": context.motorista_cpf
                    }
                ))
    
    def validar_cnpj(self, cnpj):
        cnpj = ''.join(filter(str.isdigit, cnpj))
        return len(cnpj) == 14
    
    def validar_cpf(self, cpf):
        cpf = ''.join(filter(str.isdigit, cpf))
        return len(cpf) == 11
    
    def validar_placa(self, placa):
        placa = placa.upper().replace('-', '').replace(' ', '')
        # Mercosul: AAA1B23 (7 chars) ou Antigo: AAA1234 (7 chars)
        return len(placa) == 7 and placa[:3].isalpha()
    
    def validar_ie(self, ie, uf):
        # Implementar validação IE por UF
        return len(ie) >= 6
```

---

## 🧪 Casos de Teste

```python
# test_nfe_transportadora_dados_modfrete0_sem_transporta
# modFrete=0, sem transporta → HIGH

# test_nfe_transportadora_cnpj_invalido
# CNPJ com 13 dígitos → HIGH

# test_nfe_transportadora_veiculo_obrigatorio
# modFrete=0, sem veicTransp → HIGH

# test_nfe_transportadora_rntc_interstadual
# SP→RJ, sem RNTC → MEDIUM

# test_nfe_transportadora_placa_invalida
# Placa "ABC123" (6 chars) → MEDIUM

# test_nfe_transportadora_motorista_cpf
# Veículo informado, sem motorista → MEDIUM

# test_nfe_cross_transportadora_cte_nfe_divergente
# CT-e emit=111, NF-e transporta=222 → CRITICAL (cross)
```

---

## ⚠️ Pontos de Atenção

1. **modFrete 0,2,3** = Transportadora **OBRIGATÓRIA** (CNPJ + IE)
2. **modFrete 1** = Transportadora **OPCIONAL** (conta destinatário)
3. **modFrete 9** = Sem frete = Sem transportadora/veículo
4. **Veículo obrigatório** se modFrete 0,1,2,3
5. **RNTC obrigatório** para interestadual
6. **Placa formato Mercosul** (AAA1B23) ou antigo (AAA1234)
7. **Cross CT-e**: Transportadora, Veículo, Motorista devem ser **IDÊNTICOS**
8. **Reboque**: Validar se informado (placa + RNTC)

---

## 📦 JSON para backend/app/data/nfe/transportadora_validacao.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "modfrete_regras": {
    "0": {"transportadora_obrigatoria": true, "veiculo_obrigatorio": true, "rntc_se_interstadual": true, "motorista_obrigatorio": true},
    "1": {"transportadora_obrigatoria": false, "veiculo_obrigatorio": true, "rntc_se_interstadual": true, "motorista_obrigatorio": true},
    "2": {"transportadora_obrigatoria": true, "veiculo_obrigatorio": true, "rntc_se_interstadual": true, "motorista_obrigatorio": true},
    "3": {"transportadora_obrigatoria": true, "veiculo_obrigatorio": true, "rntc_se_interstadual": true, "motorista_obrigatorio": true},
    "9": {"transportadora_obrigatoria": false, "veiculo_obrigatorio": false, "rntc_se_interstadual": false, "motorista_obrigatorio": false}
  },
  "validacoes": {
    "cnpj": {"tamanho": 14, "apenas_digitos": true},
    "cpf": {"tamanho": 11, "apenas_digitos": true},
    "placa_mercosul": {"padrao": "^[A-Z]{3}[0-9][A-Z][0-9]{2}$", "tamanho": 7},
    "placa_antiga": {"padrao": "^[A-Z]{3}[0-9]{4}$", "tamanho": 7},
    "rntc": {"tamanho_min": 6, "tamanho_max": 8, "apenas_digitos": true}
  },
  "cross_cte_campos": [
    "transporta_cnpj = cte_emit_cnpj",
    "veic_placa = cte_veic_placa",
    "motorista_cpf = cte_motorista_cpf",
    "veic_rntc = cte_veic_rntc"
  ]
}
```

---

## 🔗 Referências

- [Manual NF-e 4.00 - Grupo Transportadora](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Lei 11.442/2007](http://www.planalto.gov.br/ccivil_03/_ato2004-2006/2007/lei/l11442.htm)
- [ANTT Res. 5.839/2021](https://www.antt.gov.br/)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent