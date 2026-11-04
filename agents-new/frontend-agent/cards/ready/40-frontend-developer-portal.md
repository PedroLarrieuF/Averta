---
id: 40
title: "Developer Portal: Dashboard & Documentation"
priority: critical
type: feature
agent: frontend
sprint: 1
estimate: L
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 40: Developer Portal - Dashboard & Documentation

## Contexto
Criar o portal do desenvolvedor (`/developer`) com: dashboard de overview, documentação interativa (Scalar), autenticação, navegação.

## Decisões
- **Rota base**: `/developer` (protegida por auth - apenas usuários logados)
- **Doc interativa**: Scalar (moderno, rápido, suporta OpenAPI 3.1)
- **Layout**: Sidebar + content area (similar ao MainLayout)
- **Acesso**: Qualquer usuário autenticado pode acessar

## Tasks

### 1. Layout & Routing
```
src/pages/developer/
├── index.ts                    # Barrel exports
├── DeveloperLayout.tsx         # Layout com sidebar
├── DeveloperDashboard.tsx      # Overview page
├── DeveloperDocs.tsx           # Scalar documentation
├── DeveloperKeys.tsx           # API Key management (Card 41)
├── DeveloperAnalytics.tsx      # Usage analytics (Card 42)
├── DeveloperWebhooks.tsx       # Webhook management (future)
└── components/
    ├── DeveloperSidebar.tsx
    ├── DeveloperHeader.tsx
    ├── ApiKeyCard.tsx
    ├── ApiKeyForm.tsx
    ├── UsageChart.tsx
    └── EndpointList.tsx
```

### 2. DeveloperLayout (`src/layouts/DeveloperLayout.tsx`)
```tsx
// Extends MainLayout pattern but with developer-specific sidebar
const developerNavItems = [
  { label: 'Overview', path: '/developer', icon: HomeIcon },
  { label: 'Documentation', path: '/developer/docs', icon: BookIcon },
  { label: 'API Keys', path: '/developer/keys', icon: KeyIcon },
  { label: 'Analytics', path: '/developer/analytics', icon: BarChartIcon },
  { label: 'Webhooks', path: '/developer/webhooks', icon: WebhookIcon },
];

export function DeveloperLayout({ children }: { children: React.ReactNode }) {
  return (
    <MainLayout 
      customSidebar={<DeveloperSidebar />}
      customHeader={<DeveloperHeader />}
    >
      {children}
    </MainLayout>
  );
}
```

### 3. DeveloperDashboard (`src/pages/developer/DeveloperDashboard.tsx`)
```tsx
// KPIs cards + Quick actions + Recent activity
export function DeveloperDashboard() {
  const { data: keys } = useApiKeys();
  const { data: usage } = useUsageSummary(30); // Last 30 days

  return (
    <div className="space-y-6">
      <PageHeader title="Developer Portal" subtitle="Manage your API integrations" />
      
      {/* KPI Row */}
      <div className="grid-kpi">
        <KPICard label="Active Keys" value={keys?.filter(k => k.is_active).length} />
        <KPICard label="Requests (30d)" value={formatNumber(usage?.total_requests)} />
        <KPICard label="Error Rate" value={formatPercent(usage?.error_rate)} variant="warning" />
        <KPICard label="Avg Latency" value={`${usage?.avg_latency_ms}ms`} />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>Quick Actions</CardHeader>
        <CardBody className="flex gap-4 flex-wrap">
          <Button variant="primary" onClick={() => navigate('/developer/keys/new')}>
            <PlusIcon /> Create API Key
          </Button>
          <Button variant="secondary" onClick={() => navigate('/developer/docs')}>
            <BookIcon /> View Documentation
          </Button>
          <Button variant="ghost" onClick={() => navigate('/developer/webhooks')}>
            <WebhookIcon /> Configure Webhooks
          </Button>
        </CardBody>
      </Card>

      {/* Recent Keys */}
      <Card>
        <CardHeader className="flex justify-between">
          <span>Recent API Keys</span>
          <Button variant="ghost" size="sm" onClick={() => navigate('/developer/keys')}>View All</Button>
        </CardHeader>
        <CardBody>
          <ApiKeyList keys={keys?.slice(0, 5)} />
        </CardBody>
      </Card>

      {/* Usage Chart */}
      <Card>
        <CardHeader>Request Volume (30 days)</CardHeader>
        <CardBody>
          <UsageChart data={usage?.daily_series} />
        </CardBody>
      </Card>
    </div>
  );
}
```

### 4. DeveloperDocs - Scalar Integration (`src/pages/developer/DeveloperDocs.tsx`)
```tsx
// Embed Scalar documentation
import { useEffect, useRef } from 'react';

export function DeveloperDocs() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    
    // Load Scalar dynamically
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest';
    script.onload = () => {
      // @ts-ignore - Scalar global
      Scalar.createApiReference('#scalar-docs', {
        spec: {
          url: '/openapi/v1.yaml',  // Served from frontend public or backend
        },
        theme: 'kepler',
        layout: 'modern',
        authentication: {
          preferredSecurityScheme: 'ApiKeyAuth',
          securitySchemes: {
            ApiKeyAuth: {
              type: 'apiKey',
              in: 'header',
              name: 'X-API-Key'
            }
          }
        },
        hideDownloadButton: false,
        hideModels: false
      });
    };
    document.head.appendChild(script);
    
    return () => { document.head.removeChild(script); };
  }, []);

  return (
    <div className="h-[calc(100vh-200px)]">
      <div id="scalar-docs" ref={containerRef} className="h-full" />
    </div>
  );
}
```

### 5. OpenAPI Spec Serving
- Backend serve `/openapi/v1.yaml` (static file ou generated)
- Frontend proxy via Vite ou serve from `public/openapi/v1.yaml`
- Scalar carrega via URL absoluta

### 6. Navigation Integration
- Adicionar link "Developer Portal" no MainLayout sidebar (apenas para ADMIN/MANAGER?)
- Ou item no user dropdown menu

## Acceptance Criteria
- [ ] `/developer` acessível para usuários logados
- [ ] Sidebar navegação funcional
- [ ] Dashboard carrega KPIs e gráfico
- [ ] Scalar renderiza OpenAPI spec corretamente
- [ ] Try-it-out funciona com API Key do usuário
- [ ] Responsivo (mobile sidebar collapse)
- [ ] Testes: layout, dashboard, docs

## Referências
- `frontend/src/layouts/MainLayout.tsx` - Pattern base
- `frontend/src/components/` - Design system
- `frontend/src/hooks/useApi.ts` - Para hooks de API keys
- Scalar: https://scalar.com/
- Card 41 (API Keys UI), Card 42 (Analytics UI)