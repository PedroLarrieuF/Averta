import { useState } from 'react'
import { useDocuments, useUploadDocument, useReprocessDocument } from '@/hooks/useApi'
import { DocumentsTable } from '@/components/documents/DocumentsTable'
import { UploadZone } from '@/components/documents/UploadZone'
import { DocumentDetailModal } from '@/components/documents/DocumentDetailModal'
import { PageHeader, PageTitle, PageSubtitle } from '@/components'
import { Button } from '@/components'
import { Document } from '@/types'

export function Documents() {
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [filters, setFilters] = useState<Record<string, unknown>>({
    page: 1,
    size: 20,
  })

  const { data, isLoading } = useDocuments(filters as Record<string, unknown>)
  const uploadMutation = useUploadDocument()
  const reprocessMutation = useReprocessDocument()

  const handleUpload = (files: File[]) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    uploadMutation.mutate(formData)
  }

  const handleReprocess = (docId: string) => {
    reprocessMutation.mutate(docId)
  }

  const handleViewDetail = (doc: Document) => {
    setSelectedDoc(doc)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div>
          <PageTitle>Documentos</PageTitle>
          <PageSubtitle>Gerencie seus CT-e e NF-e</PageSubtitle>
        </div>
        <UploadZone
          onUpload={handleUpload}
          isLoading={uploadMutation.isPending}
          acceptedFiles={['.xml', '.XML']}
        />
      </PageHeader>

      {/* Filters Bar */}
      <div className="card">
        <div className="card-body p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex gap-4 flex-wrap">
              <select
                className="input w-auto"
                value={filters.status as string || ''}
                onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined, page: 1 })}
              >
                <option value="">Todos os status</option>
                <option value="PENDING">Pendente</option>
                <option value="PROCESSING">Processando</option>
                <option value="COMPLETED">Concluído</option>
                <option value="FAILED">Falhou</option>
                <option value="ARCHIVED">Arquivado</option>
              </select>
              <select
                className="input w-auto"
                value={filters.type as string || ''}
                onChange={(e) => setFilters({ ...filters, type: e.target.value || undefined, page: 1 })}
              >
                <option value="">Todos os tipos</option>
                <option value="CTE">CT-e</option>
                <option value="NFE">NF-e</option>
                <option value="CTE_COMPLEMENTAR">CT-e Complementar</option>
                <option value="NFE_COMPLEMENTAR">NF-e Complementar</option>
                <option value="OTHER">Outros</option>
              </select>
              <input
                type="date"
                className="input w-auto"
                value={(filters.dateFrom as string) || ''}
                onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value || undefined, page: 1 })}
              />
              <span className="text-secondary-400 self-center">até</span>
              <input
                type="date"
                className="input w-auto"
                value={(filters.dateTo as string) || ''}
                onChange={(e) => setFilters({ ...filters, dateTo: e.target.value || undefined, page: 1 })}
              />
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => setFilters({ page: 1, size: 20 })}>
                Limpar filtros
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Documents Table */}
      <div className="card">
        <div className="card-body p-0">
          <DocumentsTable
            documents={data?.data ?? []}
            isLoading={isLoading}
            pagination={data?.meta}
            onPageChange={(page) => setFilters({ ...filters, page })}
            onSizeChange={(size) => setFilters({ ...filters, size, page: 1 })}
            onSelect={handleViewDetail}
            onReprocess={handleReprocess}
          />
        </div>
      </div>

      {/* Document Detail Modal */}
      {selectedDoc && (
        <DocumentDetailModal
          document={selectedDoc}
          onClose={() => setSelectedDoc(null)}
          onReprocess={handleReprocess}
        />
      )}
    </div>
  )
}