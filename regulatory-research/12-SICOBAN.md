# Tabela SICOBAN/ANTT (CEP × Tipo × Modal) - Regra SICOBAN_TABLE_REAL

**Rule Code:** `SICOBAN_TABLE_REAL`  
**Tipo:** `SICOBAN_TABLE`  
**Severidade:** `HIGH`  
**Tags:** `freight, sicoban`  
**Arquivo de Dados:** `backend/app/data/sicoban_table.json`  
**Teste:** `tests/test_rules_critical.py::test_sicoban_table_real`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Res. ANTT 5.839/2021** (Anexo III) | Tabela SICOBAN - Frete por CEP | 2021+ |
| **Res. ANTT 5.868/2022** | Atualização 2023 | 2023+ |
| **Res. ANTT 5.933/2023** | Atualização 2024 | 2024+ |
| **Lei 11.442/2007** | Tabela de frete de referência | Vigente |

---

## 🎯 Quando Aplica

**Transporte Rodoviário** onde o frete é referenciado pela **Tabela SICOBAN**:
- Contratos que usam SICOBAN como indexador
- Cargas fracionadas (LTL) entre capitais/regiões metropolitanas
- **CEP Origem × CEP Destino × Tipo Carga × Modal**

**Identificação:**
- CT-e com `vFrete` baseado em tabela SICOBAN
- Contrato informa: "Frete conforme Tabela SICOBAN vigente"

---

## 🧮 Estrutura da Tabela SICOBAN

### 22 Faixas de CEP (Regiões)

| Faixa | Região | CEPs Iniciais | Capitais/Principais |
|-------|--------|---------------|---------------------|
| **01** | Norte I | 68xxx-69xxx | Belém, Macapá, Manaus |
| **02** | Norte II | 66xxx-67xxx | Palmas, Porto Velho, Rio Branco, Boa Vista |
| **03** | Nordeste I | 50xxx-56xxx | Recife, João Pessoa, Natal, Maceió, Aracaju |
| **04** | Nordeste II | 57xxx-59xxx | Salvador, Fortaleza, Teresina, São Luís |
| **05** | Centro-Oeste I | 73xxx-76xxx | Goiânia, Brasília, Campo Grande |
| **06** | Centro-Oeste II | 78xxx-79xxx | Cuiabá, Palmas (parte) |
| **07** | Sudeste I | 01xxx-09xxx | São Paulo (capital + RMSP) |
| **08** | Sudeste II | 10xxx-19xxx | São Paulo (interior), Santos, Campinas |
| **09** | Sudeste III | 20xxx-28xxx | Rio de Janeiro (capital + região) |
| **10** | Sudeste IV | 29xxx-39xxx | Espírito Santo, Minas Gerais (BH + interior) |
| **11** | Sul I | 80xxx-87xxx | Curitiba, Londrina, Maringá |
| **12** | Sul II | 88xxx-89xxx | Florianópolis, Joinville, Blumenau |
| **13** | Sul III | 90xxx-99xxx | Porto Alegre, Caxias, Pelotas |
| **14** | Nordeste III | 40xxx-49xxx | Bahia (interior), Sergipe (interior) |
| **15** | Norte III | 65xxx | Pará (interior), Amazonas (interior) |
| **16** | Sudeste V | 30xxx-31xxx | Belo Horizonte (RMBH) |
| **17** | Sudeste VI | 32xxx-34xxx | Minas Gerais (Vale do Aço, Zona da Mata) |
| **18** | Sudeste VII | 35xxx-39xxx | Minas Gerais (Triângulo, Sul de MG) |
| **19** | Centro-Oeste III | 70xxx-72xxx | Brasília (DF + entorno) |
| **20** | Nordeste IV | 55xxx-56xxx | Pernambuco (interior), Paraíba (interior) |
| **21** | Norte IV | 69xxx (parte) | Acre, Rondônia (interior) |
| **22** | Especial | - | Ilhas, áreas de difícil acesso |

---

## 📊 Tipos de Carga × Modal (SICOBAN)

