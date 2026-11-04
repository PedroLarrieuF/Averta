---
id: 42
title: "Developer Portal: Usage Analytics Dashboard"
priority: high
type: feature
agent: frontend
sprint: 2
estimate: M
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 42: Developer Portal - Usage Analytics Dashboard

## Contexto
Dashboard de analytics para desenvolvedores monitorarem uso da API: volume, latência, erros, endpoints mais usados, geografia.

## Tasks

### 1. DeveloperAnalyticsPage (`src/pages/developer/DeveloperAnalytics.tsx`)
```tsx
export function DeveloperAnalyticsPage() {
  const [range, setRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [keyFilter, setKeyFilter] = useState<string>('all');
  
  const { data: keys } = useApiKeys();
  const { data: overview } = useUsageOverview(range, keyFilter);
  const { data: endpoints } = useEndpointBreakdown(range, keyFilter);
  const { data: errors } = useErrorBreakdown(range, keyFilter);
  const { data: latency } = useLatencyDistribution(range, keyFilter);

  return (
    <div className="space-y-6">
      <PageHeader 
        title="API Analytics" 
        subtitle="Monitor your API usage and performance"
        actions={
          <div className="flex items-center gap-4">
            <Select value={range} onChange={setRange} options={[
              { value: '7d', label: 'Last 7 days' },
              { value: '30d', label: 'Last 30 days' },
              { value: '90d', label: 'Last 90 days' }
            ]} className="w-48" />
            <Select value={keyFilter} onChange={setKeyFilter} options={[
              { value: 'all', label: 'All Keys' },
              ...(keys?.map(k => ({ value: k.id, label: k.name })) || [])
            ]} className="w-56" />
          </div>
        }
      />

      {/* KPI Row */}
      <div className="grid-kpi">
        <KPICard 
          label="Total Requests" 
          value={formatNumber(overview?.total_requests)} 
          trend={overview?.requests_trend}
          trendLabel="vs previous period"
        />
        <KPICard 
          label="Error Rate" 
          value={formatPercent(overview?.error_rate)} 
          variant={overview?.error_rate > 5 ? 'danger' : 'success'}
          trend={overview?.error_trend}
        />
        <KPICard 
          label="Avg Latency (p50)" 
          value={`${overview?.avg_latency_ms}ms`} 
          trend={overview?.latency_trend}
        />
        <KPICard 
          label="P99 Latency" 
          value={`${overview?.p99_latency_ms}ms`} 
        />
      </div>

      {/* Charts Row 1: Volume + Errors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="h-[400px]">
          <CardHeader className="flex justify-between">
            <span>Request Volume</span>
            <Tooltip content="Requests per day">
              <HelpIcon className="text-gray-400 cursor-help" />
            </Tooltip>
          </CardHeader>
          <CardBody>
            <AreaChart 
              data={overview?.daily_volume} 
              xKey="date" 
              yKeys={['requests', 'errors']}
              colors={['#3b82f6', '#ef4444']}
              height={320}
            />
          </CardBody>
        </Card>

        <Card className="h-[400px]">
          <CardHeader>Error Breakdown</CardHeader>
          <CardBody>
            <PieChart 
              data={errors?.by_status_code} 
              nameKey="status" 
              valueKey="count"
              colors={['#fef08a', '#fecaca', '#fca5a5', '#f87171', '#ef4444']}
              height={320}
            />
          </CardBody>
        </Card>
      </div>

      {/* Charts Row 2: Latency Distribution + Endpoints */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="h-[400px]">
          <CardHeader>Latency Distribution</CardHeader>
          <CardBody>
            <BarChart 
              data={latency?.buckets} 
              xKey="bucket" 
              yKeys={['count']}
              height={320}
            />
          </CardBody>
        </Card>

        <Card className="h-[400px]">
          <CardHeader>Top Endpoints</CardHeader>
          <CardBody>
            <EndpointTable data={endpoints?.top_20} />
          </CardBody>
        </Card>
      </div>

      {/* Geographic Distribution (if available) */}
      {overview?.geo_distribution && (
        <Card>
          <CardHeader>Geographic Distribution</CardHeader>
          <CardBody>
            <GeoChart data={overview.geo_distribution} />
          </CardBody>
        </Card>
      )}
    </div>
  );
}
```

