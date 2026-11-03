# NF-e Complementar / Carta de Correção - Regras NFE_COMPLEMENTAR, NFE_CARTA_CORRECAO

**Rule Codes:** `NFE_COMPLEMENTAR`, `NFE_CARTA_CORRECAO`  
**Tipo:** `COMPLEMENTARY` / `CORRECTION`  
**Severidade:** `MEDIUM` / `MEDIUM`  
**Tags:** `complementar, carta_correcao, nfe`  
**Arquivo de Dados:** `backend/app/data/nfe/nfe_complementar_regras.json`  
**Teste:** `tests/test_nfe_rules_critical.py::test_nfe_complementar_validacao`

---

## 📜 Base Legal

| Norma | Descrição | Vigência |
|-------|-----------|----------|
| **Ajuste SINIEF 07/2005** | NF-e complementar | Vigente |
| **Ajuste SINIEF 19/2016** | NF-e 4.00 complementar | Vigente |
| **Convênio ICMS 188/2017** | Padronização complementar | Vigente |
| **Manual NF-e 4.00** | tpEmis complementar, Carta Correção | Vigente |
| **Decreto 9.209/2017** | Art. 33-35 (referência CT-e) | Vigente |

---

## 🎯 Tipos de NF-e Complementar (tpEmis)

| tpEmis | Tipo | Descrição | Quando Usa |
|--------|------|-----------|------------|
| **1** | Normal | NF-e normal | Padrão |
| **4** | **Complementar** | Complementa valor (frete, ICMS, IPI) | Diferença de frete, ICMS complementar |
| **5** | Contingência FS-DA | Formulário de Segurança - Declaração Antecipada | Falha SEFAZ |
| **6** | Contingência FS-IA | Formulário de Segurança - Impressão Antecipada | Falha SEFAZ |
| **7** | Contingência SVC-AN | Serviço de Validação de Contingência - Ambiente Nacional | Falha SEFAZ |
| **8** | Contingência SVC-RS | Serviço de Validação de Contingência - RS | Falha SEFAZ |
| **9** | Contingência DPEC | Declaração Prévia de Emissão em Contingência | Falha SEFAZ |

> **FOCO AUDITORIA**: `tpEmis = 4` (Complementar) - principal para recuperação valores

---

## 🔍 NF-e Complementar (tpEmis=4)

### Estrutura XML
```xml
<infNFe>
  <ide>
    <tpEmis>4</tpEmis>                    <!-- Complementar -->
    <refNFe>35250101234567890123550010000000011234567890</refNFe>  <!-- Chave NF-e original -->
  </ide>
  <emit>...</emit>
  <dest>...</dest>
  <det>                                   <!-- Itens complementares -->
    <nItem>1</nItem>
    <prod>
      <cProd>COMPL001</cProd>
      <xProd>Complemento Frete</xProd>
      <NCM>00000000</NCM>                 <!-- NCM genérico complementar -->
      <CFOP>5.352</CFOP>                  <!-- CFOP frete -->
      <uCom>UN</uCom>
      <qCom>1.0000</qCom>
      <vUnCom>500.00</vUnCom>
      <vProd>500.00</vProd>
    </prod>
    <imposto>
      <ICMS>
        <ICMS00>
          <orig>0</orig>
          <CST>00</CST>
          <vBC>500.00</vBC>
          <pICMS>18.00</pICMS>
          <vICMS>90.00</vICMS>
        </ICMS>
      </ICMS>
    </imposto>
  </det>
  <total>
    <ICMSTot>
      <vProd>500.00</vProd>
      <vFrete>500.00</vFrete>             <!-- Valor complementar frete -->
      <vICMS>90.00</vICMS>                <!-- ICMS complementar -->
      <vNF>590.00</vNF>                   <!-- Total complementar -->
    </ICMSTot>
  </total>
</infNFe>
```

### Regras Validação Complementar
1. **refNFe OBRIGATÓRIO** - Chave NF-e original
2. **NF-e original DEVE EXISTIR** e estar **AUTORIZADA**
3. **Valor complementar NÃO PODE SER NEGATIVO**
4. **CFOP deve ser de frete** (5352/3/4, 6352/3/4) ou compatível
5. **ICMS complementar** calculado sobre valor complementar
6. **Não substitui nem anula** - apenas SOMA

