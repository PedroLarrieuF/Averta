# Cruzamento CT-e × NF-e (Auditoria Core) - Regra NFE_CTE_CROSS_VALIDATION

**Rule Code:** `NFE_CTE_CROSS_VALIDATION`  
**Tipo:** `CROSS_VALIDATION`  
**Severidade:** `CRITICAL`  
**Tags:** `cross, cte, nfe, freight_audit, core`  
**Arquivo de Dados:** `backend/app/data/nfe/cross_cte_nfe_regras.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_cross_cte_nfe_valores`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Lei 11.442/2007** | Transporte rodoviário de cargas | Vigente |
| **Decreto 9.209/2017** | Regulamento CT-e | Vigente |
| **Ajuste SINIEF 07/2005** | Leiaute NF-e | Vigente |
| **Ajuste SINIEF 19/2016** | NF-e 4.00 | Vigente |
| **Manual CT-e 3.00** | Especificação CT-e | Vigente |
| **Manual NF-e 4.00** | Especificação NF-e | Vigente |
| **Convênio ICMS 188/2017** | CT-e complementar | Vigente |

---

## 🎯 Objetivo da Auditoria

> **Core Business**: Validar se o **frete cobrado no CT-e** confere com a **operação fiscal na NF-e**.
> 
> O CT-e é o documento de **transporte** (contrato de frete).
> A NF-e é o documento **fiscal** da mercadoria (base de impostos).
> 
> **Discrepância = Oportunidade de recuperação (success fee)**

---

## 🔗 Vinculação CT-e ↔ NF-e

### No CT-e (tag `<infCte><ide>`):
```xml
<refNFe>35250101234567890123550010000000011234567890</refNFe>
<!-- Chave de acesso da NF-e referenciada -->
```

### Na NF-e (tag `<infNFe><ide>`):
```xml
<mod>55</mod>                    <!-- NF-e modelo 55 -->
<serie>1</serie>
<nNF>12345</nNF>
<!-- Chave composta: UF + AAMM + CNPJ + mod + serie + nNF + tpEmis + cNF + cDV -->
```

### Regra de Ouro
> **Um CT-e DEVE referenciar uma ou mais NF-es** (tag `refNFe`).
> **Uma NF-e PODE ser referenciada por um ou mais CT-es** (redespacho, subcontratação).

---

## 🔍 Validações de Cruzamento (Prioridade CRITICAL)

### 1. VALORES: vTPrest (CT-e) vs vNF (NF-e)

| Campo CT-e | Campo NF-e | Regra | Tolerância |
|------------|------------|-------|------------|
| `vTPrest` (valor total prestação) | `vNF` (valor total nota) | **vTPrest ≈ vNF** | **±2%** ou **R$ 10,00** |
| `vRec` (valor a receber) | `vNF` | vRec ≤ vNF | Exato |
| `vCarga` (valor carga) | `vProd` (valor produtos) | vCarga ≈ vProd | ±5% |

```python
def validar_valores(cte, nfe):
    discrepancias = []
    
    # vTPrest vs vNF - REGRA PRINCIPAL
    diff_valor = abs(cte.vTPrest - nfe.vNF)
    tolerancia = max(nfe.vNF * 0.02, 10.0)  # 2% ou R$ 10
    
    if diff_valor > tolerancia:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="CRITICAL",
            expected_value=round(nfe.vNF, 2),
            actual_value=round(cte.vTPrest, 2),
            difference=round(diff_valor, 2),
            details={
                "validacao": "VALOR_TOTAL",
                "campo_cte": "vTPrest",
                "campo_nfe": "vNF",
                "tolerancia_usada": tolerancia,
                "tipo_divergencia": "FRETE_DIVERGENTE" if cte.vTPrest > nfe.vNF else "VALOR_MENOR"
            }
        ))
    
    return discrepancias
```

### 2. PESO: proPred/peso (CT-e) vs vPeso (NF-e)

