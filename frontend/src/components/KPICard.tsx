import { cn } from '../utils/helpers'
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'

interface KPICardProps {
  title: string
  value: string | number
  trend?: string
  trendUp?: boolean | null
  icon?: React.ReactNode
  iconBgClass?: string
  iconColorClass?: string
  className?: string
}

export function KPICard({
  title,
  value,
  trend,
  trendUp = null,
  icon,
  iconBgClass = 'bg-primary-50',
  iconColorClass = 'text-primary-600',
  className,
}: KPICardProps) {
  return (
    <div className={cn('kpi-card', className)}>
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="kpi-label">{title}</p>
          <p className="kpi-value truncate tabular-nums">{value}</p>
          {trend && (
            <div className="kpi-trend">
              {trendUp === true ? (
                <span className="trend-pill-positive">
                  <ArrowUpRight className="h-3 w-3" />
                  {trend}
                </span>
              ) : trendUp === false ? (
                <span className="trend-pill-negative">
                  <ArrowDownRight className="h-3 w-3" />
                  {trend}
                </span>
              ) : (
                <span className="trend-pill-neutral">
                  <Minus className="h-3 w-3" />
                  {trend}
                </span>
              )}
            </div>
          )}
        </div>
        {icon && (
          <div className={cn('kpi-icon flex-shrink-0 ml-4', iconBgClass, iconColorClass)}>
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}

interface KPICardSimpleProps {
  children: React.ReactNode
  className?: string
}

export function KPICardSimple({ children, className }: KPICardSimpleProps) {
  return <div className={cn('kpi-card', className)}>{children}</div>
}