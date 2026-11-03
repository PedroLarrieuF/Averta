# ICMS Substituição Tributária (ST) - Regra ICMS_ST

**Rule Code:** `ICMS_ST`  
**Tipo:** `ICMS_ST`  
**Severidade:** `HIGH`  
**Tags:** `icms, icms_st`  
**Arquivo de Dados:** `backend/app/data/icms_rules.json` (seção `icms_st`)  
**Teste:** `tests/test_rules_critical.py::test_icms_st_rule`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **LC 87/1996** (Art. 8º, §3º) | Autoriza ST nas operações interestaduais | Vigente |
| **Convênio ICMS 142/2018** | Protocolo ICMS ST (produtos, MVA, IVA) | Vigente |
| **Convênio ICMS 92/2015** | CEST - Código Especificador Substituição Tributária | Vigente |
| **Decretos Estaduais RICMS** | Produtos sujeitos, MVA/IVA por UF | Por UF |

---

## 🎯 Quando Aplica

**Produto sujeito a ST** na UF de **destino** (ou origem, conforme protocolo):
- NCM do produto consta na lista de ST do Convênio 142/2018
- Operação interestadual (UF Origem ≠ UF Destino)
- **Remetente** é **substituto tributário** (indústria/importador/atacadista)
- **Destinatário** é **substituído** (varejista/consumidor final)

**Identificação no XML:**
- `CST = 10, 30, 40, 41, 50, 51, 60, 70, 90` (com ST)
- `CSOSN = 201, 202, 203, 500, 900` (Simples com ST)
- Campo `vBCST`, `pST`, `vICMSST`, `vFCPST`, `pFCPST`

---

## 🧮 Fórmula de Cálculo

### 1. Base de Cálculo do ICMS ST

```python
# BC_ST = (Valor Operação + Frete + Seguro + Outras Despesas - Desconto) × (1 + MVA/100)
# OU (método IVA):
# BC_ST = (Valor Operação + Frete + Seguro + Outras Despesas - Desconto) / (1 - IVA/100)

# Onde:
# MVA = Margem de Valor Agregado (% definido por UF/NCM)
# IVA = Índice de Valor Adicionado (% definido por UF/NCM)

# Valor ICMS ST = BC_ST × Alíquota Interna Destino - ICMS Próprio (se destacado)
# ICMS ST Devido = BC_ST × aliquota_interna_destino - vICMS_operacao
```

### 2. Com FCP (se UF destino tem FCP)

```python
# BC_FCPST = BC_ST
# FCP_ST = BC_ST × aliquota_fcp_destino
# ICMS_ST_Total = ICMS_ST + FCP_ST
```

---

## 📊 Parâmetros por NCM × UF (Exemplos 2024/2025)

### Tabela Referência (Convênio ICMS 142/2018 + Decretos Estaduais)

| NCM | Descrição | CEST | UF | MVA (%) | IVA (%) | Alíq. Interna | Alíq. Interestadual |
|-----|-----------|------|-----|---------|---------|---------------|---------------------|
| **2203.00.00** | Cervejas | 01.001.00 | SP | 41.67% | - | 18% | 12% |
| **2203.00.00** | Cervejas | 01.001.00 | RJ | 51.22% | - | 20% | 12% |
| **2203.00.00** | Cervejas | 01.001.00 | MG | 33.33% | - | 18% | 12% |
| **2204.21.00** | Vinhos | 01.002.00 | SP | 41.67% | - | 18% | 12% |
| **2208.30.00** | Whiskies | 01.003.00 | SP | 55.56% | - | 18% | 12% |
| **2402.20.00** | Cigarros | 02.001.00 | SP | - | 56% | 18% | 12% |
| **2402.20.00** | Cigarros | 02.001.00 | RJ | - | 60% | 20% | 12% |
| **2710.19.21** | Óleo Diesel | 03.001.00 | SP | 13.64% | - | 18% | 12% |
| **2710.19.22** | Gasolina | 03.002.00 | SP | 13.64% | - | 18% | 12% |
| **3004.90.99** | Medicamentos | 04.001.00 | SP | 20.00% | - | 18% | 12% |
| **3304.99.00** | Cosméticos | 05.001.00 | SP | 33.33% | - | 18% | 12% |
| **3401.11.00** | Sabonetes | 05.002.00 | SP | 33.33% | - | 18% | 12% |
| **3923.21.00** | Embalagens plásticas | 06.001.00 | SP | 20.00% | - | 18% | 12% |
| **4819.10.00** | Caixas papelão | 06.002.00 | SP | 20.00% | - | 18% | 12% |
| **7208.51.00** | Chapas aço | 07.001.00 | SP | 13.64% | - | 18% | 12% |
| **8703.21.00** | Automóveis | 08.001.00 | SP | 33.33% | - | 18% | 12% |
| **8711.20.00** | Motocicletas | 08.002.00 | SP | 33.33% | - | 18% | 12% |

> ⚠️ **MVAs/IVAs variam por UF** - Cada estado publica decreto próprio. Acima: exemplos para SP.

---

## 🏷️ CEST - Código Especificador (Convênio ICMS 92/2015)

