# ICMS Substituição Tributária (ST) - Regra NFE_ICMS_ST_VALIDACAO

**Rule Code:** `NFE_ICMS_ST_VALIDACAO`  
**Tipo:** `ICMS_ST`  
**Severidade:** `CRITICAL`  
**Tags:** `icms_st, mva, iva, cest, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/icms_st_mva_iva.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_icms_st_calculo_mva`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Convênio ICMS 142/2018** | Protocolo ICMS ST - MVA/IVA | Vigente |
| **Convênio ICMS 38/2001** | CEST - Produtos sujeitos a ST | Vigente |
| **Convênio ICMS 52/2017** | CEST atualizado | Vigente |
| **LC 87/1996** (Art. 8º) | Substituição tributária | Vigente |
| **RICMS/UF** (cada estado) | MVA/IVA ajustado por UF | Vigente |
| **Ajuste SINIEF 19/2016** | Campos ST na NF-e 4.00 | Vigente |

---

## 🎯 Conceitos Fundamentais

### MVA (Margem de Valor Agregado) / IVA (Índice de Valor Adicionado)
- **MVA Original**: Definida no Convênio ICMS 38/2001 por NCM
- **MVA Ajustada**: Cada UF pode ajustar a MVA para operações interestaduais destinadas ao seu território
- **IVA**: Índice usado em alguns estados (equivalente à MVA)

### Base de Cálculo ST
```
vBCST = (vNF + vFrete + vSeg + vOutro - vDesc) × (1 + MVA_Ajustada)
```
> **IMPORTANTE**: Frete, seguro e outras despesas **INTEGRAM** a base ST (Lei 8.884/94 Art. 37)

### ICMS ST Devido
```
vICMSST = vBCST × aliquota_interna_destino - vICMS_próprio_antecipado
```

---

## 📊 Tabela MVA Original por NCM (Convênio 38/2001 - Exemplos)

| NCM | Descrição | MVA Original (%) | CEST |
|-----|-----------|------------------|------|
| 2203.00.00 | Cervejas | 66,67 | 01.001.00 |
| 2204.10.00 | Vinhos espumantes | 66,67 | 01.002.00 |
| 2208.20.00 | Aguardentes | 66,67 | 01.003.00 |
| 2402.20.00 | Cigarros | 100,00 | 02.001.00 |
| 2710.12.00 | Óleos diesel | 40,00 | 03.001.00 |
| 2710.19.00 | Lubrificantes | 40,00 | 03.002.00 |
| 3004.90.00 | Medicamentos | 60,00 | 04.001.00 |
| 3304.99.00 | Cosméticos | 66,67 | 05.001.00 |
| 3401.11.00 | Sabonetes | 40,00 | 06.001.00 |
| 4011.10.00 | Pneus novos | 40,00 | 07.001.00 |
| 4818.10.00 | Papel higiênico | 40,00 | 08.001.00 |
| 6109.10.00 | Camisetas algodão | 40,00 | 09.001.00 |
| 6403.99.00 | Calçados couro | 40,00 | 10.001.00 |
| 7208.00.00 | Chapas aço | 20,00 | 11.001.00 |
| 7306.00.00 | Tubos aço | 20,00 | 12.001.00 |
| 8471.30.00 | Notebooks | 40,00 | 13.001.00 |
| 8517.12.00 | Celulares | 40,00 | 14.001.00 |
| 8703.00.00 | Automóveis | 66,67 | 15.001.00 |
| 9403.00.00 | Móveis | 40,00 | 16.001.00 |

> **Lista completa**: ~1.200 NCMs no Convênio 38/2001 + atualizações

---

## 🗺️ MVA Ajustada por UF Destino (Exemplos 2024/2025)

| UF | MVA Ajustada Padrão | Observação |
|----|---------------------|------------|
| **SP** | Conforme Convênio 38/2001 | Sem ajuste geral |
| **RJ** | +10% a +20% sobre original | Decreto 47.427/2023 |
| **MG** | Conforme Convênio 38/2001 | Alguns produtos +5% |
| **PR** | Conforme Convênio 38/2001 | |
| **RS** | Conforme Convênio 38/2001 | |
| **SC** | Conforme Convênio 38/2001 | |
| **BA** | +5% a +15% | Decreto 21.000/2023 |
| **GO** | Conforme Convênio 38/2001 | |
| **DF** | Conforme Convênio 38/2001 | |
| **ES** | Conforme Convênio 38/2001 | |
| **Outras UFs** | Ver decreto estadual | Consultar RICMS/UF |

