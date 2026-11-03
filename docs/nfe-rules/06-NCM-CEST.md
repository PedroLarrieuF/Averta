# NCM/CEST Validação - Regra NFE_NCM_CEST_VALIDACAO

**Rule Code:** `NFE_NCM_CEST_VALIDACAO`  
**Tipo:** `NCM_CEST`  
**Severidade:** `HIGH`  
**Tags:** `ncm, cest, st, classification, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/ncm_cest_st.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_ncm_cest_valido`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Convênio ICMS 38/2001** | CEST - Produtos sujeitos a ST | Vigente |
| **Convênio ICMS 52/2017** | CEST atualizado | Vigente |
| **Decreto 6.759/2009** | TIPI - Tabela Incidência IPI (base NCM) | Vigente |
| **Ajuste SINIEF 19/2016** | NCM/CEST na NF-e 4.00 | Vigente |
| **RICMS/UF** | MVA/IVA por NCM/CEST por estado | Vigente |

---

## 🎯 NCM (Nomenclatura Comum do Mercosul)

### Estrutura NCM (8 dígitos + 2 dígitos verificador = 10 dígitos)
```
NCM: 3004.90.00
│   │  │  └─ Subitem (2 dígitos)
│   │  └──── Item (2 dígitos)
│   └─────── Subposição (2 dígitos)
└─────────── Posição (4 dígitos)
```

### Hierarquia
- **Capítulo** (2 dígitos): 97 capítulos
- **Posição** (4 dígitos): ~1.200 posições
- **Subposição** (6 dígitos): ~5.000 subposições
- **Item** (8 dígitos): ~10.000 itens NCM
- **Subitem** (10 dígitos): Específico Brasil

---

## 🎯 CEST (Código Especificador da Substituição Tributária)

### Estrutura CEST (7 dígitos + 2 dígitos = 9 dígitos)
```
CEST: 04.001.00
│   │   └─ Item (2 dígitos)
│   └───── Subitem (3 dígitos)
└──────── Segmento (2 dígitos)
```

### Segmentos CEST (2 dígitos)
| Código | Segmento |
|--------|----------|
| 01 | Bebidas |
| 02 | Fumos |
| 03 | Combustíveis e Lubrificantes |
| 04 | Medicamentos |
| 05 | Perfumaria e Cosméticos |
| 06 | Produtos de Limpeza |
| 07 | Papel e Papelão |
| 08 | Têxteis e Vestuário |
| 09 | Calçados |
| 10 | Ferro e Aço |
| 11 | Tubos e Conexões |
| 12 | Máquinas e Equipamentos |
| 13 | Informática e Telecomunicações |
| 14 | Veículos |
| 15 | Móveis |
| 16 | Materiais de Construção |
| 17 | Produtos Alimentícios |
| 18 | Produtos Químicos |
| 19 | Plásticos |
| 20 | Vidros |
| 21 | Cerâmicas |
| 22 | Outros |

---

## 🔗 Mapeamento NCM → CEST → ST

### Exemplos Principais (Convênio 38/2001 + 52/2017)

| NCM | Descrição | CEST | Segmento | ST? | MVA Original |
|-----|-----------|------|----------|-----|--------------|
| 2203.00.00 | Cervejas | 01.001.00 | 01 Bebidas | SIM | 66,67% |
| 2204.10.00 | Vinhos espumantes | 01.002.00 | 01 Bebidas | SIM | 66,67% |
| 2208.20.00 | Aguardentes | 01.003.00 | 01 Bebidas | SIM | 66,67% |
| 2402.20.00 | Cigarros | 02.001.00 | 02 Fumos | SIM | 100,00% |
| 2710.12.00 | Óleos diesel | 03.001.00 | 03 Combustíveis | SIM | 40,00% |
| 2710.19.00 | Lubrificantes | 03.002.00 | 03 Combustíveis | SIM | 40,00% |
| 3004.90.00 | Medicamentos | 04.001.00 | 04 Medicamentos | SIM | 60,00% |
| 3304.99.00 | Cosméticos | 05.001.00 | 05 Perfumaria | SIM | 66,67% |
| 3401.11.00 | Sabonetes | 06.001.00 | 06 Limpeza | SIM | 40,00% |
| 4011.10.00 | Pneus novos | 07.001.00 | 07 Borracha | SIM | 40,00% |
| 4818.10.00 | Papel higiênico | 08.001.00 | 08 Papel | SIM | 40,00% |
| 6109.10.00 | Camisetas algodão | 09.001.00 | 09 Têxteis | SIM | 40,00% |
| 6403.99.00 | Calçados couro | 10.001.00 | 10 Calçados | SIM | 40,00% |
| 7208.00.00 | Chapas aço | 11.001.00 | 11 Ferro/Aço | SIM | 20,00% |
| 7306.00.00 | Tubos aço | 12.001.00 | 12 Tubos | SIM | 20,00% |
| 8471.30.00 | Notebooks | 13.001.00 | 13 Informática | SIM | 40,00% |
| 8517.12.00 | Celulares | 13.002.00 | 13 Telecomunicações | SIM | 40,00% |
| 8703.00.00 | Automóveis | 14.001.00 | 14 Veículos | SIM | 66,67% |
| 9403.00.00 | Móveis | 15.001.00 | 15 Móveis | SIM | 40,00% |

