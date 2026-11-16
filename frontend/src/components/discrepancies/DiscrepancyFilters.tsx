'use client'

import { useMemo } from 'react'
import { X, Filter } from 'lucide-react'
import { Badge, Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components'

interface DiscrepancyFiltersProps {
  filters: DiscrepancyFilters
  onFiltersChange: (filters: DiscrepancyFilters) => void
  onClearFilters: () => void
  hasActiveFilters: boolean
  summary?: {
    by_status?: Record<string, number>
    by_severity?: Record<string, number>
    by_rule?: Record<string, number>
  }
}

interface DiscrepancyFilters {
  page?: number
  size?: number
  status?: string
  severity?: string
  rule?: string
  carrier?: string
  dateFrom?: string
  dateTo?: string
  [key: string]: unknown
}

const statusOptions = [
  { value: 'OPEN', label: 'Aberta' },
  { value: 'IN_REVIEW', label: 'Em Análise' },
  { value: 'CONTESTED', label: 'Contestada' },
  { value: 'APPROVED', label: 'Aprovada' },
  { value: 'REJECTED', label: 'Rejeitada' },
  { value: 'PAID', label: 'Paga' },
  { value: 'CLOSED', label: 'Fechada' },
]

const severityOptions = [
  { value: 'LOW', label: 'Baixa' },
  { value: 'MEDIUM', label: 'Média' },
  { value: 'HIGH', label: 'Alta' },
  { value: 'CRITICAL', label: 'Crítica' },
]

const ruleOptions = [
  { value: 'FREIGHT_VALUE', label: 'Valor Frete' },
  { value: 'ICMS', label: 'ICMS' },
  { value: 'TOLLS', label: 'Pedágios' },
  { value: 'WEIGHT', label: 'Peso' },
  { value: 'VOLUME', label: 'Volume' },
  { value: 'DIMENSIONS', label: 'Dimensões' },
  { value: 'DUPLICATE', label: 'Duplicado' },
  { value: 'MISSING_DOCUMENT', label: 'Doc. Ausente' },
  { value: 'INVALID_CNPJ', label: 'CNPJ Inválido' },
  { value: 'ROUTE_MISMATCH', label: 'Rota Divergente' },
  { value: 'OTHER', label: 'Outro' },
]

const getBadgeVariant = (variant: string): 'success' | 'warning' | 'danger' | 'primary' | 'secondary' => {
  switch (variant) {
    case 'badge-primary': return 'primary'
    case 'badge-warning': return 'warning'
    case 'badge-danger': return 'danger'
    case 'badge-success': return 'success'
    default: return 'secondary'
  }
}

const getStatusBadgeConfig = (status: string) => {
  const statusMap: Record<string, { variant: string; label: string }> = {
    OPEN: { variant: 'badge-primary', label: 'Aberta' },
    IN_REVIEW: { variant: 'badge-warning', label: 'Em Análise' },
    CONTESTED: { variant: 'badge-warning', label: 'Contestada' },
    APPROVED: { variant: 'badge-success', label: 'Aprovada' },
    REJECTED: { variant: 'badge-danger', label: 'Rejeitada' },
    PAID: { variant: 'badge-success', label: 'Paga' },
    CLOSED: { variant: 'badge-secondary', label: 'Fechada' },
  }
  return statusMap[status] || { variant: 'badge-secondary', label: status }
}

const getSeverityBadgeConfig = (severity: string) => {
  const severityMap: Record<string, { variant: string; label: string }> = {
    LOW: { variant: 'badge-secondary', label: 'Baixa' },
    MEDIUM: { variant: 'badge-primary', label: 'Média' },
    HIGH: { variant: 'badge-warning', label: 'Alta' },
    CRITICAL: { variant: 'badge-danger', label: 'Crítica' },
  }
  return severityMap[severity] || { variant: 'badge-secondary', label: severity }
}

export function DiscrepancyFilters({
  filters,
  onFiltersChange,
  onClearFilters,
  hasActiveFilters,
  summary,
}: DiscrepancyFiltersProps) {
  const activeFiltersCount = useMemo(() => {
    let count = 0
    if (filters.status) count++
    if (filters.severity) count++
    if (filters.rule) count++
    if (filters.carrier) count++
    if (filters.dateFrom) count++
    if (filters.dateTo) count++
    return count
  }, [filters])

  const renderActiveFilter = (key: string, label: string, variant: string = 'secondary') => (
    <span className="flex items-center gap-1.5">
      <Badge variant={variant as any}>{label}</Badge>
      <button
        onClick={() => onFiltersChange({ ...filters, [key]: undefined })}
        className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
        aria-label={`Remover filtro ${label}`}
      >
        <X className="h-3 w-3" />
      </button>
    </span>
  )

  return (
    <div className="card">
      <div className="card-body p-4">
        {/* Active Filters Tags */}
        {(activeFiltersCount > 0 || hasActiveFilters) && (
          <div className="flex flex-wrap items-center gap-2 mb-4 pb-4 border-b border-secondary-200/60">
            <span className="text-xs font-medium text-secondary-500 uppercase tracking-wide">Filtros ativos:</span>
            {filters.status && (
              <>
                {(() => {
                  const config = getStatusBadgeConfig(String(filters.status))
                  return renderActiveFilter('status', config.label, getBadgeVariant(config.variant))
                })()}
              </>
            )}
            {filters.severity && (
              <>
                {(() => {
                  const config = getSeverityBadgeConfig(String(filters.severity))
                  return renderActiveFilter('severity', config.label, getBadgeVariant(config.variant))
                })()}
              </>
            )}
            {filters.rule && renderActiveFilter('rule', ruleOptions.find((r) => r.value === filters.rule)?.label || String(filters.rule))}
            {filters.carrier && renderActiveFilter('carrier', `Transportadora: ${String(filters.carrier).slice(0, 8)}...`)}
            {filters.dateFrom && renderActiveFilter('dateFrom', `De: ${String(filters.dateFrom)}`)}
            {filters.dateTo && renderActiveFilter('dateTo', `Até: ${String(filters.dateTo)}`)}
            {activeFiltersCount > 0 && (
              <Button variant="ghost" size="sm" onClick={onClearFilters} className="ml-2">
                Limpar todos
              </Button>
            )}
          </div>
        )}

        {/* Filter Controls - Compact horizontal layout */}
        <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
          <div className="flex flex-wrap gap-3 flex-1">
            {/* Status Filter */}
            <div className="relative">
              <Select
                value={filters.status || ''}
                onValueChange={(value) => onFiltersChange({ ...filters, status: value || undefined, page: 1 })}
              >
                <SelectTrigger className="w-[160px] min-w-0">
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent position="popper" sideOffset={5}>
                  <SelectItem value="">Todos os status</SelectItem>
                  {statusOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      <div className="flex items-center justify-between w-full">
                        <span>{opt.label}</span>
                        {summary?.by_status?.[opt.value] !== undefined && (
                          <Badge variant="secondary" className="ml-2">
                            {summary.by_status[opt.value]}
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Severity Filter */}
            <div className="relative">
              <Select
                value={filters.severity || ''}
                onValueChange={(value) => onFiltersChange({ ...filters, severity: value || undefined, page: 1 })}
              >
                <SelectTrigger className="w-[140px] min-w-0">
                  <SelectValue placeholder="Todas severidades" />
                </SelectTrigger>
                <SelectContent position="popper" sideOffset={5}>
                  <SelectItem value="">Todas as severidades</SelectItem>
                  {severityOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      <div className="flex items-center justify-between w-full">
                        <span>{opt.label}</span>
                        {summary?.by_severity?.[opt.value] !== undefined && (
                          <Badge variant="secondary" className="ml-2">
                            {summary.by_severity[opt.value]}
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Rule Filter */}
            <div className="relative">
              <Select
                value={filters.rule || ''}
                onValueChange={(value) => onFiltersChange({ ...filters, rule: value || undefined, page: 1 })}
              >
                <SelectTrigger className="w-[180px] min-w-0">
                  <SelectValue placeholder="Todas as regras" />
                </SelectTrigger>
                <SelectContent position="popper" sideOffset={5}>
                  <SelectItem value="">Todas as regras</SelectItem>
                  {ruleOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      <div className="flex items-center justify-between w-full">
                        <span>{opt.label}</span>
                        {summary?.by_rule?.[opt.value] !== undefined && (
                          <Badge variant="secondary" className="ml-2">
                            {summary.by_rule[opt.value]}
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Carrier Filter */}
            <Input
              type="text"
              placeholder="Transportadora (ID)"
              className="w-[160px] min-w-0"
              value={filters.carrier || ''}
              onChange={(e) => onFiltersChange({ ...filters, carrier: e.target.value || undefined, page: 1 })}
            />

            {/* Date Range - Compact */}
            <div className="flex items-center gap-1.5">
              <Input
                type="date"
                className="w-[130px] min-w-0"
                value={filters.dateFrom || ''}
                onChange={(e) => onFiltersChange({ ...filters, dateFrom: e.target.value || undefined, page: 1 })}
                aria-label="Data inicial"
              />
              <span className="text-secondary-400 text-xs hidden sm:inline">até</span>
              <Input
                type="date"
                className="w-[130px] min-w-0"
                value={filters.dateTo || ''}
                onChange={(e) => onFiltersChange({ ...filters, dateTo: e.target.value || undefined, page: 1 })}
                aria-label="Data final"
              />
            </div>
          </div>

          <div className="flex gap-2 sm:ml-auto">
            <Button variant="secondary" onClick={onClearFilters} disabled={activeFiltersCount === 0 && !hasActiveFilters}>
              <Filter className="h-4 w-4 mr-2" />
              Limpar
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}