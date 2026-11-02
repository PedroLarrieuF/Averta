# Pauta Reunião Validação Tributária - AvertaSaaS
**Data**: [A agendar] | **Duração**: 2h | **Participantes**: Contador/Tax Specialist + PO + Tech Lead

---

## 🎯 OBJETIVO
Validar **18 regras** do Rules Engine v2 (auditoria de frete) para garantir conformidade legal antes de implementar/corrigir no código.

---

## 📋 PAUTA PRIORITÁRIA (Itens para Decisão)

### 1. ICMS - FCP Interno (BA, RJ, SP) 🔴 **CRÍTICO**
| Pergunta | Opção Atual | Necessita Confirmação |
|----------|-------------|----------------------|
| FCP interno (2%) em BA, RJ, SP é **destacado na NF-e** ou **incluso na alíquota interna**? | Código assume destacado | ✅ **DECIDIR** |
| Alíquota FCP interestadual: 2% para todas UFs N/NE? **AP e PB são 4%**? | JSON tem 4% para AP/PB | ✅ Confirmar vigência 2024 |
| FCP incide sobre **base ICMS normal** ou **base reduzida**? | Base normal | ✅ Confirmar |

---

### 2. ICMS ST - Cálculo via MVA/IVA Ajustado 🔴 **CRÍTICO**
| Etapa do Cálculo | Implementação Atual | Correta (Roteiro Nacional) | Decisão |
|------------------|---------------------|---------------------------|---------|
| 1. Base Inicial | VFrete + VSeg + Despesas | ✅ Igual | OK |
| 2. Aplicar MVA Ajustado | ❌ **NÃO APLICA** | BC_ST = Base × (1 + MVA_ajustado) | ✅ **IMPLEMENTAR** |
| 3. ICMS ST | BC_ST × alíq_interestadual | ✅ Igual | OK |
| 4. Deduzir ICMS Próprio | ❌ Não deduz | ICMS_ST_final = ICMS_ST - ICMS_próprio | ✅ **IMPLEMENTAR** |

**Preciso do Contador**:
- [ ] Confirmar MVA ajustado por NCM principal dos clientes (top 20 NCMs)
- [ ] Validar redução de base ST por UF
- [ ] CSTs sujeitos: 10, 30, 60, 70, 90 **(CST 41 incluso?)**

---

### 3. Piso Mínimo Frete ANTT - MAX de 3 Métodos 🔴 **CRÍTICO**
| Método | Fórmula | Status |
|--------|---------|--------|
| **1. Piso por Eixo** | `Piso_eixo(R$/km) × Distância_km` | ✅ Implementado |
| **2. Faixa Peso/Valor** | `Peso × Valor_kg (Anexo I)` | ❌ **FALTANDO** |
| **3. Faixa Cubagem** | `Volume_m³ × Valor_m³ (Anexo II)` | ❌ **FALTANDO** |
| **Regra Final** | **MAX(Método1, Método2, Método3)** | ❌ **CORRIGIR** |

**Pergunta ao Contador/Especialista ANTT**:
- [ ] Art. 7º Res. 5.839/21: **é MAX dos 3 mesmo?** (confirmar interpretação)
- [ ] Fator 1.2× para peso > 10t: **ainda vigente em 2024?**
- [ ] Piso por eixo (R$/km) 2024: validar tabela JSON `antt_piso_minimo.json`

---

### 4. SICOBAN - Tabela Completa 22×10 🟡 **ALTO**
| Item | Status | Ação |
|------|--------|------|
| 22 faixas CEP × 10 tipos carga = 220 células | ⚠️ Só fatores multiplicadores | **Obter valores absolutos 2024** |
| Valores: `valor_kg`, `valor_m3`, `valor_minimo` por célula | ❌ Ausentes | Solicitar tabela oficial ANTT/SICOBAN |
| Atualização: manual vs API | Manual | Definir processo |

---

### 5. Pedágio - Tarifas Concessionárias 🟡 **MÉDIO**
- [ ] Listar concessionárias das rotas dos clientes (CCR, EcoRodovias, Arteris, Triunfo, etc.)
- [ ] Categorias veículo por concessionária (moto, carro, leve, pesado 2/3/4+ eixos)
- [ ] Isenções: eixo suspenso, TAG, convênios municipais
- [ ] Fonte: API oficial vs publicação manual no JSON

---

### 6. Redespacho - Validações Fiscais 🟡 **MÉDIO**
| Regra | Status | Validação Necessária |
|-------|--------|---------------------|
| ICMS principal recolhe total (partilha) | ❌ Não validado | Como calcular partilha? |
| Redespachante pode ser isento (CST) | ❌ Não validado | Quais CSTs permitem isenção? |
| Piso mínimo por trecho | ⚠️ Parcial | Usar piso mínimo corrigido (item 3) |

---

## 🆕 NOVAS REGRAS - CARGAS ESPECIAIS (Definir Escopo)

### 7. Carga Perigosa 🟡 **MÉDIO**
| Validação | Obrigatória? | Observação |
|-----------|--------------|------------|
| FISPQ + Ficha RISCO + Envelope | ✅ Sim | ANTT 5.948/23 |
| Veículo certificado IPVAV + Kit + Painéis ONU | ✅ Sim | ABNT NBR 7500 |
| Condutor MOPP válido (reciclagem 5 anos) | ✅ Sim | Lei 11.442/07 |
| GRIS fator 1.30× | ✅ Sim | Já no JSON SICOBAN |
| Seguro RCTR-C + RC-Veículo | ✅ Sim | Susep |
| Roteiro rotas permitidas/restritas | 🟡 Opcional v1 | ANTT/DNIT |

---

