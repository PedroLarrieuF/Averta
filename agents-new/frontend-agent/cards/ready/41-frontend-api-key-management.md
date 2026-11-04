---
id: 41
title: "Developer Portal: API Key Management UI"
priority: critical
type: feature
agent: frontend
sprint: 1
estimate: L
status: ready
created: 2026-11-04
reviewed_by: techlead
---

# Card 41: Developer Portal - API Key Management UI

## Contexto
Interface completa para gerenciar API Keys: listar, criar, ver detalhes, rotacionar, revogar, ver usage. Backend expõe endpoints em `/admin/api-keys*`.

## Tasks

### 1. DeveloperKeysPage (`src/pages/developer/DeveloperKeys.tsx`)
```tsx
// Lista keys + botão "Create Key" + modal de criação
export function DeveloperKeysPage() {
  const { data: keys, refetch } = useApiKeys();
  const [createModal, setCreateModal] = useState(false);
  const [selectedKey, setSelectedKey] = useState<ApiKey | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <PageHeader title="API Keys" subtitle="Manage your API credentials" />
        <Button variant="primary" onClick={() => setCreateModal(true)}>
          <PlusIcon className="mr-2" /> Create API Key
        </Button>
      </div>

      {/* Keys Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Prefix</TableCell>
              <TableCell>Tier</TableCell>
              <TableCell>Scopes</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Used</TableCell>
              <TableCell>Expires</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keys?.map(key => (
              <TableRow key={key.id}>
                <TableCell className="font-mono">{key.name}</TableCell>
                <TableCell className="font-mono text-sm">{key.key_prefix}••••</TableCell>
                <TableCell><Badge variant={tierBadgeVariant(key.tier)}>{key.tier}</Badge></TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {key.scopes.map(s => <Badge key={s} variant="secondary" className="text-xs">{s}</Badge>)}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={key.is_active ? 'success' : 'danger'}>
                    {key.is_active ? 'Active' : 'Revoked'}
                  </Badge>
                </TableCell>
                <TableCell>{key.last_used_at ? formatRelativeTime(key.last_used_at) : 'Never'}</TableCell>
                <TableCell>{key.expires_at ? formatDate(key.expires_at) : 'Never'}</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenu.Item onClick={() => setSelectedKey(key)}>View Details</DropdownMenu.Item>
                    <DropdownMenu.Item onClick={() => handleRotate(key.id)}>Rotate Key</DropdownMenu.Item>
                    <DropdownMenu.Item variant="destructive" onClick={() => handleRevoke(key.id)}>Revoke</DropdownMenu.Item>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Create Key Modal */}
      <CreateKeyModal open={createModal} onClose={() => setCreateModal(false)} onSuccess={() => refetch()} />

      {/* Key Detail Modal */}
      <KeyDetailModal key={selectedKey} onClose={() => setSelectedKey(null)} onRotate={() => refetch()} onRevoke={() => refetch()} />
    </div>
  );
}
```

### 2. CreateKeyModal (`src/pages/developer/components/CreateKeyModal.tsx`)
```tsx
// Formulário: Name, Tier (select), Scopes (multi-select), Expires In (select)
export function CreateKeyModal({ open, onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState({
    name: '',
    tier: 'free',
    scopes: [] as string[],
    expires_in_days: 365
  });
  const createMutation = useCreateApiKey();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createMutation.mutateAsync(formData);
    // SHOW PLAIN KEY ONLY ONCE - Critical UX
    setShowPlainKey(true);
    setPlainKey(result.plain_key);
  };

  return (
    <Modal open={open} onClose={onClose} size="lg">
      <Modal.Header>Create API Key</Modal.Header>
      <Modal.Body>
        {!showPlainKey ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Key Name" value={formData.name} onChange={...} required />
            
            <Select label="Tier" value={formData.tier} onChange={...} options={[
              { value: 'free', label: 'Free (Sandbox only, 100 req/min)' },
              { value: 'pro', label: 'Pro (Production, 1000 req/min)' },
              { value: 'enterprise', label: 'Enterprise (High volume, 10000 req/min)' }
            ]} />
            
            <fieldset>
              <legend className="label">Scopes</legend>
              <div className="space-y-2">
                {ALL_SCOPES.map(scope => (
                  <label key={scope} className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={formData.scopes.includes(scope)} onChange={...} />
                    <span className="text-sm">{scope}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            <Select label="Expires In" value={formData.expires_in_days} options={[
              { value: 30, label: '30 days' },
              { value: 90, label: '90 days' },
              { value: 365, label: '1 year (default)' },
              { value: 730, label: '2 years' },
              { value: 0, label: 'Never expires' }
            ]} />
            
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Create Key
            </Button>
          </form>
        ) : (
          // SUCCESS STATE - Show plain key ONLY ONCE
          <div className="space-y-4 p-4 bg-green-50 rounded-lg border border-green-200">
            <AlertIcon className="text-green-600" />
            <h3 className="font-semibold">API Key Created Successfully!</h3>
            <p className="text-sm text-gray-600">
              This is the only time you'll see the full key. Copy and store it securely.
            </p>
            <div className="relative">
              <Input 
                value={plain_key} 
                readOnly 
                className="font-mono text-sm pr-12"
              />
              <Button 
                variant="ghost" 
                size="sm" 
                className="absolute right-2 top-1/2 -translate-y-1/2"
                onClick={() => { navigator.clipboard.writeText(plain_key); toast.success('Copied!'); }}
              >
                <CopyIcon />
              </Button>
            </div>
            <Checkbox label="I have copied and stored this key securely" onChange={setConfirmed} />
            <Button variant="primary" onClick={() => { onClose(); onSuccess(); }} disabled={!confirmed}>
              Done
            </Button>
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
}
```