| Campo CT-e | Campo NF-e | Regra | Tolerância |
|------------|------------|-------|------------|
| `proPred/peso` (peso bruto) | `vPeso` (peso líquido NF-e) | **Peso CT-e ≥ Peso NF-e** | **Carga geral: 5%**, **Granel: 20%** |
| `proPred/pesoCubado` | - | Se informado, validar cubagem | ±10% |

```python
def validar_peso(cte, nfe):
    discrepancias = []
    
    peso_cte = cte.peso_bruto  # proPred/peso
    peso_nfe = nfe.vPeso       # peso líquido
    
    # Tolerância por tipo de carga
    if nfe.tipo_carga in ["GRANEL_LIQUIDO", "GRANEL_SOLIDO"]:
        tolerancia_pct = 0.20  # 20% granel
    else:
        tolerancia_pct = 0.05  # 5% carga geral
    
    peso_min_esperado = peso_nfe * (1 - tolerancia_pct)
    peso_max_esperado = peso_nfe * (1 + tolerancia_pct)
    
    if peso_cte < peso_min_esperado:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="HIGH",
            expected_value=round(peso_nfe, 3),
            actual_value=round(peso_cte, 3),
            difference=round(peso_nfe - peso_cte, 3),
            details={
                "validacao": "PESO",
                "campo_cte": "proPred/peso",
                "campo_nfe": "vPeso",
                "tolerancia_pct": tolerancia_pct * 100,
                "tipo_carga": nfe.tipo_carga,
                "observacao": "Peso CT-e menor que NF-e - possível subcobrança frete peso"
            }
        ))
    
    return discrepancias
```

### 3. DESTINATÁRIO: CNPJ/CPF/IE (CT-e) vs NF-e

| Campo CT-e | Campo NF-e | Regra |
|------------|------------|-------|
| `dest/CNPJ` ou `dest/CPF` | `dest/CNPJ` ou `dest/CPF` | **IDÊNTICO** |
| `dest/IE` | `dest/IE` | **IDÊNTICO** (se contribuinte) |
| `dest/enderDest/UF` | `dest/enderDest/UF` | **IDÊNTICO** |
| `dest/enderDest/Cidade` | `dest/enderDest/cMun` | **COERENTE** |

```python
def validar_destinatario(cte, nfe):
    discrepancias = []
    
    # CNPJ/CPF
    if cte.dest_cnpj_cpf != nfe.dest_cnpj_cpf:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="CRITICAL",
            details={
                "validacao": "DESTINATARIO_CNPJ_CPF",
                "cte": cte.dest_cnpj_cpf,
                "nfe": nfe.dest_cnpj_cpf,
                "risco": "Documentos de operações diferentes"
            }
        ))
    
    # IE
    if cte.dest_ie and nfe.dest_ie and cte.dest_ie != nfe.dest_ie:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="HIGH",
            details={
                "validacao": "DESTINATARIO_IE",
                "cte": cte.dest_ie,
                "nfe": nfe.dest_ie
            }
        ))
    
    # UF
    if cte.dest_uf != nfe.dest_uf:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="CRITICAL",
            details={
                "validacao": "DESTINATARIO_UF",
                "cte": cte.dest_uf,
                "nfe": nfe.dest_uf,
                "impacto": "DIFAL/FCP calculado errado"
            }
        ))
    
    return discrepancias
```

### 4. TRANSPORTADORA: CNPJ/CPF (CT-e) vs NF-e

| Campo CT-e | Campo NF-e | Regra |
|------------|------------|-------|
| `emit/CNPJ` (CT-e) | `transp/transporta/CNPJ` (NF-e) | **IDÊNTICO** |
| `emit/IE` | `transp/transporta/IE` | **IDÊNTICO** |
| `emit/UF` | `transp/transporta/UF` | **IDÊNTICO** |

