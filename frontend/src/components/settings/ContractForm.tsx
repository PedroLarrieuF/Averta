import { useState, useEffect } from 'react'
import { X, Save, Loader2, Truck, Hash, ChevronDown, ChevronUp } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Label, Modal, Card, CardHeader, CardBody } from '@/components'
import toast from 'react-hot-toast'
import type { Contract, Client, Carrier, FreightTableEntry, FreightType, ContractStatus } from '@/types'

interface ContractFormProps {
  initialData?: Partial<Contract> | null
  clients: Client[]
  carriers: Carrier[]
  onSubmit: (data: Partial<Contract>) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
  mode: 'create' | 'edit'
}

const FREIGHT_TYPES: { value: FreightType; label: string }[] = [
  { value: 'NORMAL', label: 'Normal' },
  { value: 'EXPRESS', label: 'Expresso' },
  { value: 'FRACIONADO', label: 'Fracionado' },
  { value: 'CARGA_FECHADA', label: 'Carga Fechada' },
]

const CONTRACT_STATUSES: { value: ContractStatus; label: string }[] = [
  { value: 'DRAFT', label: 'Rascunho' },
  { value: 'ACTIVE', label: 'Ativo' },
  { value: 'EXPIRED', label: 'Expirado' },
  { value: 'CANCELLED', label: 'Cancelado' },
]

