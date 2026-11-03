import { useState, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Plus, Filter, Download, ChevronRight } from 'lucide-react'
import { useContests } from '@/hooks'
import { ContestTable, ContestCreateStepper, PageHeader, PageTitle, PageSubtitle, Button } from '@/components'
import { cn } from '@/utils/helpers'
import toast from 'react-hot-toast'

export function ContestsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Parse filters from URL
  const getInitialFilters = (): Record<string, unknown> => {
    const filters: Record<string, unknown> = {
      page: parseInt(searchParams.get('page') || '1', 10),
      size: parseInt(searchParams.get('size') || '20', 10),
    }
    if (searchParams.get('status')) filters.status = searchParams.get('status')
    if (searchParams.get('carrier')) filters.carrier = searchParams.get('carrier')
    if (searchParams.get('dateFrom')) filters.dateFrom = searchParams.get('dateFrom')
    if (searchParams.get('dateTo')) filters.dateTo = searchParams.get('dateTo')
    return filters
  }

  const [filters, setFilters] = useState<Record<string, unknown>>(getInitialFilters)
  const [selectedContest, setSelectedContest] = useState<{ id: string } | null>(null)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createFromDiscrepancies, setCreateFromDiscrepancies] = useState<string[]>([])

  // Sync filters with URL
  const updateFilters = useCallback((newFilters: Record<string, unknown>) => {
    setFilters(newFilters)
    const params = new URLSearchParams()
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        params.set(key, String(value))
      }
    })
    setSearchParams(params, { replace: true })
  }, [setSearchParams])

  const clearFilters = useCallback(() => {
    const newFilters = { page: 1, size: 20 }
    updateFilters(newFilters)
  }, [updateFilters])

  const hasActiveFilters = useCallback(() => {
    return !!(
      filters.status ||
      filters.carrier ||
      filters.dateFrom ||
      filters.dateTo
    )
  }, [filters])

  // Fetch data
  const { data: contestsData, isLoading: isLoadingContests } = useContests(filters)
  // useDiscrepancies is called inside ContestCreateStepper with selected IDs

  const handleSelect = (contest: { id: string }) => {
    setSelectedContest(contest)
  }

  const handleSelectionChange = (ids: string[]) => {
    setSelectedIds(ids)
  }

  const handleSend = (id: string) => {
    navigate(`/contests/${id}/send`)
  }

  const handleNegotiate = (id: string) => {
    navigate(`/contests/${id}/negotiate`)
  }

  const handleViewPDF = (id: string) => {
    navigate(`/contests/${id}`, { state: { viewPDF: true } })
  }

  const handleDownloadPDF = (_id: string) => {
    // This would trigger PDF download
    toast.success('Download iniciado')
  }

  const handleCreateComplete = (contestId: string) => {
    setShowCreateModal(false)
    setCreateFromDiscrepancies([])
    toast.success('Contestação criada com sucesso!')
    navigate(`/contests/${contestId}`)
  }

  const handleBulkCreateContest = () => {
    if (selectedIds.length === 0) return
    // Navigate to create page with selected IDs
    navigate(`/contests/create?discrepancyIds=${selectedIds.join(',')}`)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div>
          <PageTitle>Contestações</PageTitle>
          <PageSubtitle>Acompanhe o fluxo completo de contestações com transportadoras</PageSubtitle>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" className="hidden sm:flex">
            <Filter className="h-4 w-4 mr-2" />
            Filtros
          </Button>
          <Button variant="secondary" className="hidden sm:flex">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
          <Button variant="primary" onClick={() => { setCreateFromDiscrepancies([]); setShowCreateModal(true); }}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Contestação
          </Button>
        </div>
      </PageHeader>

      {/* Quick Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <QuickStat title="Total" value={contestsData?.meta.total ?? 0} icon={ChevronRight} color="primary" />
        <QuickStat
          title="Rascunho"
          value={contestsData?.data.filter(c => c.status === 'DRAFT').length ?? 0}
          icon={ChevronRight}
          color="secondary"
        />
        <QuickStat
          title="Em Negociação"
          value={contestsData?.data.filter(c => ['SENT', 'ACKNOWLEDGED', 'NEGOTIATING'].includes(c.status)).length ?? 0}
          icon={ChevronRight}
          color="warning"
        />
        <QuickStat
          title="Finalizadas"
          value={contestsData?.data.filter(c => ['ACCEPTED', 'PARTIAL', 'REJECTED'].includes(c.status)).length ?? 0}
          icon={ChevronRight}
          color="success"
        />
      </div>

      {/* Filters */}
      <ContestFilters
        filters={filters}
        onFiltersChange={updateFilters}
        onClearFilters={clearFilters}
        hasActiveFilters={hasActiveFilters()}
      />

      {/* Contests Table */}
      <div className="card">
        <div className="card-body p-0">
          <ContestTable
            contests={contestsData?.data ?? []}
            isLoading={isLoadingContests}
            pagination={contestsData?.meta}
            onPageChange={(page) => updateFilters({ ...filters, page })}
            onSizeChange={(size) => updateFilters({ ...filters, size, page: 1 })}
            onSelect={handleSelect}
            onSend={handleSend}
            onNegotiate={handleNegotiate}
            onViewPDF={handleViewPDF}
            onDownloadPDF={handleDownloadPDF}
            selectedIds={selectedIds}
            onSelectionChange={handleSelectionChange}
          />
        </div>
      </div>

      {/* Detail Modal */}
      {selectedContest && (
        <ContestDetailModal />
      )}

      {/* Bulk Action Bar */}
      {selectedIds.length > 0 && (
        <ContestBulkActionBar
          selectedCount={selectedIds.length}
          onBulkCreateContest={handleBulkCreateContest}
          onClearSelection={() => setSelectedIds([])}
        />
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <ContestCreateStepper
          initialDiscrepancyIds={createFromDiscrepancies}
          onComplete={handleCreateComplete}
          onCancel={() => { setShowCreateModal(false); setCreateFromDiscrepancies([]); }}
        />
      )}
    </div>
  )
}

