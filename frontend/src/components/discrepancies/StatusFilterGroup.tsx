'use client'

import { cn } from '@/utils/helpers'
import { getStatusBadge, DISCREPANCY_STATUS } from '@/utils/helpers'
import { Badge } from '@/components/Badge'

interface StatusFilterGroupProps {
  title: string
  subtitle?: string
  counts: Record<string, number>
  total: number
  activeFilter?: string
  onFilterChange: (status: string | undefined) => void
  variant?: 'status' | 'severity'
}

const statusConfig = [
  { key: DISCREPANCY_STATUS.OPEN, label: 'Abertas' },
  { key: DISCREPANCY_STATUS.IN_REVIEW, label: 'Em Análise' },
  { key: DISCREPANCY_STATUS.CONTESTED, label: 'Contestadas' },
  { key: DISCREPANCY_STATUS.APPROVED, label: 'Aprovadas' },
  { key: DISCREPANCY_STATUS.REJECTED, label: 'Rejeitadas' },
  { key: DISCREPANCY_STATUS.PAID, label: 'Pagas' },
  { key: DISCREPANCY_STATUS.CLOSED, label: 'Fechadas' },
]

const severityConfig = [
  { key: 'CRITICAL', label: 'Críticas' },
  { key: 'HIGH', label: 'Altas' },
  { key: 'MEDIUM', label: 'Médias' },
  { key: 'LOW', label: 'Baixas' },
]

const severityColors: Record<string, { bg: string; text: string; bar: string }> = {
  CRITICAL: { bg: 'bg-rose-50', text: 'text-rose-700', bar: 'bg-rose-500' },
  HIGH: { bg: 'bg-warning-50', text: 'text-warning-700', bar: 'bg-warning-500' },
  MEDIUM: { bg: 'bg-primary-50', text: 'text-primary-700', bar: 'bg-primary-500' },
  LOW: { bg: 'bg-emerald-50', text: 'text-emerald-700', bar: 'bg-emerald-500' },
}

export function StatusFilterGroup({
  title,
  subtitle,
  counts,
  total,
  activeFilter,
  onFilterChange,
  variant = 'status',
}: StatusFilterGroupProps) {
  const config = variant === 'status' ? statusConfig : severityConfig
  const isStatus = variant === 'status'

  return (
    <div className="card card-hover h-full">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-secondary-900">{title}</h3>
          {subtitle && <p className="text-sm text-secondary-500">{subtitle}</p>}
        </div>
      </div>
      <div className="card-body pt-0">
        <div className="space-y-3">
          {config.map((item) => {
            const count = counts[item.key] || 0
            const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : '0'
            const isActive = activeFilter === item.key

            if (isStatus) {
              const { variant: badgeVariant, label } = getStatusBadge(item.key)
              const variantClasses: Record<string, { bg: string; text: string }> = {
                'badge-primary': { bg: 'bg-primary-50', text: 'text-primary-700' },
                'badge-warning': { bg: 'bg-warning-50', text: 'text-warning-700' },
                'badge-danger': { bg: 'bg-rose-50', text: 'text-rose-700' },
                'badge-success': { bg: 'bg-emerald-50', text: 'text-emerald-700' },
                'badge-secondary': { bg: 'bg-secondary-100', text: 'text-secondary-700' },
              }
              const colors = variantClasses[badgeVariant] || variantClasses['badge-secondary']

              return (
                <button
                  key={item.key}
                  onClick={() => onFilterChange(isActive ? undefined : item.key)}
                  className={cn(
                    'w-full flex items-center justify-between p-3 rounded-lg transition-all duration-150 text-left',
                    isActive
                      ? 'bg-primary-50 border border-primary-200 ring-1 ring-primary-200'
                      : 'hover:bg-secondary-50 border border-transparent'
                  )}
                  aria-pressed={isActive}
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <Badge
                      variant={badgeVariant as any}
                      className={cn('flex-shrink-0', isActive && 'ring-2 ring-primary-500/50')}
                    >
                      {label}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-secondary-900 truncate">{item.label}</p>
                      <div className="h-1.5 w-full bg-secondary-100 rounded-full mt-1 overflow-hidden">
                        <div
                          className={cn('h-full rounded-full transition-all duration-300', colors.bg.replace('bg-', 'bg-'))}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 ml-3 flex-shrink-0">
                    <span className="text-sm font-bold text-secondary-900 tabular-nums w-14 text-right">{count}</span>
                    <span className="text-xs text-secondary-500 w-12 text-right">{percentage}%</span>
                  </div>
                </button>
              )
            }

            // Severity variant - stacked bar style
            const colors = severityColors[item.key] || severityColors.MEDIUM

            return (
              <button
                key={item.key}
                onClick={() => onFilterChange(isActive ? undefined : item.key)}
                className={cn(
                  'w-full p-3 rounded-lg transition-all duration-150 text-left',
                  isActive
                    ? 'bg-primary-50 border border-primary-200 ring-1 ring-primary-200'
                    : 'hover:bg-secondary-50 border border-transparent'
                )}
                aria-pressed={isActive}
              >
                <div className="flex items-center gap-3 mb-2">
                  <Badge
                    variant="secondary"
                    className={cn(colors.bg, colors.text, 'px-2 py-1', isActive && 'ring-2 ring-primary-500/50')}
                  >
                    {item.label}
                  </Badge>
                  <div className="flex-1 h-1.5 bg-secondary-100 rounded-full overflow-hidden">
                    <div
                      className={cn('h-full rounded-full transition-all duration-300', colors.bar)}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary-500">Total</span>
                  <span className="font-bold text-secondary-900 tabular-nums">{count} ({percentage}%)</span>
                </div>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}