```python
def validar_transportadora(cte, nfe):
    discrepancias = []
    
    cnpj_cte = cte.emit_cnpj
    cnpj_nfe_transp = nfe.transp_transporta_cnpj
    
    if cnpj_cte != cnpj_nfe_transp:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="CRITICAL",
            details={
                "validacao": "TRANSPORTADORA_CNPJ",
                "cte_emitente": cnpj_cte,
                "nfe_transportadora": cnpj_nfe_transp,
                "risco": "CT-e emitido por transportadora diferente da NF-e",
                "possivel_fraude": True
            }
        ))
    
    return discrepancias
```

### 5. UF ORIGEM/DESTINO: Coerência Interestadual

| Campo CT-e | Campo NF-e | Regra |
|------------|------------|-------|
| `ide/UFIni` (UF início) | `emit/enderEmit/UF` | **IDÊNTICO** |
| `ide/UFFim` (UF fim) | `dest/enderDest/UF` | **IDÊNTICO** |
| `ide/tpCTe` | `ide/mod` + CFOP | **COERENTE** |

```python
def validar_uf_origem_destino(cte, nfe):
    discrepancias = []
    
    # UF Início = UF Emitente NF-e
    if cte.uf_ini != nfe.emit_uf:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="HIGH",
            details={
                "validacao": "UF_ORIGEM",
                "cte_uf_ini": cte.uf_ini,
                "nfe_emit_uf": nfe.emit_uf
            }
        ))
    
    # UF Fim = UF Destinatário NF-e
    if cte.uf_fim != nfe.dest_uf:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="CRITICAL",
            details={
                "validacao": "UF_DESTINO",
                "cte_uf_fim": cte.uf_fim,
                "nfe_dest_uf": nfe.dest_uf,
                "impacto": "ICMS interestadual / DIFAL / FCP incorretos"
            }
        ))
    
    return discrepancias
```

### 6. CFOP × tpCTe: Coerência Operação

| CFOP (NF-e) | tpCTe (CT-e) | Operação | Válido? |
|-------------|--------------|----------|---------|
| 5.352 / 6.352 | 0 (Normal) | Venda com frete por conta emitente | ✓ |
| 5.353 / 6.353 | 0 (Normal) | Venda com frete por conta destinatário | ✓ |
| 5.354 / 6.354 | 0 (Normal) | Venda com frete por conta terceiros | ✓ |
| 5.355 / 6.355 | 0 (Normal) | Venda sem frete (não gera CT-e) | ✗ |
| 5.933 / 6.933 | - | Simples Nacional | Verificar |
| 1.202 / 2.202 | - | Devolução | Verificar |

```python
def validar_cfop_tpcte(nfe, cte):
    discrepancias = []
    
    cfop = nfe.cfop
    tpcte = cte.tpCTe
    modfrete = nfe.modFrete
    
    # CFOP de frete deve ter CT-e
    cfops_com_frete = {"5352", "5353", "5354", "6352", "6353", "6354"}
    
    if str(cfop) in cfops_com_frete:
        if not cte or cte.tpCTe != "0":
            discrepancias.append(Discrepancy(
                rule_code="NFE_CTE_CROSS_VALIDATION",
                severity="HIGH",
                details={
                    "validacao": "CFOP_FRETE_SEM_CTE",
                    "cfop": cfop,
                    "tpcte": tpcte,
                    "modfrete": modfrete,
                    "risco": "Operação com frete mas sem CT-e correspondente"
                }
            ))
    
    # CFOP sem frete não deve ter CT-e
    cfops_sem_frete = {"5355", "6355", "5101", "5102", "6101", "6102"}
    if str(cfop) in cfops_sem_frete and cte:
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="MEDIUM",
            details={
                "validacao": "CFOP_SEM_FRETE_COM_CTE",
                "cfop": cfop,
                "tpcte": tpcte
            }
        ))
    
    return discrepancias
```

### 7. VOLUME/ESPECIE: Quantidades

| Campo CT-e | Campo NF-e | Regra |
|------------|------------|-------|
| `infCte/infCTeNorm/vCarga/qCarga` | `infNFe/det/prod/qCom` | Somatório volumes ≈ qCom |
| `infCte/infCTeNorm/infCarga/proPred` | `infNFe/det/prod` | Espécie/marca coerentes |

