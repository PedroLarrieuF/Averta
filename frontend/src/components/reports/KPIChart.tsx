import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'
import { formatCurrency, formatDate } from '@/utils/helpers'

// Color palette for charts
const CHART_COLORS = [
  '#3B82F6', // primary
  '#10B981', // success
  '#F59E0B', // warning
  '#EF4444', // danger
  '#8B5CF6', // purple
  '#EC4899', // pink
  '#06B6D4', // cyan
  '#84CC16', // lime
]

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#EF4444',
  HIGH: '#F59E0B',
  MEDIUM: '#3B82F6',
  LOW: '#10B981',
}

interface TimeSeriesData {
  date: string
  count: number
  value: number
}

interface TopCarrierData {
  carrier_name: string
  recovered: number
  count: number
}

interface TopRuleData {
  rule_code: string
  count: number
  total_value: number
}

interface SeverityData {
  severity: string
  count: number
}

// Line/Area Chart - Time Series
export function TimeSeriesChart({ data }: { data: TimeSeriesData[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center bg-secondary-50 rounded-lg">
        <p className="text-secondary-500">Nenhum dado para exibir</p>
      </div>
    )
  }

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => formatDate(value, { day: '2-digit', month: '2-digit' })}
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
            labelFormatter={(value) => formatDate(value, { day: '2-digit', month: '2-digit', year: 'numeric' })}
            formatter={(value: number, name: string) => {
              if (name === 'value') return [formatCurrency(value), 'Valor']
              if (name === 'count') return [value.toString(), 'Quantidade']
              return [value.toString(), name]
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#3B82F6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorArea)"
            name="Valor"
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#10B981"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorCount)"
            name="Quantidade"
            yAxisId="right"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// Bar Chart - Top Carriers
export function TopCarriersChart({ data }: { data: TopCarrierData[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center bg-secondary-50 rounded-lg">
        <p className="text-secondary-500">Nenhum dado para exibir</p>
      </div>
    )
  }

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => formatCurrency(value)}
          />
          <YAxis
            type="category"
            dataKey="carrier_name"
            tick={{ fontSize: 11, fill: '#374151' }}
            axisLine={false}
            tickLine={false}
            width={120}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number) => [formatCurrency(value), 'Valor Recuperado']}
            labelFormatter={(label) => label}
          />
          <Legend />
          <Bar
            dataKey="recovered"
            fill="#3B82F6"
            radius={[0, 4, 4, 0]}
            maxBarSize={30}
            name="Valor Recuperado"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Pie Chart - Top Rules
export function TopRulesChart({ data }: { data: TopRuleData[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center bg-secondary-50 rounded-lg">
        <p className="text-secondary-500">Nenhum dado para exibir</p>
      </div>
    )
  }

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="count"
            nameKey="rule_code"
            label={({ rule_code, percent }) => (
              <span style={{ fontSize: 11, fontWeight: 500 }}>
                {rule_code} {(percent * 100).toFixed(1)}%
              </span>
            )}
            labelLine={false}
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
            formatter={(value: number, name: string) => {
              const item = data.find((d) => d.rule_code === name)
              return [item ? formatCurrency(item.total_value) : value.toString(), 'Valor Total']
            }}
            labelFormatter={(label) => label}
          />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            iconType="circle"
            iconSize={8}
            formatter={(value) => {
              const item = data.find((d) => d.rule_code === value)
              return item ? `${value} (${item.count} ocorrências)` : value
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

// Stacked Bar Chart - Severity Distribution
export function SeverityDistributionChart({ data }: { data: SeverityData[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-[300px] flex items-center justify-center bg-secondary-50 rounded-lg">
        <p className="text-secondary-500">Nenhum dado para exibir</p>
      </div>
    )
  }

  // Transform data for stacked bar (monthly breakdown would need different structure)
  // For now, show as regular bar chart
  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="severity"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Legend />
          <Bar
            dataKey="count"
            fill="#3B82F6"
            radius={[4, 4, 0, 0]}
            maxBarSize={50}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.severity] || CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Generic KPI Chart wrapper
export function KPIChart({
  type,
  data,
}: {
  type: 'timeseries' | 'topcarriers' | 'toprules' | 'severity'
  data: TimeSeriesData[] | TopCarrierData[] | TopRuleData[] | SeverityData[]
}) {
  switch (type) {
    case 'timeseries':
      return <TimeSeriesChart data={data as TimeSeriesData[]} />
    case 'topcarriers':
      return <TopCarriersChart data={data as TopCarrierData[]} />
    case 'toprules': {
      const chartData = data as TopRuleData[]
      return <TopRulesChart data={chartData} />
    }
    case 'severity': {
      const chartData = data as SeverityData[]
      return <SeverityDistributionChart data={chartData} />
    }
    default:
      return null
  }
}