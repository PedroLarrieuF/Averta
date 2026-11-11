---
id: 14
title: "Fix PDF Generator - Use run_in_threadpool for Large PDFs"
priority: medium
type: tech-debt
agent: backend
sprint: 2
estimate: S
status: done
created: 2026-11-01
reviewed_by: techlead
---

# Card 14: Fix PDF Generator - run_in_threadpool

## Contexto
`app/services/pdf_generator.py` usa ReportLab síncrono. PDFs grandes (>10 páginas) bloqueiam event loop FastAPI. TD-003.

## Definition of Ready
- [x] Problema identificado
- [x] Solução: `anyio.to_thread.run_sync` ou `run_in_threadpool`

## Tasks
- [ ] Identificar funções bloqueantes no `pdf_generator.py`
- [ ] Wrapper com `run_in_threadpool` para `generate_contest_pdf()`
- [ ] Adicionar timeout configurável
- [ ] Testes: PDF pequeno (sync), PDF grande (threadpool)
- [ ] Monitorar memory usage em threadpool

## Implementation
```python
# app/services/pdf_generator.py
from starlette.concurrency import run_in_threadpool

async def generate_contest_pdf_async(contest_id: str) -> bytes:
    """Generate PDF in threadpool to avoid blocking event loop"""
    return await run_in_threadpool(generate_contest_pdf_sync, contest_id)

def generate_contest_pdf_sync(contest_id: str) -> bytes:
    # ... código ReportLab existente (síncrono)
    pass
```

## Acceptance Criteria
- [ ] PDFs grandes não bloqueiam outros requests
- [ ] Latência similar para PDFs pequenos
- [ ] Timeout configurado e respeitado
- [ ] Testes passam

## Referências
- `TECHLEAD_REVIEW.md` - TD-003
- `backend/app/services/pdf_generator.py` - código atual
- Starlette concurrency: https://www.starlette.io/concurrency/