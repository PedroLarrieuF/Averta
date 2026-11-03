import { useMemo } from 'react'
import { Eye, FileText, ArrowRight, Clock, AlertTriangle, Gavel, Download } from 'lucide-react'
import { Table, Column, Pagination, Badge, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components'
import { Contest, ContestStatus } from '@/types'
import { formatCurrency, formatDateTime, getStatusBadge, cn } from '@/utils/helpers'

interface ContestTableProps {
  contests: Contest[]
  isLoading: boolean
  pagination?: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
  onPageChange: (page: number) => void
  onSizeChange: (size: number) => void
  onSelect: (contest: Contest) => void
  onSend: (id: string) => void
  onNegotiate: (id: string) => void
  onViewPDF: (id: string) => void
  onDownloadPDF: (id: string) => void
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
}

const getProgressSteps = (status: ContestStatus): { label: string; completed: boolean; current: boolean }[] => {
  const steps = [
    { label: 'Rascunho', status: 'DRAFT' as ContestStatus },
    { label: 'Enviada', status: 'SENT' as ContestStatus },
    { label: 'Recebida', status: 'ACKNOWLEDGED' as ContestStatus },
    { label: 'Negociando', status: 'NEGOTIATING' as ContestStatus },
    { label: 'Finalizada', status: 'ACCEPTED' as ContestStatus },
  ]

  const currentIndex = steps.findIndex(s => s.status === status)

  return steps.map((step, index) => ({
    label: step.label,
    completed: index < currentIndex,
    current: index === currentIndex && !['ACCEPTED', 'PARTIAL', 'REJECTED', 'EXPIRED'].includes(status),
  }))
}

const ProgressIndicator = ({ status }: { status: ContestStatus }) => {
  const steps = getProgressSteps(status)

  return (
    <div className="flex items-center gap-1">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center">
          <div
            className={cn(
              'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-all',
              step.completed
                ? 'bg-success-500 text-white'
                : step.current
                ? 'bg-primary-500 text-white'
                : 'bg-secondary-200 text-secondary-500'
            )}
          >
            {step.completed ? (
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              index + 1
            )}
          </div>
          {index < steps.length - 1 && (
            <div
              className={cn(
                'w-12 h-0.5 mx-1',
                index < steps.findIndex(s => s.current) ? 'bg-success-500' : 'bg-secondary-200'
              )}
            />
          )}
        </div>
      ))}
    </div>
  )
}

