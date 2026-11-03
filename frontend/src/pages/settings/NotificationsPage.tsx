import { useState, useEffect } from 'react'
import { Bell, Mail, Loader2, Save, CheckCircle, AlertCircle, Moon, MessageSquare, CreditCard, FileText, BarChart2 } from 'lucide-react'
import { Button, Input, Label, Badge, Card, CardHeader, CardBody, Switch, Tabs, TabsList, TabsTrigger, TabsContent } from '@/components'
import toast from 'react-hot-toast'
import { useAuth } from '@/store/auth-context'
import { useNotificationPreferences, useUpdateNotificationPreferences, useNotificationTemplates, useUpdateNotificationTemplate } from '@/hooks/useSettings'
import type { NotificationTemplate } from '@/hooks/useSettings'

const NOTIFICATION_TYPES = [
  { key: 'discrepancies', label: 'Discrepâncias', icon: AlertCircle, description: 'Novas discrepâncias encontradas' },
  { key: 'contests', label: 'Contestações', icon: MessageSquare, description: 'Atualizações em contestações' },
  { key: 'documents', label: 'Documentos', icon: FileText, description: 'Status de processamento de documentos' },
  { key: 'payments', label: 'Pagamentos', icon: CreditCard, description: 'Confirmações e atualizações de pagamentos' },
  { key: 'reports', label: 'Relatórios', icon: BarChart2, description: 'Relatórios agendados prontos' },
] as const

const CHANNELS = [
  { key: 'email', label: 'Email', icon: Mail, description: 'Receber por email' },
  { key: 'push', label: 'Push', icon: Bell, description: 'Notificações no navegador' },
] as const

