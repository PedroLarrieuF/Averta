import { useMemo } from 'react'
import { FileText, RotateCw, Eye, Download, MoreHorizontal } from 'lucide-react'
import { Table, Column, Pagination, Badge, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components'
import { Document, DocumentStatus, DocumentType } from '@/types'
import { formatCurrency, formatNumber, formatDateTime } from '@/utils/helpers'

interface DocumentsTableProps {
  documents: Document[]
  isLoading: boolean
  pagination?: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
  onPageChange: (page: number) => void
  onSizeChange: (size: number) => void
  onSelect: (doc: Document) => void
  onReprocess: (docId: string) => void
}

const typeLabels: Record<DocumentType, string> = {
  CTE: 'CT-e',
  NFE: 'NF-e',
  CTE_COMPLEMENTAR: 'CT-e Comp.',
  NFE_COMPLEMENTAR: 'NF-e Comp.',
  OTHER: 'Outro',
}

const statusLabels: Record<DocumentStatus, string> = {
  PENDING: 'Pendente',
  PROCESSING: 'Processando',
  COMPLETED: 'Concluído',
  FAILED: 'Falhou',
  ARCHIVED: 'Arquivado',
}

const statusVariants: Record<DocumentStatus, 'success' | 'warning' | 'danger' | 'primary' | 'secondary'> = {
  PENDING: 'warning',
  PROCESSING: 'primary',
  COMPLETED: 'success',
  FAILED: 'danger',
  ARCHIVED: 'secondary',
}

export function DocumentsTable({
  documents,
  isLoading,
  pagination,
  onPageChange,
  onSizeChange,
  onSelect,
  onReprocess,
}: DocumentsTableProps) {
  const columns = useMemo<Column<Document>[]>(
    () => [
      {
        key: 'fileName',
        header: 'Arquivo',
        render: (doc: Document) => (
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-secondary-100 flex items-center justify-center flex-shrink-0">
              <FileText className="h-5 w-5 text-secondary-600" />
            </div>
            <div className="min-w-0">
              <p className="font-medium text-secondary-900 truncate">{doc.fileName}</p>
              <p className="text-xs text-secondary-500">{formatNumber(doc.fileSize)} bytes</p>
            </div>
          </div>
        ),
      },
      {
        key: 'type',
        header: 'Tipo',
        className: 'hidden md:table-cell',
        render: (doc: Document) => (
          <Badge variant="secondary" className="capitalize">
            {typeLabels[doc.type] || doc.type}
          </Badge>
        ),
      },
      {
        key: 'status',
        header: 'Status',
        render: (doc: Document) => (
          <Badge variant={statusVariants[doc.status]}>
            {statusLabels[doc.status]}
          </Badge>
        ),
      },
      {
        key: 'carrier',
        header: 'Transportadora',
        className: 'hidden lg:table-cell',
        render: (doc: Document) => (
          <span className="text-secondary-700">{doc.carrierId ? `Transportadora ${doc.carrierId.slice(0, 8)}...` : '—'}</span>
        ),
      },
      {
        key: 'value',
        header: 'Valor',
        className: 'hidden lg:table-cell',
        render: (doc: Document) => (
          <span className="font-mono text-secondary-900">
            {doc.parsedData?.totalValue ? formatCurrency(Number(doc.parsedData.totalValue)) : '—'}
          </span>
        ),
      },
      {
        key: 'date',
        header: 'Data',
        className: 'hidden sm:table-cell',
        render: (doc: Document) => (
          <span className="text-secondary-700 whitespace-nowrap">{formatDateTime(doc.createdAt)}</span>
        ),
      },
      {
        key: 'actions',
        header: 'Ações',
        className: 'w-48 text-right',
        render: (doc: Document) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="p-2 rounded-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors"
                aria-label="Mais ações"
              >
                <MoreHorizontal className="h-5 w-5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => onSelect(doc)}
                className="flex items-center gap-2"
              >
                <Eye className="h-4 w-4" />
                Ver detalhes
              </DropdownMenuItem>
              {doc.fileUrl && (
                <DropdownMenuItem asChild>
                  <a href={doc.fileUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 w-full">
                    <Download className="h-4 w-4" />
                    Baixar XML
                  </a>
                </DropdownMenuItem>
              )}
              {doc.status === 'FAILED' && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => onReprocess(doc.id)}
                    className="flex items-center gap-2 text-primary-600"
                  >
                    <RotateCw className="h-4 w-4" />
                    Reprocessar
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [onSelect, onReprocess]
  )

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <Table columns={columns} data={[]} keyField="id" isLoading />
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="p-12 text-center">
        <FileText className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Nenhum documento encontrado</h3>
        <p className="text-secondary-500">Faça upload do seu primeiro CT-e ou NF-e para começar</p>
      </div>
    )
  }

  return (
    <>
      <Table
        columns={columns}
        data={documents}
        keyField="id"
        rowClassName={() => "cursor-pointer hover:bg-secondary-50 transition-colors"}
        onRowClick={(doc: Document) => onSelect(doc)}
      />
      {pagination && (
        <Pagination
          currentPage={pagination.page}
          totalPages={pagination.totalPages}
          totalItems={pagination.total}
          pageSize={pagination.limit}
          onPageChange={onPageChange}
          onPageSizeChange={onSizeChange}
          pageSizeOptions={[10, 20, 50, 100]}
        />
      )}
    </>
  )
}