export function ContestTable({
  contests,
  isLoading,
  pagination,
  onPageChange,
  onSizeChange,
  onSelect,
  onSend,
  onNegotiate,
  onViewPDF,
  onDownloadPDF,
  selectedIds,
  onSelectionChange,
}: ContestTableProps) {
  const columns = useMemo<Column<Contest>[]>(
    () => [
      {
        key: 'select',
        header: (
          <input
            type="checkbox"
            className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            checked={contests.length > 0 && selectedIds.length === contests.length}
            onChange={(e) => {
              if (e.target.checked) {
                onSelectionChange(contests.map((c) => c.id))
              } else {
                onSelectionChange([])
              }
            }}
            aria-label="Selecionar todos"
          />
        ),
        className: 'w-12 text-center',
        render: (contest) => (
          <input
            type="checkbox"
            className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500"
            checked={selectedIds.includes(contest.id)}
            onChange={(e) => {
              const newIds = e.target.checked
                ? [...selectedIds, contest.id]
                : selectedIds.filter((id) => id !== contest.id)
              onSelectionChange(newIds)
            }}
            onClick={(e) => e.stopPropagation()}
            aria-label={`Selecionar contestação ${contest.id.slice(0, 8)}`}
          />
        ),
      },
      {
        key: 'title',
        header: 'Título',
        className: 'min-w-[200px]',
        render: (contest) => (
          <div className="space-y-1">
            <span className="font-medium text-secondary-900 truncate block max-w-[250px]">{contest.title}</span>
            <span className="text-secondary-500 text-sm truncate block max-w-[250px]">{contest.description || 'Sem descrição'}</span>
          </div>
        ),
      },
      {
        key: 'status',
        header: 'Status',
        className: 'w-48',
        render: (contest) => {
          const { variant, label } = getStatusBadge(contest.status)
          return (
            <div className="space-y-1">
              <Badge variant={variant as 'primary' | 'secondary' | 'danger' | 'success' | 'warning'}>{label}</Badge>
              <ProgressIndicator status={contest.status} />
            </div>
          )
        },
      },
      {
        key: 'amounts',
        header: 'Valores',
        className: 'hidden md:table-cell font-mono',
        render: (contest) => (
          <div className="space-y-1">
            <div className="text-secondary-900">
              Solicitado: <span className="font-medium">{formatCurrency(contest.requestedAmount)}</span>
            </div>
            {contest.offeredAmount !== undefined && (
              <div className="text-secondary-500 text-sm">
                Oferecido: <span className="font-medium">{formatCurrency(contest.offeredAmount)}</span>
              </div>
            )}
            {contest.agreedAmount !== undefined && (
              <div className="text-success-600 text-sm">
                Acordado: <span className="font-medium">{formatCurrency(contest.agreedAmount)}</span>
              </div>
            )}
          </div>
        ),
      },
      {
        key: 'carrier',
        header: 'Transportadora',
        className: 'hidden lg:table-cell',
        render: (contest) => (
          <span className="text-secondary-700 truncate max-w-[150px] block">
            {contest.carrierId ? `Transportadora ${contest.carrierId.slice(0, 8)}...` : '—'}
          </span>
        ),
      },
      {
        key: 'dates',
        header: 'Datas',
        className: 'hidden sm:table-cell',
        render: (contest) => (
          <div className="space-y-1 text-secondary-700 text-sm">
            <div>Criada: {formatDateTime(contest.createdAt)}</div>
            {contest.sentAt && <div>Enviada: {formatDateTime(contest.sentAt)}</div>}
            {contest.resolvedAt && <div>Resolvida: {formatDateTime(contest.resolvedAt)}</div>}
          </div>
        ),
      },
      {
        key: 'actions',
        header: 'Ações',
        className: 'w-56 text-right',
        render: (contest) => (
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
              <DropdownMenuItem onClick={() => onSelect(contest)} className="flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Ver detalhes
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {contest.status === 'DRAFT' && (
                <>
                  <DropdownMenuItem onClick={() => onViewPDF(contest.id)} className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Visualizar PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onSend(contest.id)} className="flex items-center gap-2">
                    <ArrowRight className="h-4 w-4" />
                    Enviar para transportadora
                  </DropdownMenuItem>
                </>
              )}
              {['SENT', 'ACKNOWLEDGED', 'NEGOTIATING'].includes(contest.status) && (
                <>
                  <DropdownMenuItem onClick={() => onViewPDF(contest.id)} className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Visualizar PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onDownloadPDF(contest.id)} className="flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Download PDF
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => onNegotiate(contest.id)} className="flex items-center gap-2">
                    <Gavel className="h-4 w-4" />
                    Negociar
                  </DropdownMenuItem>
                </>
              )}
              {['ACCEPTED', 'PARTIAL'].includes(contest.status) && (
                <>
                  <DropdownMenuItem onClick={() => onViewPDF(contest.id)} className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Visualizar PDF
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onDownloadPDF(contest.id)} className="flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Download PDF
                  </DropdownMenuItem>
                </>
              )}
              {contest.status === 'REJECTED' && (
                <DropdownMenuItem className="flex items-center gap-2 text-secondary-500" disabled>
                  <AlertTriangle className="h-4 w-4" />
                  Contestação rejeitada
                </DropdownMenuItem>
              )}
              {contest.status === 'EXPIRED' && (
                <DropdownMenuItem className="flex items-center gap-2 text-secondary-500" disabled>
                  <Clock className="h-4 w-4" />
                  Contestação expirada
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [onSelect, onSend, onNegotiate, onViewPDF, onDownloadPDF, onSelectionChange, selectedIds, contests]
  )

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <Table columns={columns} data={[]} keyField="id" isLoading />
      </div>
    )
  }

  if (contests.length === 0) {
    return (
      <div className="p-12 text-center">
        <FileText className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Nenhuma contestação encontrada</h3>
        <p className="text-secondary-500">Comece criando uma nova contestação a partir das discrepâncias</p>
      </div>
    )
  }

  return (
    <>
      <Table
        columns={columns}
        data={contests}
        keyField="id"
        rowClassName={() => "cursor-pointer hover:bg-secondary-50 transition-colors"}
        onRowClick={(contest: Contest) => onSelect(contest)}
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