---

## 🔍 Validações de Cruzamento (Prioridade HIGH/MEDIUM)

### 8. FRETE NA BASE ICMS (NF-e) vs VALOR FRETE (CT-e)

```python
def validar_frete_base_icms(cte, nfe):
    """Verifica se frete do CT-e está na base ICMS da NF-e"""
    discrepancias = []
    
    # Frete no CT-e
    frete_cte = cte.vTPrest - cte.vCarga  # ou cte.vPrest/vFrete se destacado
    
    # Frete na NF-e (vFrete)
    frete_nfe = nfe.vFrete
    
    if frete_cte > 0 and frete_nfe == 0:
        discrepancias.append(Discrepancy(
            rule_code="NFE_FRETE_NA_BASE",  # Rule separada
            severity="CRITICAL",
            details={
                "validacao": "FRETE_CTE_NAO_EM_NFE",
                "frete_cte": frete_cte,
                "frete_nfe": frete_nfe,
                "impacto": "Base ICMS menor - sonegação ICMS sobre frete"
            }
        ))
    
    if frete_nfe > 0 and abs(frete_cte - frete_nfe) > max(frete_nfe * 0.05, 5.0):
        discrepancias.append(Discrepancy(
            rule_code="NFE_CTE_CROSS_VALIDATION",
            severity="HIGH",
            details={
                "validacao": "FRETE_VALOR_DIVERGENTE",
                "frete_cte": frete_cte,
                "frete_nfe": frete_nfe,
                "diferenca": abs(frete_cte - frete_nfe)
            }
        ))
    
    return discrepancias
```

### 9. ICMS: vICMS (NF-e) vs Operação (CT-e)

```python
def validar_icms_operacao(cte, nfe):
    discrepancias = []
    
    # Se interestadual (UF diferentes), deve ter ICMS interestadual
    if cte.uf_ini != cte.uf_fim:
        if nfe.vICMS == 0 and nfe.cst_icms not in ["40", "41", "50", "51"]:
            discrepancias.append(Discrepancy(
                rule_code="NFE_CTE_CROSS_VALIDATION",
                severity="HIGH",
                details={
                    "validacao": "ICMS_INTERESTADUAL_ZERADO",
                    "uf_ini": cte.uf_ini,
                    "uf_fim": cte.uf_fim,
                    "cst": nfe.cst_icms
                }
            ))
    
    return discrepancias
```

### 10. REDESPACHO/SUBCONTRATAÇÃO: Múltiplos CT-es por NF-e

```python
def validar_redespacho(nfe, ctes_list):
    """Valida se há redespacho (múltiplos CT-es para mesma NF-e)"""
    discrepancias = []
    
    if len(ctes_list) > 1:
        # Verificar se é redespacho legítimo
        transportadoras = set(cte.emit_cnpj for cte in ctes_list)
        
        if len(transportadoras) > 1:
            # Redespacho ou subcontratação
            # Verificar CT-e complementar (tpEmis=2,3,4)
            for cte in ctes_list:
                if cte.tpEmis in ["2", "3", "4"]:
                    # Validar regras complementares (ver 13-CTE-COMPLEMENTAR.md)
                    pass
                else:
                    discrepancias.append(Discrepancy(
                        rule_code="NFE_CTE_CROSS_VALIDATION",
                        severity="MEDIUM",
                        details={
                            "validacao": "MULTIPLOS_CTES_SEM_COMPLEMENTAR",
                            "nfe_chave": nfe.chave_acesso,
                            "ctes_count": len(ctes_list),
                            "transportadoras": list(transportadoras),
                            "risco": "Possível redespacho sem CT-e complementar"
                        }
                    ))
    
    return discrepancias
```

---

## 🎯 Lógica Principal no Engine

