# Regras e Alíquotas para Validação com Contadores/Tax Specialists
**Projeto**: AvertaSaaS - Freight Audit SaaS  
**Data**: 2025-01-15  
**Versão**: 1.0  
**Finalidade**: Base para reunião de validação tributária e de frete

---

## 📋 SUMÁRIO EXECUTIVO

| Status | Quantidade | Ação Necessária |
|--------|------------|-----------------|
| ✅ **Validadas/OK** | 8 regras | Apenas confirmar |
| ⚠️ **Com Gaps (Correção)** | 6 regras | Revisar cálculo/legislação |
| ❌ **Faltando (Novas)** | 4 regras | Definir escopo e validar |
| **Total** | **18 regras** | |

---

## ✅ REGRAS PARA CONFIRMAÇÃO (Já Implementadas - Baixo Risco)

### 1. ICMS_DIFAL - Diferencial de Alíquota Interestadual
- **Legislação**: LC 87/96, LC 190/22, Convênio ICMS 109/24
- **Cálculo**: `(Alíquota Interestadual - Alíquota Interna Destino) × BC` + FCP
- **Alíquotas Interestaduais**: 7% (N/NE/CO → S/SE), 12% (S/SE → N/NE/CO), 4% (importados)
- **JSON**: `icms_rules.json` → `difal[].aliquota_interestadual`, `aliquota_difal`, `aliquota_fcp`

### 2. FRETE_PESO_VALOR - Faixas Peso/Valor ANTT
- **Legislação**: ANTT Res. 5.839/21 Art. 6º, Anexo I
- **Cálculo**: `Peso × Valor_kg` (mínimo `Valor_mínimo` por faixa)
- **10 faixas** × 5 tipos carga (Geral, Perigosa, Frigorífica, Granel, Neogranel)
- **JSON**: `antt_faixas_peso_valor.json`

### 3. FRETE_CUBAGE - Faixas Cubagem ANTT
- **Legislação**: ANTT Res. 5.839/21 Anexo II
- **Cálculo**: `Volume_m³ × Valor_m³` (mínimo `Valor_mínimo` por faixa)
- **10 faixas** × 5 tipos carga
- **JSON**: `antt_faixas_cubagem.json`

### 4. PESO_REAL_VS_FATURADO - Tolerância de Peso
- **Legislação**: ANTT Res. 5.839/21 Art. 7º
- **Tolerâncias por tipo carga** (JSON: `pesos_tolerancia.json`):
  - Carga Geral: 5%
  - Carga Perigosa: 3%
  - Frigorífica: 5%
  - Granel Líquido: 20%
  - Granel Sólido: 20%
  - Neogranel: 5%
  - Container: 5%
  - Carga Projeto: 5%
  - Veículos: 3%
  - Carga Viva: 10%
- **Fontes peso real válidas**: balança fiscal, balança transportador, nota pesagem

### 5. REDESPACHO_VALIDACAO - Validação Básica
- **Legislação**: Lei 11.442/07, Decreto 9.209/17, ANTT 5.839/21
- **Regras** (JSON: `redespacho_regras.json`):
  - refCTe obrigatório ✓
  - Transportadores diferentes ✓
  - Piso mínimo por trecho ✓
  - Soma fretes ≥ piso direto ✓
  - **PENDENTE**: ICMS principal recolhe total / Redespachante pode ser isento

### 6. CTE_ANULACAO / CTE_SUBSTITUICAO / CTE_COMPLEMENTO_VALOR
- **Legislação**: Decreto 9.209/17, Convênio ICMS 188/17, Manual CT-e 3.00
- **Tipos**: tpEmis=3 (Anulação), 2 (Substituição), 4 (Complemento)
- **Validações** (JSON: `cte_complementar_regras.json`):
  - refCTe obrigatório + deve existir + não anulado
  - Substituição: apenas 1 vez, valores diferentes
  - Complemento: apenas aumentar valores, requer aditivo contratual

### 7. AD_VALOREM - Seguro sobre Valor
- **Legislação**: Susep Circular 615/21, Lei 11.442/07
- **Alíquotas por tipo carga** (JSON: `ad_valorem_taxas.json`):
  - Geral: 0.10% | Perigosa: 0.25% | Frigorífica: 0.15%
  - Granel Líquido: 0.08% | Granel Sólido: 0.05%
  - Neogranel: 0.10% | Container: 0.12% | Projeto: 0.30%
  - Veículos: 0.20% | Viva: 0.25%
- **Teto**: Configurável por contrato