> **Total**: ~1.200 NCMs com CEST definido no Convênio 38/2001 + atualizações

---

## 🔍 Lógica de Detecção no Engine

```python
class NFENCMESTValidacaoRule(BaseRule):
    code = "NFE_NCM_CEST_VALIDACAO"
    relevance_tags = {"ncm", "cest", "st", "classification", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.ncm_produto is not None
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        ncm = context.ncm_produto[:8]  # 8 dígitos
        cest_informado = context.cest_produto
        
        # 1. Buscar CEST oficial para o NCM
        cest_oficial = self.get_cest_by_ncm(ncm)
        
        if cest_oficial:
            # NCM tem CEST oficial - validar
            if not cest_informado:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CEST_OBRIGATORIO_NAO_INFORMADO",
                        "ncm": ncm,
                        "cest_oficial": cest_oficial,
                        "cest_informado": None,
                        "risco": "Produto sujeito a ST sem CEST na NF-e"
                    }
                ))
            elif cest_informado != cest_oficial:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CEST_DIVERGENTE",
                        "ncm": ncm,
                        "cest_oficial": cest_oficial,
                        "cest_informado": cest_informado,
                        "risco": "CEST informado não confere com NCM"
                    }
                ))
            
            # 2. Validar se CST/CSOSN condiz com ST
            self.validar_cst_st_consistencia(context, discrepancies, cest_oficial)
            
            # 3. Validar MVA/IVA para o CEST/UF
            self.validar_mva_uf(context, discrepancies, cest_oficial)
        
        else:
            # NCM NÃO tem CEST oficial
            if cest_informado:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "CEST_INFORMADO_SEM_NCM_SUJEITO",
                        "ncm": ncm,
                        "cest_informado": cest_informado,
                        "risco": "CEST informado mas NCM não está na lista ST"
                    }
                ))
            
            # Verificar se CST indica ST mas NCM não tem CEST
            if context.cst_icms in ["10", "30", "60", "70"]:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CST_ST_SEM_CEST_NCM",
                        "ncm": ncm,
                        "cst": context.cst_icms,
                        "risco": "CST indica ST mas NCM não tem CEST oficial"
                    }
                ))
        
        # 4. Validar NCM válido (existe na TIPI)
        if not self.ncm_valido(ncm):
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={
                    "validacao": "NCM_INVALIDO",
                    "ncm": ncm,
                    "risco": "NCM não existe na TIPI vigente"
                }
            ))
        
        return discrepancies
    
    def validar_cst_st_consistencia(self, context, discrepancies, cest):
        """Valida se CST/CSOSN condiz com produto ter ST"""
        cst = context.cst_icms
        csosn = context.csosn_icms
        
        csts_com_st = {"10", "30", "60", "70"}
        csosns_com_st = {"201", "202", "203", "500"}
        
        tem_st_cst = cst in csts_com_st
        tem_st_csosn = csosn in csosns_com_st
        
        if tem_st_cst or tem_st_csosn:
            # CST indica ST - NCM deve ter CEST
            if not cest:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "validacao": "CST_ST_MAS_NCM_SEM_CEST",
                        "cst": cst,
                        "csosn": csosn,
                        "ncm": context.ncm_produto[:8]
                    }
                ))
        else:
            # CST NÃO indica ST - mas NCM tem CEST
            if cest:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "NCM_COM_CEST_MAS_CST_SEM_ST",
                        "cst": cst,
                        "csosn": csosn,
                        "ncm": context.ncm_produto[:8],
                        "cest": cest,
                        "risco": "Produto sujeito a ST mas CST não prevê ST"
                    }
                ))
    
    def validar_mva_uf(self, context, discrepancies, cest):
        """Valida MVA/IVA para o CEST na UF destino"""
        mva_original = self.get_mva_original(cest)
        mva_ajustada = self.get_mva_ajustada(cest, context.uf_destino)
        
        if mva_ajustada and mva_original:
            if abs(mva_ajustada - mva_original) > 0.01:  # Diferença > 1%
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "validacao": "MVA_AJUSTADA_UF_DESTINO",
                        "cest": cest,
                        "uf_destino": context.uf_destino,
                        "mva_original": mva_original,
                        "mva_ajustada": mva_ajustada,
                        "observacao": f"UF {context.uf_destino} ajusta MVA para este CEST"
                    }
                ))
```

