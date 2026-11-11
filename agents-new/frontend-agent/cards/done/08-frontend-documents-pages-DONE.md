---
id: 08
title: "Build Document Upload & List Pages"
priority: critical
type: feature
agent: frontend
sprint: 2
estimate: L
status: done
created: 2026-11-01
reviewed_by: techlead
---

# Card 08: Build Document Upload & List Pages

## Contexto
Core feature: upload CT-e/NF-e XML → processamento assíncrono → listagem com status.

## Definition of Ready
- [x] API endpoints: POST /documents/upload, GET /documents, GET /documents/{id}
- [x] react-dropzone instalado
- [x] Design system components (Card 07) - dependency

## Tasks
- [ ] `src/pages/DocumentsPage.tsx` - lista com filtros, paginação, status
- [ ] `src/pages/DocumentUploadPage.tsx` - drag & drop + progress
- [ ] `src/pages/DocumentDetailPage.tsx` - parsed data, discrepancies link
- [ ] Hooks:
  - `src/hooks/useDocuments.ts` - list, upload, detail, reprocess
  - `src/hooks/useDocumentUpload.ts` - upload com progress
- [ ] Componentes:
  - `src/components/documents/DocumentTable.tsx` - usa Table component
  - `src/components/documents/DocumentUploadDropzone.tsx` - react-dropzone
  - `src/components/documents/DocumentStatusBadge.tsx` - usa getStatusBadge
  - `src/components/documents/DocumentFilters.tsx` - tipo, status, data, carrier
- [ ] Upload flow:
  - Validação client-side (XML, tamanho 50MB)
  - Upload multipart → retorna document_id
  - Polling status (PROCESSING → COMPLETED/FAILED)
  - Toast notifications
- [ ] Testes: upload, list, filters, status polling

## API Contract
```typescript
// POST /documents/upload (multipart/form-data)
interface UploadResponse {
  id: string
  status: 'UPLOADED' | 'PENDING'
  message: string
}

// GET /documents?page=1&page_size=20&status=COMPLETED&type=CTE
interface DocumentListResponse {
  data: Document[]
  meta: { total: number; page: number; page_size: number }
}

interface Document {
  id: string
  type: 'CTE' | 'NFE' | ...
  status: 'UPLOADED' | 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'ARCHIVED'
  original_name: string
  issue_date: string
  total_value: number
  freight_value: number
  carrier_name: string
  discrepancy_count: number
  created_at: string
}
```

## Acceptance Criteria
- [ ] Drag & drop múltiplos arquivos
- [ ] Progress bar durante upload
- [ ] Polling automático até COMPLETED/FAILED
- [ ] Filtros funcionais (tipo, status, data, carrier)
- [ ] Paginação server-side
- [ ] Link para detalhes → discrepancies
- [ ] Testes integração com MSW

## Referências
- `backend/README.md` - seção "Processamento de Documentos"
- `frontend-agent.md` - API contract