### 8. GRIS - Gerenciamento de Risco
- **Legislação**: Susep, Lei 11.442/07 Art. 15
- **Alíquotas por região/rota** (JSON: `gris_taxas.json`):
  - Capital-Capital: 0.15% | Capital-Interior: 0.25%
  - Interior-Interior: 0.20% | Fronteira: 0.40%
  - Rota Crítica: 0.50% | Normal: 0.10%
- **Teto**: Configurável por contrato

---

## ⚠️ REGRAS COM GAPS (PRECISAM CORREÇÃO/REVISÃO CRÍTICA)

### 9. ICMS_FCP - Fundo de Combate à Pobreza ⚠️ **PARCIAL**
| Item | Atual | Correto | Ação |
|------|-------|---------|------|
| **Escopo** | Só interestadual (UFs N/NE) | **Interestadual + Interno (BA, RJ, SP)** | Adicionar validação intraestadual |
| **Alíquota** | 2% fixo para UFs N/NE | 2% (maioria) + **4% (AP, PB)** | Atualizar tabela no JSON |
| **Base** | BC ICMS | BC ICMS (mesma) | OK |
| **UFs c/ FCP Interno** | Não validado | **BA (2%), RJ (2%), SP (2%)** | Incluir na regra |

**JSON já tem**: `icms_rules.json` → `ufs[].fcp_interno: true` para BA/RJ/SP + `aliquota_fcp_interno`

---

### 10. ICMS_ST - Substituição Tributária ⚠️ **CÁLCULO INCORRETO**
| Item | Atual (Errado) | Correto (Roteiro Nacional) | Ação |
|------|----------------|---------------------------|------|
| **Base ST** | Usa `aliquota_st` direto | `VFrete + VSeguro + Outras Despesas` | Reescrever |
| **MVA/IVA** | Não aplica | Aplicar **MVA Ajustado** por NCM/UF | Usar `mva_ajustado` do JSON |
| **Cálculo Completo** | `BC_ST × alíq_ST` | 1. BC = VFrete + VSeg + Desp<br>2. BC_ST = BC × (1 + MVA)<br>3. ICMS_ST = BC_ST × alíq_interestadual<br>4. Deduzir ICMS próprio | Implementar roteiro |
| **CSTs válidos** | 10,30,60,70,90 | Confirmar + CST 41 (isentos ST) | Revisar |

**JSON tem**: `icms_rules.json` → `icms_st[].mva_ajustado`, `aliquota_interestadual`, `aliquota_interna`, `reducao_bc_st`

---

### 11. VALOR_MINIMO_FRETE - Piso Mínimo ANTT ⚠️ **INCOMPLETO**
| Item | Atual | Correto (Art. 7º ANTT 5.839/21) | Ação |
|------|-------|----------------------------------|------|
| **Método** | Só Piso por Eixo × Distância | **MAX de 3 métodos:** | Reescrever cálculo |
| **Método 1** | ✓ Piso Eixo × km | Piso por Eixo × Distância | OK |
| **Método 2** | ❌ Falta | **Peso × Faixa Peso/Valor (Anexo I)** | Adicionar |
| **Método 3** | ❌ Falta | **Cubagem × Faixa Cubagem (Anexo II)** | Adicionar |
| **Fator peso >10t** | ×1.2 hardcoded | Verificar se regulamentado | Validar com ANTT |
| **Eixos** | 2 a 9 eixos | Confirmar até 9 eixos (JSON tem 2-9) | OK |

**JSONs necessários**: `antt_piso_minimo.json` + `antt_faixas_peso_valor.json` + `antt_faixas_cubagem.json`

---

### 12. SICOBAN_TABLE_REAL - Tabela SICOBAN ⚠️ **MATRIZ INCOMPLETA**
| Item | Atual | Necessário | Ação |
|------|-------|------------|------|
| **Estrutura** | 22 faixas CEP + 10 tipos carga | **22 × 10 = 220 combinações** | Popular completa |
| **Valores** | Só fatores multiplicadores | **Valor_kg, Valor_m3, Valor_minimo** absolutos por célula | Obter tabela ANTT 2024 |
| **CEP Lookup** | 5 dígitos (prefixo) | Confirmar granularidade | Validar |
| **Atualização** | Manual | **API ANTT/SICOBAN** ou publicação oficial | Definir processo |

**JSON tem**: `sicoban_table.json` → `faixas_cep` (22), `fatores_tipo_carga` (10), `valores_base_exemplos` (apenas 5 exemplos)
**Falta**: Matriz completa `valor_kg`, `valor_m3`, `valor_minimo` por faixa × tipo