---

## 🎯 Carta de Correção (CC-e)

### O que é
Documento eletrônico para **corrigir erros** na NF-e **SEM ALTERAR VALORES**.

### Campos Permitidos (até 20)
| Campo | Tag XML | Pode Corrigir? |
|-------|---------|----------------|
| Dados emitente (endereço, IE) | `<enderEmit>`, `<IE>` | ✓ |
| Dados destinatário (endereço, IE) | `<enderDest>`, `<IE>` | ✓ |
| CFOP | `<CFOP>` | ✓ |
| NCM | `<NCM>` | ✓ |
| Peso/Volume | `<peso>`, `<vol>` | ✓ |
| Transportadora/Veículo | `<transp>` | ✓ |
| Natureza operação | `<natOp>` | ✓ |
| Informações complementares | `<infCpl>` | ✓ |
| **vNF, vProd, vFrete, vICMS, vBC, CST** | **VALORES** | **✗ NÃO** |
| **Quantidade produtos** | `<qCom>` | **✗ NÃO** |

### Estrutura CC-e
```xml
<evento>
  <infEvento>
    <tpEvento>110110</tpEvento>           <!-- Carta Correção -->
    <chNFe>35250101234567890123550010000000011234567890</chNFe>
    <nSeqEvento>1</nSeqEvento>
    <detEvento>
      <xCorrecao>Correção endereço destinatário: Rua X, 123 → Rua Y, 456</xCorrecao>
      <xCondUso>A Carta de Correção é disciplinada pelo § 1º-A do art. 7º do Convênio SINIEF 06/89</xCondUso>
    </detEvento>
  </infEvento>
</evento>
```

---

## 🔍 Lógica de Detecção no Engine

```python
class NFEComplementarRule(BaseRule):
    code = "NFE_COMPLEMENTAR"
    relevance_tags = {"complementar", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.tpEmis == "4"
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        
        # 1. refNFe obrigatório
        if not context.refNFe:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "NF-e complementar sem refNFe (chave original)"}
            ))
        
        # 2. NF-e original existe e autorizada
        nfe_original = self.get_nfe_by_chave(context.refNFe)
        if not nfe_original:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": "NF-e original não encontrada", "refNFe": context.refNFe}
            ))
        elif nfe_original.status != "AUTORIZADA":
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": f"NF-e original status: {nfe_original.status}", "refNFe": context.refNFe}
            ))
        
        # 3. Valor complementar não negativo
        if context.vProd < 0 or context.vFrete < 0 or context.vICMS < 0:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={"erro": "Valor complementar não pode ser negativo"}
            ))
        
        # 4. CFOP compatível com complementar
        if context.cfop not in ["5352", "5353", "5354", "6352", "6353", "6354"]:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={"erro": f"CFOP {context.cfop} incomum para complementar"}
            ))
        
        return discrepancies


class NFECartaCorrecaoRule(BaseRule):
    code = "NFE_CARTA_CORRECAO"
    relevance_tags = {"carta_correcao", "nfe"}
    
    def is_relevant(self, context: NFERuleContext) -> bool:
        return context.tem_carta_correcao
    
    def evaluate(self, context: NFERuleContext) -> List[Discrepancy]:
        discrepancies = []
        cce = context.carta_correcao
        
        # 1. Máximo 20 CC-e por NF-e
        if cce.sequencia > 20:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="HIGH",
                details={"erro": f"Sequência CC-e {cce.sequencia} > 20 (máximo)"}
            ))
        
        # 2. Não altera valores
        campos_proibidos = ["vNF", "vProd", "vFrete", "vSeg", "vOutro", "vDesc",
                           "vICMS", "vBC", "vIPI", "vII", "vPIS", "vCOFINS",
                           "vFCP", "vFCPST", "vFCPSTRet", "CST", "CSOSN",
                           "qCom", "vUnCom", "vProd_item"]
        
        for campo in campos_proibidos:
            if campo in cce.campos_alterados:
                discrepancies.append(Discrepancy(
                    rule_code=self.code,
                    severity="HIGH",
                    details={
                        "erro": f"Carta Correção não pode alterar: {campo}",
                        "campo": campo
                    }
                ))
        
        # 3. Texto correção obrigatório
        if not cce.xCorrecao or len(cce.xCorrecao) < 15:
            discrepancies.append(Discrepancy(
                rule_code=self.code,
                severity="MEDIUM",
                details={"erro": "Texto correção (xCorrecao) obrigatório e mínimo 15 caracteres"}
            ))
        
        return discrepancies
```

