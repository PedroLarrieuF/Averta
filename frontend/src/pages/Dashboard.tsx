import { useDashboardKPIs } from '@/hooks'
import { DashboardKPIs } from '../types'
import { Card, CardBody, CardHeader } from '@/components'
import { Badge, Button } from '@/components'
import { KPICard } from '@/components/KPICard'
import { AnalyticsChart } from '@/components/charts/AnalyticsChart'
import { formatCurrency, formatNumber, formatPercent } from '@/utils/helpers'
import {
  FileText,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  RefreshCw,
  BarChart2,
  Plus,
  Upload,
} from 'lucide-react'

function ChartCard({
  title,
  subtitle,
  children,
  action,
}: {
  title: string
  subtitle?: string
  children: React.ReactNode
  action?: React.ReactNode
}) {
  return (
    <Card className="h-full card-hover">
      <CardHeader className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-secondary-900">{title}</h3>
          {subtitle && <p className="text-sm text-secondary-500">{subtitle}</p>}
        </div>
        {action}
      </CardHeader>
      <CardBody className="pt-0">{children}</CardBody>
    </Card>
  )
}

export function Dashboard() {
  const { data: kpis, isLoading, error } = useDashboardKPIs()

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid-kpi">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="kpi-card">
              <CardBody className="p-5">
                <div className="h-4 bg-secondary-200 rounded w-3/4 mb-2" />
                <div className="h-8 bg-secondary-200 rounded w-1/2" />
              </CardBody>
            </Card>
          ))}
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          <Card className="h-[400px]">
            <div className="h-full bg-secondary-200 rounded" />
          </Card>
          <Card className="h-[400px]">
            <div className="h-full bg-secondary-200 rounded" />
          </Card>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="page-header">
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Visão geral da auditoria de fretes e recuperação de valores</p>
        </div>
        <div className="card p-8 text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-warning-500 mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">Erro ao carregar dashboard</h3>
          <p className="text-secondary-500 mb-4">Não foi possível carregar os dados do dashboard. Tente novamente mais tarde.</p>
          <Button variant="primary" onClick={() => window.location.reload()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Tentar Novamente
          </Button>
        </div>
      </div>
    )
  }

  // Fallback to empty data if no real data (for development)
  const fallbackKPIs: DashboardKPIs = kpis ?? {
    totalDiscrepancies: 50,
    openDiscrepancies: 32,
    contestedAmount: 753482,
    recoveredAmount: 3462094,
    recoveryRate: 45.9,
    documentsProcessed: 1240,
    documentsPending: 45,
    avgResolutionTime: 14,
    trends: {
      discrepancies: [
        { date: '2024-10-01', count: 42 },
        { date: '2024-10-08', count: 38 },
        { date: '2024-10-15', count: 52 },
        { date: '2024-10-22', count: 45 },
        { date: '2024-10-29', count: 48 },
        { date: '2024-11-05', count: 50 },
        { date: '2024-11-12', count: 47 },
      ],
      recovered: [
        { date: '2024-10-01', amount: 285000 },
        { date: '2024-10-08', amount: 320000 },
        { date: '2024-10-15', amount: 410000 },
        { date: '2024-10-22', amount: 380000 },
        { date: '2024-10-29', amount: 450000 },
        { date: '2024-11-05', amount: 520000 },
        { date: '2024-11-12', amount: 480000 },
      ],
    },
  }

  return (
    <div className="space-y-6 animate-in">
      {/* Page Header with Breadcrumb and Actions */}
      <div className="space-y-4">
        {/* Breadcrumb */}
        <nav className="breadcrumb" aria-label="Navegação">
          <span className="breadcrumb-item text-secondary-500">AvertaSaaS</span>
          <span className="breadcrumb-separator" aria-hidden="true">/</span>
          <span className="breadcrumb-item font-medium text-secondary-900">Dashboard</span>
        </nav>

        {/* Title Row */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="page-title">Dashboard</h1>
            <p className="page-subtitle">Visão geral da auditoria de fretes e recuperação de valores</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Importar XML
            </Button>
            <Button variant="primary" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Nova Auditoria
            </Button>
          </div>
        </div>
      </div>

      {/* Demo Mode Badge */}
      <div className="flex items-center gap-2 px-3 py-1.5 bg-primary-50 border border-primary-200 rounded-lg w-fit" role="status" aria-live="polite">
        <span className="h-2 w-2 rounded-full bg-primary-500 animate-pulse" aria-hidden="true" />
        <span className="text-sm font-medium text-primary-700">Modo Demo</span>
      </div>

      {/* KPI Grid */}
      <div className="grid-kpi">
        <KPICard
          title="Total de Discrepâncias"
          value={formatNumber(fallbackKPIs.totalDiscrepancies)}
          trend="+12% vs mês anterior"
          trendUp={false}
          icon={<FileText className="h-5 w-5" />}
          iconBgClass="bg-blue-50"
          iconColorClass="text-blue-600"
        />
        <KPICard
          title="Discrepâncias Abertas"
          value={formatNumber(fallbackKPIs.openDiscrepancies)}
          trend="32 aguardando análise"
          trendUp={null}
          icon={<AlertTriangle className="h-5 w-5" />}
          iconBgClass="bg-warning-50"
          iconColorClass="text-warning-600"
        />
        <KPICard
          title="Valor Contestado"
          value={formatCurrency(fallbackKPIs.contestedAmount)}
          trend="+8% vs mês anterior"
          trendUp={true}
          icon={<DollarSign className="h-5 w-5" />}
          iconBgClass="bg-emerald-50"
          iconColorClass="text-emerald-600"
        />
        <KPICard
          title="Taxa de Recuperação"
          value={formatPercent(fallbackKPIs.recoveryRate)}
          trend="+2.3pp vs mês anterior"
          trendUp={true}
          icon={<TrendingUp className="h-5 w-5" />}
          iconBgClass="bg-primary-50"
          iconColorClass="text-primary-600"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-5 lg:grid-cols-2">
        {/* Discrepancies Trend - Area Chart */}
        <AnalyticsChart
          title="Discrepâncias por Semana"
          subtitle="Evolução semanal das discrepâncias detectadas"
          data={fallbackKPIs.trends.discrepancies}
          dataKey="count"
          type="area"
          color="#0284c7"
          gradientId="colorDiscrepancies"
          yAxisFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(0)}k` : String(value)}
          tooltipFormatter={(value) => [formatNumber(value), 'Discrepâncias']}
          tooltipLabelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}
          action={
            <Button variant="ghost" size="sm">
              <BarChart2 className="h-4 w-4 mr-1" />
              Ver relatório
            </Button>
          }
          periodOptions={[
            { label: '7S', value: '7d' },
            { label: '30D', value: '30d' },
            { label: '90D', value: '90d' },
            { label: '12M', value: '12m' },
          ]}
          currentPeriod="30d"
        />

        {/* Recovery Trend - Line Chart */}
        <AnalyticsChart
          title="Valores Recuperados"
          subtitle="Evolução semanal dos valores recuperados"
          data={fallbackKPIs.trends.recovered}
          dataKey="amount"
          type="line"
          color="#16a34a"
          yAxisFormatter={(value) => {
            if (value >= 1000000) return `R$ ${(value / 1000000).toFixed(1)}M`
            if (value >= 1000) return `R$ ${(value / 1000).toFixed(0)}k`
            return `R$ ${value}`
          }}
          tooltipFormatter={(value) => [formatCurrency(value), 'Recuperado']}
          tooltipLabelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}
          action={
            <Button variant="ghost" size="sm">
              <DollarSign className="h-4 w-4 mr-1" />
              Ver detalhes
            </Button>
          }
          periodOptions={[
            { label: '7S', value: '7d' },
            { label: '30D', value: '30d' },
            { label: '90D', value: '90d' },
            { label: '12M', value: '12m' },
          ]}
          currentPeriod="30d"
        />
      </div>

      {/* Summary Cards Row */}
      <div className="grid gap-5 lg:grid-cols-3">
        <ChartCard title="Documentos Processados" subtitle="Este mês">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="text-center sm:text-left">
              <p className="text-4xl font-bold text-secondary-900 tabular-nums">{formatNumber(fallbackKPIs.documentsProcessed)}</p>
              <p className="text-sm text-secondary-500">Total processados</p>
            </div>
            <div className="text-right">
              <Badge variant="primary">{formatNumber(fallbackKPIs.documentsPending)} pendentes</Badge>
              <p className="text-xs text-secondary-500 mt-1">Aguardando processamento</p>
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Valor Recuperado Total" subtitle="Acumulado">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="text-center sm:text-left">
              <p className="text-4xl font-bold text-emerald-600 tabular-nums">{formatCurrency(fallbackKPIs.recoveredAmount)}</p>
              <p className="text-sm text-secondary-500">De {formatCurrency(fallbackKPIs.contestedAmount)} contestados</p>
            </div>
            <div className="text-right">
              <Badge variant="success">{formatPercent(fallbackKPIs.recoveryRate)} de recuperação</Badge>
              <p className="text-xs text-secondary-500 mt-1">Taxa de sucesso</p>
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Tempo Médio de Resolução" subtitle="Em dias úteis">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="text-center sm:text-left">
              <p className="text-4xl font-bold text-secondary-900 tabular-nums">{fallbackKPIs.avgResolutionTime}</p>
              <p className="text-sm text-secondary-500">Dias úteis</p>
            </div>
            <div className="text-right">
              <Badge variant="secondary">{'Meta: < 10 dias'}</Badge>
              <p className="text-xs text-secondary-500 mt-1">Acima da meta atual</p>
            </div>
          </div>
        </ChartCard>
      </div>

      {/* Quick Actions */}
      <ChartCard title="Ações Rápidas" subtitle="Acesse as funcionalidades mais usadas">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" className="h-24 flex-col gap-2 p-6" onClick={() => window.location.href = '/discrepancies'}>
            <FileText className="h-8 w-8 text-primary-600" />
            <span className="font-medium">Nova Discrepância</span>
            <span className="text-xs text-secondary-500">Criar manualmente</span>
          </Button>
          <Button variant="secondary" className="h-24 flex-col gap-2 p-6" onClick={() => window.location.href = '/documents'}>
            <Upload className="h-8 w-8 text-emerald-600" />
            <span className="font-medium">Upload Documentos</span>
            <span className="text-xs text-secondary-500">XML CTe/NFe</span>
          </Button>
          <Button variant="secondary" className="h-24 flex-col gap-2 p-6" onClick={() => window.location.href = '/contests'}>
            <TrendingUp className="h-8 w-8 text-warning-600" />
            <span className="font-medium">Nova Contestação</span>
            <span className="text-xs text-secondary-500">Iniciar processo</span>
          </Button>
          <Button variant="secondary" className="h-24 flex-col gap-2 p-6" onClick={() => window.location.href = '/reports'}>
            <BarChart2 className="h-8 w-8 text-secondary-600" />
            <span className="font-medium">Gerar Relatório</span>
            <span className="text-xs text-secondary-500">PDF ou Excel</span>
          </Button>
        </div>
      </ChartCard>
    </div>
  )
}