---

### 13. PEDAGIO_CONFERENCIA - Conferência de Pedágio ⚠️ **SIMPLIFICADO**
| Item | Atual | Necessário | Ação |
|------|-------|------------|------|
| **Validação** | Valor doc vs tabela estática | **Praça × Eixos × Categoria Veículo** | Refatorar |
| **Isenções** | Não considera | Eixo suspenso, TAG, Convênios | Implementar |
| **Tarifas** | Estáticas no JSON | **APIs Concessionárias** (CCR, EcoRodovias, Arteris, Triunfo, etc.) | Integrar |
| **Categorias** | Não tem | Moto, Carro, Comercial Leve, Pesado 2/3/4+ eixos | Mapear |

**JSON**: `pedagio_tarifas.json` tem estrutura, **precisa popular tarifas 2024 por concessionária**

---

### 14. REDESPACHO_VALIDACAO - Validações Fiscais ⚠️ **FALTANDO**
| Regra (JSON `redespacho_regras.json`) | Status | Ação |
|--------------------------------------|--------|------|
| ICMS principal recolhe total | ❌ Não validado | Implementar partilha ICMS |
| Redespachante pode ser isento | ❌ Não validado | Validar CST do redespachante |
| Piso mínimo por trecho | ⚠️ Parcial | Confirmar cálculo por trecho |
| Soma fretes ≥ piso direto | ⚠️ Parcial | Validar com piso mínimo corrigido |

---

## ❌ REGRAS FALTANDO (NOVAS - CARGAS ESPECIAIS)

### 15. CARGA_PERIGOSA_VALIDACAO
**Legislação**: ANTT Res. 5.948/23, ABNT NBR 7500, Regulamento ONU
| Validação | Detalhamento | Fonte |
|-----------|--------------|-------|
| **Documentação** | FISPQ, Ficha RISCO, Envelope de Emergência | ANTT 5.948/23 |
| **Veículo** | Certificado IPVAV, Kit emergência, Painéis ONU | ABNT NBR 7500 |
| **Condutor** | Curso MOPP válido (reciclagem 5 anos) | Lei 11.442/07 |
| **GRIS** | Fator 1.30× (JSON `sicoban_table.json` fator 02=1.30) | SICOBAN |
| **Seguro** | RCTR-C obrigatório + RC-Veículo | Susep |
| **Roteiro** | Rotas permitidas/restritas para perigosos | ANTT/DNIT |

---

### 16. CARGA_FRIORIFICA_VALIDACAO
**Legislação**: ANVISA RDC 216/04, ANTT Res. 5.839/21
| Validação | Detalhamento | Fonte |
|-----------|--------------|-------|
| **Temperatura** | Registro termoógrafo/datalogger (todo trajeto) | ANVISA RDC 216/04 |
| **Certificado** | Certificado Sanitário / Certificado de Origem | MAPA/ANVISA |
| **Prazo Máximo** | Definir por tipo produto (congelado/resfriado) | Boas práticas |
| **Veículo** | Isolamento, refrigeração, limpeza | ANTT |
| **Fator SICOBAN** | 1.15× (JSON fator 03=1.15) | SICOBAN |

---

### 17. CARGA_PROJETO_VALIDACAO
**Legislação**: ANTT Res. 5.839/21, DNIT Portaria 198/06
| Validação | Detalhamento | Fonte |
|-----------|--------------|-------|
| **AET** | Autorização Especial de Trânsito (obrigatória) | DNIT Port. 198/06 |
| **Chofer/Batedor** | Credenciados, comunicação radio | ANTT |
| **Rota** | Aprovada previamente, horários restritos | DNIT/ANTT |
| **Dimensões** | Largura, altura, comprimento, peso por eixo | AET |
| **Seguro** | Responsabilidade civil especial | Contrato |
| **Fator SICOBAN** | 1.50× (JSON fator 08=1.50) | SICOBAN |

---

### 18. CARGA_VIVA_VALIDACAO
**Legislação**: ANTT Res. 5.839/21, Lei 10.931/04 (Bem-estar animal)
| Validação | Detalhamento | Fonte |
|-----------|--------------|-------|
| **GTA** | Guia de Trânsito Animal (obrigatória) | MAPA |
| **Tempo Confinamento** | Máx. 24h (bovinos) / 12h (suínos/aves) | Lei 10.931/04 |
| **Condições** | Ventilação, bebedouro, comedouro, piso antiderrapante | Bem-estar |
| **Motorista** | Treinamento manejo animais | Lei 11.442/07 |
| **Veterinário** | Responsável técnico (grandes volumes) | MAPA |
| **Fator SICOBAN** | 1.25× (JSON fator 10=1.25) | SICOBAN |

