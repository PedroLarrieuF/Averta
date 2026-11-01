# Revisão de Regras - AvertaSaaS Rules Engine v2
**Data**: 2025-01-15  
**Base**: Pesquisa regulatória (18 arquivos .md) + 12 JSONs de dados  
**Engine Atual**: 15 regras registradas em `create_engine_v2()`

---

## ✅ REGRAS IMPLEMENTADAS (15/17 esperadas)

| # | Regra (Código) | Classe | Legislação Coberta | Status |
|---|----------------|--------|-------------------|--------|
| 1 | **ICMS_DIFAL** | `ICMSDifferentialRule` | LC 87/96, LC 190/22, Conv. 109/24 | ✅ OK |
| 2 | **ICMS_FCP** | `FCPRule` | LC 190/22, Conv. ICMS 109/24 | ⚠️ PARCIAL |
| 3 | **ICMS_ST** | `ICMSSTRule` | Conv. ICMS 52/91, 142/18, Decreto 9.209/17 | ⚠️ PARCIAL |
| 4 | **FRETE_PESO_VALOR** | `FreightWeightValueRule` | ANTT Res. 5.839/21 Art. 6º, Anexo I | ✅ OK |
| 5 | **FRETE_CUBAGE** | `FreightCubageRule` | ANTT Res. 5.839/21 Anexo II | ✅ OK |
| 6 | **VALOR_MINIMO_FRETE** | `ValorMinimoFreteRule` | ANTT Res. 5.839/21 Art. 7º (Piso por Eixo) | ⚠️ PARCIAL |
| 7 | **PESO_REAL_VS_FATURADO** | `PesoRealVsFaturadoRule` | ANTT Res. 5.839/21 Art. 7º, Tolerâncias por tipo | ✅ OK |
| 8 | **REDESPACHO_VALIDACAO** | `RedespachoRule` | Lei 11.442/07, Decreto 9.209/17, ANTT 5.839/21 | ✅ OK |
| 9 | **PEDAGIO_CONFERENCIA** | `TollPlazaRule` | Lei 10.233/01, Res. ANTT 5.839/21 | ⚠️ PARCIAL |
| 10 | **AD_VALOREM** | `AdValoremRule` | Susep Circular 615/21, Lei 11.442/07 | ✅ OK |
| 11 | **GRIS** | `GRISRule` | Susep, Lei 11.442/07 Art. 15 | ✅ OK |
| 11 | **SICOBAN_TABLE_REAL** | `SicobanTableRuleReal` | ANTT Res. 5.933/23 Anexo III | ⚠️ PARCIAL |
| 12 | **CTE_ANULACAO** | `ComplementaryCTEAnulationRule` | Decreto 9.209/17, Conv. ICMS 188/17 | ✅ OK |
| 13 | **CTE_SUBSTITUICAO** | `ComplementaryCTESubstitutionRule` | Decreto 9.209/17, Conv. ICMS 188/17 | ✅ OK |
| 14 | **CTE_COMPLEMENTO_VALOR** | `ComplementaryCTEComplementRule` | Decreto 9.209/17, Conv. ICMS 188/17 | ✅ OK |

---

## ❌ REGRAS FALTANDO (Identificadas na Pesquisa Regulatória)

