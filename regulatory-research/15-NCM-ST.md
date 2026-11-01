# NCMs Sujeitos a ST por UF - Convênio ICMS 142/2018

**Arquivo:** Referência para `backend/app/data/icms_rules.json` (seção `icms_st`)  
**Fonte:** Convênio ICMS 142/2018, Convênio ICMS 92/2015 (CEST), Decretos Estaduais  
**Atualização:** Janeiro 2025

---

## 📋 Estrutura CEST (Convênio ICMS 92/2015)

**Formato:** `SS.GGG.CC` (Segmento.Grupo.Código)

| Segmento | Descrição | NCMs Principais |
|----------|-----------|-----------------|
| **01** | Bebidas | 2203, 2204, 2208 |
| **02** | Fumos | 2402, 2403 |
| **03** | Combustíveis | 2710 |
| **04** | Medicamentos | 3004 |
| **05** | Perfumaria/Cosméticos | 3303, 3304, 3401 |
| **06** | Material Embalagem | 3923, 4819 |
| **07** | Siderúrgicos | 7208-7229 |
| **08** | Veículos | 8703, 8711 |
| **09** | Eletroeletrônicos | 8517, 8528 |
| **10** | Móveis | 9401, 9403 |
| **11** | Brinquedos | 9503 |
| **12** | Artigos Esporte | 9506 |
| **13** | Papelaria | 4802, 4810 |
| **14** | Vidros | 7007, 7009 |
| **15** | Cerâmicos | 6907, 6910 |
| **16** | Couro/Calçados | 6401-6406 |
| **17** | Têxteis | 6101-6117, 6201-6217 |
| **18** | Alimentos | 0201-0210, 0401-0406 |
| **19** | Produtos Limpeza | 3402 |
| **20** | Autopeças | 8708 |
| **21** | Material Construção | 2523, 6810 |
| **22** | Produtos Químicos | 3208-3210 |
| **23** | Instrumentos Médicos | 9018-9022 |
| **24** | Artigos Plásticos | 3924-3926 |
| **25** | Outros | Diversos |

---

## 📊 NCMs Principais com ST por UF (Exemplos 2024/2025)

### SP (Decreto 45.490/2000 + atualizações)

| NCM | Descrição | CEST | Método | MVA/IVA | Alíq. Interna |
|-----|-----------|------|--------|---------|---------------|
| 22030000 | Cervejas | 01.001.00 | MVA | 41,67% | 18% |
| 22042100 | Vinhos | 01.002.00 | MVA | 41,67% | 18% |
| 22083000 | Whiskies | 01.003.00 | MVA | 55,56% | 18% |
| 22087000 | Licores | 01.004.00 | MVA | 41,67% | 18% |
| 24022000 | Cigarros | 02.001.00 | IVA | 56,00% | 18% |
| 27101921 | Óleo Diesel | 03.001.00 | MVA | 13,64% | 18% |
| 27101922 | Gasolina | 03.002.00 | MVA | 13,64% | 18% |
| 30049099 | Medicamentos | 04.001.00 | MVA | 20,00% | 18% |
| 33049900 | Cosméticos | 05.001.00 | MVA | 33,33% | 18% |
| 34011100 | Sabonetes | 05.002.00 | MVA | 33,33% | 18% |
| 39232100 | Embalagens plásticas | 06.001.00 | MVA | 20,00% | 18% |
| 48191000 | Caixas papelão | 06.002.00 | MVA | 20,00% | 18% |
| 72085100 | Chapas aço laminado | 07.001.00 | MVA | 13,64% | 18% |
| 87032100 | Automóveis até 1000cc | 08.001.00 | MVA | 33,33% | 18% |
| 87112000 | Motocicletas | 08.002.00 | MVA | 33,33% | 18% |
| 85171200 | Celulares | 09.001.00 | MVA | 20,00% | 18% |
| 85287200 | TVs | 09.002.00 | MVA | 25,00% | 18% |

