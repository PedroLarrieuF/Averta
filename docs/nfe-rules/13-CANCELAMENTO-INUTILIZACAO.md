# Cancelamento e Inutilização NF-e - Regras NFE_CANCELAMENTO, NFE_INUTILIZACAO

**Rule Codes:** `NFE_CANCELAMENTO`, `NFE_INUTILIZACAO`  
**Tipo:** `CANCELLATION` / `INUTILIZATION`  
**Severidade:** `MEDIUM` / `MEDIUM`  
**Tags:** `cancellation, inutilizacao, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/cancelamento_inutilizacao.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_cancelamento_prazo`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Ajuste SINIEF 07/2005** | Cancelamento NF-e | Vigente |
| **Ajuste SINIEF 19/2016** | NF-e 4.00 cancelamento/inutilização | Vigente |
| **Manual NF-e 4.00** | Eventos cancelamento (110111) e inutilização | Vigente |
| **RICMS/UF** | Prazos estaduais cancelamento | Vigente |

---

## 🎯 Cancelamento NF-e (Evento 110111)

### O que é
Tornar a NF-e **sem efeitos jurídicos** após autorização.

### Requisitos Obrigatórios
1. **NF-e AUTORIZADA** (status = "AUTORIZADA")
2. **NÃO houve circulação da mercadoria**
3. **NÃO foi utilizado** o crédito de ICMS pelo destinatário
4. **Prazo** respeitado (ver abaixo)
5. **Justificativa** informada

### Prazo Cancelamento (Por UF - Exemplos)

| UF | Prazo Padrão | Prazo Estendido | Observação |
|----|--------------|-----------------|------------|
| **SP** | 24 horas | 168 horas (7 dias) | Com justificativa |
| **RJ** | 24 horas | 168 horas | |
| **MG** | 24 horas | 168 horas | |
| **PR** | 24 horas | 168 horas | |
| **RS** | 24 horas | 168 horas | |
| **Outras** | 24 horas | Ver legislação | Maioria 24h/168h |

> ⚠️ **Verificar RICMS/UF** - prazos podem variar

### Estrutura Evento Cancelamento
```xml
<evento>
  <infEvento>
    <tpEvento>110111</tpEvento>           <!-- Cancelamento -->
    <chNFe>35250101234567890123550010000000011234567890</chNFe>
    <nSeqEvento>1</nSeqEvento>
    <detEvento>
      <descEvento>Cancelamento</descEvento>
      <nProt>352501012345678</nProt>      <!-- Protocolo autorização -->
      <xJust>Erro emissão - mercadoria não saiu</xJust>  <!-- Mín 15 chars -->
    </detEvento>
  </infEvento>
</evento>
```

---

## 🎯 Inutilização de Numeração (Evento 110112)

### O que é
Declarar que uma **faixa de numeração** **NÃO SERÁ UTILIZADA**.

### Quando Usar
- Numeração pulada por erro de sistema
- Falha emissão que não gerou XML
- Troca de série/numeração
- Fim de atividades (fechamento empresa)

### Requisitos
1. **Numeração NÃO foi usada** em nenhuma NF-e
2. **Justificativa** obrigatória
3. **Ano, Série, Inicial, Final** informados
4. **CNPJ emitente** correto

### Estrutura Evento Inutilização
```xml
<inutNFe>
  <infInut>
    <tpAmb>1</tpAmb>                      <!-- 1=Produção, 2=Homologação -->
    <xServ>INUTILIZAR</xServ>
    <cUF>35</cUF>                         <!-- UF emitente -->
    <ano>25</ano>                         <!-- Ano (2 dígitos) -->
    <CNPJ>12345678000199</CNPJ>
    <mod>55</mod>                         <!-- Modelo NF-e -->
    <serie>1</serie>
    <nNFIni>100</nNFIni>                  <!-- Inicial -->
    <nNFFin>105</nNFFin>                  <!-- Final -->
    <xJust>Erro numeração - notas 100 a 105 não emitidas</xJust>
  </infInut>
</inutNFe>
```

---

## 🔍 Lógica de Detecção no Engine

