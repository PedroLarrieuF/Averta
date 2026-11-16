import { useState } from 'react'
import { formatNumber, formatPercent } from '../../utils/helpers'
import { Download, TrendingUp, AlertCircle, Shield } from 'lucide-react'
import { Button, Card, CardHeader, CardBody, Badge, Select, SelectTrigger, SelectValue, SelectContent, SelectItem, KPICard } from '../../components'

interface UsageMetrics {
  total_requests: number
  successful_requests: number
  failed_requests: number
  error_rate: number
  avg_latency_ms: number
  p95_latency_ms: number
  p99_latency_ms: number
  daily_series: DailyMetric[]
  endpoint_breakdown: EndpointMetric[]
  status_code_breakdown: StatusCodeMetric[]
}

interface DailyMetric {
  date: string
  requests: number
  errors: number
  avg_latency: number
}

interface EndpointMetric {
  endpoint: string
  method: string
  requests: number
  errors: number
  avg_latency: number
}

interface StatusCodeMetric {
  code: number
  count: number
}

export function DeveloperAnalytics() {
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d')

  // Mock data - will be replaced with real API calls
  const mockMetrics: UsageMetrics = {
    total_requests: 125430,
    successful_requests: 122540,
    failed_requests: 2890,
    error_rate: 0.023,
    avg_latency_ms: 145,
    p95_latency_ms: 320,
    p99_latency_ms: 580,
    daily_series: [
      { date: '2024-01-01', requests: 4200, errors: 12, avg_latency: 138 },
      { date: '2024-01-02', requests: 3800, errors: 8, avg_latency: 142 },
      { date: '2024-01-03', requests: 5100, errors: 15, avg_latency: 156 },
      { date: '2024-01-04', requests: 4500, errors: 10, avg_latency: 134 },
      { date: '2024-01-05', requests: 4900, errors: 11, avg_latency: 148 },
      { date: '2024-01-06', requests: 3200, errors: 5, avg_latency: 125 },
      { date: '2024-01-07', requests: 2800, errors: 3, avg_latency: 118 },
      { date: '2024-01-08', requests: 4100, errors: 9, avg_latency: 141 },
      { date: '2024-01-09', requests: 4600, errors: 12, avg_latency: 152 },
      { date: '2024-01-10', requests: 5200, errors: 14, avg_latency: 160 },
      { date: '2024-01-11', requests: 3800, errors: 7, avg_latency: 133 },
      { date: '2024-01-12', requests: 3400, errors: 4, avg_latency: 122 },
      { date: '2024-01-13', requests: 4000, errors: 8, avg_latency: 139 },
      { date: '2024-01-14', requests: 4700, errors: 11, avg_latency: 147 },
      { date: '2024-01-15', requests: 5300, errors: 16, avg_latency: 165 },
      { date: '2024-01-16', requests: 3900, errors: 6, avg_latency: 128 },
      { date: '2024-01-17', requests: 3500, errors: 5, avg_latency: 124 },
      { date: '2024-01-18', requests: 4200, errors: 9, avg_latency: 143 },
      { date: '2024-01-19', requests: 4800, errors: 10, avg_latency: 150 },
      { date: '2024-01-20', requests: 5400, errors: 13, avg_latency: 158 },
      { date: '2024-01-21', requests: 3700, errors: 7, avg_latency: 131 },
      { date: '2024-01-22', requests: 3300, errors: 4, avg_latency: 119 },
      { date: '2024-01-23', requests: 4100, errors: 8, avg_latency: 140 },
      { date: '2024-01-24', requests: 4900, errors: 12, avg_latency: 154 },
      { date: '2024-01-25', requests: 5500, errors: 15, avg_latency: 162 },
      { date: '2024-01-26', requests: 4000, errors: 6, avg_latency: 129 },
      { date: '2024-01-27', requests: 3600, errors: 5, avg_latency: 126 },
      { date: '2024-01-28', requests: 4300, errors: 10, avg_latency: 145 },
      { date: '2024-01-29', requests: 5000, errors: 11, avg_latency: 151 },
      { date: '2024-01-30', requests: 5600, errors: 14, avg_latency: 167 },
    ],
    endpoint_breakdown: [
      { endpoint: '/api/v1/discrepancies', method: 'GET', requests: 35420, errors: 210, avg_latency: 180 },
      { endpoint: '/api/v1/documents', method: 'POST', requests: 28100, errors: 560, avg_latency: 420 },
      { endpoint: '/api/v1/contests', method: 'GET', requests: 22300, errors: 180, avg_latency: 145 },
      { endpoint: '/api/v1/contracts', method: 'GET', requests: 18900, errors: 95, avg_latency: 120 },
      { endpoint: '/api/v1/reports/dashboard', method: 'GET', requests: 12400, errors: 45, avg_latency: 280 },
      { endpoint: '/api/v1/clients', method: 'GET', requests: 8300, errors: 20, avg_latency: 95 },
    ],
    status_code_breakdown: [
      { code: 200, count: 115400 },
      { code: 201, count: 7140 },
      { code: 400, count: 1240 },
      { code: 401, count: 890 },
      { code: 403, count: 320 },
      { code: 404, count: 440 },
      { code: 500, count: 210 },
      { code: 503, count: 30 },
    ],
  }

  // Calculate period-specific data
  const periodDays = period === '7d' ? 7 : period === '30d' ? 30 : 90
  const recentData = mockMetrics.daily_series.slice(-periodDays)

  return (
    <div className="space-y-6">
      <div className="page-header flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Analytics de Uso</h1>
          <p className="page-subtitle">Monitore o consumo da API, latência e erros</p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm text-secondary-500">Período:</label>
          <Select value={period} onValueChange={(value: '7d' | '30d' | '90d') => setPeriod(value)}>
            <SelectTrigger className="w-[160px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Últimos 7 dias</SelectItem>
              <SelectItem value="30d">Últimos 30 dias</SelectItem>
              <SelectItem value="90d">Últimos 90 dias</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="secondary" className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Exportar CSV
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-kpi">
        <KPICard
          title="Total de Requisições"
          value={formatNumber(mockMetrics.total_requests)}
          trend="+12.5% vs período anterior"
          trendUp={true}
          icon={<TrendingUp className="h-5 w-5" />}
          iconBgClass="bg-primary-50"
          iconColorClass="text-primary-600"
        />
        <KPICard
          title="Taxa de Sucesso"
          value={formatPercent(1 - mockMetrics.error_rate)}
          trend="-0.3% vs período anterior"
          trendUp={false}
          icon={<Shield className="h-5 w-5" />}
          iconBgClass="bg-emerald-50"
          iconColorClass="text-emerald-600"
        />
        <KPICard
          title="Latência Média"
          value={`${mockMetrics.avg_latency_ms}ms`}
          trend="+5.2% vs período anterior"
          trendUp={false}
          icon={<TrendingUp className="h-5 w-5" />}
          iconBgClass="bg-warning-50"
          iconColorClass="text-warning-600"
        />
        <KPICard
          title="P95 Latência"
          value={`${mockMetrics.p95_latency_ms}ms`}
          trend="+8.1% vs período anterior"
          trendUp={false}
          icon={<AlertCircle className="h-5 w-5" />}
          iconBgClass="bg-rose-50"
          iconColorClass="text-rose-600"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Requests Volume Chart */}
        <Card>
          <CardHeader>Volume de Requisições</CardHeader>
          <CardBody>
            <RequestsChart data={recentData} />
          </CardBody>
        </Card>

        {/* Latency Chart */}
        <Card>
          <CardHeader>Latência (Média / P95 / P99)</CardHeader>
          <CardBody>
            <LatencyChart data={recentData} p95={mockMetrics.p95_latency_ms} p99={mockMetrics.p99_latency_ms} />
          </CardBody>
        </Card>
      </div>

      {/* Error Rate & Status Codes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Error Rate Chart */}
        <Card>
          <CardHeader>Taxa de Erro</CardHeader>
          <CardBody>
            <ErrorRateChart data={recentData} />
          </CardBody>
        </Card>

        {/* Status Codes */}
        <Card>
          <CardHeader>Distribuição de Status Codes</CardHeader>
          <CardBody>
            <StatusCodesChart data={mockMetrics.status_code_breakdown} />
          </CardBody>
        </Card>
      </div>

      {/* Endpoint Breakdown */}
      <Card>
        <CardHeader>Top Endpoints por Volume</CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th className="w-48">Endpoint</th>
                  <th className="w-24 text-center">Método</th>
                  <th className="text-right">Requisições</th>
                  <th className="text-right">Erros</th>
                  <th className="text-right">Taxa de Erro</th>
                  <th className="text-right">Latência Média</th>
                </tr>
              </thead>
              <tbody>
                {mockMetrics.endpoint_breakdown.map((ep, i) => (
                  <tr key={i}>
                    <td className="font-mono text-sm text-secondary-900">{ep.endpoint}</td>
                    <td className="text-center">
                      <Badge variant={ep.method === 'GET' ? 'success' : ep.method === 'POST' ? 'primary' : 'secondary'}>
                        {ep.method}
                      </Badge>
                    </td>
                    <td className="text-right font-mono">{formatNumber(ep.requests)}</td>
                    <td className="text-right font-mono text-rose-600">{formatNumber(ep.errors)}</td>
                    <td className="text-right">
                      <Badge variant={ep.errors / ep.requests > 0.05 ? 'danger' : 'success'}>
                        {formatPercent(ep.errors / ep.requests)}
                      </Badge>
                    </td>
                    <td className="text-right font-mono">{ep.avg_latency}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Health Indicators */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <HealthIndicator
          label="Uptime"
          value="99.97%"
          icon={TrendingUp}
          variant="success"
          description="Últimos 30 dias"
        />
        <HealthIndicator
          label="Disponibilidade da API"
          value="Healthy"
          icon={Shield}
          variant="success"
          description="Todos os endpoints operacionais"
        />
        <HealthIndicator
          label="Taxa de Erro Atual"
          value={`${(mockMetrics.error_rate * 100).toFixed(2)}%`}
          icon={AlertCircle}
          variant={mockMetrics.error_rate > 0.05 ? 'danger' : 'warning'}
          description="Limite de alerta: 5%"
        />
      </div>
    </div>
  )
}

// Chart Components
function RequestsChart({ data }: { data: DailyMetric[] }) {
  const maxRequests = Math.max(...data.map(d => d.requests), 1)
  const chartHeight = 200
  const width = data.length * 40

  return (
    <div className="h-[200px] relative">
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${chartHeight}`}>
        <defs>
          <linearGradient id="reqGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>

        {/* Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <line key={ratio} x1="0" y1={chartHeight * ratio} x2={width} y2={chartHeight * ratio} stroke="#e5e7eb" strokeWidth="1" />
        ))}

        {/* Area */}
        <path
          d={(data.map((d, i) => {
            const x = i * 40 + 20
            const y = chartHeight - (d.requests / maxRequests) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ') + ` L${width - 20} ${chartHeight} L20 ${chartHeight} Z`)}
          fill="url(#reqGradient)"
        />

        {/* Line */}
        <path
          d={data.map((d, i) => {
            const x = i * 40 + 20
            const y = chartHeight - (d.requests / maxRequests) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ')}
          stroke="#3b82f6" strokeWidth="2" fill="none"
        />

        {/* Points */}
        {data.map((d, i) => (
          <circle key={i} cx={i * 40 + 20} cy={chartHeight - (d.requests / maxRequests) * (chartHeight * 0.85) - (chartHeight * 0.075)} r={3} fill="#3b82f6" stroke="white" strokeWidth={1.5} />
        ))}
      </svg>
    </div>
  )
}

function LatencyChart({ data, p95, p99 }: { data: DailyMetric[]; p95: number; p99: number }) {
  const maxLatency = Math.max(...data.map(d => d.avg_latency), p95, p99, 1)
  const chartHeight = 200
  const width = data.length * 40

  return (
    <div className="h-[200px] relative">
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${chartHeight}`}>
        {/* P99 Reference Line */}
        <line x1="0" y1={chartHeight - (p99 / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075)} x2={width} y2={chartHeight - (p99 / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075)} stroke="#ef4444" strokeWidth="1" strokeDasharray="4,4" opacity={0.5} />
        <text x={width - 5} y={chartHeight - (p99 / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075) - 5} textAnchor="end" fontSize="9" fill="#ef4444" opacity={0.7}>P99</text>

        {/* P95 Reference Line */}
        <line x1="0" y1={chartHeight - (p95 / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075)} x2={width} y2={chartHeight - (p95 / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075)} stroke="#f59e0b" strokeWidth="1" strokeDasharray="4,4" opacity={0.5} />
        <text x={width - 5} y={chartHeight - (p95 / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075) - 5} textAnchor="end" fontSize="9" fill="#f59e0b" opacity={0.7}>P95</text>

        {/* Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <line key={ratio} x1="0" y1={chartHeight * ratio} x2={width} y2={chartHeight * ratio} stroke="#e5e7eb" strokeWidth="1" />
        ))}

        {/* Avg Latency Line */}
        <path
          d={data.map((d, i) => {
            const x = i * 40 + 20
            const y = chartHeight - (d.avg_latency / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ')}
          stroke="#3b82f6" strokeWidth="2" fill="none"
        />

        {/* Points */}
        {data.map((d, i) => (
          <circle key={i} cx={i * 40 + 20} cy={chartHeight - (d.avg_latency / maxLatency) * (chartHeight * 0.85) - (chartHeight * 0.075)} r={3} fill="#3b82f6" stroke="white" strokeWidth={1.5} />
        ))}
      </svg>
    </div>
  )
}

function ErrorRateChart({ data }: { data: DailyMetric[] }) {
  const maxErrorRate = Math.max(...data.map(d => d.errors / Math.max(d.requests, 1)), 0.01)
  const chartHeight = 200
  const width = data.length * 40

  return (
    <div className="h-[200px] relative">
      <svg className="w-full h-full" viewBox={`0 0 ${width} ${chartHeight}`}>
        <defs>
          <linearGradient id="errGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
          </linearGradient>
        </defs>

        {/* Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <line key={ratio} x1="0" y1={chartHeight * ratio} x2={width} y2={chartHeight * ratio} stroke="#e5e7eb" strokeWidth="1" />
        ))}

        {/* Area */}
        <path
          d={(data.map((d, i) => {
            const errorRate = d.errors / Math.max(d.requests, 1)
            const x = i * 40 + 20
            const y = chartHeight - (errorRate / maxErrorRate) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ') + ` L${width - 20} ${chartHeight} L20 ${chartHeight} Z`)}
          fill="url(#errGradient)"
        />

        {/* Line */}
        <path
          d={data.map((d, i) => {
            const errorRate = d.errors / Math.max(d.requests, 1)
            const x = i * 40 + 20
            const y = chartHeight - (errorRate / maxErrorRate) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ')}
          stroke="#ef4444" strokeWidth="2" fill="none"
        />

        {/* Points */}
        {data.map((d, i) => {
          const errorRate = d.errors / Math.max(d.requests, 1)
          return (
            <circle key={i} cx={i * 40 + 20} cy={chartHeight - (errorRate / maxErrorRate) * (chartHeight * 0.85) - (chartHeight * 0.075)} r={3} fill="#ef4444" stroke="white" strokeWidth={1.5} />
          )
        })}
      </svg>
    </div>
  )
}

function StatusCodesChart({ data }: { data: StatusCodeMetric[] }) {
  const total = data.reduce((sum, d) => sum + d.count, 0)
  const colors: Record<number, string> = {
    200: '#22c55e', 201: '#16a34a',
    400: '#f59e0b', 401: '#f97316', 403: '#fb923c', 404: '#fbbf24',
    500: '#ef4444', 503: '#dc2626',
  }

  return (
    <div className="h-[200px] flex items-end justify-around px-4">
      {data.map((d) => (
        <div key={d.code} className="flex flex-col items-center">
          <div
            className="w-8 rounded-t transition-all hover:opacity-80"
            style={{
              height: `${(d.count / total) * 180}px`,
              backgroundColor: colors[d.code] || '#6b7280',
            }}
            title={`${d.code}: ${d.count} (${((d.count / total) * 100).toFixed(1)}%)`}
          />
          <span className="text-xs font-mono text-secondary-500 mt-2">{d.code}</span>
          <span className="text-xs text-secondary-400">{((d.count / total) * 100).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  )
}

function HealthIndicator({ label, value, icon: Icon, variant, description }: {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  variant: 'success' | 'warning' | 'danger'
  description: string
}) {
  const variantStyles = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    warning: 'bg-warning-50 border-warning-200 text-warning-700',
    danger: 'bg-rose-50 border-rose-200 text-rose-700',
  }

  return (
    <Card className={`${variantStyles[variant]} p-4 border`}>
      <div className="flex items-center gap-3">
        <Icon className="h-6 w-6" />
        <div>
          <p className="text-sm font-medium">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-xs text-secondary-500">{description}</p>
        </div>
      </div>
    </Card>
  )
}