```python
class NFECTECrossValidationRule(BaseRule):
    code = "NFE_CTE_CROSS_VALIDATION"
    relevance_tags = {"cross", "cte", "nfe", "freight_audit", "core"}
    
    def is_relevant(self, context: CrossRuleContext) -> bool:
        # Só roda se temos AMBOS os documentos
        return context.cte is not None and context.nfe is not None
    
    def evaluate(self, context: CrossRuleContext) -> List[Discrepancy]:
        all_discrepancies = []
        cte = context.cte
        nfe = context.nfe
        
        # 1. Valores (CRITICAL)
        all_discrepancies.extend(self.validar_valores(cte, nfe))
        
        # 2. Peso (HIGH)
        all_discrepancies.extend(self.validar_peso(cte, nfe))
        
        # 3. Destinatário (CRITICAL)
        all_discrepancies.extend(self.validar_destinatario(cte, nfe))
        
        # 4. Transportadora (CRITICAL)
        all_discrepancies.extend(self.validar_transportadora(cte, nfe))
        
        # 5. UF Origem/Destino (CRITICAL/HIGH)
        all_discrepancies.extend(self.validar_uf_origem_destino(cte, nfe))
        
        # 6. CFOP × tpCTe (HIGH)
        all_discrepancies.extend(self.validar_cfop_tpcte(nfe, cte))
        
        # 7. Frete na base ICMS (CRITICAL - rule separada mas dispara aqui)
        all_discrepancies.extend(self.validar_frete_base_icms(cte, nfe))
        
        # 8. ICMS operação (HIGH)
        all_discrepancies.extend(self.validar_icms_operacao(cte, nfe))
        
        # 9. Redespacho (MEDIUM)
        if context.ctes_list:
            all_discrepancies.extend(self.validar_redespacho(nfe, context.ctes_list))
        
        return all_discrepancies
```

---

## 🧮 Exemplos de Recuperação (Success Fee)

### Caso 1: Frete no CT-e NÃO está na NF-e
```
CT-e: vTPrest = 5.500,00 (vCarga=5.000 + vFrete=500)
NF-e: vNF = 5.000,00, vFrete = 0,00, CST=00

Divergência: R$ 500,00 de frete não destacado na NF-e
ICMS sonegado: 500 × 18% (SP) = R$ 90,00
Recuperação: R$ 90,00 + multa + juros
Success Fee (15%): R$ 13,50 + percentual sobre multa/juros
```

### Caso 2: Peso CT-e < Peso NF-e (Carga Geral 5%)
```
CT-e: peso = 9.500 kg
NF-e: peso = 10.000 kg
Tolerância 5%: 9.500 kg (mínimo)
Divergência: 500 kg (5% exato - limite)
```

### Caso 3: UF Destino Diferente
```
CT-e: UF Fim = RJ
NF-e: UF Destino = SP
Impacto: ICMS interestadual SP→RJ (12%) vs SP→SP (18% interna)
DIFAL/FCP calculado errado
Recuperação: Diferença ICMS + multa
```

### Caso 4: Transportadora Diferente
```
CT-e emitente: CNPJ 11.111.111/0001-11
NF-e transportadora: CNPJ 22.222.222/0001-22
Risco: Fraude, sonegação, CT-e frio
```

---

## 🧪 Casos de Teste

```python
# test_cross_cte_nfe_valores_vtprest_vnf
# CT-e vTPrest=5500, NF-e vNF=5000 → CRITICAL (10% diff > 2%)

# test_cross_cte_nfe_valores_dentro_tolerancia
# CT-e vTPrest=5100, NF-e vNF=5000 → OK (2% = 100, diff=100)

# test_cross_cte_nfe_peso_carga_geral
# CT-e peso=9500, NF-e peso=10000 → OK (5% tolerância)

# test_cross_cte_nfe_peso_abaixo_tolerancia
# CT-e peso=9000, NF-e peso=10000 → HIGH (10% > 5%)

# test_cross_cte_nfe_destinatario_cnpj_diferente
# CT-e CNPJ=111, NF-e CNPJ=222 → CRITICAL

# test_cross_cte_nfe_transportadora_diferente
# CT-e emit=111, NF-e transp=222 → CRITICAL

# test_cross_cte_nfe_uf_destino_diferente
# CT-e UFFim=RJ, NF-e destUF=SP → CRITICAL

# test_cross_cte_nfe_cfop_frete_sem_cte
# NF-e CFOP=5352, sem CT-e → HIGH

# test_cross_cte_nfe_frete_cte_nao_em_nfe
# CT-e tem frete, NF-e vFrete=0 → CRITICAL

# test_cross_cte_nfe_redespacho_sem_complementar
# 2 CT-es mesmo NF-e, transportadoras diferentes, sem tpEmis=2/3/4 → MEDIUM
```