### 3. KeyDetailModal (`src/pages/developer/components/KeyDetailModal.tsx`)
```tsx
// Mostra detalhes completos + usage chart + ações
export function KeyDetailModal({ key, onClose, onRotate, onRevoke }: Props) {
  const { data: usage } = useApiKeyUsage(key.id, 30);
  const rotateMutation = useRotateApiKey();
  const revokeMutation = useRevokeApiKey();

  return (
    <Modal open={!!key} onClose={onClose} size="xl">
      <Modal.Header>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">{key.name}</h3>
            <span className="text-sm text-gray-500 font-mono">{key.key_prefix}••••</span>
          </div>
          <Badge variant={tierBadgeVariant(key.tier)}>{key.tier}</Badge>
        </div>
      </Modal.Header>
      
      <Modal.Body className="space-y-6">
        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-4">
          <InfoItem label="Key ID" value={key.id} />
          <InfoItem label="Company" value={key.company_name} />
          <InfoItem label="Created" value={formatDateTime(key.created_at)} />
          <InfoItem label="Created By" value={key.created_by_name} />
          <InfoItem label="Status" value={<Badge variant={key.is_active ? 'success' : 'danger'}>{key.is_active ? 'Active' : 'Revoked'}</Badge>} />
          <InfoItem label="Expires" value={key.expires_at ? formatDate(key.expires_at) : 'Never'} />
        </div>

        {/* Scopes */}
        <div>
          <h4 className="font-medium mb-2">Scopes</h4>
          <div className="flex flex-wrap gap-2">
            {key.scopes.map(s => <Badge key={s} variant="secondary">{s}</Badge>)}
          </div>
        </div>

        {/* Usage Chart */}
        <Card>
          <CardHeader>Usage (Last 30 Days)</CardHeader>
          <CardBody>
            <UsageChart data={usage?.daily_series} />
            <div className="grid grid-cols-4 gap-4 mt-4 text-sm">
              <div><span className="text-gray-500">Total Requests</span><p className="font-semibold">{formatNumber(usage?.total_requests)}</p></div>
              <div><span className="text-gray-500">Error Rate</span><p className="font-semibold text-red-600">{formatPercent(usage?.error_rate)}</p></div>
              <div><span className="text-gray-500">Avg Latency</span><p className="font-semibold">{usage?.avg_latency_ms}ms</p></div>
              <div><span className="text-gray-500">Data Transferred</span><p className="font-semibold">{formatBytes(usage?.bytes_transferred)}</p></div>
            </div>
          </CardBody>
        </Card>

        {/* Recent Requests Table */}
        <Card>
          <CardHeader>Recent Requests</CardHeader>
          <CardBody>
            <RequestLogTable requests={usage?.recent_requests} />
          </CardBody>
        </Card>
      </Modal.Body>

      <Modal.Footer className="justify-start gap-3">
        <Button variant="secondary" onClick={() => rotateMutation.mutate(key.id, { onSuccess: onRotate })}>
          <RotateIcon /> Rotate Key
        </Button>
        <Button variant="danger" onClick={() => revokeMutation.mutate(key.id, { onSuccess: onRevoke })}>
          <TrashIcon /> Revoke Key
        </Button>
        <Button variant="ghost" onClick={onClose}>Close</Button>
      </Modal.Footer>
    </Modal>
  );
}
```

### 4. Hooks (`src/hooks/useApiKeys.ts`)
```typescript
export function useApiKeys() {
  return useQuery({
    queryKey: ['apiKeys'],
    queryFn: () => api.get<ApiKey[]>('/admin/api-keys'),
    select: res => res.data
  });
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateApiKeyRequest) => api.post<{ key: ApiKey; plain_key: string }>('/admin/api-keys', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
  });
}

export function useRotateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.post<{ key: ApiKey; plain_key: string }>(`/admin/api-keys/${id}/rotate`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
  });
}

export function useRevokeApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/admin/api-keys/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
  });
}

export function useApiKeyUsage(keyId: string, days: number) {
  return useQuery({
    queryKey: ['apiKeyUsage', keyId, days],
    queryFn: () => api.get<UsageStats>(`/admin/api-keys/${keyId}/usage`, { params: { days } }),
    enabled: !!keyId,
    select: res => res.data
  });
}
```

### 5. Types (`src/types/api.ts`)
```typescript
export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  tier: 'free' | 'pro' | 'enterprise';
  rate_limit_override: number | null;
  expires_at: string | null;
  last_used_at: string | null;
  usage_count: number;
  is_active: boolean;
  created_by: string;
  company_id: string;
  created_at: string;
  updated_at: string;
  // Joined fields
  company_name?: string;
  created_by_name?: string;
}

export interface UsageStats {
  total_requests: number;
  error_rate: number;
  avg_latency_ms: number;
  bytes_transferred: number;
  daily_series: { date: string; requests: number; errors: number; latency_p95: number }[];
  recent_requests: RequestLog[];
}

export interface RequestLog {
  id: string;
  endpoint: string;
  method: string;
  status_code: number;
  response_time_ms: number;
  created_at: string;
}
```

## Acceptance Criteria
- [ ] Lista keys com paginação
- [ ] Cria key → mostra plain key UMA VEZ com copy button
- [ ] Rotação invalida key antiga, mostra nova plain key
- [ ] Revogação soft-delete (is_active = false)
- [ ] Usage chart carrega dados
- [ ] Scopes multi-select funcional
- [ ] Tier select com descrições
- [ ] Testes: CRUD keys, rotação, revogação, copy key

## Referências
- Card 40 (Developer Portal) - Layout base
- Card 41 backend (API Key Model) - Endpoints
- `frontend/src/components/` - Modal, Table, Badge, Select, Input
- `frontend/src/hooks/useApi.ts` - TanStack Query pattern