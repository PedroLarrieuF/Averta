import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button, PageHeader, PageTitle, PageSubtitle, Card, CardHeader, CardBody, Badge } from '@/components'
import { ReportFilters } from '@/components/reports/ReportFilters'
import { ExportPanel } from '@/components/reports/ExportPanel'
import { useReportDashboard, useExportPDF, useExportExcel, ReportFilters as ReportFiltersType } from '@/hooks/useReports'
import toast from 'react-hot-toast'

export function ReportExportPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [filters, setFilters] = useState<Record<string, unknown>>({})
  const [initialLoad, setInitialLoad] = useState(true)

  // Parse filters from URL on mount
  useEffect(() => {
    const urlFilters: Record<string, unknown> = {}
    searchParams.forEach((value, key) => {
      urlFilters[key] = value
    })
    // Default to 30d if no period specified
    if (!urlFilters.period && !urlFilters.dateFrom && !urlFilters.dateTo) {
      urlFilters.period = '30d'
    }
    setFilters(urlFilters)
    setInitialLoad(false)
  }, [searchParams])

  const updateFilters = (newFilters: Record<string, unknown>) => {
    setFilters(newFilters)
    const params = new URLSearchParams()
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        params.set(key, String(value))
      }
    })
    navigate(`/reports/export?${params.toString()}`, { replace: true })
  }

  const clearFilters = () => {
    updateFilters({ period: '30d' })
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== '' && v !== null && v !== '30d')

  // Dashboard data for preview
  const { data: dashboardData } = useReportDashboard(filters as ReportFiltersType)

  // Export mutations
  const exportPDF = useExportPDF(filters as ReportFiltersType)
  const exportExcel = useExportExcel(filters as ReportFiltersType)

  const handleExportPDF = async () => {
    try {
      const blob = await exportPDF.mutateAsync()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `relatorio-discrepancias-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('PDF baixado com sucesso!')
    } catch (_error) {
      toast.error('Erro ao gerar PDF')
    }
  }

  const handleExportExcel = async () => {
    try {
      const blob = await exportExcel.mutateAsync()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `relatorio-discrepancias-${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('Excel baixado com sucesso!')
    } catch (_error) {
      toast.error('Erro ao gerar Excel')
    }
  }

  const formatFilterLabel = (key: string, value: unknown) => {
    const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())
    if (key === 'period') {
      const periods: Record<string, string> = {
        '7d': 'Últimos 7 dias',
        '30d': 'Últimos 30 dias',
        '90d': 'Últimos 90 dias',
        '12m': 'Últimos 12 meses',
      }
      return `${label}: ${periods[value as string] || value}`
    }
    return `${label}: ${value}`
  }

  if (initialLoad) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-secondary-100 rounded w-1/4" />
        <div className="h-24 bg-secondary-100 rounded-xl" />
        <div className="h-24 bg-secondary-100 rounded-xl" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => navigate('/reports')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <PageTitle>Exportar Relatório</PageTitle>
            <PageSubtitle>Configure os filtros e baixe o relatório em PDF ou Excel</PageSubtitle>
          </div>
        </div>
      </PageHeader>

      {/* Active Filters Summary */}
      {hasActiveFilters && (
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h3 className="font-medium text-secondary-900">Filtros Ativos</h3>
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Limpar todos
            </Button>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-2">
              {Object.entries(filters).map(([key, value]) => {
                if (value === undefined || value === '' || value === null) return null
                return (
                  <Badge key={key} variant="secondary" className="flex items-center gap-1">
                    {formatFilterLabel(key, value)}
                    <button
                      type="button"
                      onClick={() => {
                        const newFilters = { ...filters }
                        delete newFilters[key]
                        updateFilters(newFilters)
                      }}
                      className="ml-1 hover:text-danger-600"
                    >
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </Badge>
                )
              })}
            </div>
          </CardBody>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <ReportFilters
            filters={filters}
            onFiltersChange={updateFilters}
            onClearFilters={clearFilters}
            hasActiveFilters={hasActiveFilters}
          />
        </div>

        {/* Preview & Export */}
        <div className="lg:col-span-2 space-y-6">
          {/* KPIs Preview */}
          {dashboardData?.kpis && (
            <Card>
              <CardHeader>
                <h3 className="font-medium text-secondary-900">Pré-visualização dos KPIs</h3>
              </CardHeader>
              <CardBody className="p-0">
                <div className="grid grid-cols-2 gap-4 p-4">
                  <div className="p-4 rounded-lg bg-primary-50 border border-primary-100">
                    <p className="text-xs text-primary-700 uppercase tracking-wide">Total Discrepâncias</p>
                    <p className="font-bold text-primary-900 text-2xl">{dashboardData.kpis.total_discrepancies}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-success-50 border border-success-100">
                    <p className="text-xs text-success-700 uppercase tracking-wide">Valor Recuperado</p>
                    <p className="font-bold text-success-900 text-2xl">{dashboardData.kpis.total_recovered.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-warning-50 border border-warning-100">
                    <p className="text-xs text-warning-700 uppercase tracking-wide">Taxa de Sucesso</p>
                    <p className="font-bold text-warning-900 text-2xl">{dashboardData.kpis.success_rate.toFixed(1)}%</p>
                  </div>
                  <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-100">
                    <p className="text-xs text-secondary-700 uppercase tracking-wide">Tempo Médio</p>
                    <p className="font-bold text-secondary-900 text-2xl">{dashboardData.kpis.avg_resolution_days.toFixed(1)} dias</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Export Panel */}
          <ExportPanel
            filters={filters}
            kpis={dashboardData?.kpis}
            onExportPDF={handleExportPDF}
            onExportExcel={handleExportExcel}
          />

          {/* Data Preview */}
          {dashboardData && (
            <Card>
              <CardHeader>
                <h3 className="font-medium text-secondary-900">Pré-visualização dos Dados</h3>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-secondary-900 mb-2">Série Temporal</h4>
                    <div className="h-64">
                      {dashboardData.time_series.length > 0 ? (
                        <canvas id="timeSeriesPreview" className="w-full h-full" />
                      ) : (
                        <p className="text-secondary-500 text-center py-8">Sem dados</p>
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-secondary-900 mb-2">Top Transportadoras</h4>
                    {dashboardData.top_carriers.length > 0 ? (
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {dashboardData.top_carriers.slice(0, 5).map((carrier, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <span className="w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">
                                {index + 1}
                              </span>
                              <span className="font-medium text-secondary-900">{carrier.carrier_name}</span>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-success-700">{carrier.recovered.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</p>
                              <p className="text-xs text-secondary-500">{carrier.count} discrepâncias</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-secondary-500 text-center py-4">Sem dados</p>
                    )}
                  </div>
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}