export function NotificationsPage() {
  const { user } = useAuth()
  const isAdminOrManager = user ? ['ADMIN', 'MANAGER'].includes(user.role) : false
  const [activeTab, setActiveTab] = useState<string>('preferences')

  // Preferences
  const { data: preferences, isLoading: loadingPrefs, refetch: refetchPrefs } = useNotificationPreferences(user?.id || '')
  const updatePreferences = useUpdateNotificationPreferences()

  // Templates (admin only)
  const { data: templates, isLoading: loadingTemplates, refetch: refetchTemplates } = useNotificationTemplates()
  const updateTemplate = useUpdateNotificationTemplate()

  // Local state for preferences
  const [prefs, setPrefs] = useState<Record<string, boolean>>({})

  useEffect(() => {
    if (preferences) {
      setPrefs({
        email: preferences.email ?? true,
        push: preferences.push ?? true,
        discrepancies: preferences.discrepancies ?? true,
        contests: preferences.contests ?? true,
        documents: preferences.documents ?? true,
        payments: preferences.payments ?? true,
        reports: preferences.reports ?? true,
      })
    }
  }, [preferences])

  const handlePrefChange = (key: string, value: boolean) => {
    setPrefs((prev) => ({ ...prev, [key]: value }))
  }

  const handleSavePreferences = async () => {
    try {
      await updatePreferences.mutateAsync({ userId: user?.id || '', data: prefs })
      toast.success('Preferências salvas com sucesso!')
      refetchPrefs()
    } catch (_err) {
      toast.error('Erro ao salvar preferências')
    }
  }

  // Local state for templates
  const [templateEdits, setTemplateEdits] = useState<Record<string, Partial<NotificationTemplate>>>({})

  const handleTemplateChange = (id: string, field: string, value: unknown) => {
    setTemplateEdits((prev) => ({
      ...prev,
      [id]: { ...prev[id], [field]: value },
    }))
  }

  const handleSaveTemplate = async (id: string) => {
    const edits = templateEdits[id]
    if (!edits) return
    try {
      await updateTemplate.mutateAsync({ id, data: edits })
      toast.success('Template atualizado!')
      setTemplateEdits((prev) => { const n = { ...prev }; delete n[id]; return n })
      refetchTemplates()
    } catch (_err) {
      toast.error('Erro ao atualizar template')
    }
  }

  if (loadingPrefs) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-secondary-100 rounded w-1/4" />
        <div className="h-24 bg-secondary-100 rounded-xl" />
        <div className="h-24 bg-secondary-100 rounded-xl" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Notificações</h1>
          <p className="text-secondary-500">
            {isAdminOrManager
              ? 'Configure preferências e gerencie templates de notificação'
              : 'Configure suas preferências de notificação'}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="preferences" className="flex items-center justify-center gap-2">
            <Bell className="h-4 w-4" />
            Minhas Preferências
          </TabsTrigger>
          {isAdminOrManager && (
            <TabsTrigger value="templates" className="flex items-center justify-center gap-2">
              <FileText className="h-4 w-4" />
              Templates (Admin)
            </TabsTrigger>
          )}
        </TabsList>

        {/* Preferences Tab */}
        <TabsContent value="preferences" className="space-y-6">
          {/* Channels */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-secondary-900 flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Canais de Notificação
              </h2>
            </CardHeader>
            <CardBody className="space-y-4">
              {CHANNELS.map((channel) => (
                <label key={channel.key} className="flex items-center justify-between p-4 rounded-lg border border-secondary-200 hover:bg-secondary-50">
                  <div className="flex items-center gap-3">
                    <channel.icon className="h-5 w-5 text-primary-600" />
                    <div>
                      <p className="font-medium text-secondary-900">{channel.label}</p>
                      <p className="text-sm text-secondary-500">{channel.description}</p>
                    </div>
                  </div>
                  <Switch
                    id={`channel-${channel.key}`}
                    checked={prefs[channel.key] ?? true}
                    onCheckedChange={(value) => handlePrefChange(channel.key, value)}
                  />
                </label>
              ))}
            </CardBody>
          </Card>

          {/* Types */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-secondary-900 flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Tipos de Notificação
              </h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <p className="text-sm text-secondary-500">
                Configure quais tipos de eventos geram notificações. O canal (email/push) segue a configuração acima.
              </p>
              {NOTIFICATION_TYPES.map((type) => (
                <label key={type.key} className="flex items-center justify-between p-4 rounded-lg border border-secondary-200 hover:bg-secondary-50">
                  <div className="flex items-center gap-3">
                    <type.icon className="h-5 w-5 text-primary-600" />
                    <div>
                      <p className="font-medium text-secondary-900">{type.label}</p>
                      <p className="text-sm text-secondary-500">{type.description}</p>
                    </div>
                  </div>
                  <Switch
                    id={`type-${type.key}`}
                    checked={prefs[type.key] ?? true}
                    onCheckedChange={(value) => handlePrefChange(type.key, value)}
                  />
                </label>
              ))}
            </CardBody>
          </Card>

          {/* Quiet Hours (placeholder) */}
          <Card>
            <CardHeader>
              <h2 className="font-semibold text-secondary-900 flex items-center gap-2">
                <Moon className="h-5 w-5" />
                Horário Silencioso
              </h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <p className="text-sm text-secondary-500">
                Defina um período em que não deseja receber notificações push (exceto urgentes).
              </p>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="quietStart" className="block text-sm font-medium text-secondary-700">
                    Início
                  </Label>
                  <Input id="quietStart" type="time" placeholder="22:00" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="quietEnd" className="block text-sm font-medium text-secondary-700">
                    Fim
                  </Label>
                  <Input id="quietEnd" type="time" placeholder="07:00" />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Switch id="quietEnabled" checked={false} onCheckedChange={() => {}} />
                <Label htmlFor="quietEnabled" className="text-sm font-medium text-secondary-700 cursor-pointer">
                  Ativar horário silencioso
                </Label>
              </div>
            </CardBody>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button variant="primary" onClick={handleSavePreferences} loading={updatePreferences.isPending} disabled={updatePreferences.isPending}>
              {updatePreferences.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Salvar Preferências
                </>
              )}
            </Button>
          </div>
        </TabsContent>

        {/* Templates Tab (Admin) */}
        {isAdminOrManager && (
          <TabsContent value="templates" className="space-y-6">
            <Card>
              <CardHeader>
                <h2 className="font-semibold text-secondary-900">Templates de Notificação</h2>
              </CardHeader>
              <CardBody>
                {loadingTemplates ? (
                  <div className="animate-pulse space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="h-20 bg-secondary-100 rounded" />
                    ))}
                  </div>
                ) : templates && templates.length > 0 ? (
                  <div className="space-y-4">
                    {templates.map((template) => {
                      const edits = templateEdits[template.id] || {}
                      const isEditing = !!edits
                      return (
                        <Card key={template.id} className="p-4">
                          <div className="flex items-start justify-between gap-4 mb-4">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-3">
                                <Badge variant="primary">{template.type}</Badge>
                                <Badge variant="secondary">{template.channel}</Badge>
                                <Badge variant={template.isActive ? 'success' : 'secondary'}>
                                  {template.isActive ? 'Ativo' : 'Inativo'}
                                </Badge>
                              </div>
                              <p className="text-sm text-secondary-500 mt-1">Variáveis: {template.variables.join(', ') || 'Nenhuma'}</p>
                            </div>
                            {isEditing ? (
                              <Button variant="primary" size="sm" onClick={() => handleSaveTemplate(template.id)} loading={updateTemplate.isPending}>
                                <CheckCircle className="h-4 w-4 mr-2" />
                                Salvar
                              </Button>
                            ) : (
                              <Button variant="ghost" size="sm" onClick={() => setTemplateEdits({...templateEdits, [template.id]: { subject: template.subject, body: template.body, isActive: template.isActive }})}>
                                Editar
                              </Button>
                            )}
                          </div>

                          {isEditing ? (
                            <div className="space-y-4">
                              <div className="space-y-2">
                                <Label className="block text-sm font-medium text-secondary-700">Assunto</Label>
                                <Input
                                  value={edits.subject || template.subject}
                                  onChange={(e) => handleTemplateChange(template.id, 'subject', e.target.value)}
                                />
                              </div>
                              <div className="space-y-2">
                                <Label className="block text-sm font-medium text-secondary-700">Corpo</Label>
                                <textarea
                                  value={edits.body || template.body}
                                  onChange={(e) => handleTemplateChange(template.id, 'body', e.target.value)}
                                  className="w-full p-3 border border-secondary-300 rounded-lg text-sm font-mono min-h-[120px] resize-y focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                                  placeholder="Template com variáveis: {{user_name}}, {{document_number}}, etc."
                                />
                              </div>
                              <div className="flex items-center gap-3">
                                <Switch
                                  id={`template-active-${template.id}`}
                                  checked={edits.isActive ?? template.isActive}
                                  onCheckedChange={(value) => handleTemplateChange(template.id, 'isActive', value)}
                                />
                                <Label htmlFor={`template-active-${template.id}`} className="text-sm font-medium text-secondary-700 cursor-pointer">
                                  Template ativo
                                </Label>
                              </div>
                            </div>
                          ) : (
                            <div className="space-y-2 text-sm">
                              <p className="font-medium text-secondary-900">{template.subject}</p>
                              <p className="text-secondary-500 font-mono whitespace-pre-wrap max-h-24 overflow-hidden">{template.body}</p>
                            </div>
                          )}
                        </Card>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="mx-auto h-12 w-12 text-secondary-300 mb-4" />
                    <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum template encontrado</h3>
                    <p className="text-secondary-500">Templates serão criados automaticamente pelo sistema</p>
                  </div>
                )}
              </CardBody>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}