import { useState, useEffect } from 'react'
import { X, Save, Loader2, FileText, AlertCircle, Trash2, Edit, Copy } from 'lucide-react'
import { Button, Input, Textarea, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Label, Card, CardBody, Badge, Modal, Tabs, TabsList, TabsTrigger, TabsContent } from '@/components'
import toast from 'react-hot-toast'
// import type { FreightTableEntry } from '@/types'

interface FreightTableEditorProps {
  initialRules: Record<string, unknown>[]
  onSave: (rules: Record<string, unknown>[]) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
}

export function FreightTableEditor({ initialRules, onSave, onCancel, isSubmitting = false }: FreightTableEditorProps) {
  const [jsonText, setJsonText] = useState('')
  const [parsedRules, setParsedRules] = useState<Record<string, unknown>[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState<string>('visual')
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [editFormData, setEditFormData] = useState<Record<string, unknown>>({})
  const [freightModalOpen, setFreightModalOpen] = useState(false)

  useEffect(() => {
    if (initialRules && initialRules.length > 0) {
      setParsedRules(initialRules)
      setJsonText(JSON.stringify(initialRules, null, 2))
    } else {
      setParsedRules([])
      setJsonText('[]')
    }
  }, [initialRules])

  const validateJson = (text: string): { valid: boolean; rules: Record<string, unknown>[]; errors: string[] } => {
    try {
      const parsed = JSON.parse(text)
      if (!Array.isArray(parsed)) {
        return { valid: false, rules: [], errors: ['O JSON deve ser um array de objetos'] }
      }
      const validationErrors: string[] = []
      parsed.forEach((rule, index) => {
        if (typeof rule !== 'object' || rule === null) {
          validationErrors.push(`Item ${index}: deve ser um objeto`)
          return
        }
        const required = ['originCity', 'originState', 'destinationCity', 'destinationState', 'freightType', 'weightMin', 'weightMax', 'value', 'valueType']
        required.forEach((field) => {
          if (!(field in rule)) {
            validationErrors.push(`Item ${index}: campo obrigatório "${field}" ausente`)
          }
        })
      })
      return { valid: validationErrors.length === 0, rules: parsed, errors: validationErrors }
    } catch (e) {
      return { valid: false, rules: [], errors: ['JSON inválido: ' + (e as Error).message] }
    }
  }

  const handleJsonChange = (text: string) => {
    setJsonText(text)
    const { valid, rules, errors: validationErrors } = validateJson(text)
    if (valid) {
      setParsedRules(rules)
    }
    setErrors(validationErrors)
  }

  const handleSave = async () => {
    const { valid, rules, errors: validationErrors } = validateJson(activeTab === 'visual' ? JSON.stringify(parsedRules) : jsonText)
    if (!valid) {
      setErrors(validationErrors)
      setActiveTab('json')
      toast.error('Erros de validação encontrados')
      return
    }
    try {
      await onSave(rules)
      toast.success('Tabela de frete salva com sucesso!')
      onCancel()
    } catch (_error) {
      toast.error('Erro ao salvar tabela de frete')
    }
  }

  
  const openEditRule = (index: number) => {
    setEditingIndex(index)
    setEditFormData({ ...parsedRules[index] })
    setFreightModalOpen(true)
  }

  const closeEditRule = () => {
    setEditingIndex(null)
    setEditFormData({})
    setFreightModalOpen(false)
  }

  const saveEditRule = () => {
    const newRules = [...parsedRules]
    newRules[editingIndex!] = editFormData
    setParsedRules(newRules)
    setJsonText(JSON.stringify(newRules, null, 2))
    closeEditRule()
  }

  const deleteRule = (index: number) => {
    if (!confirm('Excluir esta regra?')) return
    const newRules = parsedRules.filter((_, i) => i !== index)
    setParsedRules(newRules)
    setJsonText(JSON.stringify(newRules, null, 2))
  }

  const duplicateRule = (index: number) => {
    const newRules = [...parsedRules]
    const duplicated = { ...parsedRules[index], id: crypto.randomUUID() }
    newRules.splice(index + 1, 0, duplicated)
    setParsedRules(newRules)
    setJsonText(JSON.stringify(newRules, null, 2))
  }

  const addNewRule = () => {
    const newRule: Record<string, unknown> = {
      originCity: '',
      originState: '',
      destinationCity: '',
      destinationState: '',
      freightType: 'NORMAL',
      weightMin: 0,
      weightMax: 0,
      value: 0,
      valueType: 'FIXED',
    }
    const newRules = [...parsedRules, newRule]
    setParsedRules(newRules)
    setJsonText(JSON.stringify(newRules, null, 2))
    setEditingIndex(newRules.length - 1)
    setEditFormData(newRule)
    setFreightModalOpen(true)
  }

  return (
    <>
      <Modal
        open={true}
        onOpenChange={onCancel}
        title="Editor de Tabela de Frete"
        size="xl"
      >
        <form className="flex-1 overflow-auto" onSubmit={(e) => { e.preventDefault(); handleSave() }}>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-2 border-b border-secondary-200">
              <TabsTrigger value="visual" className="flex items-center justify-center gap-2">
                <span>Visual</span>
                <Badge variant={parsedRules.length > 0 ? 'primary' : 'secondary'}>{parsedRules.length}</Badge>
              </TabsTrigger>
              <TabsTrigger value="json" className="flex items-center justify-center gap-2">
                <FileText className="h-4 w-4" />
                JSON
                {errors.length > 0 && <Badge variant="danger">{errors.length}</Badge>}
              </TabsTrigger>
            </TabsList>

            {/* Visual Editor */}
            <TabsContent value="visual" className="flex-1 overflow-auto p-4 space-y-4">
              {parsedRules.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 text-secondary-300 mx-auto mb-4" />
                  <p className="text-secondary-500 mb-4">Nenhuma regra de frete configurada</p>
                  <Button variant="primary" type="button" onClick={addNewRule}>
                    Adicionar primeira regra
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {parsedRules.map((rule, index) => (
                    <Card key={index} className={editingIndex === index ? 'ring-2 ring-primary-500' : ''}>
                      <CardBody className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-1">
                              <span className="font-medium text-secondary-900 truncate">
                                {rule.originCity as string}/{rule.originState as string} → {rule.destinationCity as string}/{rule.destinationState as string}
                              </span>
                              <Badge variant="secondary">{rule.freightType as string}</Badge>
                              <Badge variant="primary">{rule.valueType as string}</Badge>
                            </div>
                            <p className="text-sm text-secondary-500">
                              {rule.weightMin as number}–{rule.weightMax as number} kg •
                              {Number(rule.value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                              {rule.volumeMin !== undefined && rule.volumeMax !== undefined ? ` • ${rule.volumeMin as number}–${rule.volumeMax as number} m³` : ''}
                              {rule.icms !== undefined ? ` • ICMS: ${rule.icms as number}%` : ''}
                              {rule.tolls !== undefined ? ` • Pedágios: ${Number(rule.tolls).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}` : ''}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <Button variant="ghost" size="sm" onClick={() => openEditRule(index)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => duplicateRule(index)}>
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="text-danger-600 hover:bg-danger-50" onClick={() => deleteRule(index)}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardBody>
                    </Card>
                  ))}
                </div>
              )}

              <div className="pt-4 border-t border-secondary-200 flex justify-end">
                <Button variant="secondary" type="button" onClick={addNewRule} className="w-full sm:w-auto">
                  <span className="flex items-center justify-center gap-2">
                    <FileText className="h-4 w-4" />
                    Adicionar Nova Regra
                  </span>
                </Button>
              </div>
            </TabsContent>

            {/* JSON Editor */}
            <TabsContent value="json" className="flex-1 overflow-auto p-4 space-y-4">
              {errors.length > 0 && (
                <div className="p-4 rounded-lg bg-danger-50 border border-danger-200">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 text-danger-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-danger-800">Erros de validação:</p>
                      <ul className="list-disc list-inside text-sm text-danger-700 mt-1 space-y-1">
                        {errors.map((error, i) => <li key={i}>{error}</li>)}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
              <div className="space-y-2">
                <Label className="block text-sm font-medium text-secondary-700">JSON da Tabela de Frete</Label>
                <Textarea
                  value={jsonText}
                  onChange={(e) => handleJsonChange(e.target.value)}
                  placeholder='[{"originCity": "São Paulo", "originState": "SP", "destinationCity": "Rio de Janeiro", "destinationState": "RJ", "freightType": "NORMAL", "weightMin": 0, "weightMax": 1000, "value": 500, "valueType": "FIXED"}]'
                  className="font-mono text-sm h-[400px]"
                  rows={20}
                />
                <p className="text-xs text-secondary-500">
                  {parsedRules.length} regra(s) • Formato: array de objetos com campos obrigatórios
                </p>
              </div>
            </TabsContent>
          </Tabs>

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
                  Salvar Tabela de Frete
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Rule Modal */}
      <Modal
        open={freightModalOpen}
        onOpenChange={closeEditRule}
        title={editingIndex !== null ? 'Editar Regra' : 'Nova Regra'}
        size="md"
      >
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Cidade de Origem *</Label>
              <Input value={editFormData.originCity as string} onChange={(e) => setEditFormData({...editFormData, originCity: e.target.value})} placeholder="São Paulo" required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Estado de Origem *</Label>
              <Input value={editFormData.originState as string} onChange={(e) => setEditFormData({...editFormData, originState: e.target.value})} placeholder="SP" maxLength={2} required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Cidade de Destino *</Label>
              <Input value={editFormData.destinationCity as string} onChange={(e) => setEditFormData({...editFormData, destinationCity: e.target.value})} placeholder="Rio de Janeiro" required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Estado de Destino *</Label>
              <Input value={editFormData.destinationState as string} onChange={(e) => setEditFormData({...editFormData, destinationState: e.target.value})} placeholder="RJ" maxLength={2} required />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Tipo de Frete</Label>
              <Select value={editFormData.freightType as string} onValueChange={(value) => setEditFormData({...editFormData, freightType: value})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="NORMAL">Normal</SelectItem>
                  <SelectItem value="EXPRESS">Expresso</SelectItem>
                  <SelectItem value="FRACIONADO">Fracionado</SelectItem>
                  <SelectItem value="CARGA_FECHADA">Carga Fechada</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Tipo de Valor</Label>
              <Select value={editFormData.valueType as string} onValueChange={(value) => setEditFormData({...editFormData, valueType: value})}>
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
              <Input type="number" min="0" step="0.01" value={editFormData.weightMin as number} onChange={(e) => setEditFormData({...editFormData, weightMin: Number(e.target.value)})} required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Peso Máximo (kg) *</Label>
              <Input type="number" min="0" step="0.01" value={editFormData.weightMax as number} onChange={(e) => setEditFormData({...editFormData, weightMax: Number(e.target.value)})} required />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Valor *</Label>
              <Input type="number" min="0" step="0.01" value={editFormData.value as number} onChange={(e) => setEditFormData({...editFormData, value: Number(e.target.value)})} required />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Volume Mínimo (m³)</Label>
              <Input type="number" min="0" step="0.01" value={editFormData.volumeMin as number} onChange={(e) => setEditFormData({...editFormData, volumeMin: e.target.value ? Number(e.target.value) : undefined})} />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Volume Máximo (m³)</Label>
              <Input type="number" min="0" step="0.01" value={editFormData.volumeMax as number} onChange={(e) => setEditFormData({...editFormData, volumeMax: e.target.value ? Number(e.target.value) : undefined})} />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">ICMS (%)</Label>
              <Input type="number" min="0" max="100" step="0.01" value={editFormData.icms as number} onChange={(e) => setEditFormData({...editFormData, icms: e.target.value ? Number(e.target.value) : undefined})} />
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Pedágios</Label>
              <Input type="number" min="0" step="0.01" value={editFormData.tolls as number} onChange={(e) => setEditFormData({...editFormData, tolls: e.target.value ? Number(e.target.value) : undefined})} />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
            <Button variant="secondary" onClick={closeEditRule}>
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
            <Button variant="primary" onClick={saveEditRule}>
              <Save className="h-4 w-4 mr-2" />
              {editingIndex !== null ? 'Atualizar' : 'Adicionar'}
            </Button>
          </div>
        </div>
      </Modal>
    </>
  )
}