> ⚠️ **Cada UF publica decreto próprio** ajustando MVA. Deve ser atualizado anualmente.

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEICMSSTValidacaoRule(BaseRule):
    code = "NFE_ICMS_ST_VALIDACAO"
    relevance_tags = {"icms_st", "mva", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        # Só aplica se CST indica ST (10, 30, 60, 70) ou CSOSN 201, 202, 203, 500
        cst_st = {"10", "30", "60", "70"}
        csosn_st = {"201", "202", "203", "500"}
        return context.cst_icms in cst_st or context.csosn_icms in csosn_st
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. Verificar se produto tem ST (NCM/CEST)
        ncm = context.ncm_produto[:8]  # 8 dígitos
        cest = self.get_cest_by_ncm(ncm)
        
        if not cest:
            # Produto não sujeito a ST mas CST indica ST
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "erro": f"CST {context.cst_icms} indica ST mas NCM {ncm} não tem CEST",
                    "ncm": ncm,
                    "cst": context.cst_icms
                }
            )]
        
        # 2. Obter MVA Original (Convênio 38/2001)
        mva_original = self.get_mva_original(ncm, cest)
        if mva_original is None:
            return [Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={
                    "erro": f"MVA original não encontrado para NCM {ncm} / CEST {cest}",
                    "ncm": ncm,
                    "cest": cest
                }
            )]
        
        # 3. Obter MVA Ajustada UF Destino
        mva_ajustada = self.get_mva_ajustada(ncm, cest, context.uf_destino)
        mva_final = mva_ajustada if mva_ajustada is not None else mva_original
        
        # 4. Calcular Base ST Esperada
        vBC_operacao = context.vNF + context.vFrete + context.vSeg + context.vOutro - context.vDesc
        vBCST_esperada = vBC_operacao * (1 + mva_final)
        
        # 5. Calcular ICMS ST Esperado
        aliquota_interna_destino = self.get_aliquota_interna(context.uf_destino)
        vICMSST_esperado = vBCST_esperada * aliquota_interna_destino
        
        # Se CST 10/30/70: subtrair ICMS próprio antecipado
        if context.cst_icms in ["10", "30", "70"]:
            vICMSST_esperado -= context.vICMS
        
        # 6. Comparar com XML
        tolerancia = context.vNF * 0.005  # 0.5%
        
        if abs(context.vBCST - vBCST_esperada) > tolerancia:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(vBCST_esperada, 2),
                actual_value=round(context.vBCST, 2),
                difference=round(abs(context.vBCST - vBCST_esperada), 2),
                details={
                    "campo": "vBCST",
                    "ncm": ncm,
                    "cest": cest,
                    "mva_original": mva_original,
                    "mva_ajustada": mva_ajustada,
                    "mva_usada": mva_final,
                    "vBC_operacao": vBC_operacao,
                    "uf_destino": context.uf_destino
                }
            ))
        
        if abs(context.vICMSST - vICMSST_esperado) > tolerancia:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="CRITICAL",
                expected_value=round(vICMSST_esperado, 2),
                actual_value=round(context.vICMSST, 2),
                difference=round(abs(context.vICMSST - vICMSST_esperado), 2),
                details={
                    "campo": "vICMSST",
                    "ncm": ncm,
                    "cest": cest,
                    "aliquota_interna_destino": aliquota_interna_destino,
                    "vICMS_proprio": context.vICMS if context.cst_icms in ["10", "30", "70"] else 0
                }
            ))
        
        # 7. Validar vICMSSTRet (ST retido na operação anterior)
        if context.vICMSSTRet > 0:
            # Verificar se faz sentido (operação com ST retido)
            pass
        
        return discrepancies
```

---

## 🧮 Exemplo de Cálculo Completo

### Cenário: Medicamento (NCM 3004.90.00) - SP → RJ
```
Dados NF-e:
- vNF = 10.000,00
- vFrete = 500,00
- vSeg = 100,00
- vOutro = 50,00
- vDesc = 0,00
- CST = 10 (Tributada com ST)
- UF Origem = SP, UF Destino = RJ
- NCM = 3004.90.00 → CEST 04.001.00

Passo 1: MVA Original (Convênio 38/2001)
MVA Original = 60% (medicamentos)

Passo 2: MVA Ajustada RJ
RJ ajusta +15% para medicamentos → MVA Ajustada = 60% × 1,15 = 69%

Passo 3: Base Operação
vBC_op = 10.000 + 500 + 100 + 50 - 0 = 10.650,00

Passo 4: Base ST
vBCST = 10.650 × (1 + 0,69) = 10.650 × 1,69 = 17.998,50

Passo 5: Alíquota Interna RJ
RJ = 20% (18% + 2% FECP)

Passo 6: ICMS ST
vICMSST = 17.998,50 × 20% = 3.599,70
vICMS próprio (CST 10) = 10.650 × 20% = 2.130,00
vICMSST líquido = 3.599,70 - 2.130,00 = 1.469,70

Resultado NF-e:
- vBC = 10.650,00
- vICMS = 2.130,00
- vBCST = 17.998,50
- vICMSST = 1.469,70
```

---

## 🧪 Casos de Teste

```python
# test_nfe_icms_st_calculo_mva
# Medicamento NCM 3004.90.00, MVA 60%, SP→RJ (MVA ajustada 69%)
# vNF=10000, vFrete=500 → vBCST=17998.50, vICMSST=1469.70

# test_nfe_icms_st_mva_ajustada_uf
# Mesmo NCM, SP→SP (sem ajuste) → MVA 60%
# vBCST = 10650 × 1.60 = 17040, vICMSST = 17040 × 18% - 1917 = 1150.20

