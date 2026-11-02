import { useMemo } from 'react'
import { X, Filter } from 'lucide-react'
import { Badge, Button, Input } from '@/components'

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

  return (
    <div className="card">
      <div className="card-body p-4">
        {/* Active Filters Tags */}
        {(activeFiltersCount > 0 || hasActiveFilters) && (
          <div className="flex flex-wrap items-center gap-2 mb-4 pb-4 border-b border-secondary-200">
            <span className="text-xs font-medium text-secondary-500 uppercase tracking-wide">Filtros ativos:</span>
            {filters.status && (
              <span className="flex items-center gap-1.5">
                <Badge variant="secondary">{statusOptions.find((s) => s.value === filters.status)?.label || String(filters.status)}</Badge>
                <button
                  onClick={() => onFiltersChange({ ...filters, status: undefined })}
                  className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
                  aria-label="Remover filtro status"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )}
            {filters.severity && (
              <span className="flex items-center gap-1.5">
                <Badge variant="secondary">{severityOptions.find((s) => s.value === filters.severity)?.label || String(filters.severity)}</Badge>
                <button
                  onClick={() => onFiltersChange({ ...filters, severity: undefined })}
                  className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
                  aria-label="Remover filtro severidade"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )}
            {filters.rule && (
              <span className="flex items-center gap-1.5">
                <Badge variant="secondary">{ruleOptions.find((r) => r.value === filters.rule)?.label || String(filters.rule)}</Badge>
                <button
                  onClick={() => onFiltersChange({ ...filters, rule: undefined })}
                  className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
                  aria-label="Remover filtro regra"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )}
            {filters.carrier && (
              <span className="flex items-center gap-1.5">
                <Badge variant="secondary">Transportadora: {String(filters.carrier).slice(0, 8)}...</Badge>
                <button
                  onClick={() => onFiltersChange({ ...filters, carrier: undefined })}
                  className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
                  aria-label="Remover filtro transportadora"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )}
            {filters.dateFrom && (
              <span className="flex items-center gap-1.5">
                <Badge variant="secondary">De: {String(filters.dateFrom)}</Badge>
                <button
                  onClick={() => onFiltersChange({ ...filters, dateFrom: undefined })}
                  className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
                  aria-label="Remover filtro data inicial"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )}
            {filters.dateTo && (
              <span className="flex items-center gap-1.5">
                <Badge variant="secondary">Até: {String(filters.dateTo)}</Badge>
                <button
                  onClick={() => onFiltersChange({ ...filters, dateTo: undefined })}
                  className="p-0.5 rounded hover:bg-secondary-200 transition-colors"
                  aria-label="Remover filtro data final"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            )}
            {activeFiltersCount > 0 && (
              <Button variant="ghost" size="sm" onClick={onClearFilters} className="ml-2">
                Limpar todos
              </Button>
            )}
          </div>
        )}

        {/* Filter Controls */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex gap-4 flex-wrap">
            {/* Status Filter */}
            <select
              className="input w-auto"
              value={filters.status || ''}
              onChange={(e) => onFiltersChange({ ...filters, status: e.target.value || undefined, page: 1 })}
            >
              <option value="">Todos os status</option>
              {statusOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label} {summary?.by_status?.[opt.value] !== undefined && ` (${summary.by_status[opt.value]})`}
                </option>
              ))}
            </select>

            {/* Severity Filter */}
            <select
              className="input w-auto"
              value={filters.severity || ''}
              onChange={(e) => onFiltersChange({ ...filters, severity: e.target.value || undefined, page: 1 })}
            >
              <option value="">Todas as severidades</option>
              {severityOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label} {summary?.by_severity?.[opt.value] !== undefined && ` (${summary.by_severity[opt.value]})`}
                </option>
              ))}
            </select>

            {/* Rule Filter */}
            <select
              className="input w-auto min-w-[200px]"
              value={filters.rule || ''}
              onChange={(e) => onFiltersChange({ ...filters, rule: e.target.value || undefined, page: 1 })}
            >
              <option value="">Todas as regras</option>
              {ruleOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label} {summary?.by_rule?.[opt.value] !== undefined && ` (${summary.by_rule[opt.value]})`}
                </option>
              ))}
            </select>

            {/* Carrier Filter */}
            <Input
              type="text"
              placeholder="Transportadora (ID)"
              className="w-[180px]"
              value={filters.carrier || ''}
              onChange={(e) => onFiltersChange({ ...filters, carrier: e.target.value || undefined, page: 1 })}
            />

            {/* Date Range */}
            <div className="flex items-center gap-2">
              <span className="text-secondary-400 self-center">De</span>
              <Input
                type="date"
                className="w-[140px]"
                value={filters.dateFrom || ''}
                onChange={(e) => onFiltersChange({ ...filters, dateFrom: e.target.value || undefined, page: 1 })}
              />
              <span className="text-secondary-400 self-center">até</span>
              <Input
                type="date"
                className="w-[140px]"
                value={filters.dateTo || ''}
                onChange={(e) => onFiltersChange({ ...filters, dateTo: e.target.value || undefined, page: 1 })}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="secondary" onClick={onClearFilters} disabled={activeFiltersCount === 0 && !hasActiveFilters}>
              <Filter className="h-4 w-4 mr-2" />
              Limpar filtros
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}