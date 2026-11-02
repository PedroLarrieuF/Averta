---
id: 12
title: "Fix XML Parser Namespace Handling for NF-e 4.00"
priority: high
type: tech-debt
agent: backend
sprint: 1
estimate: M
status: ready
created: 2026-11-01
reviewed_by: techlead
---

# Card 12: Fix XML Parser Namespace Handling

## Contexto
`app/services/xml_parser.py` usa `xmltodict` que tem handling frágil de namespaces para NF-e 4.00. TD-001.

## Definition of Ready
- [x] Problema identificado no techlead review
- [x] Código atual em `xml_parser.py` usando xmltodict
- [x] Solução: migrar para `lxml.etree` com `register_namespace`

## Tasks
- [ ] Refatorar `parse_nfe_xml` para usar `lxml.etree`
- [ ] Registrar namespaces NF-e 4.00: `http://www.portalfiscal.inf.br/nfe`
- [ ] Usar XPath com namespaces para extração robusta
- [ ] Manter mesma interface de retorno (dict estruturado)
- [ ] Adicionar testes com NF-e 4.00 samples reais
- [ ] Verificar CT-e ainda funciona (mesmo namespace ou diferente)
- [ ] Benchmark performance vs xmltodict

## Implementation Sketch
```python
from lxml import etree

NS_NFE = "http://www.portalfiscal.inf.br/nfe"
NS_MAP = {"nfe": NS_NFE}

def parse_nfe_xml(xml_content: str | bytes) -> dict:
    if isinstance(xml_content, bytes):
        xml_content = xml_content.decode("utf-8")
    
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_content.encode(), parser)
    
    # Register namespace for output
    etree.register_namespace("nfe", NS_NFE)
    
    # XPath with namespace
    inf_nfe = root.find(".//nfe:infNFe", namespaces=NS_MAP)
    # ... extração robusta
```

## Acceptance Criteria
- [ ] Parse NF-e 4.00 sem erros de namespace
- [ ] CT-e continua funcionando
- [ ] Performance igual ou melhor
- [ ] Testes com XMLs reais passam
- [ ] Mesma estrutura de retorno (compatibilidade)

## Referências
- `backend/app/services/xml_parser.py` - código atual
- `TECHLEAD_REVIEW.md` - TD-001
- lxml docs: https://lxml.de/xpathxslt.html