| # | Regra Necessária | Legislação / Fonte | Motivo |
|---|------------------|-------------------|--------|
| 15 | **CARGA_PERIGOSA_VALIDACAO** | ANTT Res. 5.948/23, ABNT NBR 7500, ONU | Produtos perigosos exigem: <br/>• Documentação completa (FISPQ, RISCO, Envelope)<br/>• Veículo/condutor certificado (MOPP)<br/>• Kit emergência, painéis ONU<br/>• GRIS majorado (fator 1.30 no SICOBAN)<br/>• Seguro RCTR-C obrigatório |
| 16 | **CARGA_FRIORIFICA_VALIDACAO** | ANVISA RDC 216/04, ANTT Res. 5.839/21 | Carga frigorífica exige:<br/>• Controle temperatura (registro termoógrafo)<br/>• Certificado sanitário<br/>• Prazo máximo viagem<br/>• Fator SICOBAN 1.15 |
| 17 | **CARGA_PROJETO_VALIDACAO** | ANTT Res. 5.839/21, DNIT Portaria 198/06 | Carga projeto (excedente) exige:<br/>• AET (Autorização Especial de Trânsito)<br/>• Chofer/batedor credenciado<br/>• Rota aprovada, horários restritos<br/>• Fator SICOBAN 1.50, seguro especial |
| 18 | **CARGA_VIVA_VALIDACAO** | ANTT Res. 5.839/21, Lei 10.931/04 (Bem-estar animal) | Carga viva exige:<br/>• GTA (Guia Trânsito Animal)<br/>• Tempo máximo confinamento<br/>• Ventilação, água, alimentação<br/>• Motorista treinado<br/>• Fator SICOBAN 1.25 |

---

## ⚠️ REGRAS EXISTENTES COM GAPS (Precisam Alteração)

### 1. **FCPRule** - Faltando FCP Interno (BA, RJ, SP)
- **Atual**: Só valida FCP em interestadual (UFs Norte/Nordeste)
- **Faltando**: FCP interno nas UFs **BA (2%), RJ (2%), SP (2%)** - incluso na alíquota interna
- **JSON**: `icms_rules.json` já tem `"fcp_interno": true` para essas UFs
- **Ação**: Adicionar validação para operações **intraestaduais** nessas UFs

### 2. **ICMSSTRule** - Cálculo MVA/IVA-ST Incorreto
- **Atual**: Usa `aliquota_st` direto da tabela
- **Correto**: Base ST = `VFrete + VSeguro + Outras Despesas` → **Aplicar MVA/IVA** → BC ST → Aplicar alíquota interestadual → Deduzir ICMS próprio
- **JSON**: `icms_rules.json` tem `mva_ajustado` por NCM/UF
- **Ação**: Reescrever cálculo seguindo Roteiro ST nacional (Conv. 142/18)

### 3. **ValorMinimoFreteRule** - Piso Mínimo = MAX(3 Métodos)
- **Atual**: Só usa **Piso por Eixo × Distância**
- **Regulamentação (Art. 7º ANTT 5.839/21)**: Piso = **MÁXIMO** de:
  1. Piso por Eixo × Distância
  2. Peso × Faixa Peso/Valor (ANTT Anexo I)
  3. Cubagem × Faixa Cubagem (ANTT Anexo II)
- **Ação**: Calcular os 3 e pegar o maior

### 4. **SicobanTableRuleReal** - Matriz Incompleta
- **Atual**: Estrutura básica, lookup por CEP 5 dígitos
- **Necessário**: Matriz completa **22 faixas × 10 tipos carga** com `valor_kg`, `valor_m3`, `valor_minimo` por combinação
- **JSON**: `sicoban_table.json` tem fatores por tipo carga, mas **faltam valores absolutos** por faixa
- **Ação**: Popular tabela completa ou integrar com API ANTT/SICOBAN

### 5. **TollPlazaRule** - Validação Simplificada
- **Atual**: Compara valor documento vs tabela estática
- **Necessário**: 
  - Validar **praça × eixos × categoria veículo** (tabela concessionária)
  - Considerar **isento** (eixo suspenso, TAG, convênio)
  - **API concessionárias** (CCR, EcoRodovias, Arteris) para tarifas vigentes
- **JSON**: `pedagio_tarifas.json` tem estrutura, precisa popular

### 6. **RedespachoRule** - Faltando Validações Obrigatórias
- **Atual**: Só soma valores e compara com frete principal
- **Faltando** (conforme `redespacho_regras.json`):
  - ✅ refCTe obrigatório
  - ✅ Transportadores diferentes
  - ✅ Piso mínimo por trecho
  - ✅ Soma fretes ≥ piso direto
  - ⚠️ ICMS: Principal recolhe total (validar partilha)
  - ⚠️ Redespachante pode ser isento (validar CST)

---