---

## ⚠️ Pontos Críticos para Auditoria

1. **refNFe OBRIGATÓRIO** no CT-e para rastreabilidade
2. **Um CT-e pode referenciar MÚLTIPLAS NF-es** (carga fracionada)
3. **Uma NF-e pode ter MÚLTIPLOS CT-es** (redespacho, subcontratação)
4. **Tolerâncias configuráveis** por cliente/tipo carga
5. **Success Fee calculado sobre**: ICMS sonegado + multa + juros
6. **Prescrição**: 5 anos (CT-e/NF-e) - buscar histórico
7. **Documentos complementares**: Carta correção NF-e, CT-e complementar

---

## 📦 JSON para backend/app/data/nfe/cross_cte_nfe_regras.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Lei 11.442/2007, Decreto 9.209/2017, Manual CT-e 3.00, Manual NF-e 4.00",
  "tolerancias": {
    "valor_total_pct": 0.02,
    "valor_total_minimo": 10.0,
    "peso_carga_geral_pct": 0.05,
    "peso_granel_pct": 0.20,
    "frete_valor_pct": 0.05,
    "frete_valor_minimo": 5.0,
    "cubagem_pct": 0.10
  },
  "validacoes_critical": [
    "VALOR_TOTAL_vTPrest_vs_vNF",
    "DESTINATARIO_CNPJ_CPF",
    "TRANSPORTADORA_CNPJ",
    "UF_DESTINO",
    "FRETE_NA_BASE_ICMS"
  ],
  "validacoes_high": [
    "PESO",
    "DESTINATARIO_IE",
    "UF_ORIGEM",
    "CFOP_TPCTE",
    "ICMS_OPERACAO"
  ],
  "validacoes_medium": [
    "DESTINATARIO_CIDADE",
    "VOLUMES_QUANTIDADE",
    "REDESPACHO_SEM_COMPLEMENTAR",
    "FRETE_VALOR_DIVERGENTE"
  ],
  "cfop_frete_obrigatorio_cte": [
    "5352", "5353", "5354", "6352", "6353", "6354"
  ],
  "cfop_sem_frete": [
    "5355", "6355", "5101", "5102", "6101", "6102", "5103", "6103"
  ],
  "tipos_carga_granel": [
    "GRANEL_LIQUIDO", "GRANEL_SOLIDO", "GRANEL_GASOSO"
  ],
  "regras_sucess_fee": {
    "base_calculo": "ICMS_sonegado + multa + juros",
    "percentual_padrao": 0.15,
    "prescricao_anos": 5
  }
}
```

---

## 🔗 Referências

- [Lei 11.442/2007 - Transporte Cargas](http://www.planalto.gov.br/ccivil_03/_ato2004-2006/2007/lei/l11442.htm)
- [Decreto 9.209/2017 - CT-e](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2017/decreto/D9209.htm)
- [Manual CT-e 3.00](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Manual NF-e 4.00](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Convênio ICMS 188/2017](https://www.confaz.fazenda.gov.br/legislacao/convenios/2017/convenio-icms-188-2017)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Conforme atualização Manual CT-e/NF-e  

---

> **🎯 ESTA É A REGRA CORE DO NEGÓCIO** - O cruzamento CT-e × NF-e é onde o AvertaSaaS encontra as discrepâncias que geram **success fee**. Cada validação acima representa uma oportunidade de recuperação de valores para o cliente.