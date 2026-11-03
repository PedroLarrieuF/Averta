import { useMemo } from 'react'
import { FileText, ArrowRight } from 'lucide-react'
import { Table, Column, Badge } from '@/components'
import { Discrepancy } from '@/types'
import { formatCurrency, getSeverityBadge, getStatusBadge, cn } from '@/utils/helpers'

interface ContestItemTableProps {
  discrepancies: Discrepancy[]
  isLoading?: boolean
  onSelect?: (discrepancy: Discrepancy) => void
  showActions?: boolean
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

export function ContestItemTable({ discrepancies, isLoading = false, onSelect, showActions = false }: ContestItemTableProps) {
  const columns = useMemo<Column<Discrepancy>[]>(
    () => [
      {
        key: 'type',
        header: 'Regra',
        render: (discrepancy: Discrepancy) => (
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs capitalize">
              {typeLabels[discrepancy.type] || discrepancy.type}
            </Badge>
            <span className="text-secondary-700 max-w-xs truncate block">{discrepancy.description}</span>
          </div>
        ),
      },
      {
        key: 'severity',
        header: 'Severidade',
        className: 'hidden sm:table-cell',
        render: (discrepancy: Discrepancy) => {
          const { variant, label } = getSeverityBadge(discrepancy.severity)
          return <Badge variant={getBadgeVariant(variant)}>{label}</Badge>
        },
      },
      {
        key: 'status',
        header: 'Status',
        render: (discrepancy: Discrepancy) => {
          const { variant, label } = getStatusBadge(discrepancy.status)
          return <Badge variant={getBadgeVariant(variant)}>{label}</Badge>
        },
      },
      {
        key: 'values',
        header: 'Valores',
        className: 'hidden md:table-cell font-mono',
        render: (discrepancy: Discrepancy) => (
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
        render: (discrepancy: Discrepancy) => (
          <div className="space-y-1 text-right">
            <div className={cn('font-medium', discrepancy.difference > 0 ? 'text-danger-600' : 'text-success-600')}>
              {discrepancy.difference > 0 ? '+' : ''}{formatCurrency(discrepancy.difference)}
            </div>
            <div className="text-secondary-500 text-xs">
              {discrepancy.differencePercent.toFixed(1)}%
            </div>
          </div>
        ),
      },
      {
        key: 'contract',
        header: 'Contrato',
        className: 'hidden xl:table-cell',
        render: (discrepancy: Discrepancy) => (
          <span className="text-secondary-700 truncate max-w-[120px] block">
            {discrepancy.contractId ? `Contrato ${discrepancy.contractId.slice(0, 8)}...` : '—'}
          </span>
        ),
      },
      {
        key: 'document',
        header: 'Documento',
        className: 'hidden sm:table-cell',
        render: (discrepancy: Discrepancy) => (
          <span className="text-secondary-700 truncate max-w-[120px] block">
            {discrepancy.documentId ? `Doc ${discrepancy.documentId.slice(0, 8)}...` : '—'}
          </span>
        ),
      },
      ...(showActions
        ? [
            {
              key: 'actions',
              header: '',
              className: 'w-24 text-right',
              render: (discrepancy: Discrepancy) => (
                <button
                  onClick={() => onSelect?.(discrepancy)}
                  className="p-2 rounded-lg text-secondary-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                  aria-label="Ver detalhes da discrepância"
                >
                  <ArrowRight className="h-4 w-4" />
                </button>
              ),
            },
          ]
        : []),
    ],
    [onSelect, showActions]
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
      <div className="p-8 text-center">
        <FileText className="mx-auto h-12 w-12 text-secondary-300 mb-3" />
        <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum item na contestação</h3>
        <p className="text-secondary-500">As discrepâncias selecionadas aparecerão aqui</p>
      </div>
    )
  }

  // Calculate totals
  const totalExpected = discrepancies.reduce((sum, d) => sum + d.expectedValue, 0)
  const totalActual = discrepancies.reduce((sum, d) => sum + d.actualValue, 0)
  const totalDifference = discrepancies.reduce((sum, d) => sum + d.difference, 0)

  return (
    <div className="space-y-4">
      <Table
        columns={columns}
        data={discrepancies}
        keyField="id"
        rowClassName={() => onSelect ? "cursor-pointer hover:bg-secondary-50 transition-colors" : ""}
        onRowClick={onSelect}
      />

      {/* Totals Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 p-4 bg-secondary-50 rounded-lg border border-secondary-200">
        <div className="text-center">
          <p className="text-xs text-secondary-500 uppercase tracking-wide">Total Esperado</p>
          <p className="font-mono font-bold text-lg text-secondary-900">{formatCurrency(totalExpected)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-secondary-500 uppercase tracking-wide">Total Atual</p>
          <p className="font-mono font-bold text-lg text-secondary-900">{formatCurrency(totalActual)}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-secondary-500 uppercase tracking-wide">Total Diferença</p>
          <p className={cn('font-mono font-bold text-lg', totalDifference > 0 ? 'text-danger-600' : 'text-success-600')}>
            {totalDifference > 0 ? '+' : ''}{formatCurrency(totalDifference)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-secondary-500 uppercase tracking-wide">Itens</p>
          <p className="font-bold text-lg text-secondary-900">{discrepancies.length}</p>
        </div>
      </div>
    </div>
  )
}