**Estrutura:** `SS.GGG.CC` (Segmento.Grupo.Código)

| Segmento | Descrição | Exemplos |
|----------|-----------|----------|
| **01** | Bebidas | 01.001.00 Cerveja, 01.002.00 Vinho |
| **02** | Fumos | 02.001.00 Cigarros |
| **03** | Combustíveis | 03.001.00 Diesel, 03.002.00 Gasolina |
| **04** | Medicamentos | 04.001.00 Medicamentos |
| **05** | Perfumaria/Cosméticos | 05.001.00 Cosméticos, 05.002.00 Sabonetes |
| **06** | Material Embalagem | 06.001.00 Plásticos, 06.002.00 Papelão |
| **07** | Siderúrgicos | 07.001.00 Aço |
| **08** | Veículos | 08.001.00 Autos, 08.002.00 Motos |
| **09** | Eletroeletrônicos | 09.001.00 Celulares, 09.002.00 TVs |
| **10** | Móveis | 10.001.00 Móveis |
| **11** | Brinquedos | 11.001.00 Brinquedos |
| **12** | Artigos Esporte | 12.001.00 Bicicletas |
| **13** | Papelaria | 13.001.00 Papéis |
| **14** | Vidros | 14.001.00 Vidros |
| **15** | Cerâmicos | 15.001.00 Pisos |
| **16** | Couro/Calçados | 16.001.00 Calçados |
| **17** | Têxteis | 17.001.00 Confecções |
| **18** | Alimentos | 18.001.00 Carnes, 18.002.00 Laticínios |
| **19** | Produtos Limpeza | 19.001.00 Detergentes |
| **20** | Autopeças | 20.001.00 Peças |
| **21** | Material Construção | 21.001.00 Cimento |
| **22** | Produtos Químicos | 22.001.00 Tintas |
| **23** | Instrumentos Médicos | 23.001.00 Equipamentos |
| **24** | Artigos Plásticos | 24.001.00 Utensílios |
| **25** | Outros | 25.001.00 Diversos |

---

## 🔍 Lógica de Detecção no Engine

```python
class ICMSSTRule(BaseRule):
    code = "ICMS_ST"
    relevance_tags = {"icms", "icms_st"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        # Só interestadual
        if context.uf_origem == context.uf_destino:
            return False
        # Produto deve ter NCM sujeito a ST na UF destino
        if not self.is_ncm_subject_to_st(context.ncm, context.uf_destino):
            return False
        # Operação deve ter CST/CSOSN com ST
        if not self.has_st_cst(context.cst, context.csosn):
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        # Buscar parâmetros ST para NCM × UF Destino
        st_params = self.get_st_params(context.ncm, context.uf_destino)
        if not st_params:
            return []
        
        mva = st_params.get("mva", 0)
        iva = st_params.get("iva", 0)
        aliquota_interna = st_params.get("aliquota_interna", 0)
        aliquota_interestadual = self.get_aliquota_interestadual(
            context.uf_origem, context.uf_destino
        )
        
        # Base de cálculo da operação
        vBC_op = context.vBC  # vBC da operação própria
        
        # Calcular BC_ST
        if mva > 0:
            bc_st = vBC_op * (1 + mva / 100)
        elif iva > 0:
            bc_st = vBC_op / (1 - iva / 100)
        else:
            return []  # Sem parâmetro válido
        
        # ICMS ST Devido
        icms_st_devido = bc_st * aliquota_interna
        
        # ICMS próprio da operação (se destacado)
        icms_proprio = context.vICMS or 0
        
        # ICMS ST a recolher
        icms_st_recolher = icms_st_devido - icms_proprio
        
        # FCP ST (se UF destino tem FCP)
        fcp_rate = self.get_fcp_rate(context.uf_destino)
        fcp_st = bc_st * fcp_rate if fcp_rate > 0 else 0
        
        total_st_devido = icms_st_recolher + fcp_st
        
        # Valor efetivamente recolhido (vICMSST do XML)
        icms_st_recolhido = context.vICMSST or 0
        fcp_st_recolhido = context.vFCPST or 0
        total_st_recolhido = icms_st_recolhido + fcp_st_recolhido
        
        diferenca = total_st_devido - total_st_recolhido
        
        if abs(diferenca) > context.vBC * 0.01:  # 1% tolerância
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(total_st_devido, 2),
                actual_value=round(total_st_recolhido, 2),
                difference=round(diferenca, 2),
                details={
                    "ncm": context.ncm,
                    "cest": context.cest,
                    "uf_destino": context.uf_destino,
                    "mva": mva,
                    "iva": iva,
                    "aliquota_interna": aliquota_interna,
                    "aliquota_interestadual": aliquota_interestadual,
                    "bc_operacao": vBC_op,
                    "bc_st": round(bc_st, 2),
                    "icms_st_devido": round(icms_st_recolher, 2),
                    "fcp_st_devido": round(fcp_st, 2),
                    "cst": context.cst,
                    "csosn": context.csosn
                }
            )]
        return []
```

---

## 🧪 Casos de Teste (test_rules_critical.py)

