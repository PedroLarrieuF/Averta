import { cn } from '../utils/helpers'

interface KPICardProps {
  children: React.ReactNode
  className?: string
}

export function KPICard({ children, className }: KPICardProps) {
  return (
    <div className={cn('card p-4', className)}>
      {children}
    </div>
  )
}

interface KPIValueProps {
  children: React.ReactNode
  className?: string
}

export function KPIValue({ children, className }: KPIValueProps) {
  return (
    <p className={cn('text-2xl font-bold text-secondary-900', className)}>
      {children}
    </p>
  )
}

interface KPILabelProps {
  children: React.ReactNode
  className?: string
}

export function KPILabel({ children, className }: KPILabelProps) {
  return (
    <p className={cn('text-sm text-secondary-500', className)}>
      {children}
    </p>
  )
}

interface KPITrendProps {
  children: React.ReactNode
  className?: string
  trend?: 'up' | 'down' | 'neutral'
}

export function KPITrend({ children, className, trend = 'neutral' }: KPITrendProps) {
  const trendColors = {
    up: 'text-success-600',
    down: 'text-danger-600',
    neutral: 'text-secondary-500',
  }

  return (
    <span className={cn('text-sm font-medium', trendColors[trend], className)}>
      {children}
    </span>
  )
}