---

## 🧮 Exemplos Práticos

### Exemplo 1: Medicamento (NCM 3004.90.00)
```
NF-e item:
- NCM: 30049000
- CEST informado: 04.001.00
- CST: 10 (com ST)
- UF Destino: RJ

Validação:
✓ NCM 30049000 → CEST oficial 04.001.00 (confere)
✓ CST 10 indica ST (confere com produto ter CEST)
✓ RJ ajusta MVA medicamentos para 69% (original 60%)
✓ VÁLIDO
```

### Exemplo 2: Cosmético sem CEST
```
NF-e item:
- NCM: 33049900
- CEST informado: (vazio)
- CST: 00 (sem ST)
- UF Destino: SP

Validação:
✗ NCM 33049900 → CEST oficial 05.001.00
✗ CEST obrigatório não informado
✗ CST 00 não prevê ST mas produto tem CEST
→ DIVERGÊNCIA HIGH: CEST_OBRIGATORIO_NAO_INFORMADO
→ DIVERGÊNCIA MEDIUM: NCM_COM_CEST_MAS_CST_SEM_ST
```

### Exemplo 3: CEST Divergente
```
NF-e item:
- NCM: 22030000 (Cerveja)
- CEST informado: 01.002.00 (Vinho - ERRADO)
- CST: 10

Validação:
✗ NCM 22030000 → CEST oficial 01.001.00 (Cerveja)
✗ CEST informado 01.002.00 ≠ 01.001.00
→ DIVERGÊNCIA HIGH: CEST_DIVERGENTE
```

### Exemplo 4: Produto Não Sujeito a ST com CEST
```
NF-e item:
- NCM: 10010000 (Trigo - não tem CEST)
- CEST informado: 17.001.00
- CST: 00

Validação:
✗ NCM 10010000 não está na lista CEST
✗ CEST informado indevidamente
→ DIVERGÊNCIA MEDIUM: CEST_INFORMADO_SEM_NCM_SUJEITO
```

---

## 🧪 Casos de Teste

```python
# test_nfe_ncm_cest_valido_medicamento
# NCM 30049000, CEST 04.001.00, CST 10 → OK

# test_nfe_ncm_cest_obrigatorio_nao_informado
# NCM 30049000, CEST vazio, CST 10 → HIGH

# test_nfe_ncm_cest_divergente
# NCM 22030000, CEST 01.002.00 (errado) → HIGH

# test_nfe_ncm_cest_informado_sem_ncm_sujeito
# NCM 10010000 (sem CEST), CEST 17.001.00 → MEDIUM

# test_nfe_ncm_cst_st_sem_cest
# CST 10, NCM sem CEST → HIGH

# test_nfe_ncm_cest_com_cst_sem_st
# NCM com CEST, CST 00 → MEDIUM

# test_nfe_ncm_invalido
# NCM 99999999 (não existe) → HIGH

# test_nfe_ncm_mva_ajustada_uf
# NCM 30049000, UF RJ → MVA 69% (ajustada) vs 60% (original) → MEDIUM info
```

---

## ⚠️ Pontos de Atenção

1. **CEST OBRIGATÓRIO** para NCMs listados no Convênio 38/2001 + 52/2017
2. **NCM 8 dígitos** na NF-e (campo `cProd`/`NCM`), CEST 7 dígitos (campo `CEST`)
3. **CST/CSOSN × CEST consistência**: Se tem CEST → CST deve prever ST (10,30,60,70 ou CSOSN 201,202,203,500)
4. **MVA Original** (Convênio 38/2001) vs **MVA Ajustada** (por UF destino)
5. **Atualização Anual**: Convênio ICMS 52/2017 atualiza CEST anualmente
6. **TIPI Vigente**: NCM deve existir na Tabela Incidência IPI
7. **Cross com ST**: Ver regra NFE_ICMS_ST_VALIDACAO (02-ICMS-ST.md)
8. **Simples Nacional**: Optante Simples pode ter CEST mas regras diferentes (ver 16-REGRAS-ESPECIAIS.md)

---