### 2. Chart Components (reusing UI Agent components)
- `AreaChart` - Request volume over time (dual line: requests + errors)
- `PieChart` - Error breakdown by status code
- `BarChart` - Latency histogram (buckets: <50ms, 50-100ms, 100-200ms, 200-500ms, 500-1000ms, >1000ms)
- `EndpointTable` - Table com: endpoint, method, requests, avg latency, error rate, p99
- `GeoChart` - Mapa mundi ou tabela por país (opcional)

### 3. Hooks (`src/hooks/useDeveloperAnalytics.ts`)
```typescript
export function useUsageOverview(range: string, keyFilter: string) {
  return useQuery({
    queryKey: ['usageOverview', range, keyFilter],
    queryFn: () => api.get<UsageOverview>('/developer/analytics/overview', { 
      params: { range, key_id: keyFilter === 'all' ? undefined : keyFilter } 
    }),
    select: res => res.data
  });
}

export function useEndpointBreakdown(range: string, keyFilter: string) {
  return useQuery({
    queryKey: ['endpointBreakdown', range, keyFilter],
    queryFn: () => api.get<EndpointBreakdown>('/developer/analytics/endpoints', { 
      params: { range, key_id: keyFilter === 'all' ? undefined : keyFilter } 
    }),
    select: res => res.data
  });
}

export function useErrorBreakdown(range: string, keyFilter: string) {
  return useQuery({
    queryKey: ['errorBreakdown', range, keyFilter],
    queryFn: () => api.get<ErrorBreakdown>('/developer/analytics/errors', { 
      params: { range, key_id: keyFilter === 'all' ? undefined : keyFilter } 
    }),
    select: res => res.data
  });
}

export function useLatencyDistribution(range: string, keyFilter: string) {
  return useQuery({
    queryKey: ['latencyDistribution', range, keyFilter],
    queryFn: () => api.get<LatencyDistribution>('/developer/analytics/latency', { 
      params: { range, key_id: keyFilter === 'all' ? undefined : keyFilter } 
    }),
    select: res => res.data
  });
}
```

### 4. Backend Endpoints Needed (for backend-agent)
```
GET /developer/analytics/overview?range=30d&key_id={id}
GET /developer/analytics/endpoints?range=30d&key_id={id}
GET /developer/analytics/errors?range=30d&key_id={id}
GET /developer/analytics/latency?range=30d&key_id={id}
```
- Agregam dados de `api_key_usage` table
- Filtros por range (7d, 30d, 90d) e key_id opcional
- Retornam séries temporais + agregações

### 5. Types (`src/types/analytics.ts`)
```typescript
export interface UsageOverview {
  total_requests: number;
  requests_trend: number; // percent change
  error_rate: number;
  error_trend: number;
  avg_latency_ms: number;
  latency_trend: number;
  p99_latency_ms: number;
  daily_volume: { date: string; requests: number; errors: number }[];
  geo_distribution?: { country: string; requests: number; error_rate: number }[];
}

export interface EndpointBreakdown {
  top_20: {
    endpoint: string;
    method: string;
    requests: number;
    avg_latency_ms: number;
    p99_latency_ms: number;
    error_rate: number;
  }[];
}

export interface ErrorBreakdown {
  by_status_code: { status: number; count: number; percentage: number }[];
  by_endpoint: { endpoint: string; errors: number; rate: number }[];
}

export interface LatencyDistribution {
  buckets: { bucket: string; count: number; percentage: number }[];
  percentiles: { p50: number; p90: number; p95: number; p99: number; p999: number };
}
```

## Acceptance Criteria
- [ ] Range selector (7d/30d/90d) atualiza todos gráficos
- [ ] Key filter funciona (todas ou específica)
- [ ] KPIs mostram trend vs período anterior
- [ ] AreaChart: volume + errors dual axis
- [ ] PieChart: errors por status code
- [ ] BarChart: latency histogram
- [ ] EndpointTable: top 20 endpoints com métricas
- [ ] Loading states em cada card
- [ ] Responsivo (charts stack no mobile)
- [ ] Testes: hooks, componentes, filtros

## Referências
- Card 40 (Developer Portal) - Layout
- Card 41 (API Keys) - Key filter source
- `agents/frontend/ui/ui-agent.md` - Chart components (Recharts)
- `frontend/src/utils/helpers.ts` - formatNumber, formatPercent
- Backend: `api_key_usage` table aggregation