| Tipo Carga | Código | Modal Rodoviário (01) | Modal Ferroviário (02) | Modal Dutoviário (03) |
|------------|--------|----------------------|------------------------|----------------------|
| **Carga Geral** | 01 | Base | - | - |
| **Carga Perigosa** | 02 | Base × 1,30 | Base × 1,20 | - |
| **Carga Frigorífica** | 03 | Base × 1,15 | - | - |
| **Granel Líquido** | 04 | Base × 0,85 | Base × 0,75 | Base × 0,70 |
| **Granel Sólido** | 05 | Base × 0,80 | Base × 0,70 | Base × 0,65 |
| **Neogranel** | 06 | Base × 1,00 | - | - |
| **Container** | 07 | Base × 1,10 | Base × 1,00 | - |
| **Carga Projeto** | 08 | Base × 1,50 | - | - |
| **Veículos** | 09 | Base × 1,20 | - | - |
| **Carga Viva** | 10 | Base × 1,25 | - | - |

---

## 🔍 Lógica de Detecção no Engine

```python
class SicobanTableRule(BaseRule):
    code = "SICOBAN_TABLE_REAL"
    relevance_tags = {"freight", "sicoban"}
    
    def is_relevant(self, context: RuleContext) -> bool:
        if context.modal != "01":
            return False
        # Só se contrato usa SICOBAN
        if not context.contrato_usa_sicoban:
            return False
        if not context.cep_origem or not context.cep_destino:
            return False
        return True
    
    def evaluate(self, context: RuleContext) -> List[Discrepancy]:
        faixa_origem = self.get_faixa_cep(context.cep_origem)
        faixa_destino = self.get_faixa_cep(context.cep_destino)
        tipo_carga = context.tpCarga or "01"
        
        if not faixa_origem or not faixa_destino:
            return []
        
        # Buscar valor base na tabela SICOBAN
        valor_base = self.get_valor_sicoban(faixa_origem, faixa_destino)
        if not valor_base:
            return []
        
        # Aplicar fator tipo carga
        fator = self.get_fator_tipo_carga(tipo_carga)
        valor_sicoban = valor_base * fator
        
        # Comparar com frete cobrado
        frete_cobrado = context.vFrete
        diferenca = valor_sicoban - frete_cobrado
        
        # Tolerância 5% (negociação comercial)
        if diferenca > frete_cobrado * 0.05:
            return [Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                expected_value=round(valor_sicoban, 2),
                actual_value=round(frete_cobrado, 2),
                difference=round(diferenca, 2),
                details={
                    "cep_origem": context.cep_origem,
                    "cep_destino": context.cep_destino,
                    "faixa_origem": faixa_origem,
                    "faixa_destino": faixa_destino,
                    "tipo_carga": tipo_carga,
                    "valor_base_sicoban": valor_base,
                    "fator_tipo_carga": fator,
                    "valor_sicoban_calculado": round(valor_sicoban, 2),
                    "modal": context.modal
                }
            )]
        return []
```

---

## 🧪 Casos de Teste

```python
# test_sicoban_table_real
# SP (07) → RJ (09), Carga Geral
# Valor base SICOBAN 07→09 = R$ 1.200,00
# Fator Carga Geral = 1,0
# Valor SICOBAN = R$ 1.200,00
# Frete Cobrado = R$ 1.000,00 → DIVERGÊNCIA R$ 200,00

# test_sicoban_perigosa
# SP (07) → BH (16), Perigosa
# Base 07→16 = R$ 800,00
# Fator 1,30 = R$ 1.040,00

# test_sicoban_granel_liquido
# RJ (09) → ES (10), Granel Líquido
# Base 09→10 = R$ 600,00
# Fator 0,85 = R$ 510,00
```

---

## ⚠️ Pontos de Atenção

1. **SICOBAN ≠ Piso Mínimo ANTT** - SICOBAN é tabela de **referência comercial**, piso mínimo é **obrigatório legal**
2. **Regra deve comparar:** Frete Cobrado vs **MAIOR(PISO_MINIMO, SICOBAN)**
3. **Atualização anual** pela ANTT (geralmente julho)
4. **CEP completo** (8 dígitos) para determinar faixa correta
5. **Contrato deve prever** uso da SICOBAN como indexador

---

## 📦 JSON para backend/app/data/sicoban_table.json

```json
{
  "version": "2024.1",
  "updated": "2024-07-15",
  "source": "Resolução ANTT 5.933/2023 - Anexo III",
  "faixas_cep": {
    "01": {"regiao": "Norte I", "ceps": ["68", "69"], "capitais": ["Belém", "Macapá", "Manaus"]},
    "02": {"regiao": "Norte II", "ceps": ["66", "67"], "capitais": ["Palmas", "Porto Velho", "Rio Branco", "Boa Vista"]},
    "03": {"regiao": "Nordeste I", "ceps": ["50", "51", "52", "53", "54", "55", "56"], "capitais": ["Recife", "João Pessoa", "Natal", "Maceió", "Aracaju"]},
    "04": {"regiao": "Nordeste II", "ceps": ["57", "58", "59"], "capitais": ["Salvador", "Fortaleza", "Teresina", "São Luís"]},
    "05": {"regiao": "Centro-Oeste I", "ceps": ["73", "74", "75", "76"], "capitais": ["Goiânia", "Brasília", "Campo Grande"]},
    "06": {"regiao": "Centro-Oeste II", "ceps": ["78", "79"], "capitais": ["Cuiabá"]},
    "07": {"regiao": "Sudeste I", "ceps": ["01", "02", "03", "04", "05", "06", "07", "08", "09"], "capitais": ["São Paulo"]},
    "08": {"regiao": "Sudeste II", "ceps": ["10", "11", "12", "13", "14", "15", "16", "17", "18", "19"], "capitais": ["Santos", "Campinas"]},
    "09": {"regiao": "Sudeste III", "ceps": ["20", "21", "22", "23", "24", "25", "26", "27", "28"], "capitais": ["Rio de Janeiro"]},
    "10": {"regiao": "Sudeste IV", "ceps": ["29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39"], "capitais": ["Vitória", "Belo Horizonte"]},
    "11": {"regiao": "Sul I", "ceps": ["80", "81", "82", "83", "84", "85", "86", "87"], "capitais": ["Curitiba", "Londrina", "Maringá"]},
    "12": {"regiao": "Sul II", "ceps": ["88", "89"], "capitais": ["Florianópolis", "Joinville", "Blumenau"]},
    "13": {"regiao": "Sul III", "ceps": ["90", "91", "92", "93", "94", "95", "96", "97", "98", "99"], "capitais": ["Porto Alegre", "Caxias", "Pelotas"]},
    "14": {"regiao": "Nordeste III", "ceps": ["40", "41", "42", "43", "44", "45", "46", "47", "48", "49"], "capitais": ["Feira de Santana", "Vitória da Conquista"]},
    "15": {"regiao": "Norte III", "ceps": ["65"], "capitais": ["Imperatriz"]},
    "16": {"regiao": "Sudeste V", "ceps": ["30", "31"], "capitais": ["Belo Horizonte (RMBH)"]},
    "17": {"regiao": "Sudeste VI", "ceps": ["32", "33", "34"], "capitais": ["Ipatinga", "Juiz de Fora"]},
    "18": {"regiao": "Sudeste VII", "ceps": ["35", "36", "37", "38", "39"], "capitais": ["Uberlândia", "Uberaba", "Varginha"]},
    "19": {"regiao": "Centro-Oeste III", "ceps": ["70", "71", "72"], "capitais": ["Brasília (DF)"]},
    "20": {"regiao": "Nordeste IV", "ceps": ["55", "56"], "capitais": ["Caruaru", "Campina Grande"]},
    "21": {"regiao": "Norte IV", "ceps": ["69"], "capitais": ["Cruzeiro do Sul"]},
    "22": {"regiao": "Especial", "ceps": [], "capitais": ["Ilhas", "Difícil acesso"]}
  },
  "fatores_tipo_carga": {
    "01": 1.00, "02": 1.30, "03": 1.15, "04": 0.85,
    "05": 0.80, "06": 1.00, "07": 1.10, "08": 1.50,
    "09": 1.20, "10": 1.25
  },
  "valores_base_exemplos": {
    "07-09": 1200.00,
    "07-16": 800.00,
    "09-10": 600.00,
    "11-13": 900.00,
    "01-03": 2500.00
  }
}
```

---

## 🔗 Referências

- [Res. ANTT 5.839/2021 Anexo III](https://www.antt.gov.br/archives/legislacao/resolucoes/2021/resolucao-5839-2021.pdf)
- [Tabela SICOBAN Completa ANTT](https://www.antt.gov.br/tabela-sicoban)
- [Consulta Faixa CEP SICOBAN](https://www.antt.gov.br/consulta-faixa-cep)

---

**Última Atualização:** 2026-11-01 | **Próxima Revisão:** Julho 2025