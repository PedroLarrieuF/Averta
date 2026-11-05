import { useState } from 'react'
import { formatDate, formatRelativeTime } from '../../utils/helpers'
import { Plus, Key, Copy, Trash2, Eye, EyeOff } from 'lucide-react'
import { Button, Card, CardHeader, CardBody, Input, Modal, Badge } from '../../components'
import { useNavigate } from 'react-router-dom'

interface ApiKey {
  id: string
  name: string
  key_prefix: string
  key_hash: string
  is_active: boolean
  last_used_at: string | null
  expires_at: string | null
  created_at: string
  scopes: string[]
}

export function DeveloperKeys() {
  const navigate = useNavigate()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [selectedKey, setSelectedKey] = useState<ApiKey | null>(null)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyScopes, setNewKeyScopes] = useState<string[]>(['read'])
  const [generatedKey, setGeneratedKey] = useState<string | null>(null)
  const [showKey, setShowKey] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Mock data - will be replaced with real API calls
  const mockKeys: ApiKey[] = [
    {
      id: '1',
      name: 'Production API Key',
      key_prefix: 'avt_live_',
      key_hash: 'avt_live_abc123...xyz789',
      is_active: true,
      last_used_at: '2024-01-20T10:30:00Z',
      expires_at: null,
      created_at: '2024-01-15T08:00:00Z',
      scopes: ['read', 'write', 'admin'],
    },
    {
      id: '2',
      name: 'Staging API Key',
      key_prefix: 'avt_staging_',
      key_hash: 'avt_staging_def456...uvw012',
      is_active: true,
      last_used_at: '2024-01-19T15:45:00Z',
      expires_at: '2024-12-31T23:59:59Z',
      created_at: '2024-02-20T12:00:00Z',
      scopes: ['read', 'write'],
    },
    {
      id: '3',
      name: 'Development Key (Expired)',
      key_prefix: 'avt_dev_',
      key_hash: 'avt_dev_ghi789...rst345',
      is_active: false,
      last_used_at: '2023-12-01T09:00:00Z',
      expires_at: '2023-12-31T23:59:59Z',
      created_at: '2023-11-10T10:00:00Z',
      scopes: ['read'],
    },
  ]

  const availableScopes = [
    { value: 'read', label: 'Leitura', description: 'Acesso de leitura aos recursos' },
    { value: 'write', label: 'Escrita', description: 'Criar e modificar recursos' },
    { value: 'admin', label: 'Admin', description: 'Acesso administrativo completo' },
    { value: 'webhooks', label: 'Webhooks', description: 'Gerenciar webhooks' },
  ]

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return
    setIsSubmitting(true)

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Generate mock key
    const prefix = 'avt_live_'
    const randomPart = Math.random().toString(36).substring(2, 20)
    const fullKey = `${prefix}${randomPart}`

    setGeneratedKey(fullKey)
    setIsSubmitting(false)
    setIsCreateModalOpen(false)
    setNewKeyName('')
    setNewKeyScopes(['read'])
  }

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    // TODO: Show toast notification
  }

  const handleDeleteKey = () => {
    if (selectedKey) {
      // TODO: Call delete API
      setIsDeleteModalOpen(false)
      setSelectedKey(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="page-header flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Gerenciar API Keys</h1>
          <p className="page-subtitle">Crie, revogue e monitore suas chaves de acesso à API</p>
        </div>
        <Button variant="primary" onClick={() => setIsCreateModalOpen(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Nova API Key
        </Button>
      </div>

      {/* Keys Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <span>Suas Chaves de API</span>
            <div className="flex items-center gap-2 text-sm text-secondary-500">
              <span>Chaves são mostradas apenas uma vez na criação</span>
            </div>
          </div>
        </CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th className="w-40">Nome</th>
                  <th>Prefixo</th>
                  <th>Escopos</th>
                  <th>Status</th>
                  <th className="w-40">Último Uso</th>
                  <th className="w-32">Criada em</th>
                  <th className="w-40 text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                {mockKeys.map((key) => (
                  <tr key={key.id} className={!key.is_active ? 'bg-secondary-50' : ''}>
                    <td className="font-medium text-secondary-900">{key.name}</td>
                    <td className="font-mono text-sm text-secondary-600">{key.key_prefix}****</td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {key.scopes.map((scope) => (
                          <Badge key={scope} variant="secondary" className="text-xs">
                            {scope}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td>
                      <Badge variant={key.is_active ? 'success' : 'secondary'}>
                        {key.is_active ? 'Ativa' : 'Revogada/Expirada'}
                      </Badge>
                    </td>
                    <td className="text-sm text-secondary-500">
                      {key.last_used_at ? formatRelativeTime(key.last_used_at) : 'Nunca usada'}
                    </td>
                    <td className="text-sm text-secondary-500">
                      {formatDate(key.created_at)}
                    </td>
                    <td>
                      <div className="flex items-center justify-end gap-2 pr-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyKey(key.key_hash)}
                          aria-label="Copiar prefixo da chave"
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                        {key.is_active && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => { setSelectedKey(key); setIsDeleteModalOpen(true); }}
                            className="text-danger-600 hover:text-danger-700"
                            aria-label="Revogar chave"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {mockKeys.length === 0 && (
            <div className="empty-state">
              <Key className="empty-state-icon" />
              <h3 className="empty-state-title">Nenhuma API Key criada</h3>
              <p className="empty-state-description">
                Crie sua primeira chave para começar a integrar com a API da AvertaSaaS
              </p>
              <Button variant="primary" onClick={() => setIsCreateModalOpen(true)} className="mt-4">
                <Plus className="h-4 w-4" />
                Criar Primeira Chave
              </Button>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Create Key Modal */}
      <Modal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        title="Criar Nova API Key"
        description="Configure os detalhes da nova chave de API"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Nome da Chave</label>
            <Input
              placeholder="ex: Production API Key"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              error={isSubmitting && !newKeyName.trim() ? 'Nome é obrigatório' : undefined}
            />
          </div>

          <div>
            <label className="label">Escopos (Permissões)</label>
            <div className="space-y-2">
              {availableScopes.map((scope) => (
                <label key={scope.value} className="flex items-center gap-3 p-3 border border-secondary-200 rounded-lg cursor-pointer hover:bg-secondary-50 transition-colors">
                  <input
                    type="checkbox"
                    checked={newKeyScopes.includes(scope.value)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setNewKeyScopes([...newKeyScopes, scope.value])
                      } else {
                        setNewKeyScopes(newKeyScopes.filter(s => s !== scope.value))
                      }
                    }}
                    className="h-4 w-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                  />
                  <div>
                    <p className="font-medium text-secondary-900">{scope.label}</p>
                    <p className="text-sm text-secondary-500">{scope.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-secondary-200">
            <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button variant="primary" onClick={handleCreateKey} disabled={isSubmitting || !newKeyName.trim()} loading={isSubmitting}>
              {isSubmitting ? 'Criando...' : 'Criar Chave'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Generated Key Modal */}
      {generatedKey && (
        <Modal
          open={true}
          onOpenChange={(open: boolean) => { if (!open) setGeneratedKey(null); }}
          title="API Key Criada com Sucesso!"
          description="Copie a chave agora - ela não será exibida novamente"
        >
          <div className="space-y-4">
            <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm break-all">
                  {showKey ? generatedKey : generatedKey.replace(/./g, '•')}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowKey(!showKey)}
                  aria-label={showKey ? 'Ocultar chave' : 'Mostrar chave'}
                >
                  {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="primary"
                className="flex-1"
                onClick={() => handleCopyKey(generatedKey)}
              >
                <Copy className="h-4 w-4" />
                Copiar Chave
              </Button>
              <Button
                variant="secondary"
                className="flex-1"
                onClick={() => { setGeneratedKey(null); navigate('/developer/keys'); }}
              >
                Fechar
              </Button>
            </div>

            <p className="text-sm text-warning-700 bg-warning-50 p-3 rounded-lg">
              <strong>Importante:</strong> Guarde esta chave em local seguro. Ela não poderá ser recuperada novamente.
              Se perdida, você precisará criar uma nova chave e revogar esta.
            </p>
          </div>
        </Modal>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        open={isDeleteModalOpen}
        onOpenChange={setIsDeleteModalOpen}
        title="Revogar API Key"
        description={selectedKey ? `Tem certeza que deseja revogar "${selectedKey.name}"? Esta ação não pode ser desfeita.` : ''}
      >
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => { setIsDeleteModalOpen(false); setSelectedKey(null); }}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={handleDeleteKey}>
            <Trash2 className="h-4 w-4" />
            Revogar
          </Button>
        </div>
      </Modal>
    </div>
  )
}