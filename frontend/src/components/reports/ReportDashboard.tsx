import { TrendingUp, DollarSign, Percent, Clock } from 'lucide-react'
import { KPICard, KPIValue, KPILabel } from '@/components'
import { TimeSeriesChart, TopCarriersChart, TopRulesChart, SeverityDistributionChart } from './KPIChart'
import { DashboardResponse } from '@/hooks/useReports'
import { formatCurrency, formatPercent } from '@/utils/helpers'

interface ReportDashboardProps {
  data?: DashboardResponse
  isLoading?: boolean
}

export function ReportDashboard({ data, isLoading = false }: ReportDashboardProps) {
  const kpis = data?.kpis

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="h-24 bg-secondary-100 rounded-xl" />
          <div className="h-24 bg-secondary-100 rounded-xl" />
          <div className="h-24 bg-secondary-100 rounded-xl" />
          <div className="h-24 bg-secondary-100 rounded-xl" />
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="h-80 bg-secondary-100 rounded-xl" />
          <div className="h-80 bg-secondary-100 rounded-xl" />
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="h-80 bg-secondary-100 rounded-xl" />
          <div className="h-80 bg-secondary-100 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-secondary-500">Nenhum dado disponível</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard>
          <div className="flex items-center justify-between">
            <div>
              <KPILabel>Total Discrepâncias</KPILabel>
              <KPIValue>{kpis?.total_discrepancies ?? 0}</KPIValue>
            </div>
            <div className="p-3 rounded-xl bg-primary-100 text-primary-600">
              <TrendingUp className="h-6 w-6" />
            </div>
          </div>
        </KPICard>

        <KPICard>
          <div className="flex items-center justify-between">
            <div>
              <KPILabel>Valor Recuperado</KPILabel>
              <KPIValue>{formatCurrency(kpis?.total_recovered ?? 0)}</KPIValue>
            </div>
            <div className="p-3 rounded-xl bg-success-100 text-success-600">
              <DollarSign className="h-6 w-6" />
            </div>
          </div>
        </KPICard>

        <KPICard>
          <div className="flex items-center justify-between">
            <div>
              <KPILabel>Taxa de Sucesso</KPILabel>
              <KPIValue>{formatPercent((kpis?.success_rate ?? 0) / 100)}</KPIValue>
            </div>
            <div className="p-3 rounded-xl bg-warning-100 text-warning-600">
              <Percent className="h-6 w-6" />
            </div>
          </div>
        </KPICard>

        <KPICard>
          <div className="flex items-center justify-between">
            <div>
              <KPILabel>Tempo Médio Resolução</KPILabel>
              <KPIValue>{(kpis?.avg_resolution_days ?? 0).toFixed(1)} dias</KPIValue>
            </div>
            <div className="p-3 rounded-xl bg-secondary-100 text-secondary-600">
              <Clock className="h-6 w-6" />
            </div>
          </div>
        </KPICard>
      </div>

      {/* Charts Row 1 */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <div className="card-header">
            <h3 className="font-medium text-secondary-900">Discrepâncias ao Longo do Tempo</h3>
          </div>
          <div className="card-body">
            <TimeSeriesChart data={data.time_series} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="font-medium text-secondary-900">Top Transportadoras por Valor Recuperado</h3>
          </div>
          <div className="card-body">
            <TopCarriersChart data={data.top_carriers} />
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <div className="card-header">
            <h3 className="font-medium text-secondary-900">Distribuição por Tipo de Regra</h3>
          </div>
          <div className="card-body">
            <TopRulesChart data={data.top_rules} />
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="font-medium text-secondary-900">Distribuição por Severidade</h3>
          </div>
          <div className="card-body">
            <SeverityDistributionChart data={data.by_severity} />
          </div>
        </div>
      </div>
    </div>
  )
}