### RJ (Decreto 47.627/2022)

| NCM | Descrição | CEST | Método | MVA/IVA | Alíq. Interna |
|-----|-----------|------|--------|---------|---------------|
| 22030000 | Cervejas | 01.001.00 | MVA | 51,22% | 20% |
| 24022000 | Cigarros | 02.001.00 | IVA | 60,00% | 20% |
| 27101921 | Óleo Diesel | 03.001.00 | MVA | 17,65% | 20% |

### MG (Decreto 48.589/2023)

| NCM | Descrição | CEST | Método | MVA/IVA | Alíq. Interna |
|-----|-----------|------|--------|---------|---------------|
| 22030000 | Cervejas | 01.001.00 | MVA | 33,33% | 18% |
| 24022000 | Cigarros | 02.001.00 | IVA | 52,00% | 18% |

---

## ⚠️ REGRAS IMPORTANTES

### 1. MVA vs IVA - Por Produto
| Produto | Método |
|---------|--------|
| Bebidas, Cosméticos, Eletroeletrônicos, Veículos | **MVA** |
| Cigarros, Combustíveis, Medicamentos | **IVA** |
| Verificar decreto de cada UF | |

### 2. MVA Ajustado (Redução de Base)
Alguns estados dão redução na base de cálculo:
```
MVA_Ajustado = MVA × (1 - Redução)
Ex: MVA 41,67% com redução 20% = 33,33%
```

### 3. ST Antecipado (Substituição "Para Frente")
- Indústria/Importador = Substituto
- Atacadista/Varejista = Substituído
- ICMS ST recolhido na entrada interestadual

### 4. Simples Nacional
- CSOSN 201/202/203: ST retido pelo substituto
- CSOSN 500/900: Geralmente sem ST (verificar lei estadual)

---

## 📦 JSON para backend/app/data/icms_rules.json (seção icms_st expandida)

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
          "SP": {"mva": 41.67, "aliquota_interna": 0.18, "reducao_base": 0},
          "RJ": {"mva": 51.22, "aliquota_interna": 0.20, "reducao_base": 0},
          "MG": {"mva": 33.33, "aliquota_interna": 0.18, "reducao_base": 0},
          "RS": {"mva": 33.33, "aliquota_interna": 0.18, "reducao_base": 0},
          "PR": {"mva": 33.33, "aliquota_interna": 0.18, "reducao_base": 0},
          "SC": {"mva": 41.67, "aliquota_interna": 0.17, "reducao_base": 0},
          "BA": {"mva": 45.45, "aliquota_interna": 0.205, "reducao_base": 0},
          "GO": {"mva": 33.33, "aliquota_interna": 0.19, "reducao_base": 0}
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
          "RJ": {"iva": 60.00, "aliquota_interna": 0.20},
          "MG": {"iva": 52.00, "aliquota_interna": 0.18}
        }
      },
      "27101921": {
        "descricao": "Óleo Diesel",
        "cest": "03.001.00",
        "metodo": "MVA",
        "ufs": {
          "SP": {"mva": 13.64, "aliquota_interna": 0.18},
          "RJ": {"mva": 17.65, "aliquota_interna": 0.20}
        }
      },
      "30049099": {
        "descricao": "Medicamentos genéricos",
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

- [Convênio ICMS 142/2018](https://www.confaz.fazenda.gov.br/legislacao/convenios/2018/convenio-icms-142-2018)
- [Convênio ICMS 92/2015 - CEST](https://www.confaz.fazenda.gov.br/legislacao/convenios/2015/convenio-icms-92-2015)
- [Decretos Estaduais RICMS](https://www.icms.ind.br/legislacao/)
- [Tabela CEST Completa](https://www.confaz.fazenda.gov.br/legislacao/convenios/2015)

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Janeiro 2026 (verificar decretos estaduais)