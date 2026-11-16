'use client'

import { DollarSign, AlertTriangle, Gavel } from 'lucide-react'
import { Card, CardBody } from '@/components'
import { KPICard } from '@/components/KPICard'
import { StatusFilterGroup } from './StatusFilterGroup'
import { formatCurrency } from '@/utils/helpers'

interface DiscrepancySummaryCardsProps {
  summary: {
    by_status?: Record<string, number>
    by_severity?: Record<string, number>
    by_rule?: Record<string, number>
    total_recovered?: number
    total_contested?: number
  } | null
  isLoading: boolean
  activeStatusFilter?: string
  activeSeverityFilter?: string
  onStatusFilterChange?: (status: string | undefined) => void
  onSeverityFilterChange?: (severity: string | undefined) => void
}

export function DiscrepancySummaryCards({
  summary,
  isLoading,
  activeStatusFilter,
  activeSeverityFilter,
  onStatusFilterChange,
  onSeverityFilterChange,
}: DiscrepancySummaryCardsProps) {
  if (isLoading) {
    return (
      <div className="space-y-5 animate-pulse">
        {/* Row 1: 3 Main KPIs */}
        <div className="grid-kpi">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="kpi-card">
              <CardBody className="p-5">
                <div className="h-4 bg-secondary-200 rounded w-1/4 mb-2" />
                <div className="h-8 bg-secondary-200 rounded w-1/2" />
                <div className="h-4 bg-secondary-200 rounded w-1/3 mt-3" />
              </CardBody>
            </Card>
          ))}
        </div>
        {/* Row 2: Status & Severity */}
        <div className="grid gap-5 lg:grid-cols-2">
          <Card key="status-skeleton" className="card h-[300px]">
            <div className="h-10 bg-secondary-200 rounded mb-4" />
            <div className="space-y-3">
              {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                <div key={i} className="h-12 bg-secondary-200 rounded" />
              ))}
            </div>
          </Card>
          <Card key="severity-skeleton" className="card h-[300px]">
            <div className="h-10 bg-secondary-200 rounded mb-4" />
            <div className="space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-16 bg-secondary-200 rounded" />
              ))}
            </div>
          </Card>
        </div>
      </div>
    )
  }

  if (!summary) {
    return null
  }

  const totalDiscrepancies = Object.values(summary.by_status || {}).reduce((a, b) => a + b, 0)
  const totalRecovered = summary.total_recovered || 0
  const totalContested = summary.total_contested || 0

  return (
    <div className="space-y-5">
      {/* Row 1: Main KPIs - 3 columns */}
      <div className="grid-kpi">
        <KPICard
          title="Total de Discrepâncias"
          value={totalDiscrepancies}
          trend="+12% vs mês anterior"
          trendUp={false}
          icon={<AlertTriangle className="h-5 w-5" />}
          iconBgClass="bg-blue-50"
          iconColorClass="text-blue-600"
        />
        <KPICard
          title="Total Recuperado"
          value={formatCurrency(totalRecovered)}
          trend="+8% vs mês anterior"
          trendUp={true}
          icon={<DollarSign className="h-5 w-5" />}
          iconBgClass="bg-emerald-50"
          iconColorClass="text-emerald-600"
        />
        <KPICard
          title="Total Contestado"
          value={formatCurrency(totalContested)}
          trend="+2.3pp vs mês anterior"
          trendUp={true}
          icon={<Gavel className="h-5 w-5" />}
          iconBgClass="bg-primary-50"
          iconColorClass="text-primary-600"
        />
      </div>

      {/* Row 2: Status & Severity Distribution */}
      <div className="grid gap-5 lg:grid-cols-2">
        <StatusFilterGroup
          title="Distribuição por Status"
          subtitle="Clique para filtrar a tabela"
          counts={summary.by_status || {}}
          total={totalDiscrepancies}
          activeFilter={activeStatusFilter}
          onFilterChange={onStatusFilterChange || (() => {})}
          variant="status"
        />
        <StatusFilterGroup
          title="Distribuição por Severidade"
          subtitle="Clique para filtrar a tabela"
          counts={summary.by_severity || {}}
          total={totalDiscrepancies}
          activeFilter={activeSeverityFilter}
          onFilterChange={onSeverityFilterChange || (() => {})}
          variant="severity"
        />
      </div>
    </div>
  )
}