```python
# test_icms_st_rule
# NCM 22030000 (Cerveja) - CEST 01.001.00
# SP → SP (interna) - NÃO aplica (mesma UF)
# SP → RJ (interestadual) - APLICA
# MVA SP = 41.67%, Alíq. Interna RJ = 20%
# vBC = 1000
# BC_ST = 1000 × 1.4167 = 1416.70
# ICMS ST = 1416.70 × 20% = 283.34
# ICMS Próprio (12%) = 120.00
# ST Recolher = 283.34 - 120.00 = 163.34

# test_icms_st_with_fcp
# RJ tem FCP 2%
# FCP ST = 1416.70 × 2% = 28.33
# Total = 163.34 + 28.33 = 191.67

# test_icms_st_iva_method
# Cigarros (NCM 24022000) usa IVA
# IVA SP = 56%
# BC_ST = 1000 / (1 - 0.56) = 2272.73

# test_icms_st_not_subject
# NCM não sujeito a ST - rule não dispara
```

---

## ⚠️ Pontos Críticos

### 1. **MVA vs IVA - Método por Produto**
| Produto | Método | Exemplo |
|---------|--------|---------|
| Bebidas, Cosméticos, Eletroeletrônicos | **MVA** | Cerveja MVA 41.67% |
| Cigarros, Combustíveis, Medicamentos | **IVA** | Cigarro IVA 56% |
| Alguns estados usam ambos | Verificar decreto | - |

### 2. **FCP sobre ST**
- Se UF destino tem FCP (ver `02-ICMS-FCP.md`)
- FCP incide sobre **BC_ST** (não sobre BC operação)
- Campo XML: `vFCPST`, `pFCPST`

### 3. **Substituição "Para Frente" vs "Para Trás"**
- **Para Frente** (padrão): Indústria → Atacado → Varejo (industrial substitui)
- **Para Trás**: Varejo recolhe antecipado (raro, alguns estados)

### 4. **Simples Nacional**
- CSOSN 201, 202, 203: ST retido por substituto
- CSOSN 500, 900: ST não se aplica (exceto se lei estadual exigir)

### 5. **DIFAL + ST na mesma operação**
- Primeiro calcula DIFAL (se não contribuinte)
- Depois calcula ST (se produto sujeito)
- **Não cumulam bases** - são regimes diferentes

---

## 📦 JSON para backend/app/data/icms_rules.json (seção ICMS ST)

```json
{
  "icms_st": {
    "version": "2025.1",
    "updated": "2025-01-15",
    "source": "Convênio ICMS 142/2018, Convênio ICMS 92/2015, Decretos Estaduais",
    "produtos_st": {
      "22030000": {
        "descricao": "Cervejas",
        "cest": "01.001.00",
        "metodo": "MVA",
        "ufs": {
          "SP": {"mva": 41.67, "aliquota_interna": 0.18},
          "RJ": {"mva": 51.22, "aliquota_interna": 0.20},
          "MG": {"mva": 33.33, "aliquota_interna": 0.18},
          "RS": {"mva": 33.33, "aliquota_interna": 0.18},
          "PR": {"mva": 33.33, "aliquota_interna": 0.18},
          "SC": {"mva": 41.67, "aliquota_interna": 0.17}
        }
      },
      "22042100": {
        "descricao": "Vinhos",
        "cest": "01.002.00",
        "metodo": "MVA",
        "ufs": {
          "SP": {"mva": 41.67, "aliquota_interna": 0.18},
          "RJ": {"mva": 51.22, "aliquota_interna": 0.20}
        }
      },
      "24022000": {
        "descricao": "Cigarros",
        "cest": "02.001.00",
        "metodo": "IVA",
        "ufs": {
          "SP": {"iva": 56.00, "aliquota_interna": 0.18},
          "RJ": {"iva": 60.00, "aliquota_interna": 0.20}
        }
      },
      "27101921": {
        "descricao": "Óleo Diesel",
        "cest": "03.001.00",
        "metodo": "MVA",
        "ufs": {
          "SP": {"mva": 13.64, "aliquota_interna": 0.18}
        }
      },
      "30049099": {
        "descricao": "Medicamentos",
        "cest": "04.001.00",
        "metodo": "MVA",
        "ufs": {
          "SP": {"mva": 20.00, "aliquota_interna": 0.18}
        }
      }
    },
    "cst_com_st": ["10", "30", "40", "41", "50", "51", "60", "70", "90"],
    "csosn_com_st": ["201", "202", "203", "500", "900"]
  }
}
```

---

## 🔗 Referências

- [Convênio ICMS 142/2018 - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2018/convenio-icms-142-2018)
- [Convênio ICMS 92/2015 (CEST) - Confaz](https://www.confaz.fazenda.gov.br/legislacao/convenios/2015/convenio-icms-92-2015)
- [Portal ICMS ST por Estado](https://www.icms.ind.br/st/)
- [Tabela CEST Completa](https://www.confaz.fazenda.gov.br/legislacao/convenios/2015)

---

**Última Atualização:** 2026-11-01  
**Responsável:** PO Agent  
**Próxima Revisão:** Janeiro 2026 (verificar decretos estaduais de MVA/IVA)