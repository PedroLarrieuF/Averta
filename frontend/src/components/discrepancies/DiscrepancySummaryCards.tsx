import { FileText, AlertTriangle, DollarSign, TrendingUp, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Card, CardBody, Badge } from '@/components'
import { DashboardKPIs } from '@/types'
import { cn, formatCurrency, formatNumber, formatPercent } from '@/utils/helpers'

interface DiscrepancySummaryCardsProps {
  summary: DashboardKPIs
  className?: string
}

export function DiscrepancySummaryCards({ summary, className }: DiscrepancySummaryCardsProps) {
  const cards = [
    {
      title: 'Total Discrepâncias',
      value: formatNumber(summary.totalDiscrepancies),
      icon: FileText,
      iconColor: 'text-primary-600',
      bgColor: 'bg-primary-50',
      trend: '+12% vs mês anterior',
      trendUp: false,
    },
    {
      title: 'Discrepâncias Abertas',
      value: formatNumber(summary.openDiscrepancies),
      icon: AlertTriangle,
      iconColor: 'text-warning-600',
      bgColor: 'bg-warning-50',
      trend: `${summary.openDiscrepancies > 0 ? 'Aguardando análise' : 'Todas resolvidas'}`,
      trendUp: false,
    },
    {
      title: 'Valor Contestável',
      value: formatCurrency(summary.contestedAmount),
      icon: DollarSign,
      iconColor: 'text-success-600',
      bgColor: 'bg-success-50',
      trend: '+8% vs mês anterior',
      trendUp: true,
    },
    {
      title: 'Taxa de Recuperação',
      value: formatPercent(summary.recoveryRate),
      icon: TrendingUp,
      iconColor: 'text-primary-600',
      bgColor: 'bg-primary-50',
      trend: '+2.3pp vs mês anterior',
      trendUp: true,
    },
  ]

  return (
    <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4', className)}>
      {cards.map((card, index) => (
        <Card key={index} className="kpi-card">
          <div className="flex items-start justify-between">
            <div>
              <p className="kpi-label">{card.title}</p>
              <p className="kpi-value">{card.value}</p>
              {card.trend && (
                <div className="kpi-trend">
                  <span className={cn(card.trendUp ? 'kpi-trend-up' : 'kpi-trend-down')}>
                    {card.trendUp ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                    {card.trend}
                  </span>
                </div>
              )}
            </div>
            <div className={cn('p-3 rounded-xl', card.bgColor)}>
              <card.icon className={cn('h-6 w-6', card.iconColor)} />
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

// Need to import TrendingDown
import { TrendingDown } from 'lucide-react'