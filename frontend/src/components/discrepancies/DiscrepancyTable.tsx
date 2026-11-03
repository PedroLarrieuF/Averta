import { useMemo } from 'react'
import { Eye, AlertTriangle, Gavel } from 'lucide-react'
import { Table, Column, Pagination, Badge, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components'
import { Discrepancy } from '@/types'
import { formatCurrency, formatDateTime, getStatusBadge, getSeverityBadge } from '@/utils/helpers'

interface DiscrepancyTableProps {
  discrepancies: Discrepancy[]
  isLoading: boolean
  pagination?: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
  onPageChange: (page: number) => void
  onSizeChange: (size: number) => void
  onSelect: (discrepancy: Discrepancy) => void
  onBulkReview: (ids: string[]) => void
  onBulkContest: (ids: string[]) => void
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
}

const typeLabels: Record<string, string> = {
  FREIGHT_VALUE: 'Valor Frete',
  ICMS: 'ICMS',
  TOLLS: 'Pedágios',
  WEIGHT: 'Peso',
  VOLUME: 'Volume',
  DIMENSIONS: 'Dimensões',
  DUPLICATE: 'Duplicado',
  MISSING_DOCUMENT: 'Doc. Ausente',
  INVALID_CNPJ: 'CNPJ Inválido',
  ROUTE_MISMATCH: 'Rota Divergente',
  OTHER: 'Outro',
}

const getBadgeVariant = (variant: string): 'primary' | 'secondary' | 'danger' | 'success' | 'warning' => {
  switch (variant) {
    case 'badge-primary': return 'primary'
    case 'badge-warning': return 'warning'
    case 'badge-danger': return 'danger'
    case 'badge-success': return 'success'
    default: return 'secondary'
  }
}

export function DiscrepancyTable({
  discrepancies,
  isLoading,
  pagination,
  onPageChange,
  onSizeChange,
  onSelect,
  onBulkReview,
  onBulkContest,
  selectedIds,
  onSelectionChange,
}: DiscrepancyTableProps) {
  const columns = useMemo<Column<Discrepancy>[]>(
    () => [
      {
        key: 'select',
        header: (
          <input
            type="checkbox"
            className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            checked={discrepancies.length > 0 && selectedIds.length === discrepancies.length}
            onChange={(e) => {
              if (e.target.checked) {
                onSelectionChange(discrepancies.map((d) => d.id))
              } else {
                onSelectionChange([])
              }
            }}
            aria-label="Selecionar todos"
          />
        ),
        className: 'w-12 text-center',
        render: (discrepancy) => (
          <input
            type="checkbox"
            className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            checked={selectedIds.includes(discrepancy.id)}
            onChange={(e) => {
              const newIds = e.target.checked
                ? [...selectedIds, discrepancy.id]
                : selectedIds.filter((id) => id !== discrepancy.id)
              onSelectionChange(newIds)
            }}
            onClick={(e) => e.stopPropagation()}
            aria-label={`Selecionar discrepância ${discrepancy.id.slice(0, 8)}`}
          />
        ),
      },
      {
        key: 'type',
        header: 'Regra',
        render: (discrepancy) => (
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs capitalize">
              {typeLabels[discrepancy.type] || discrepancy.type}
            </Badge>
            <span className="text-secondary-700 max-w-xs truncate">{discrepancy.description}</span>
          </div>
        ),
      },
      {
        key: 'severity',
        header: 'Severidade',
        className: 'hidden sm:table-cell',
        render: (discrepancy) => {
          const { variant, label } = getSeverityBadge(discrepancy.severity)
          return <Badge variant={getBadgeVariant(variant)}>{label}</Badge>
        },
      },
      {
        key: 'status',
        header: 'Status',
        render: (discrepancy) => {
          const { variant, label } = getStatusBadge(discrepancy.status)
          return <Badge variant={getBadgeVariant(variant)}>{label}</Badge>
        },
      },
      {
        key: 'values',
        header: 'Valores',
        className: 'hidden md:table-cell font-mono',
        render: (discrepancy) => (
          <div className="space-y-1">
            <div className="text-secondary-900">
              Esperado: <span className="font-medium">{formatCurrency(discrepancy.expectedValue)}</span>
            </div>
            <div className="text-secondary-900">
              Atual: <span className="font-medium">{formatCurrency(discrepancy.actualValue)}</span>
            </div>
          </div>
        ),
      },
      {
        key: 'difference',
        header: 'Diferença',
        className: 'hidden lg:table-cell font-mono text-right',
        render: (discrepancy) => (
          <div className="space-y-1 text-right">
            <div className={discrepancy.difference > 0 ? 'text-danger-600' : 'text-success-600'}>
              {discrepancy.difference > 0 ? '+' : ''}{formatCurrency(discrepancy.difference)}
            </div>
            <div className="text-secondary-500 text-xs">
              {discrepancy.differencePercent.toFixed(1)}%
            </div>
          </div>
        ),
      },
      {
        key: 'carrier',
        header: 'Transportadora',
        className: 'hidden xl:table-cell',
        render: (discrepancy) => (
          <span className="text-secondary-700 truncate max-w-[150px] block">
            {discrepancy.carrierId ? `Transportadora ${discrepancy.carrierId.slice(0, 8)}...` : '—'}
          </span>
        ),
      },
      {
        key: 'date',
        header: 'Data',
        className: 'hidden sm:table-cell',
        render: (discrepancy) => (
          <span className="text-secondary-700 whitespace-nowrap">{formatDateTime(discrepancy.createdAt)}</span>
        ),
      },
      {
        key: 'actions',
        header: 'Ações',
        className: 'w-48 text-right',
        render: (discrepancy) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="p-2 rounded-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors"
                aria-label="Mais ações"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => onSelect(discrepancy)}
                className="flex items-center gap-2"
              >
                <Eye className="h-4 w-4" />
                Ver detalhes
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {discrepancy.status === 'OPEN' && (
                <>
                  <DropdownMenuItem
                    onClick={() => onBulkReview([discrepancy.id])}
                    className="flex items-center gap-2"
                  >
                    <AlertTriangle className="h-4 w-4" />
                    Revisar
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onBulkContest([discrepancy.id])}
                    className="flex items-center gap-2"
                  >
                    <Gavel className="h-4 w-4" />
                    Contestar
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [onSelect, onBulkReview, onBulkContest, onSelectionChange, selectedIds, discrepancies]
  )

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <Table columns={columns} data={[]} keyField="id" isLoading />
      </div>
    )
  }

  if (discrepancies.length === 0) {
    return (
      <div className="p-12 text-center">
        <AlertTriangle className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Nenhuma discrepância encontrada</h3>
        <p className="text-secondary-500">Tente ajustar os filtros ou aguarde novos documentos serem processados</p>
      </div>
    )
  }

  return (
    <>
      <Table
        columns={columns}
        data={discrepancies}
        keyField="id"
        rowClassName={() => "cursor-pointer hover:bg-secondary-50 transition-colors"}
        onRowClick={(discrepancy: Discrepancy) => onSelect(discrepancy)}
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