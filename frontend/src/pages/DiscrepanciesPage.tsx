import { useState, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Download, Filter } from 'lucide-react'
import { useDiscrepancies, useDiscrepancySummary, useBulkUpdateDiscrepancyStatus, useReviewDiscrepancy } from '@/hooks'
import { DiscrepancyTable, DiscrepancyFilters, DiscrepancySummaryCards, DiscrepancyDetailModal, BulkActionBar, PageHeader, PageTitle, PageSubtitle, Button } from '@/components'
import { Discrepancy } from '@/types'
import toast from 'react-hot-toast'

export function DiscrepanciesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  // Parse filters from URL
  const getInitialFilters = (): Record<string, unknown> => {
    const filters: Record<string, unknown> = {
      page: parseInt(searchParams.get('page') || '1', 10),
      size: parseInt(searchParams.get('size') || '20', 10),
    }
    if (searchParams.get('status')) filters.status = searchParams.get('status')
    if (searchParams.get('severity')) filters.severity = searchParams.get('severity')
    if (searchParams.get('rule')) filters.rule = searchParams.get('rule')
    if (searchParams.get('carrier')) filters.carrier = searchParams.get('carrier')
    if (searchParams.get('dateFrom')) filters.dateFrom = searchParams.get('dateFrom')
    if (searchParams.get('dateTo')) filters.dateTo = searchParams.get('dateTo')
    return filters
  }

  const [filters, setFilters] = useState<Record<string, unknown>>(getInitialFilters)
  const [selectedDiscrepancy, setSelectedDiscrepancy] = useState<Discrepancy | null>(null)
  const [selectedIds, setSelectedIds] = useState<string[]>([])

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
      filters.severity ||
      filters.rule ||
      filters.carrier ||
      filters.dateFrom ||
      filters.dateTo
    )
  }, [filters])

  // Fetch data
  const { data: discrepanciesData, isLoading: isLoadingDiscrepancies } = useDiscrepancies(filters)
  const { data: summaryData, isLoading: isLoadingSummary } = useDiscrepancySummary(filters)

  // Mutations
  const bulkUpdateStatus = useBulkUpdateDiscrepancyStatus()
  const reviewDiscrepancy = useReviewDiscrepancy()

  const handleSelect = (discrepancy: Discrepancy) => {
    setSelectedDiscrepancy(discrepancy)
  }

  const handleCloseDetail = () => {
    setSelectedDiscrepancy(null)
  }

  const handleSelectionChange = (ids: string[]) => {
    setSelectedIds(ids)
  }

  const handleBulkReview = async () => {
    if (selectedIds.length === 0) return
    try {
      await bulkUpdateStatus.mutateAsync({ ids: selectedIds, status: 'IN_REVIEW' })
      toast.success(`${selectedIds.length} discrepância(s) marcada(s) como "Em Análise"`)
      setSelectedIds([])
    } catch (_error) {
      toast.error('Erro ao atualizar status das discrepâncias')
    }
  }

  const handleBulkContest = () => {
    if (selectedIds.length === 0) return
    // Navigate to contest creation page with selected IDs
    navigate(`/contests/create?discrepancyIds=${selectedIds.join(',')}`)
  }

  const handleReview = async (id: string, notes?: string) => {
    try {
      await reviewDiscrepancy.mutateAsync({ id, notes })
      toast.success('Discrepância revisada com sucesso')
      handleCloseDetail()
    } catch (_error) {
      toast.error('Erro ao revisar discrepância')
    }
  }

  const handleContest = (ids: string[]) => {
    navigate(`/contests/create?discrepancyIds=${ids.join(',')}`)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div>
          <PageTitle>Discrepâncias</PageTitle>
          <PageSubtitle>Gerencie e analise discrepâncias encontradas nas auditorias</PageSubtitle>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" className="hidden sm:flex">
            <Filter className="h-4 w-4 mr-2" />
            Filtros
          </Button>
          <Button variant="primary" className="hidden sm:flex">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </PageHeader>

      {/* Summary Cards */}
      <DiscrepancySummaryCards
        summary={summaryData ?? null}
        isLoading={isLoadingSummary}
      />

      {/* Filters */}
      <DiscrepancyFilters
        filters={filters}
        onFiltersChange={updateFilters}
        onClearFilters={clearFilters}
        hasActiveFilters={hasActiveFilters()}
        summary={summaryData ?? undefined}
      />

      {/* Discrepancies Table */}
      <div className="card">
        <div className="card-body p-0">
          <DiscrepancyTable
            discrepancies={discrepanciesData?.data ?? []}
            isLoading={isLoadingDiscrepancies}
            pagination={discrepanciesData?.meta}
            onPageChange={(page) => updateFilters({ ...filters, page })}
            onSizeChange={(size) => updateFilters({ ...filters, size, page: 1 })}
            onSelect={handleSelect}
            onBulkReview={handleBulkReview}
            onBulkContest={handleBulkContest}
            selectedIds={selectedIds}
            onSelectionChange={handleSelectionChange}
          />
        </div>
      </div>

      {/* Detail Modal */}
      {selectedDiscrepancy && (
        <DiscrepancyDetailModal
          discrepancy={selectedDiscrepancy}
          onClose={handleCloseDetail}
          onReview={handleReview}
          onContest={handleContest}
          isReviewing={reviewDiscrepancy.isPending}
          isContesting={false}
        />
      )}

      {/* Bulk Action Bar */}
      <BulkActionBar
        selectedCount={selectedIds.length}
        onBulkReview={handleBulkReview}
        onBulkContest={handleBulkContest}
        onClearSelection={() => setSelectedIds([])}
        isReviewing={bulkUpdateStatus.isPending}
        isContesting={false}
      />
    </div>
  )
}