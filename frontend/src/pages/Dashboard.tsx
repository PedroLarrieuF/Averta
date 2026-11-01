import { useQuery } from '@tanstack/react-query'
import { api, handleApiError } from '../services/api'
import { DashboardKPIs } from '../types'
import { Card, CardBody, CardHeader } from '../components/Card'
import { Badge } from '../components/Badge'
import { cn, formatCurrency, formatNumber, formatPercent, formatRelativeTime } from '../utils/helpers'
import {
  FileText,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  BarChart2,
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

// Mock data for development - replace with actual API calls
const mockKPIs: DashboardKPIs = {
  totalDiscrepancies: 1247,
  openDiscrepancies: 342,
  contestedAmount: 2847500,
  recoveredAmount: 1923400,
  recoveryRate: 67.5,
  documentsProcessed: 8934,
  documentsPending: 156,
  avgResolutionTime: 12.5,
  trends: {
    discrepancies: [
      { date: '2024-01-01', count: 45 },
      { date: '2024-01-08', count: 52 },
      { date: '2024-01-15', count: 38 },
      { date: '2024-01-22', count: 61 },
      { date: '2024-01-29', count: 47 },
      { date: '2024-02-05', count: 55 },
      { date: '2024-02-12', count: 49 },
    ],
    recovered: [
      { date: '2024-01-01', amount: 120000 },
      { date: '2024-01-08', amount: 180000 },
      { date: '2024-01-15', amount: 95000 },
      { date: '2024-01-22', amount: 210000 },
      { date: '2024-01-29', amount: 165000 },
      { date: '2024-02-05', amount: 190000 },
      { date: '2024-02-12', amount: 175000 },
    ],
  },
}

function KPICard({
  title,
  value,
  trend,
  trendUp,
  icon: Icon,
  iconColor,
  bgColor,
}: {
  title: string
  value: string | number
  trend?: string
  trendUp?: boolean
  icon: React.ComponentType<{ className?: string }>
  iconColor: string
  bgColor: string
}) {
  return (
    <Card className="kpi-card">
      <div className="flex items-start justify-between">
        <div>
          <p className="kpi-label">{title}</p>
          <p className="kpi-value">{value}</p>
          {trend && (
            <div className="kpi-trend">
              <span className={cn(trendUp ? 'kpi-trend-up' : 'kpi-trend-down')}>
                {trendUp ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                {trend}
              </span>
            </div>
          )}
        </div>
        <div className={cn('p-3 rounded-xl', bgColor)}>
          <Icon className={cn('h-6 w-6', iconColor)} />
        </div>
      </div>
    </Card>
  )
}

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
    <Card className="h-full">
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
  // In production, replace with actual API call:
  // const { data: kpis, isLoading } = useQuery({
  //   queryKey: ['dashboard', 'kpis'],
  //   queryFn: () => api.get<DashboardKPIs>('/reports/dashboard').then(r => r.data),
  // })

  const { data: kpis = mockKPIs, isLoading } = useQuery({
    queryKey: ['dashboard', 'kpis'],
    queryFn: async () => {
      // Simulate API delay
      await new Promise(r => setTimeout(r, 500))
      return mockKPIs
    },
    staleTime: 1000 * 60 * 5,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid-kpi">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="kpi-card">
              <div className="h-4 bg-secondary-200 rounded w-3/4 mb-2" />
              <div className="h-8 bg-secondary-200 rounded w-1/2" />
            </Card>
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Visão geral da auditoria de fretes e recuperação de valores</p>
      </div>

      {/* KPI Grid */}
      <div className="grid-kpi">
        <KPICard
          title="Total de Discrepâncias"
          value={formatNumber(kpis.totalDiscrepancies)}
          trend="+12% vs mês anterior"
          trendUp={false}
          icon={FileText}
          iconColor="text-primary-600"
          bgColor="bg-primary-50"
        />
        <KPICard
          title="Discrepâncias Abertas"
          value={formatNumber(kpis.openDiscrepancies)}
          trend="32 aguardando análise"
          trendUp={false}
          icon={AlertTriangle}
          iconColor="text-warning-600"
          bgColor="bg-warning-50"
        />
        <KPICard
          title="Valor Contestado"
          value={formatCurrency(kpis.contestedAmount)}
          trend="+8% vs mês anterior"
          trendUp={true}
          icon={DollarSign}
          iconColor="text-success-600"
          bgColor="bg-success-50"
        />
        <KPICard
          title="Taxa de Recuperação"
          value={formatPercent(kpis.recoveryRate)}
          trend="+2.3pp vs mês anterior"
          trendUp={true}
          icon={TrendingUp}
          iconColor="text-primary-600"
          bgColor="bg-primary-50"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Discrepancies Trend */}
        <ChartCard
          title="Discrepâncias por Semana"
          subtitle="Últimas 7 semanas"
          action={
            <Button variant="ghost" size="sm">
              <BarChart2 className="h-4 w-4 mr-1" />
              Ver relatório completo
            </Button>
          }
        >
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={kpis.trends.discrepancies}>
                <defs>
                  <linearGradient id="colorDiscrepancies" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' })}
                  axisLine={{ stroke: '#e2e8f0' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                  }}
                  formatter={(value: number) => [formatNumber(value), 'Discrepâncias']}
                  labelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}
                />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorDiscrepancies)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Recovery Trend */}
        <ChartCard
          title="Valores Recuperados"
          subtitle="Últimas 7 semanas"
          action={
            <Button variant="ghost" size="sm">
              <DollarSign className="h-4 w-4 mr-1" />
              Ver detalhes
            </Button>
          }
        >
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={kpis.trends.recovered}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' })}
                  axisLine={{ stroke: '#e2e8f0' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value) => `R$ ${(value/1000000).toFixed(1)}M`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                  }}
                  formatter={(value: number) => [formatCurrency(value), 'Recuperado']}
                  labelFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })}
                />
                <Line
                  type="monotone"
                  dataKey="amount"
                  stroke="#22c55e"
                  strokeWidth={3}
                  dot={{ fill: '#22c55e', strokeWidth: 2, r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Summary Cards Row */}
      <div className="grid gap-4 lg:grid-cols-3">
        <ChartCard title="Documentos Processados" subtitle="Este mês">
          <div className="flex items-center justify-between">
            <div className="text-center">
              <p className="text-4xl font-bold text-secondary-900">{formatNumber(kpis.documentsProcessed)}</p>
              <p className="text-sm text-secondary-500">Total processados</p>
            </div>
            <div className="text-right">
              <Badge variant="primary">{formatNumber(kpis.documentsPending)} pendentes</Badge>
              <p className="text-xs text-secondary-500 mt-1">Aguardando processamento</p>
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Valor Recuperado Total" subtitle="Acumulado">
          <div className="flex items-center justify-between">
            <div className="text-center">
              <p className="text-4xl font-bold text-success-600">{formatCurrency(kpis.recoveredAmount)}</p>
              <p className="text-sm text-secondary-500">De {formatCurrency(kpis.contestedAmount)} contestados</p>
            </div>
            <div className="text-right">
              <Badge variant="success">{formatPercent(kpis.recoveryRate)} de recuperação</Badge>
              <p className="text-xs text-secondary-500 mt-1">Taxa de sucesso</p>
            </div>
          </div>
        </ChartCard>

        <ChartCard title="Tempo Médio de Resolução" subtitle="Em dias úteis">
          <div className="flex items-center justify-between">
            <div className="text-center">
              <p className="text-4xl font-bold text-secondary-900">{kpis.avgResolutionTime}</p>
              <p className="text-sm text-secondary-500">Dias úteis</p>
            </div>
            <div className="text-right">
              <Badge variant="secondary">Meta: {'<'} 10 dias</Badge>
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
            <RefreshCw className="h-8 w-8 text-success-600" />
            <span className="font-medium">Upload Documentos</span>
            <span className="text-xs text-secondary-500">XML CTe/NFe</span>
          </Button>
          <Button variant="secondary" className="h-24 flex-col gap-2 p-6" onClick={() => window.location.href = '/contests'}>
            <CheckCircle className="h-8 w-8 text-warning-600" />
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