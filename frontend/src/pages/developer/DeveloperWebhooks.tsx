import { Plus, Bell, Trash2, ExternalLink, Copy } from 'lucide-react'
import { Button, Card, CardHeader, CardBody, Badge, Input, Modal } from '../../components'
import { useState } from 'react'

interface Webhook {
  id: string
  name: string
  url: string
  events: string[]
  is_active: boolean
  secret: string
  created_at: string
  last_triggered_at: string | null
  success_count: number
  failure_count: number
}

export function DeveloperWebhooks() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null)
  const [newWebhook, setNewWebhook] = useState({ name: '', url: '', events: ['discrepancy.created'] as string[], secret: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const availableEvents = [
    { value: 'discrepancy.created', label: 'Discrepância Criada' },
    { value: 'discrepancy.updated', label: 'Discrepância Atualizada' },
    { value: 'discrepancy.resolved', label: 'Discrepância Resolvida' },
    { value: 'document.uploaded', label: 'Documento Enviado' },
    { value: 'document.processed', label: 'Documento Processado' },
    { value: 'contest.created', label: 'Contestação Criada' },
    { value: 'contest.updated', label: 'Contestação Atualizada' },
    { value: 'contract.created', label: 'Contrato Criado' },
    { value: 'contract.updated', label: 'Contrato Atualizado' },
  ]

  // Mock data
  const mockWebhooks: Webhook[] = [
    {
      id: '1',
      name: 'Production Webhook',
      url: 'https://api.meusistema.com/webhooks/averta',
      events: ['discrepancy.created', 'discrepancy.resolved', 'document.processed'],
      is_active: true,
      secret: 'whsec_abc123...',
      created_at: '2024-01-15T08:00:00Z',
      last_triggered_at: '2024-01-20T10:30:00Z',
      success_count: 1245,
      failure_count: 12,
    },
    {
      id: '2',
      name: 'Staging Webhook',
      url: 'https://staging.meusistema.com/webhooks/averta',
      events: ['discrepancy.created', 'discrepancy.updated', 'document.uploaded'],
      is_active: true,
      secret: 'whsec_def456...',
      created_at: '2024-02-20T12:00:00Z',
      last_triggered_at: '2024-01-19T15:45:00Z',
      success_count: 342,
      failure_count: 5,
    },
    {
      id: '3',
      name: 'Legacy Webhook (Inativo)',
      url: 'https://legacy.meusistema.com/webhook',
      events: ['discrepancy.created'],
      is_active: false,
      secret: 'whsec_old...',
      created_at: '2023-11-10T10:00:00Z',
      last_triggered_at: '2023-12-01T09:00:00Z',
      success_count: 89,
      failure_count: 34,
    },
  ]

  const handleCreateWebhook = async () => {
    if (!newWebhook.name.trim() || !newWebhook.url.trim() || newWebhook.events.length === 0) return
    setIsSubmitting(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsSubmitting(false)
    setIsCreateModalOpen(false)
    setNewWebhook({ name: '', url: '', events: ['discrepancy.created'], secret: '' })
  }

  const handleDeleteWebhook = () => {
    if (selectedWebhook) {
      setIsDeleteModalOpen(false)
      setSelectedWebhook(null)
    }
  }

  const handleCopySecret = (secret: string) => {
    navigator.clipboard.writeText(secret)
  }

  return (
    <div className="space-y-6">
      <div className="page-header flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Gerenciar Webhooks</h1>
          <p className="page-subtitle">Configure webhooks para receber notificações em tempo real</p>
        </div>
        <Button variant="primary" onClick={() => setIsCreateModalOpen(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Novo Webhook
        </Button>
      </div>

      {/* Info Card */}
      <Card className="bg-primary-50 border-primary-200">
        <CardBody className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <ExternalLink className="h-5 w-5 text-primary-600" />
            <div>
              <p className="font-medium text-primary-900">Como funcionam os Webhooks</p>
              <p className="text-sm text-primary-700">
                A AvertaSaaS enviará POST requests para sua URL com o payload do evento.
                Valide a assinatura usando o secret para garantir autenticidade.
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" className="flex items-center gap-2">
              <ExternalLink className="h-3.5 w-3.5" />
              Ver Documentação
            </Button>
            <Button variant="primary" size="sm" className="flex items-center gap-2">
              <Copy className="h-3.5 w-3.5" />
              Exemplo de Payload
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Webhooks Table */}
      <Card>
        <CardHeader>Seus Webhooks</CardHeader>
        <CardBody className="p-0">
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr>
                  <th className="w-40">Nome</th>
                  <th>URL</th>
                  <th>Eventos</th>
                  <th>Status</th>
                  <th className="w-36">Último Trigger</th>
                  <th className="w-32">Sucesso / Falha</th>
                  <th className="w-40 text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                {mockWebhooks.map((webhook) => (
                  <tr key={webhook.id} className={!webhook.is_active ? 'bg-secondary-50' : ''}>
                    <td className="font-medium text-secondary-900">{webhook.name}</td>
                    <td className="font-mono text-sm text-secondary-600 max-w-xs truncate">{webhook.url}</td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {webhook.events.map((event) => (
                          <Badge key={event} variant="secondary" className="text-xs">
                            {event}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td>
                      <Badge variant={webhook.is_active ? 'success' : 'secondary'}>
                        {webhook.is_active ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </td>
                    <td className="text-sm text-secondary-500">
                      {webhook.last_triggered_at
                        ? new Date(webhook.last_triggered_at).toLocaleString('pt-BR')
                        : 'Nunca'}
                    </td>
                    <td className="text-sm font-mono">
                      <span className="text-success-600">{webhook.success_count}</span>
                      <span className="text-secondary-300 mx-1">/</span>
                      <span className="text-danger-600">{webhook.failure_count}</span>
                    </td>
                    <td>
                      <div className="flex items-center justify-end gap-2 pr-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopySecret(webhook.secret)}
                          aria-label="Copiar secret"
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className={webhook.is_active ? 'text-warning-600' : 'text-success-600'}
                          onClick={() => {}}
                          aria-label={webhook.is_active ? 'Desativar' : 'Ativar'}
                        >
                          {webhook.is_active ? <span>✕</span> : <span>✓</span>}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => { setSelectedWebhook(webhook); setIsDeleteModalOpen(true); }}
                          className="text-danger-600 hover:text-danger-700"
                          aria-label="Excluir webhook"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {mockWebhooks.length === 0 && (
            <div className="empty-state">
              <Bell className="empty-state-icon" />
              <h3 className="empty-state-title">Nenhum webhook configurado</h3>
              <p className="empty-state-description">
                Crie seu primeiro webhook para receber notificações em tempo real
              </p>
              <Button variant="primary" onClick={() => setIsCreateModalOpen(true)} className="mt-4">
                <Plus className="h-4 w-4" />
                Criar Primeiro Webhook
              </Button>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Create Webhook Modal */}
      <Modal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        title="Criar Novo Webhook"
        description="Configure a URL de destino e os eventos que deseja receber"
      >
        <div className="space-y-4">
          <div>
            <label className="label">Nome do Webhook</label>
            <Input
              placeholder="ex: Meu Sistema de Produção"
              value={newWebhook.name}
              onChange={(e) => setNewWebhook({ ...newWebhook, name: e.target.value })}
              error={isSubmitting && !newWebhook.name.trim() ? 'Nome é obrigatório' : undefined}
            />
          </div>

          <div>
            <label className="label">URL de Destino</label>
            <Input
              type="url"
              placeholder="https://api.seusistema.com/webhooks/averta"
              value={newWebhook.url}
              onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
              error={isSubmitting && !newWebhook.url.trim() ? 'URL é obrigatória' : undefined}
            />
          </div>

          <div>
            <label className="label">Eventos para Escutar</label>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {availableEvents.map((event) => (
                <label key={event.value} className="flex items-center gap-3 p-3 border border-secondary-200 rounded-lg cursor-pointer hover:bg-secondary-50 transition-colors">
                  <input
                    type="checkbox"
                    checked={newWebhook.events.includes(event.value)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setNewWebhook({ ...newWebhook, events: [...newWebhook.events, event.value] })
                      } else {
                        setNewWebhook({ ...newWebhook, events: newWebhook.events.filter(ev => ev !== event.value) })
                      }
                    }}
                    className="h-4 w-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-secondary-700">{event.label}</span>
                </label>
              ))}
            </div>
            {newWebhook.events.length === 0 && (
              <p className="text-sm text-danger-600 mt-1">Selecione pelo menos um evento</p>
            )}
          </div>

          <div>
            <label className="label">Secret (opcional - gerado automaticamente se vazio)</label>
            <Input
              placeholder="whsec_... (deixe em branco para gerar automaticamente)"
              value={newWebhook.secret}
              onChange={(e) => setNewWebhook({ ...newWebhook, secret: e.target.value })}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-secondary-200">
            <Button variant="secondary" onClick={() => setIsCreateModalOpen(false)} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button variant="primary" onClick={handleCreateWebhook} disabled={isSubmitting || !newWebhook.name.trim() || !newWebhook.url.trim() || newWebhook.events.length === 0} loading={isSubmitting}>
              {isSubmitting ? 'Criando...' : 'Criar Webhook'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        open={isDeleteModalOpen}
        onOpenChange={setIsDeleteModalOpen}
        title="Excluir Webhook"
        description={selectedWebhook ? `Tem certeza que deseja excluir "${selectedWebhook.name}"? Esta ação não pode ser desfeita.` : ''}
      >
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => { setIsDeleteModalOpen(false); setSelectedWebhook(null); }}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={handleDeleteWebhook}>
            <Trash2 className="h-4 w-4" />
            Excluir
          </Button>
        </div>
      </Modal>
    </div>
  )
}