export function ContractForm({ initialData, clients, carriers, onSubmit, onCancel, isSubmitting = false, mode }: ContractFormProps) {
  const [formData, setFormData] = useState<Partial<Contract>>({
    name: '',
    number: '',
    clientId: '',
    carrierId: '',
    status: 'DRAFT',
    startDate: '',
    endDate: '',
    version: 1,
    freightTable: [],
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showFreightTable, setShowFreightTable] = useState(false)
  const [editingFreightEntry, setEditingFreightEntry] = useState<FreightTableEntry | null>(null)
  const [freightFormData, setFreightFormData] = useState<Partial<FreightTableEntry>>({})
  const [freightModalOpen, setFreightModalOpen] = useState(false)

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        number: initialData.number || '',
        clientId: initialData.clientId || '',
        carrierId: initialData.carrierId || '',
        status: initialData.status || 'DRAFT',
        startDate: initialData.startDate ? initialData.startDate.split('T')[0] : '',
        endDate: initialData.endDate ? initialData.endDate.split('T')[0] : '',
        version: initialData.version || 1,
        freightTable: initialData.freightTable || [],
      })
    } else {
      setFormData({
        name: '',
        number: '',
        clientId: '',
        carrierId: '',
        status: 'DRAFT',
        startDate: '',
        endDate: '',
        version: 1,
        freightTable: [],
      })
    }
  }, [initialData])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.name?.trim()) newErrors.name = 'Nome é obrigatório'
    if (!formData.number?.trim()) newErrors.number = 'Número do contrato é obrigatório'
    if (!formData.clientId) newErrors.clientId = 'Cliente é obrigatório'
    if (!formData.carrierId) newErrors.carrierId = 'Transportadora é obrigatória'
    if (!formData.startDate) newErrors.startDate = 'Data de início é obrigatória'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (field: string, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return

    const submitData = {
      ...formData,
      version: mode === 'create' ? 1 : (formData.version || 1),
      freightTable: formData.freightTable || [],
    }

    try {
      await onSubmit(submitData)
      toast.success(mode === 'create' ? 'Contrato criado com sucesso!' : 'Contrato atualizado com sucesso!')
      onCancel()
    } catch (_error) {
      toast.error('Erro ao salvar contrato')
    }
  }

  const openFreightTableModal = () => setShowFreightTable(true)

  const openEditFreightEntry = (entry: FreightTableEntry) => {
    setEditingFreightEntry(entry)
    setFreightFormData({ ...entry })
    setFreightModalOpen(true)
  }

  const openNewFreightEntry = () => {
    setEditingFreightEntry(null)
    setFreightFormData({
      originCity: '',
      originState: '',
      destinationCity: '',
      destinationState: '',
      freightType: 'NORMAL',
      weightMin: 0,
      weightMax: 0,
      value: 0,
      valueType: 'FIXED',
    })
    setFreightModalOpen(true)
  }

  const handleFreightChange = (field: string, value: unknown) => {
    setFreightFormData((prev) => ({ ...prev, [field]: value }))
  }

  const saveFreightEntry = () => {
    if (!freightFormData.originCity?.trim()) { toast.error('Cidade de origem é obrigatória'); return }
    if (!freightFormData.destinationCity?.trim()) { toast.error('Cidade de destino é obrigatória'); return }
    if (!freightFormData.originState?.trim()) { toast.error('Estado de origem é obrigatório'); return }
    if (!freightFormData.destinationState?.trim()) { toast.error('Estado de destino é obrigatório'); return }
    if (freightFormData.weightMin === undefined || freightFormData.weightMin === null) { toast.error('Peso mínimo é obrigatório'); return }
    if (freightFormData.weightMax === undefined || freightFormData.weightMax === null) { toast.error('Peso máximo é obrigatório'); return }
    if (freightFormData.value === undefined || freightFormData.value === null) { toast.error('Valor é obrigatório'); return }

    const entry: FreightTableEntry = {
      id: editingFreightEntry?.id || crypto.randomUUID(),
      originCity: freightFormData.originCity || '',
      originState: freightFormData.originState || '',
      destinationCity: freightFormData.destinationCity || '',
      destinationState: freightFormData.destinationState || '',
      freightType: freightFormData.freightType || 'NORMAL',
      weightMin: Number(freightFormData.weightMin) || 0,
      weightMax: Number(freightFormData.weightMax) || 0,
      volumeMin: freightFormData.volumeMin ? Number(freightFormData.volumeMin) : undefined,
      volumeMax: freightFormData.volumeMax ? Number(freightFormData.volumeMax) : undefined,
      value: Number(freightFormData.value) || 0,
      valueType: freightFormData.valueType || 'FIXED',
      icms: freightFormData.icms ? Number(freightFormData.icms) : undefined,
      tolls: freightFormData.tolls ? Number(freightFormData.tolls) : undefined,
    }

    setFormData((prev) => ({
      ...prev,
      freightTable: editingFreightEntry
        ? prev.freightTable?.map((e) => (e.id === entry.id ? entry : e)) || []
        : [...(prev.freightTable || []), entry]
    }))

    setEditingFreightEntry(null)
    setFreightFormData({})
    setFreightModalOpen(false)
  }

  const deleteFreightEntry = (id: string) => {
    if (!confirm('Excluir esta regra de frete?')) return
    setFormData((prev) => ({
      ...prev,
      freightTable: prev.freightTable?.filter((e) => e.id !== id) || []
    }))
  }

  return (
    <>
      <Modal
        open={true}
        onOpenChange={onCancel}
        title={mode === 'create' ? 'Novo Contrato' : 'Editar Contrato'}
        size="xl"
      >
        <form onSubmit={handleSubmit} className="flex-1 overflow-auto">
          <div className="space-y-6 p-6 pb-0">
            {/* Basic Info */}
            <Card>
              <CardHeader>
                <h4 className="font-medium text-secondary-900 flex items-center gap-2">
                  <Hash className="h-5 w-5" />
                  Informações Básicas
                </h4>
              </CardHeader>
              <CardBody className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="block text-sm font-medium text-secondary-700">
                      Nome do Contrato *
                    </Label>
                    <Input
                      id="name"
                      value={formData.name || ''}
                      onChange={(e) => handleChange('name', e.target.value)}
                      placeholder="Ex: Contrato de Frete SP-RJ"
                      error={errors.name}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="number" className="block text-sm font-medium text-secondary-700">
                      Número do Contrato *
                    </Label>
                    <Input
                      id="number"
                      value={formData.number || ''}
                      onChange={(e) => handleChange('number', e.target.value)}
                      placeholder="Ex: CT-2024-001"
                      error={errors.number}
                      required
                    />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="clientId" className="block text-sm font-medium text-secondary-700">
                      Cliente *
                    </Label>
                    <Select value={formData.clientId || ''} onValueChange={(value) => handleChange('clientId', value)}>
                      <SelectTrigger className={errors.clientId ? 'border-danger-500' : ''}>
                        <SelectValue placeholder="Selecione um cliente" />
                      </SelectTrigger>
                      <SelectContent>
                        {clients.map((client) => (
                          <SelectItem key={client.id} value={client.id}>
                            {client.name} ({client.cnpj})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.clientId && <p className="text-sm text-danger-600">{errors.clientId}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="carrierId" className="block text-sm font-medium text-secondary-700">
                      Transportadora *
                    </Label>
                    <Select value={formData.carrierId || ''} onValueChange={(value) => handleChange('carrierId', value)}>
                      <SelectTrigger className={errors.carrierId ? 'border-danger-500' : ''}>
                        <SelectValue placeholder="Selecione uma transportadora" />
                      </SelectTrigger>
                      <SelectContent>
                        {carriers.map((carrier) => (
                          <SelectItem key={carrier.id} value={carrier.id}>
                            {carrier.name} ({carrier.cnpj})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.carrierId && <p className="text-sm text-danger-600">{errors.carrierId}</p>}
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="space-y-2">
                    <Label htmlFor="status" className="block text-sm font-medium text-secondary-700">
                      Status
                    </Label>
                    <Select value={formData.status || 'DRAFT'} onValueChange={(value) => handleChange('status', value as ContractStatus)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CONTRACT_STATUSES.map((s) => (
                          <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="startDate" className="block text-sm font-medium text-secondary-700">
                      Data de Início *
                    </Label>
                    <Input
                      id="startDate"
                      type="date"
                      value={formData.startDate || ''}
                      onChange={(e) => handleChange('startDate', e.target.value)}
                      error={errors.startDate}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="endDate" className="block text-sm font-medium text-secondary-700">
                      Data de Fim
                    </Label>
                    <Input
                      id="endDate"
                      type="date"
                      value={formData.endDate || ''}
                      onChange={(e) => handleChange('endDate', e.target.value)}
                    />
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Freight Table */}
            <Card>
              <CardHeader className="flex items-center justify-between">
                <h4 className="font-medium text-secondary-900 flex items-center gap-2">
                  <Truck className="h-5 w-5" />
                  Tabela de Frete
                </h4>
                <Button variant="secondary" size="sm" onClick={openFreightTableModal}>
                  <span className="flex items-center gap-1">
                    {showFreightTable ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    {showFreightTable ? 'Ocultar' : 'Configurar'}
                  </span>
                </Button>
              </CardHeader>

              {showFreightTable && (
                <CardBody className="space-y-4">
                  {formData.freightTable && formData.freightTable.length > 0 ? (
                    <div className="space-y-2">
                      {formData.freightTable.map((entry) => (
                        <div key={entry.id} className="p-3 bg-secondary-50 rounded-lg border border-secondary-200 flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-secondary-900 truncate">
                              {entry.originCity}/{entry.originState} → {entry.destinationCity}/{entry.destinationState}
                            </p>
                            <p className="text-sm text-secondary-500">
                              {FREIGHT_TYPES.find(t => t.value === entry.freightType)?.label || entry.freightType} •
                              {entry.weightMin}–{entry.weightMax} kg •
                              {entry.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} ({entry.valueType})
                            </p>
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <Button variant="ghost" size="sm" onClick={() => openEditFreightEntry(entry)}>
                              Editar
                            </Button>
                            <Button variant="ghost" size="sm" className="text-danger-600 hover:bg-danger-50" onClick={() => deleteFreightEntry(entry.id)}>
                              Excluir
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-secondary-500">
                      <p>Nenhuma regra de frete configurada</p>
                      <Button variant="secondary" size="sm" className="mt-2" onClick={openNewFreightEntry}>
                        Adicionar primeira regra
                      </Button>
                    </div>
                  )}

                  <div className="pt-4 border-t border-secondary-200">
                    <Button variant="secondary" size="sm" onClick={openNewFreightEntry} className="w-full sm:w-auto">
                      <span className="flex items-center justify-center gap-2">
                        <Truck className="h-4 w-4" />
                        Adicionar Regra de Frete
                      </span>
                    </Button>
                  </div>
                </CardBody>
              )}
            </Card>
          </div>

          <div className="flex justify-end gap-3 p-6 border-t border-secondary-200">
            <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting}>
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
            <Button type="submit" variant="primary" loading={isSubmitting} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {mode === 'create' ? 'Criar Contrato' : 'Atualizar Contrato'}
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Freight Table Entry Modal */}
      <Modal
        open={freightModalOpen}
        onOpenChange={setFreightModalOpen}
        title={editingFreightEntry ? 'Editar Regra de Frete' : 'Nova Regra de Frete'}
        size="md"
      >
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Cidade de Origem *</Label>
              <Input value={freightFormData.originCity || ''} onChange={(e) => handleFreightChange('originCity', e.target.value)} placeholder="São Paulo" required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Estado de Origem *</Label>
              <Input value={freightFormData.originState || ''} onChange={(e) => handleFreightChange('originState', e.target.value)} placeholder="SP" maxLength={2} required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Cidade de Destino *</Label>
              <Input value={freightFormData.destinationCity || ''} onChange={(e) => handleFreightChange('destinationCity', e.target.value)} placeholder="Rio de Janeiro" required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Estado de Destino *</Label>
              <Input value={freightFormData.destinationState || ''} onChange={(e) => handleFreightChange('destinationState', e.target.value)} placeholder="RJ" maxLength={2} required />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Tipo de Frete</Label>
              <Select value={freightFormData.freightType || 'NORMAL'} onValueChange={(value) => handleFreightChange('freightType', value)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {FREIGHT_TYPES.map((t) => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Tipo de Valor</Label>
              <Select value={freightFormData.valueType || 'FIXED'} onValueChange={(value) => handleFreightChange('valueType', value)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="FIXED">Fixo</SelectItem>
                  <SelectItem value="PER_KG">Por kg</SelectItem>
                  <SelectItem value="PER_VOLUME">Por volume</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Peso Mínimo (kg) *</Label>
              <Input type="number" min="0" step="0.01" value={freightFormData.weightMin || ''} onChange={(e) => handleFreightChange('weightMin', Number(e.target.value))} required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Peso Máximo (kg) *</Label>
              <Input type="number" min="0" step="0.01" value={freightFormData.weightMax || ''} onChange={(e) => handleFreightChange('weightMax', Number(e.target.value))} required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Valor *</Label>
              <Input type="number" min="0" step="0.01" value={freightFormData.value || ''} onChange={(e) => handleFreightChange('value', Number(e.target.value))} required />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Volume Mínimo (m³)</Label>
              <Input type="number" min="0" step="0.01" value={freightFormData.volumeMin || ''} onChange={(e) => handleFreightChange('volumeMin', e.target.value ? Number(e.target.value) : undefined)} />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Volume Máximo (m³)</Label>
              <Input type="number" min="0" step="0.01" value={freightFormData.volumeMax || ''} onChange={(e) => handleFreightChange('volumeMax', e.target.value ? Number(e.target.value) : undefined)} />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">ICMS (%)</Label>
              <Input type="number" min="0" max="100" step="0.01" value={freightFormData.icms || ''} onChange={(e) => handleFreightChange('icms', e.target.value ? Number(e.target.value) : undefined)} />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Pedágios</Label>
              <Input type="number" min="0" step="0.01" value={freightFormData.tolls || ''} onChange={(e) => handleFreightChange('tolls', e.target.value ? Number(e.target.value) : undefined)} />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
            <Button variant="secondary" onClick={() => setFreightModalOpen(false)}>
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
            <Button variant="primary" onClick={saveFreightEntry}>
              <Save className="h-4 w-4 mr-2" />
              {editingFreightEntry ? 'Atualizar' : 'Adicionar'}
            </Button>
          </div>
        </div>
      </Modal>
    </>
  )
}