```python
class NFECancelamentoRule(BaseRule):
    code = "NFE_CANCELAMENTO"
    relevance_tags = {"cancellation", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.tem_evento_cancelamento
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        canc = context.evento_cancelamento
        
        # 1. NF-e deve estar AUTORIZADA
        nfe = self.get_nfe_by_chave(canc.chNFe)
        if not nfe:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "NF-e para cancelamento não encontrada", "chNFe": canc.chNFe}
            ))
        elif nfe.status != "AUTORIZADA":
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": f"NF-e não está AUTORIZADA (status: {nfe.status})", "chNFe": canc.chNFe}
            ))
        
        # 2. Prazo cancelamento
        if nfe and nfe.dhAutorizacao:
            horas_decorridas = (datetime.now() - nfe.dhAutorizacao).total_seconds() / 3600
            prazo_padrao = 24
            prazo_estendido = self.get_prazo_estendido_uf(nfe.uf_emitente)  # ex: 168h
            
            if horas_decorridas > prazo_estendido:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "erro": f"Cancelamento fora do prazo ({horas_decorridas:.0f}h > {prazo_estendido}h)",
                        "horas_decorridas": horas_decorridas,
                        "prazo_maximo": prazo_estendido,
                        "uf": nfe.uf_emitente
                    }
                ))
            elif horas_decorridas > prazo_padrao and not canc.tem_justificativa_estendida:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="MEDIUM",
                    details={
                        "aviso": f"Cancelamento após {prazo_padrao}h - requer justificativa estendida",
                        "horas_decorridas": horas_decorridas
                    }
                ))
        
        # 3. Protocolo autorização obrigatório
        if not canc.nProt:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "Protocolo autorização (nProt) obrigatório no cancelamento"}
            ))
        
        # 4. Justificativa mínima 15 caracteres
        if not canc.xJust or len(canc.xJust) < 15:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={"erro": "Justificativa (xJust) obrigatória, mínimo 15 caracteres"}
            ))
        
        # 5. Verificar se mercadoria circulou (cross com CT-e)
        if context.cte and nfe:
            if context.cte.status in ["AUTORIZADO", "EM_TRANSITO"]:
                discrepancies.append(Discrepancy(
                    rule_code="NFE_CTE_CROSS_VALIDATION",
                    severity="CRITICAL",
                    details={
                        "validacao": "CANCELAMENTO_COM_CTE_AUTORIZADO",
                        "nfe_chave": nfe.chave_acesso,
                        "cte_chave": context.cte.chave_acesso,
                        "risco": "Mercadoria pode ter circulado - cancelamento irregular"
                    }
                ))
        
        return discrepancies


class NFEInutilizacaoRule(BaseRule):
    code = "NFE_INUTILIZACAO"
    relevance_tags = {"inutilizacao", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.tem_evento_inutilizacao
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        inut = context.evento_inutilizacao
        
        # 1. Verificar se numeração JÁ foi usada
        for n in range(inut.nNFIni, inut.nNFFin + 1):
            nfe_existente = self.get_nfe_por_numero(inut.CNPJ, inut.serie, n, inut.ano)
            if nfe_existente:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "erro": f"Numeração {n} já usada na NF-e {nfe_existente.chave_acesso}",
                        "nNF": n,
                        "serie": inut.serie
                    }
                ))
        
        # 2. Justificativa obrigatória
        if not inut.xJust or len(inut.xJust) < 15:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={"erro": "Justificativa inutilização obrigatória, mínimo 15 caracteres"}
            ))
        
        # 3. Faixa válida (inicial <= final)
        if inut.nNFIni > inut.nNFFin:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "Numeração inicial > final"}
            ))
        
        # 4. CNPJ emitente correto
        if inut.CNPJ != context.emit_cnpj:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "CNPJ inutilização difere do emitente NF-e"}
            ))
        
        return discrepancies
```

---

## 🧪 Casos de Teste

```python
# test_nfe_cancelamento_prazo_24h
# Cancelamento 12h após autorização → OK

# test_nfe_cancelamento_prazo_estendido
# Cancelamento 100h (SP) com justificativa → OK

# test_nfe_cancelamento_fora_prazo
# Cancelamento 200h (SP) → HIGH

# test_nfe_cancelamento_nao_autorizada
# NF-e REJEITADA, tentar cancelar → HIGH

# test_nfe_cancelamento_sem_protocolo
# Sem nProt → HIGH

# test_nfe_cancelamento_sem_justificativa
# xJust vazio → MEDIUM

# test_nfe_cancelamento_com_cte
# NF-e cancelada mas CT-e autorizado → CRITICAL (cross)

# test_nfe_inutilizacao_numero_usado
# Inutilizar 100-105 mas 102 já emitida → HIGH

# test_nfe_inutilizacao_sem_justificativa
# xJust vazio → MEDIUM

# test_nfe_inutilizacao_faixa_invalida
# nNFIni=105, nNFFin=100 → HIGH
```

---

## ⚠️ Pontos de Atenção

### Cancelamento
1. **Só NF-e AUTORIZADA** pode ser cancelada
2. **Prazo**: 24h padrão, até 168h (7 dias) com justificativa (ver UF)
3. **Sem circulação mercadoria** - cross com CT-e crítico
4. **Sem crédito ICMS destinatário** - destinatário não pode ter usado
5. **Protocolo autorização (nProt)** obrigatório
6. **Justificativa ≥ 15 chars**

### Inutilização
1. **Numeração NÃO PODE TER SIDO USADA** - verificar base
2. **Faixa contígua** (inicial ≤ final)
3. **Justificativa ≥ 15 chars**
4. **CNPJ, Ano, Série, Modelo** corretos
5. **Não desfaz** - apenas declara que não usará

---

## 📦 JSON para backend/app/data/nfe/cancelamento_inutilizacao.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "cancelamento": {
    "tpEvento": "110111",
    "requisitos": [
      "nfe_autorizada",
      "sem_circulacao_mercadoria",
      "sem_credito_icms_destinatario",
      "prazo_respeitado",
      "protocolo_autorizacao",
      "justificativa_min_15_chars"
    ],
    "prazos_uf": {
      "padrao_horas": 24,
      "estendido_horas": {
        "SP": 168, "RJ": 168, "MG": 168, "PR": 168, "RS": 168,
        "SC": 168, "BA": 168, "GO": 168, "DF": 168, "ES": 168
      },
      "observacao": "Verificar RICMS/UF para UFs não listadas"
    },
    "cross_cte": {
      "verificar_cte_autorizado": true,
      "bloquear_se_cte_circulando": true
    }
  },
  "inutilizacao": {
    "tpEvento": "110112",
    "requisitos": [
      "numeracao_nao_usada",
      "faixa_contigua",
      "justificativa_min_15_chars",
      "cnpj_emitente_correto",
      "ano_serie_modelo_corretos"
    ],
    "validacoes": {
      "verificar_base_nfe": true,
      "faixa_maxima": 1000
    }
  }
}
```

---

## 🔗 Referências

- [Manual NF-e 4.00 - Cancelamento](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Manual NF-e 4.00 - Inutilização](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent