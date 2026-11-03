import { DollarSign, AlertTriangle, Gavel, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Card, CardBody } from '@/components'
import { cn, formatCurrency } from '@/utils/helpers'

interface DiscrepancySummaryCardsProps {
  summary: {
    by_status?: Record<string, number>
    by_severity?: Record<string, number>
    by_rule?: Record<string, number>
    total_recovered?: number
    total_contested?: number
  } | null
  isLoading: boolean
}

const statusConfig = [
  { key: 'OPEN', label: 'Abertas', icon: Clock, variant: 'default' as const },
  { key: 'IN_REVIEW', label: 'Em Análise', icon: AlertTriangle, variant: 'warning' as const },
  { key: 'CONTESTED', label: 'Contestadas', icon: Gavel, variant: 'warning' as const },
  { key: 'APPROVED', label: 'Aprovadas', icon: CheckCircle, variant: 'success' as const },
  { key: 'REJECTED', label: 'Rejeitadas', icon: XCircle, variant: 'danger' as const },
  { key: 'PAID', label: 'Pagas', icon: DollarSign, variant: 'success' as const },
  { key: 'CLOSED', label: 'Fechadas', icon: CheckCircle, variant: 'default' as const },
]

const severityConfig = [
  { key: 'CRITICAL', label: 'Críticas', icon: AlertTriangle, variant: 'danger' as const },
  { key: 'HIGH', label: 'Altas', icon: AlertTriangle, variant: 'warning' as const },
  { key: 'MEDIUM', label: 'Médias', icon: AlertTriangle, variant: 'default' as const },
  { key: 'LOW', label: 'Baixas', icon: AlertTriangle, variant: 'success' as const },
]

export function DiscrepancySummaryCards({ summary, isLoading }: DiscrepancySummaryCardsProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="kpi-card">
            <CardBody className="p-5">
              <div className="h-4 bg-secondary-200 rounded w-1/4 mb-2" />
              <div className="h-8 bg-secondary-200 rounded w-1/2" />
            </CardBody>
          </Card>
        ))}
      </div>
    )
  }

  if (!summary) {
    return null
  }

  const totalDiscrepancies = Object.values(summary.by_status || {}).reduce((a, b) => a + b, 0)

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-7">
      {/* Total Discrepancies */}
      <Card className="kpi-card lg:col-span-2">
        <CardBody className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="kpi-label">Total de Discrepâncias</p>
              <p className="kpi-value text-secondary-900">{totalDiscrepancies}</p>
              <p className="text-xs text-secondary-500 mt-1">Encontradas nos documentos processados</p>
            </div>
            <div className="h-10 w-10 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Recovered Amount */}
      <Card className="kpi-card">
        <CardBody className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="kpi-label">Total Recuperado</p>
              <p className="kpi-value text-success-600">{formatCurrency(summary.total_recovered || 0)}</p>
              <p className="text-xs text-secondary-500 mt-1">Valor total recuperado em contestações</p>
            </div>
            <div className="h-10 w-10 rounded-xl bg-success-50 text-success-600 flex items-center justify-center flex-shrink-0">
              <DollarSign className="h-5 w-5" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Contested Amount */}
      <Card className="kpi-card">
        <CardBody className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="kpi-label">Total Contestado</p>
              <p className="kpi-value text-primary-600">{formatCurrency(summary.total_contested || 0)}</p>
              <p className="text-xs text-secondary-500 mt-1">Valor em disputa ativa</p>
            </div>
            <div className="h-10 w-10 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center flex-shrink-0">
              <Gavel className="h-5 w-5" />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Status Breakdown */}
      {statusConfig.map((config) => {
        const count = summary.by_status?.[config.key] || 0
        return (
          <Card key={config.key} className="kpi-card">
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={cn('h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0', {
                    'bg-warning-50 text-warning-600': config.variant === 'warning',
                    'bg-danger-50 text-danger-600': config.variant === 'danger',
                    'bg-success-50 text-success-600': config.variant === 'success',
                    'bg-primary-50 text-primary-600': config.variant === 'default',
                  })}>
                    <config.icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs text-secondary-500">{config.label}</p>
                    <p className="text-lg font-bold text-secondary-900">{count}</p>
                  </div>
                </div>
                {totalDiscrepancies > 0 && (
                  <span className="text-xs text-secondary-500">
                    {((count / totalDiscrepancies) * 100).toFixed(1)}%
                  </span>
                )}
              </div>
            </CardBody>
          </Card>
        )
      })}

      {/* Severity Breakdown */}
      {severityConfig.map((config) => {
        const count = summary.by_severity?.[config.key] || 0
        return (
          <Card key={config.key} className="kpi-card">
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={cn('h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0', {
                    'bg-danger-50 text-danger-600': config.variant === 'danger',
                    'bg-warning-50 text-warning-600': config.variant === 'warning',
                    'bg-primary-50 text-primary-600': config.variant === 'default',
                    'bg-success-50 text-success-600': config.variant === 'success',
                  })}>
                    <config.icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-xs text-secondary-500">{config.label}</p>
                    <p className="text-lg font-bold text-secondary-900">{count}</p>
                  </div>
                </div>
                {totalDiscrepancies > 0 && (
                  <span className="text-xs text-secondary-500">
                    {((count / totalDiscrepancies) * 100).toFixed(1)}%
                  </span>
                )}
              </div>
            </CardBody>
          </Card>
        )
      })}
    </div>
  )
}