## 📦 JSON para backend/app/data/nfe/ncm_cest_st.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "source": "Convênio ICMS 38/2001, 52/2017, Decreto 6.759/2009 (TIPI)",
  "ncm_cest": {
    "22030000": {"cest": "01.001.00", "descricao": "Cervejas", "segmento": "01", "mva_original": 0.6667, "tem_st": true},
    "22041000": {"cest": "01.002.00", "descricao": "Vinhos espumantes", "segmento": "01", "mva_original": 0.6667, "tem_st": true},
    "22082000": {"cest": "01.003.00", "descricao": "Aguardentes", "segmento": "01", "mva_original": 0.6667, "tem_st": true},
    "24022000": {"cest": "02.001.00", "descricao": "Cigarros", "segmento": "02", "mva_original": 1.0000, "tem_st": true},
    "27101200": {"cest": "03.001.00", "descricao": "Óleos diesel", "segmento": "03", "mva_original": 0.4000, "tem_st": true},
    "27101900": {"cest": "03.002.00", "descricao": "Lubrificantes", "segmento": "03", "mva_original": 0.4000, "tem_st": true},
    "30049000": {"cest": "04.001.00", "descricao": "Medicamentos", "segmento": "04", "mva_original": 0.6000, "tem_st": true},
    "33049900": {"cest": "05.001.00", "descricao": "Cosméticos", "segmento": "05", "mva_original": 0.6667, "tem_st": true},
    "34011100": {"cest": "06.001.00", "descricao": "Sabonetes", "segmento": "06", "mva_original": 0.4000, "tem_st": true},
    "40111000": {"cest": "07.001.00", "descricao": "Pneus novos", "segmento": "07", "mva_original": 0.4000, "tem_st": true},
    "48181000": {"cest": "08.001.00", "descricao": "Papel higiênico", "segmento": "08", "mva_original": 0.4000, "tem_st": true},
    "61091000": {"cest": "09.001.00", "descricao": "Camisetas algodão", "segmento": "09", "mva_original": 0.4000, "tem_st": true},
    "64039900": {"cest": "10.001.00", "descricao": "Calçados couro", "segmento": "10", "mva_original": 0.4000, "tem_st": true},
    "72080000": {"cest": "11.001.00", "descricao": "Chapas aço", "segmento": "11", "mva_original": 0.2000, "tem_st": true},
    "73060000": {"cest": "12.001.00", "descricao": "Tubos aço", "segmento": "12", "mva_original": 0.2000, "tem_st": true},
    "84713000": {"cest": "13.001.00", "descricao": "Notebooks", "segmento": "13", "mva_original": 0.4000, "tem_st": true},
    "85171200": {"cest": "13.002.00", "descricao": "Celulares", "segmento": "13", "mva_original": 0.4000, "tem_st": true},
    "87030000": {"cest": "14.001.00", "descricao": "Automóveis", "segmento": "14", "mva_original": 0.6667, "tem_st": true},
    "94030000": {"cest": "15.001.00", "descricao": "Móveis", "segmento": "15", "mva_original": 0.4000, "tem_st": true}
  },
  "segmentos_cest": {
    "01": "Bebidas", "02": "Fumos", "03": "Combustíveis e Lubrificantes",
    "04": "Medicamentos", "05": "Perfumaria e Cosméticos", "06": "Produtos de Limpeza",
    "07": "Papel e Papelão", "08": "Têxteis e Vestuário", "09": "Calçados",
    "10": "Ferro e Aço", "11": "Tubos e Conexões", "12": "Máquinas e Equipamentos",
    "13": "Informática e Telecomunicações", "14": "Veículos", "15": "Móveis",
    "16": "Materiais de Construção", "17": "Produtos Alimentícios",
    "18": "Produtos Químicos", "19": "Plásticos", "20": "Vidros",
    "21": "Cerâmicas", "22": "Outros"
  },
  "mva_ajustada_uf": {
    "RJ": {"04.001.00": 0.69, "05.001.00": 0.7667, "14.001.00": 0.80},
    "BA": {"04.001.00": 0.63, "05.001.00": 0.70},
    "MG": {"02.001.00": 1.10}
  },
  "csts_com_st": ["10", "30", "60", "70"],
  "csosns_com_st": ["201", "202", "203", "500"]
}
```

---

## 🔗 Referências

- [Convênio ICMS 38/2001 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2001/convenio-icms-38-2001)
- [Convênio ICMS 52/2017 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2017/convenio-icms-52-2017)
- [TIPI - Tabela Incidência IPI](https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/tipi)
- [Portal CEST - Receita Federal](https://www.nfe.fazenda.gov.br/portal/listaConteudo.aspx?tipoConteudo=P2V5c0lHVnliRzlJYjI1MWMyVnlkRzl5)

---

**Última Atualização:** 2026-11-03  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar Convênio ICMS 52 atualizações)