'use client'

import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Dot,
} from 'recharts'
import { formatNumber } from '@/utils/helpers'
import { cn } from '@/utils/helpers'
import { useMemo } from 'react'

interface DataPoint {
  date: string
  [key: string]: string | number
}

interface AnalyticsChartProps {
  title: string
  subtitle?: string
  data: DataPoint[]
  dataKey: string
  type: 'line' | 'area'
  color: string
  gradientId?: string
  yAxisFormatter?: (value: number) => string
  tooltipFormatter?: (value: number, name: string) => [string, string]
  tooltipLabelFormatter?: (value: string) => string
  action?: React.ReactNode
  periodOptions?: { label: string; value: string }[]
  currentPeriod?: string
  onPeriodChange?: (period: string) => void
  className?: string
}

const defaultPeriodOptions = [
  { label: '7S', value: '7d' },
  { label: '30D', value: '30d' },
  { label: '90D', value: '90d' },
  { label: '12M', value: '12m' },
]

const ChartTooltip = ({
  active,
  payload,
  label,
  formatter,
  labelFormatter,
}: {
  active?: boolean
  payload?: Array<{ value: number; name: string; color: string }>
  label?: string
  formatter?: (value: number, name: string) => [string, string]
  labelFormatter?: (value: string) => string
}) => {
  if (!active || !payload || !payload.length) return null

  const item = payload[0]
  const formattedValue = formatter ? formatter(item.value, item.name)[0] : formatNumber(item.value)
  const formattedLabel = labelFormatter ? labelFormatter(label || '') : new Date(label || '').toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  // Calculate week-over-week change if we have enough data
  // This is a placeholder - in real implementation you'd compare with previous period
  const change = '+12.5%'

  return (
    <div className="chart-tooltip">
      <p className="font-medium text-white mb-1">{formattedLabel}</p>
      <div className="flex items-center gap-2 text-sm">
        <span className="font-mono text-primary-300">{formattedValue}</span>
        <span className="text-emerald-400">{change} vs semana anterior</span>
      </div>
    </div>
  )
}

const CustomDot = ({ cx, cy, r, fill, stroke, strokeWidth, ...props }: any) => {
  if (cx === undefined || cy === undefined) return null
  return (
    <Dot
      cx={cx}
      cy={cy}
      r={r || 5}
      fill={fill}
      stroke={stroke || '#ffffff'}
      strokeWidth={strokeWidth || 2}
      {...props}
    />
  )
}

export function AnalyticsChart({
  title,
  subtitle,
  data,
  dataKey,
  type,
  color,
  gradientId,
  yAxisFormatter,
  tooltipFormatter,
  tooltipLabelFormatter,
  action,
  periodOptions = defaultPeriodOptions,
  currentPeriod = '30d',
  onPeriodChange,
  className,
}: AnalyticsChartProps) {
  const chartContent = useMemo(() => {
    if (type === 'area') {
      return (
        <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
          {gradientId && (
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
          )}
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e2e8f0"
            vertical={false}
            horizontal={true}
          />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'inherit' }}
            tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' })}
            axisLine={{ stroke: '#e2e8f0' }}
            tickLine={false}
            dy={8}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'inherit', fontVariant: 'tabular-nums' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={yAxisFormatter}
            width={60}
          />
          <Tooltip
            content={<ChartTooltip formatter={tooltipFormatter} labelFormatter={tooltipLabelFormatter} />}
            wrapperStyle={{ outline: 'none' }}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            fill={gradientId ? `url(#${gradientId})` : color}
            fillOpacity={gradientId ? 1 : 0.1}
          />
        </AreaChart>
      )
    }

    return (
      <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="#e2e8f0"
          vertical={false}
          horizontal={true}
        />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'inherit' }}
          tickFormatter={(value) => new Date(value).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' })}
          axisLine={{ stroke: '#e2e8f0' }}
          tickLine={false}
          dy={8}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'inherit', fontVariant: 'tabular-nums' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={yAxisFormatter}
          width={60}
        />
        <Tooltip
          content={<ChartTooltip formatter={tooltipFormatter} labelFormatter={tooltipLabelFormatter} />}
          wrapperStyle={{ outline: 'none' }}
        />
        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          strokeWidth={2}
          dot={<CustomDot fill={color} stroke="#ffffff" strokeWidth={2} r={5} />}
          activeDot={{ r: 7, fill: color, stroke: '#ffffff', strokeWidth: 2 }}
        />
      </LineChart>
    )
  }, [data, dataKey, type, color, gradientId, yAxisFormatter, tooltipFormatter, tooltipLabelFormatter])

  return (
    <div className={cn('card card-hover h-full', className)}>
      <div className="card-header flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-secondary-900">{title}</h3>
          {subtitle && <p className="text-sm text-secondary-500">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          {periodOptions.length > 1 && (
            <div className="flex items-center gap-1 bg-secondary-50 rounded-lg p-0.5" role="group" aria-label="Período do gráfico">
              {periodOptions.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => onPeriodChange?.(opt.value)}
                  className={cn(
                    'px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-150',
                    currentPeriod === opt.value
                      ? 'bg-white text-primary-700 shadow-sm'
                      : 'text-secondary-500 hover:text-secondary-700'
                  )}
                  aria-pressed={currentPeriod === opt.value}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          )}
          {action}
        </div>
      </div>
      <div className="card-body pt-0">
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">{chartContent}</ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}