---

## 📊 TABELAS DE ALÍQUOTAS PARA VALIDAÇÃO

### ICMS por UF (2024) - Resumo Crítico
| UF | Interna | Interestadual (origem) | FCP Interno | FCP Interestadual | MVA ST (Geral) |
|----|---------|------------------------|-------------|-------------------|----------------|
| SP | 18% | 12% (→S/SE) / 7% (→N/NE) | **2%** | - | 40-60% |
| RJ | 20% | 12% / 7% | **2%** | - | 40-60% |
| MG | 18% | 12% / 7% | - | 2% | 40-50% |
| RS | 17-18% | 12% / 7% | - | 2% | 40-50% |
| PR | 18% | 12% / 7% | - | 2% | 40-50% |
| SC | 17-18% | 12% / 7% | - | 2% | 40-50% |
| BA | 19-20% | 7% (→S/SE) / 12% (→N/NE) | **2%** | 2% | 40-50% |
| GO | 17-19% | 7% / 12% | - | 2% | 40-50% |
| DF | 18-20% | 7% / 12% | - | 2% | 40-50% |
| **N/NE (demais)** | 17-20% | 7% / 12% | - | **2%** | 40-50% |

> **Ver completo**: `icms_rules.json` → `ufs[]` (27 UFs com todas alíquotas, FCP, MVA por NCM)

---

### ANTT Piso Mínimo por Eixo (2024) - R$/km
| Eixos | Piso (R$/km) | Fator >10t | Fonte |
|-------|--------------|------------|-------|
| 2 | 1.85 | 1.2× | ANTT 5.839/21 |
| 3 | 2.45 | 1.2× | ANTT 5.839/21 |
| 4 | 3.05 | 1.2× | ANTT 5.839/21 |
| 5 | 3.65 | 1.2× | ANTT 5.839/21 |
| 6 | 4.25 | 1.2× | ANTT 5.839/21 |
| 7 | 4.85 | 1.2× | ANTT 5.839/21 |
| 8 | 5.45 | 1.2× | ANTT 5.839/21 |
| 9 | 6.05 | 1.2× | ANTT 5.839/21 |

> **JSON**: `antt_piso_minimo.json` → `piso_por_eixo`, `fator_peso_acima_10t`

---

### SICOBAN - Fatores por Tipo Carga
| Código | Tipo Carga | Fator | GRIS Adicional |
|--------|------------|-------|----------------|
| 01 | Carga Geral | 1.00 | Base |
| 02 | **Carga Perigosa** | **1.30** | +0.15-0.25% |
| 03 | Carga Frigorífica | 1.15 | Base |
| 04 | Granel Líquido | 0.85 | Base |
| 05 | Granel Sólido | 0.80 | Base |
| 06 | Neogranel | 1.00 | Base |
| 07 | Container | 1.10 | Base |
| 08 | **Carga Projeto** | **1.50** | +0.20% |
| 09 | Veículos | 1.20 | Base |
| 10 | **Carga Viva** | **1.25** | +0.10% |

> **JSON**: `sicoban_table.json` → `fatores_tipo_carga`

---

## 🔍 CHECKLIST DA REUNIÃO COM CONTADORES

### ICMS (Prioridade ALTA)
- [ ] Confirmar alíquotas internas 2024 por UF (27 UFs)
- [ ] Validar FCP interno: BA 2%, RJ 2%, SP 2% - **incluso na alíquota interna ou destacado?**
- [ ] Validar FCP interestadual: 2% (maioria) / 4% (AP, PB) - **destacado na NF?**
- [ ] Confirmar MVA/IVA-ST por NCM principal (top 50 NCMs do cliente)
- [ ] Validar redução de base ST por UF/NCM
- [ ] Confirmar CSTs sujeitos a ST (10,30,60,70,90,41?)
- [ ] **DIFAL**: Alíquota interestadual 7%/12%/4% - confirma vigência 2024?