---

## 🧪 Casos de Teste

```python
# test_nfe_complementar_sem_refnfe
# tpEmis=4, sem refNFe → HIGH

# test_nfe_complementar_original_nao_existe
# refNFe inexistente → HIGH

# test_nfe_complementar_original_cancelada
# Original CANCELADA → HIGH

# test_nfe_complementar_valor_negativo
# vFrete=-100 → MEDIUM

# test_nfe_carta_correcao_sequencia_21
# 21ª CC-e → HIGH

# test_nfe_carta_correcao_altera_valor
# CC-e altera vNF → HIGH

# test_nfe_carta_correcao_altera_cst
# CC-e altera CST → HIGH

# test_nfe_carta_correcao_sem_texto
# xCorrecao vazio → MEDIUM
```

---

## ⚠️ Pontos de Atenção

### Complementar (tpEmis=4)
1. **SÓ SOMA** - Não substitui, não anula
2. **refNFe OBRIGATÓRIO** - Vincula à original
3. **Valor ≥ 0** - Nunca negativo
4. **ICMS próprio** - Calculado sobre valor complementar
5. **Cross CT-e**: Se complementa frete, CT-e pode precisar complementar (tpEmis=4)

### Carta Correção
1. **MÁXIMO 20** por NF-e
2. **NÃO ALTERA VALORES** - nem quantidades
3. **Texto obrigatório** - descrever o que corrigiu
4. **Evento 110110** - registrado na SEFAZ
5. **Não gera nova NF-e** - apenas corrige metadados

---

## 📦 JSON para backend/app/data/nfe/nfe_complementar_regras.json

```json
{
  "version": "2025.1",
  "updated": "2025-01-15",
  "tpEmis_complementar": "4",
  "complementar": {
    "refNFe_obrigatorio": true,
    "original_deve_existir": true,
    "original_deve_estar_autorizada": true,
    "valor_nao_negativo": true,
    "cfops_permitidos": ["5352", "5353", "5354", "6352", "6353", "6354"],
    "apenas_soma": true,
    "nao_substitui": true,
    "nao_anula": true
  },
  "carta_correcao": {
    "tpEvento": "110110",
    "max_por_nfe": 20,
    "campos_proibidos": [
      "vNF", "vProd", "vFrete", "vSeg", "vOutro", "vDesc",
      "vICMS", "vBC", "vIPI", "vII", "vPIS", "vCOFINS",
      "vFCP", "vFCPST", "vFCPSTRet", "CST", "CSOSN",
      "qCom", "vUnCom", "vProd_item"
    ],
    "campos_permitidos_exemplos": [
      "enderEmit", "enderDest", "IE_emit", "IE_dest",
      "CFOP", "NCM", "peso", "vol", "transp", "natOp", "infCpl"
    ],
    "xCorrecao_obrigatorio": true,
    "xCorrecao_min_chars": 15
  }
}
```

---

## 🔗 Referências

- [Manual NF-e 4.00 - Complementar](https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=Y6Lj7G0uWI8=)
- [Convênio ICMS 188/2017](https://www.confaz.fazenda.gov.br/legislacao/convenios/2017/convenio-icms-188-2017)
- [Carta Correção - § 1º-A art. 7º Convênio SINIEF 06/89](https://www.confaz.fazenda.gov.br/legislacao/convenios/1989/convenio-icms-06-1989)

---

**Última Atualização:** 2026-11-03 | **Responsável:** PO Agent