## 📊 RESUMO DE AÇÕES

| Categoria | Quantidade |
|-----------|------------|
| Regras implementadas OK | 8 |
| Regras com gaps (precisam alteração) | 6 |
| Regras **faltando** (novas) | 4 |
| **Total regras alvo** | **18** |

---

## 🗂️ ARQUIVOS JSON CRIADOS (Dados para Rules Engine)

| Arquivo | Regras que Consomem | Status |
|---------|-------------------|--------|
| `icms_rules.json` | ICMS_DIFAL, ICMS_FCP, ICMS_ST | ✅ Completo (27 UFs, MVA, FCP interno) |
| `antt_faixas_peso_valor.json` | FRETE_PESO_VALOR, VALOR_MINIMO_FRETE | ✅ 10 faixas × 5 tipos carga |
| `antt_faixas_cubagem.json` | FRETE_CUBAGE, VALOR_MINIMO_FRETE | ✅ 10 faixas × 5 tipos carga |
| `antt_piso_minimo.json` | VALOR_MINIMO_FRETE | ✅ 6 eixos + fatores |
| `pedagio_tarifas.json` | PEDAGIO_CONFERENCIA | ⚠️ Estrutura OK, **precisa popular tarifas reais** |
| `ad_valorem_taxas.json` | AD_VALOREM | ✅ Por tipo carga (0.03% a 0.60%) |
| `gris_taxas.json` | GRIS | ✅ Por região/rota (0.1% a 0.5%) |
| `sicoban_table.json` | SICOBAN_TABLE_REAL | ⚠️ Estrutura OK, **faltam valores absolutos por faixa** |
| `cte_complementar_regras.json` | 3 CT-e Complementar | ✅ Completo |
| `redespacho_regras.json` | REDESPACHO_VALIDACAO | ✅ Regras de negócio documentadas |
| `pesos_tolerancia.json` | PESO_REAL_VS_FATURADO | ✅ 10 tipos carga com tolerâncias |
| `referencia_cep_faixa.json` | SICOBAN_TABLE_REAL | ✅ 22 faixas mapeadas |

---

## 🔍 PRÓXIMOS PASSOS RECOMENDADOS

### Sprint Imediato (Correções Críticas)
1. **Corrigir `ValorMinimoFreteRule`** - Implementar MAX dos 3 métodos ANTT
2. **Corrigir `FCPRule`** - Adicionar FCP interno (BA/RJ/SP) 
3. **Corrigir `ICMSSTRule`** - Implementar cálculo MVA/IVA-ST correto
4. **Popular `pedagio_tarifas.json`** - Tarifas concessionárias 2024

### Próxima Sprint (Regras Faltando)
5. Implementar `CargaPerigosaRule` (validação docs + MOPP + GRIS majorado)
6. Implementar `CargaFrigorificaRule` (temp + certificado + prazo)
7. Implementar `CargaProjetoRule` (AET + rota + batedor)
8. Implementar `CargaVivaRule` (GTA + bem-estar + tempo)

### Melhorias Contínuas
9. **SICOBAN**: Completar matriz 22×10 com valores reais ou integrar API ANTT
10. **Pedágio**: Integrar APIs concessionárias (CCR, EcoRodovias, Arteris)
11. **Cache Redis**: Implementar `_cache` no `RulesEngineV2` (atualmente `None`)
12. **Testes**: Atualizar `test_rules_critical.py` com casos reais da pesquisa

---

## 📝 OBSERVAÇÕES TÉCNICAS

- **Tag Filtering**: Engine usa `relevance_tags` para O(tag) vs O(total) - funcionando
- **Multi-tenancy**: `company_id` no `context.metadata` - OK
- **DB Config**: Regras podem vir do banco (tabela `freight_table.rules`) - preparado
- **Evidências**: `evidence` no `DiscrepancyResult` para auditoria - OK
- **Severidades**: CRITICAL/HIGH/MEDIUM/LOW - consistente

---

**Preparado por**: PO/Scrum Master Agent  
**Para revisão**: Tech Lead / Tax Specialist / Contador