### ANTT/Frete (Prioridade ALTA)
- [ ] Validar Piso Mínimo = **MAX(3 métodos)** - Art. 7º ANTT 5.839/21
- [ ] Confirmar fator 1.2× para peso >10t - **ainda vigente?**
- [ ] Validar faixas peso/valor Anexo I (10 faixas × 5 tipos) - **valores 2024?**
- [ ] Validar faixas cubagem Anexo II (10 faixas × 5 tipos) - **valores 2024?**
- [ ] Confirmar tolerâncias peso por tipo carga (5%/3%/20%/10%)
- [ ] **SICOBAN**: Obter tabela oficial 2024 completa (220 células)

### Pedágio (Prioridade MÉDIA)
- [ ] Listar concessionárias relevantes para rotas dos clientes
- [ ] Confirmar categorias veículo por concessionária
- [ ] Validar isenções: eixo suspenso, TAG, convênios
- [ ] Definir fonte de tarifas: API vs publicação manual

### Cargas Especiais (Prioridade MÉDIA)
- [ ] **Perigosa**: Confirmar exigências MOPP, FISPQ, seguro RCTR-C
- [ ] **Frigorífica**: Confirmar prazo máximo por produto, certificados
- [ ] **Projeto**: Confirmar fluxo AET DNIT, batedores, rotas
- [ ] **Viva**: Confirmar GTA, tempos máximos, bem-estar

### Seguros (Prioridade BAIXA)
- [ ] Ad Valorem: alíquotas por tipo carga (0.03% a 0.60%) - **confirmar com corretora**
- [ ] GRIS: alíquotas por região/rota - **confirmar com corretora**
- [ ] Tetos contratuais: definir padrão por cliente

---

## 📁 ARQUIVOS JSON DE APOIO (Já Criados)

| Arquivo | Localização | Conteúdo |
|---------|-------------|----------|
| `icms_rules.json` | `backend/app/data/` | 27 UFs, DIFAL, FCP, ST, MVA |
| `antt_faixas_peso_valor.json` | `backend/app/data/` | 10 faixas × 5 tipos |
| `antt_faixas_cubagem.json` | `backend/app/data/` | 10 faixas × 5 tipos |
| `antt_piso_minimo.json` | `backend/app/data/` | 8 eixos + fatores |
| `pedagio_tarifas.json` | `backend/app/data/` | Estrutura concessionárias |
| `ad_valorem_taxas.json` | `backend/app/data/` | 10 tipos carga |
| `gris_taxas.json` | `backend/app/data/` | 6 regiões/rotas |
| `sicoban_table.json` | `backend/app/data/` | 22 faixas, 10 tipos, fatores |
| `cte_complementar_regras.json` | `backend/app/data/` | 3 tipos + validações |
| `redespacho_regras.json` | `backend/app/data/` | 6 regras negócio |
| `pesos_tolerancia.json` | `backend/app/data/` | 10 tipos + fontes |
| `referencia_cep_faixa.json` | `backend/app/data/` | 22 faixas ↔ CEPs |

---

## 📅 PRÓXIMOS PASSOS PÓS-REUNIÃO

1. **Correções Imediatas** (Sprint 1):
   - ValorMinimoFreteRule → MAX 3 métodos
   - FCPRule → FCP interno BA/RJ/SP
   - ICMSSTRule → Roteiro MVA/IVA completo

2. **Implementação Novas Regras** (Sprint 2):
   - CargaPerigosaRule, CargaFrigorificaRule, CargaProjetoRule, CargaVivaRule

3. **Dados Faltantes**:
   - Popular `sicoban_table.json` com 220 valores absolutos
   - Popular `pedagio_tarifas.json` com tarifas 2024 concessionárias
   - Validar/atualizar MVA ST por NCM no `icms_rules.json`

4. **Automação** (Paralelo - Card XX-techlead-alert-config):
   - Monitoramento DOU, CONFAZ, ANTT, Concessionárias
   - Workflow aprovação → atualização JSONs/DB → hot reload

---

## 👥 PARTICIPANTES SUGERIDOS REUNIÃO

| Papel | Responsabilidade |
|-------|------------------|
| **Contador/Tax Specialist** | Validar ICMS, FCP, ST, MVA, legislação tributária |
| **Especialista Frete/ANTT** | Validar piso mínimo, faixas, SICOBAN, cargas especiais |
| **Corretora Seguros** | Validar Ad Valorem, GRIS, tetos, coberturas |
| **Tech Lead** | Viabilidade técnica, arquitetura, priorização |
| **PO/Scrum Master** | Facilitação, decisões de produto, documentação |

---

**Documento preparado por**: PO/Scrum Master Agent  
**Base**: Pesquisa regulatória completa (18 arquivos .md + 12 JSONs)  
**Próxima atualização**: Após reunião de validação