// Quick Stat Card
function QuickStat({ title, value, icon: Icon, color }: { title: string; value: number; icon: React.ComponentType<{ className?: string }>; color: string }) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600 border-primary-200',
    secondary: 'bg-secondary-50 text-secondary-600 border-secondary-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    success: 'bg-success-50 text-success-600 border-success-200',
  }

  return (
    <div className={cn('p-4 rounded-xl border', colorClasses[color as keyof typeof colorClasses] || colorClasses.primary)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary-500">{title}</p>
          <p className="text-2xl font-bold text-secondary-900 mt-1">{value}</p>
        </div>
        <Icon className="h-8 w-8" />
      </div>
    </div>
  )
}

// Filters Component
function ContestFilters({
  filters,
  onFiltersChange,
  onClearFilters,
  hasActiveFilters,
}: {
  filters: Record<string, unknown>
  onFiltersChange: (filters: Record<string, unknown>) => void
  onClearFilters: () => void
  hasActiveFilters: boolean
}) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h3 className="font-medium text-secondary-900 flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filtros
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 rounded-lg text-secondary-500 hover:bg-secondary-100 transition-colors"
            aria-label={isOpen ? 'Ocultar filtros' : 'Mostrar filtros'}
          >
            {isOpen ? <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" /></svg> : <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>}
          </button>
          {hasActiveFilters && (
            <button onClick={onClearFilters} className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              Limpar
            </button>
          )}
        </div>
      </div>

      {isOpen && (
        <div className="card-body p-4 pt-0">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Status</label>
              <select
                value={(filters.status as string) || ''}
                onChange={(e) => onFiltersChange({ ...filters, status: e.target.value || undefined, page: 1 })}
                className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Todos</option>
                <option value="DRAFT">Rascunho</option>
                <option value="SENT">Enviada</option>
                <option value="ACKNOWLEDGED">Recebida</option>
                <option value="NEGOTIATING">Negociando</option>
                <option value="ACCEPTED">Aceita</option>
                <option value="PARTIAL">Parcial</option>
                <option value="REJECTED">Rejeitada</option>
                <option value="EXPIRED">Expirada</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Transportadora</label>
              <input
                type="text"
                value={(filters.carrier as string) || ''}
                onChange={(e) => onFiltersChange({ ...filters, carrier: e.target.value || undefined, page: 1 })}
                placeholder="ID ou nome"
                className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Data Inicial</label>
              <input
                type="date"
                value={(filters.dateFrom as string) || ''}
                onChange={(e) => onFiltersChange({ ...filters, dateFrom: e.target.value || undefined, page: 1 })}
                className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Data Final</label>
              <input
                type="date"
                value={(filters.dateTo as string) || ''}
                onChange={(e) => onFiltersChange({ ...filters, dateTo: e.target.value || undefined, page: 1 })}
                className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Bulk Action Bar
function ContestBulkActionBar({
  selectedCount,
  onBulkCreateContest,
  onClearSelection,
}: {
  selectedCount: number
  onBulkCreateContest: () => void
  onClearSelection: () => void
}) {
  return (
    <div className="fixed bottom-4 left-4 right-4 sm:right-auto sm:left-auto sm:w-96 z-50 animate-slide-up">
      <div className="card shadow-lg">
        <div className="card-body p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="font-medium text-secondary-900">
              {selectedCount} contestação{selectedCount > 1 ? 'ões' : ''} selecionada{selectedCount > 1 ? 's' : ''}
            </span>
            <Button variant="primary" onClick={onBulkCreateContest}>
              <Plus className="h-4 w-4 mr-2" />
              Criar Contestação
            </Button>
          </div>
          <button onClick={onClearSelection} className="p-2 text-secondary-400 hover:text-secondary-600">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>
    </div>
  )
}

// Detail Modal (placeholder - will be replaced by full page)
function ContestDetailModal() {
  // In a real implementation, this would fetch contest details
  // For now, we navigate to the detail page
  return null
}