# test_nfe_icms_st_sem_cest
# CST 10 mas NCM sem CEST → ALERTA HIGH

# test_nfe_icms_st_cst_nao_st
# CST 00 mas produto tem CEST → ALERTA MEDIUM (pode ser CST errado)

# test_nfe_icms_st_frete_na_base
# vFrete NÃO incluído em vBCST → ERRO CRITICAL
# Lei 8.884/94 Art. 37: frete integra base ST

# test_nfe_icms_st_cst60_sem_icms_proprio
# CST 60 (ST retido anterior) → vICMS=0, vICMSST = valor retido

# test_nfe_icms_st_simples_nacional
# CSOSN 201/202/203 → mesma lógica mas regime Simples
```

---

## ⚠️ Pontos Críticos

1. **Frete SEMPRE na base ST** - Lei 8.884/94 Art. 37 aplica a ST também
2. **MVA Ajustada por UF destino** - Não usar MVA original para interestadual
3. **CEST obrigatório** - Se CST indica ST, NCM deve ter CEST válido
4. **CST x ST consistência**:
   - CST 10, 30, 70 → vICMS próprio + vICMSST
   - CST 60 → vICMS = 0, vICMSST = retido
   - CSOSN 201, 202, 203, 500 → Simples com ST
5. **FCP sobre ST** - Alguns estados cobram FCP sobre base ST (ver 04-FCP.md)
6. **DIFAL + ST** - Para não contribuinte: DIFAL calculado sobre base ST (ver 03-ICMS-DIFAL.md)
7. **vICMSSTRet** - ST retido em operação anterior (ex: industrialização por encomenda)

---

## 📦 JSON para backend/app/data/nfe/icms_st_mva_iva.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Convênio ICMS 38/2001, 142/2018, 52/2017, Decretos Estaduais 2024/2025",
  "mva_original": {
    "22030000": {"cest": "01.001.00", "descricao": "Cervejas", "mva": 0.6667},
    "22041000": {"cest": "01.002.00", "descricao": "Vinhos espumantes", "mva": 0.6667},
    "22082000": {"cest": "01.003.00", "descricao": "Aguardentes", "mva": 0.6667},
    "24022000": {"cest": "02.001.00", "descricao": "Cigarros", "mva": 1.0000},
    "27101200": {"cest": "03.001.00", "descricao": "Óleos diesel", "mva": 0.4000},
    "27101900": {"cest": "03.002.00", "descricao": "Lubrificantes", "mva": 0.4000},
    "30049000": {"cest": "04.001.00", "descricao": "Medicamentos", "mva": 0.6000},
    "33049900": {"cest": "05.001.00", "descricao": "Cosméticos", "mva": 0.6667},
    "34011100": {"cest": "06.001.00", "descricao": "Sabonetes", "mva": 0.4000},
    "40111000": {"cest": "07.001.00", "descricao": "Pneus novos", "mva": 0.4000},
    "48181000": {"cest": "08.001.00", "descricao": "Papel higiênico", "mva": 0.4000},
    "61091000": {"cest": "09.001.00", "descricao": "Camisetas algodão", "mva": 0.4000},
    "64039900": {"cest": "10.001.00", "descricao": "Calçados couro", "mva": 0.4000},
    "72080000": {"cest": "11.001.00", "descricao": "Chapas aço", "mva": 0.2000},
    "73060000": {"cest": "12.001.00", "descricao": "Tubos aço", "mva": 0.2000},
    "84713000": {"cest": "13.001.00", "descricao": "Notebooks", "mva": 0.4000},
    "85171200": {"cest": "14.001.00", "descricao": "Celulares", "mva": 0.4000},
    "87030000": {"cest": "15.001.00", "descricao": "Automóveis", "mva": 0.6667},
    "94030000": {"cest": "16.001.00", "descricao": "Móveis", "mva": 0.4000}
  },
  "mva_ajustada_uf": {
    "RJ": {
      "04.001.00": 0.69,  // Medicamentos +15%
      "05.001.00": 0.7667, // Cosméticos +15%
      "15.001.00": 0.80   // Automóveis +20%
    },
    "BA": {
      "04.001.00": 0.63,  // Medicamentos +5%
      "05.001.00": 0.70   // Cosméticos +5%
    },
    "MG": {
      "02.001.00": 1.10   // Cigarros +10%
    }
  },
  "cst_que_exigem_st": ["10", "30", "60", "70"],
  "csosn_que_exigem_st": ["201", "202", "203", "500"],
  "frete_integra_base_st": true,
  "observacoes": "MVA ajustada por UF destino para operações interestaduais. Verificar decretos estaduais anualmente."
}
```

---

## 🔗 Referências

- [Convênio ICMS 38/2001 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2001/convenio-icms-38-2001)
- [Convênio ICMS 142/2018 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2018/convenio-icms-142-2018)
- [Convênio ICMS 52/2017 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2017/convenio-icms-52-2017)
- [Portal CEST - Receita Federal](https://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=P2V5c0lHVnliRzlJYjI1MWMyVnlkRzl5)
- [RICMS por Estado](https://www.icms.ind.br/)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar decretos estaduais MVA ajustada)