### 8. Carga Frigorífica 🟡 **MÉDIO**
| Validação | Obrigatória? | Observação |
|-----------|--------------|------------|
| Registro termoógrafo (todo trajeto) | ✅ Sim | ANVISA RDC 216/04 |
| Certificado Sanitário / Origem | ✅ Sim | MAPA/ANVISA |
| Prazo máximo viagem (por produto) | 🟡 Definir | Congelado vs Resfriado |
| Fator SICOBAN 1.15× | ✅ Sim | JSON fator 03=1.15 |

---

### 9. Carga Projeto (Excedente) 🟢 **BAIXO v1**
| Validação | Obrigatória? | Observação |
|-----------|--------------|------------|
| AET (Autorização Especial Trânsito) | ✅ Sim | DNIT Port. 198/06 |
| Chofer/Batedor credenciados | ✅ Sim | ANTT |
| Rota aprovada + horários | ✅ Sim | DNIT/ANTT |
| Fator SICOBAN 1.50× | ✅ Sim | JSON fator 08=1.50 |

---

### 10. Carga Viva 🟢 **BAIXO v1**
| Validação | Obrigatória? | Observação |
|-----------|--------------|------------|
| GTA (Guia Trânsito Animal) | ✅ Sim | MAPA |
| Tempo máx. confinamento (24h bovinos / 12h suínos/aves) | ✅ Sim | Lei 10.931/04 |
| Ventilação, água, alimentação, piso | ✅ Sim | Bem-estar animal |
| Fator SICOBAN 1.25× | ✅ Sim | JSON fator 10=1.25 |

---

## ✅ REGRAS PARA APENAS CONFIRMAR (Baixo Risco)

| Regra | Item a Confirmar |
|-------|------------------|
| ICMS DIFAL | Alíquotas interestaduais 7%/12%/4% vigentes 2024? |
| Frete Peso/Valor | 10 faixas × 5 tipos - valores Anexo I 2024 OK? |
| Frete Cubagem | 10 faixas × 5 tipos - valores Anexo II 2024 OK? |
| Peso Real vs Faturado | Tolerâncias por tipo (5%/3%/20%/10%) OK? |
| CT-e Complementar | 3 tipos (anu/subst/compl) - validações OK? |
| Ad Valorem | Alíquotas 0.03%-0.60% por tipo - confirmar com corretora? |
| GRIS | Alíquotas 0.10%-0.50% por região - confirmar com corretora? |

---

## 📊 MATRIZ DE DECISÕES NECESSÁRIAS

| # | Decisão | Responsável | Prazo | Impacto se Não Decidir |
|---|---------|-------------|-------|------------------------|
| 1 | FCP interno destacado ou incluso? | Contador | Reunião | Regra FCP incorreta para BA/RJ/SP |
| 2 | MVA/IVA-ST: roteiro completo confirmado? | Contador | Reunião | ST calculado errado (risco fiscal alto) |
| 3 | Piso Mínimo = MAX 3 métodos? | Esp. ANTT | Reunião | Frete abaixo do mínimo legal |
| 4 | Top 20 NCMs com MVA ajustado por UF | Contador | Pós-reunião | ST genérico vs específico |
| 5 | Tabela SICOBAN 2024 completa | Esp. ANTT | Sprint 1 | SICOBAN usa apenas fatores |
| 6 | Concessionárias pedágio prioritárias | Operações | Sprint 1 | Pedágio validado só por tabela estática |
| 7 | Cargas especiais: quais clientes têm? | Comercial | Sprint 1 | Escopo v1 vs v2 |

---

## 📁 DOCUMENTOS DE APOIO (Levar para Reunião)

1. **`docs/regras_validacao_contadores.md`** - Documento completo (este repo)
2. **`backend/app/data/icms_rules.json`** - 27 UFs com alíquotas, FCP, MVA
3. **`backend/app/data/antt_piso_minimo.json`** - Pisos por eixo
4. **`backend/app/data/antt_faixas_peso_valor.json`** - Anexo I
5. **`backend/app/data/antt_faixas_cubagem.json`** - Anexo II
6. **`backend/app/data/sicoban_table.json`** - 22 faixas × 10 tipos (fatores)
7. **`backend/app/data/pesos_tolerancia.json`** - Tolerâncias ANTT
8. **`backend/app/data/cte_complementar_regras.json`** - 3 tipos CT-e
9. **`backend/app/data/redespacho_regras.json`** - Regras negócio redespacho

---

## 🎬 PRÓXIMOS PASSOS PÓS-REUNIÃO

| Ação | Responsável | Prazo |
|------|-------------|-------|
| Atualizar JSONs com decisões | Dev Backend | 2 dias |
| Corrigir 6 regras com gaps | Dev Backend | Sprint 1 |
| Implementar 4 novas regras (cargas) | Dev Backend | Sprint 2 |
| Criar cards Kanban para cada item | PO | Imediato |
| Agendar validação corretora seguros | PO | Semana 1 |

---

## ✍️ REGISTRO DE DECISÕES (Preencher na Reunião)

| Item | Decisão | Justificativa | Ação Código |
|------|---------|---------------|-------------|
| FCP Interno | | | |
| ST MVA Roteiro | | | |
| Piso Mínimo MAX 3 | | | |
| SICOBAN Valores | | | |
| Pedágio Concessionárias | | | |
| Redespacho ICMS Partilha | | | |
| Carga Perigosa Escopo | | | |
| Carga Frigorífica Escopo | | | |
| Carga Projeto Escopo | | | |
| Carga Viva Escopo | | | |

---

**Preparado por**: PO/Scrum Master Agent  
**Versão**: 1.0 - Pronta para reunião