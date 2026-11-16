import { KPICard } from '../../components'
import { formatNumber, formatPercent } from '../../utils/helpers'
import { Plus, Book, Key, Webhook } from 'lucide-react'
import { Button, Card, CardHeader, CardBody } from '../../components'
import { useNavigate } from 'react-router-dom'

export function DeveloperDashboard() {
  const navigate = useNavigate()

  // Mock data - will be replaced with real API calls
  const mockKeys = [
    { id: '1', name: 'Production Key', is_active: true, created_at: '2024-01-15' },
    { id: '2', name: 'Staging Key', is_active: true, created_at: '2024-02-20' },
    { id: '3', name: 'Development Key', is_active: false, created_at: '2024-03-10' },
  ]

  const mockUsage = {
    total_requests: 125430,
    error_rate: 0.023,
    avg_latency_ms: 145,
    daily_series: [
      { date: '2024-01-01', requests: 4200, errors: 12 },
      { date: '2024-01-02', requests: 3800, errors: 8 },
      { date: '2024-01-03', requests: 5100, errors: 15 },
      { date: '2024-01-04', requests: 4500, errors: 10 },
      { date: '2024-01-05', requests: 4900, errors: 11 },
      { date: '2024-01-06', requests: 3200, errors: 5 },
      { date: '2024-01-07', requests: 2800, errors: 3 },
    ],
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Developer Portal</h1>
        <p className="page-subtitle">Gerencie suas integrações API, visualize documentação e monitore uso</p>
      </div>

      {/* KPI Row */}
      <div className="grid-kpi">
        <KPICard
          title="Active Keys"
          value={mockKeys.filter(k => k.is_active).length}
          icon={<Key className="h-5 w-5" />}
          iconBgClass="bg-primary-50"
          iconColorClass="text-primary-600"
        />
        <KPICard
          title="Requests (30d)"
          value={formatNumber(mockUsage.total_requests)}
          icon={<Plus className="h-5 w-5" />}
          iconBgClass="bg-emerald-50"
          iconColorClass="text-emerald-600"
        />
        <KPICard
          title="Error Rate"
          value={formatPercent(mockUsage.error_rate)}
          icon={<Book className="h-5 w-5" />}
          iconBgClass="bg-warning-50"
          iconColorClass="text-warning-600"
        />
        <KPICard
          title="Avg Latency"
          value={`${mockUsage.avg_latency_ms}ms`}
          icon={<Webhook className="h-5 w-5" />}
          iconBgClass="bg-secondary-50"
          iconColorClass="text-secondary-600"
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>Ações Rápidas</CardHeader>
        <CardBody className="flex gap-4 flex-wrap">
          <Button variant="primary" onClick={() => navigate('/developer/keys/new')}>
            <Plus className="h-4 w-4" /> Criar API Key
          </Button>
          <Button variant="secondary" onClick={() => navigate('/developer/docs')}>
            <Book className="h-4 w-4" /> Ver Documentação
          </Button>
          <Button variant="ghost" onClick={() => navigate('/developer/webhooks')}>
            <Webhook className="h-4 w-4" /> Configurar Webhooks
          </Button>
        </CardBody>
      </Card>

      {/* Recent Keys & Usage Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Recent Keys */}
        <Card>
          <CardHeader className="flex justify-between items-center">
            <span>API Keys Recentes</span>
            <Button variant="ghost" size="sm" onClick={() => navigate('/developer/keys')}>
              Ver Todas
            </Button>
          </CardHeader>
          <CardBody>
            <div className="space-y-3">
              {mockKeys.slice(0, 5).map((key) => (
                <div key={key.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-primary-100 flex items-center justify-center">
                      <Key className="h-4 w-4 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-secondary-900">{key.name}</p>
                      <p className="text-sm text-secondary-500">Criada em {new Date(key.created_at).toLocaleDateString('pt-BR')}</p>
                    </div>
                  </div>
                  <span className={`
                    inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                    ${key.is_active
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-secondary-100 text-secondary-700'
                    }
                  `}>
                    {key.is_active ? 'Ativa' : 'Inativa'}
                  </span>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Usage Chart */}
        <Card>
          <CardHeader>Volume de Requisições (7 dias)</CardHeader>
          <CardBody>
            <UsageChart data={mockUsage.daily_series} />
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

// Simple usage chart component
function UsageChart({ data }: { data: { date: string; requests: number; errors: number }[] }) {
  const maxRequests = Math.max(...data.map(d => d.requests), 1)
  const chartHeight = 200

  return (
    <div className="h-[200px] relative">
      <svg className="w-full h-full" viewBox={`0 0 ${data.length * 50} ${chartHeight}`}>
        <defs>
          <linearGradient id="requestsGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <line
            key={ratio}
            x1="0"
            y1={chartHeight * ratio}
            x2={data.length * 50}
            y2={chartHeight * ratio}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        ))}

        {/* Area chart */}
        <path
          d={(data.map((d, i) => {
            const x = i * 50 + 25
            const y = chartHeight - (d.requests / maxRequests) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ') + ` L${data.length * 50 - 25} ${chartHeight} L25 ${chartHeight} Z`)}
          fill="url(#requestsGradient)"
        />

        {/* Line chart */}
        <path
          d={data.map((d, i) => {
            const x = i * 50 + 25
            const y = chartHeight - (d.requests / maxRequests) * (chartHeight * 0.85) - (chartHeight * 0.075)
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
          }).join(' ')}
          stroke="#3b82f6"
          strokeWidth="2"
          fill="none"
        />

        {/* Data points */}
        {data.map((d, i) => (
          <circle
            key={i}
            cx={i * 50 + 25}
            cy={chartHeight - (d.requests / maxRequests) * (chartHeight * 0.85) - (chartHeight * 0.075)}
            r={4}
            fill="#3b82f6"
            stroke="white"
            strokeWidth={2}
          />
        ))}

        {/* X-axis labels */}
        {data.map((d, i) => (
          <text
            key={i}
            x={i * 50 + 25}
            y={chartHeight + 20}
            textAnchor="middle"
            fontSize="10"
            fill="#9ca3af"
          >
            {new Date(d.date).toLocaleDateString('pt-BR', { weekday: 'short' })}
          </text>
        ))}
      </svg>
    </div>
  )
}