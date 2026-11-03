import { useState, useEffect } from 'react'
import { Calendar, X, Filter } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Badge } from '@/components'
import { cn } from '@/utils/helpers'

interface ReportFiltersProps {
  filters: Record<string, unknown>
  onFiltersChange: (filters: Record<string, unknown>) => void
  onClearFilters: () => void
  hasActiveFilters: boolean
}

export function ReportFilters({ filters, onFiltersChange, onClearFilters, hasActiveFilters }: ReportFiltersProps) {
  const [isOpen, setIsOpen] = useState(false)

  // Sync with URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlFilters: Record<string, unknown> = {}
    params.forEach((value, key) => {
      urlFilters[key] = value
    })
    if (Object.keys(urlFilters).length > 0) {
      onFiltersChange(urlFilters)
    }
  }, [onFiltersChange])

  const handlePeriodChange = (period: string) => {
    const newFilters = { ...filters }
    if (period === 'custom') {
      newFilters.dateFrom = ''
      newFilters.dateTo = ''
    } else {
      delete newFilters.dateFrom
      delete newFilters.dateTo
    }
    newFilters.period = period !== 'custom' ? period : undefined
    onFiltersChange(newFilters)
  }

  const handleDateChange = (field: 'dateFrom' | 'dateTo', value: string) => {
    const newFilters = { ...filters, [field]: value || undefined, period: 'custom' }
    onFiltersChange(newFilters)
  }

  const handleSelectChange = (field: string, value: string) => {
    const newFilters = { ...filters, [field]: value || undefined }
    onFiltersChange(newFilters)
  }

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <h3 className="font-medium text-secondary-900 flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filtros do Relatório
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 rounded-lg text-secondary-500 hover:bg-secondary-100 transition-colors"
            aria-label={isOpen ? 'Ocultar filtros' : 'Mostrar filtros'}
          >
            {isOpen ? (
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            )}
          </button>
          {hasActiveFilters && (
            <button onClick={onClearFilters} className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              Limpar
            </button>
          )}
        </div>
      </div>

      {isOpen && (
        <div className="card-body p-4 pt-0 space-y-4">
          {/* Period Selector */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-secondary-700">Período</label>
            <div className="flex flex-wrap gap-2">
              {[
                { value: '7d', label: 'Últimos 7 dias' },
                { value: '30d', label: 'Últimos 30 dias' },
                { value: '90d', label: 'Últimos 90 dias' },
                { value: '12m', label: 'Últimos 12 meses' },
                { value: 'custom', label: 'Personalizado' },
              ].map((p) => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => handlePeriodChange(p.value)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                    (filters.period === p.value || (p.value === 'custom' && filters.period === 'custom'))
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Date Range */}
          {(filters.period === 'custom' || !filters.period) && (
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-secondary-700">Data Inicial</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
                  <input
                    type="date"
                    value={(filters.dateFrom as string) || ''}
                    onChange={(e) => handleDateChange('dateFrom', e.target.value)}
                    className="w-full pl-10 pr-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-secondary-700">Data Final</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
                  <input
                    type="date"
                    value={(filters.dateTo as string) || ''}
                    onChange={(e) => handleDateChange('dateTo', e.target.value)}
                    className="w-full pl-10 pr-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Additional Filters */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Transportadora</label>
              <Select
                value={(filters.carrierId as string) || ''}
                onValueChange={(value) => handleSelectChange('carrierId', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Todas" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todas</SelectItem>
                  {/* Options would be populated from API */}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Cliente</label>
              <Select
                value={(filters.clientId as string) || ''}
                onValueChange={(value) => handleSelectChange('clientId', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Status</label>
              <Select
                value={(filters.status as string) || ''}
                onValueChange={(value) => handleSelectChange('status', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="DRAFT">Rascunho</SelectItem>
                  <SelectItem value="SENT">Enviada</SelectItem>
                  <SelectItem value="ACKNOWLEDGED">Recebida</SelectItem>
                  <SelectItem value="NEGOTIATING">Negociando</SelectItem>
                  <SelectItem value="ACCEPTED">Aceita</SelectItem>
                  <SelectItem value="PARTIAL">Parcial</SelectItem>
                  <SelectItem value="REJECTED">Rejeitada</SelectItem>
                  <SelectItem value="EXPIRED">Expirada</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-secondary-700">Regra</label>
              <Select
                value={(filters.ruleCode as string) || ''}
                onValueChange={(value) => handleSelectChange('ruleCode', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Todas" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Active Filters Chips */}
          {hasActiveFilters && (
            <div className="flex flex-wrap gap-2 pt-2 border-t border-secondary-200">
              <span className="text-xs text-secondary-500">Filtros ativos:</span>
              {Object.entries(filters).map(([key, value]) => {
                if (value === undefined || value === '' || value === null) return null
                const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())
                return (
                  <Badge key={key} variant="secondary" className="flex items-center gap-1">
                    {label}: {String(value)}
                    <button
                      type="button"
                      onClick={() => {
                        const newFilters = { ...filters }
                        delete newFilters[key]
                        onFiltersChange(newFilters)
                      }}
                      className="ml-1 hover:text-danger-600"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}