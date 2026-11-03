import { useState, useEffect } from 'react'
import { Mail, Bell, Calendar, Save, X, Loader2 } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Switch, Label } from '@/components'
import toast from 'react-hot-toast'
import type { ScheduleResponse } from '@/hooks/useReports'

interface ScheduleFormProps {
  initialData?: ScheduleResponse | null
  onSubmit: (data: {
    name: string
    frequency: 'weekly'
    day_of_week: number
    hour: number
    format: 'pdf' | 'excel'
    filters: Record<string, unknown>
    recipients: string[]
    is_active: boolean
  }) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Domingo' },
  { value: 1, label: 'Segunda-feira' },
  { value: 2, label: 'Terça-feira' },
  { value: 3, label: 'Quarta-feira' },
  { value: 4, label: 'Quinta-feira' },
  { value: 5, label: 'Sexta-feira' },
  { value: 6, label: 'Sábado' },
]

const HOURS = Array.from({ length: 24 }, (_, i) => ({
  value: i,
  label: `${i.toString().padStart(2, '0')}:00`,
}))

export function ScheduleForm({ initialData, onSubmit, onCancel, isSubmitting = false }: ScheduleFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    frequency: 'weekly' as const,
    day_of_week: 1,
    hour: 9,
    format: 'pdf' as 'pdf' | 'excel',
    filters: {} as Record<string, unknown>,
    recipients: [] as string[],
    is_active: true,
  })
  const [recipientInput, setRecipientInput] = useState('')

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name,
        frequency: initialData.frequency,
        day_of_week: initialData.day_of_week,
        hour: initialData.hour,
        format: initialData.format,
        filters: initialData.filters as Record<string, unknown>,
        recipients: initialData.recipients,
        is_active: initialData.is_active,
      })
    }
  }, [initialData])

  const handleStringChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleNumberChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: Number(value) }))
  }

  const handleBooleanChange = (field: string, value: boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const addRecipient = () => {
    const email = recipientInput.trim()
    if (!email) return
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      toast.error('Email inválido')
      return
    }
    if (formData.recipients.includes(email)) {
      toast.error('Email já adicionado')
      return
    }
    setFormData((prev) => ({ ...prev, recipients: [...prev.recipients, email] }))
    setRecipientInput('')
  }

  const removeRecipient = (email: string) => {
    setFormData((prev) => ({ ...prev, recipients: prev.recipients.filter((e) => e !== email) }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name.trim()) {
      toast.error('Nome é obrigatório')
      return
    }
    if (formData.recipients.length === 0) {
      toast.error('Adicione pelo menos um destinatário')
      return
    }
    try {
      await onSubmit(formData)
      toast.success(initialData ? 'Agendamento atualizado!' : 'Agendamento criado!')
    } catch (_error) {
      toast.error('Erro ao salvar agendamento')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Info */}
      <div className="space-y-4">
        <h4 className="font-medium text-secondary-900 flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Configurações do Agendamento
        </h4>
        <div className="space-y-2">
          <Label htmlFor="name" className="block text-sm font-medium text-secondary-700">
            Nome do Agendamento *
          </Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => handleStringChange('name', e.target.value)}
            placeholder="Ex: Relatório Semanal de Discrepâncias"
            required
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label className="block text-sm font-medium text-secondary-700">Frequência</Label>
            <Select value={formData.frequency} onValueChange={(value) => handleStringChange('frequency', value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="weekly">Semanal</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label className="block text-sm font-medium text-secondary-700">Dia da Semana</Label>
            <Select value={String(formData.day_of_week)} onValueChange={(value) => handleNumberChange('day_of_week', value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DAYS_OF_WEEK.map((d) => (
                  <SelectItem key={d.value} value={String(d.value)}>
                    {d.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label className="block text-sm font-medium text-secondary-700">Horário</Label>
            <Select value={String(formData.hour)} onValueChange={(value) => handleNumberChange('hour', value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {HOURS.map((h) => (
                  <SelectItem key={h.value} value={String(h.value)}>
                    {h.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label className="block text-sm font-medium text-secondary-700">Formato</Label>
            <Select value={formData.format} onValueChange={(value) => handleStringChange('format', value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">PDF</SelectItem>
                <SelectItem value="excel">Excel</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Switch
            id="is_active"
            checked={formData.is_active}
            onCheckedChange={(value) => handleBooleanChange('is_active', value)}
          />
          <Label htmlFor="is_active" className="text-sm font-medium text-secondary-700 cursor-pointer">
            Agendamento ativo
          </Label>
        </div>
      </div>

      {/* Filters Summary */}
      <div className="space-y-4 p-4 rounded-lg bg-secondary-50 border border-secondary-200">
        <h4 className="font-medium text-secondary-900 flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Filtros do Relatório
        </h4>
        <p className="text-sm text-secondary-600">
          Os filtros abaixo serão aplicados automaticamente a cada execução do agendamento.
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          {Object.entries(formData.filters).map(([key, value]) => {
            if (value === undefined || value === '' || value === null) return null
            const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())
            return (
              <div key={key} className="flex items-center justify-between p-2 bg-white rounded border">
                <span className="text-sm text-secondary-700">{label}</span>
                <span className="text-sm font-medium text-secondary-900">{String(value)}</span>
              </div>
            )
          })}
          {Object.keys(formData.filters).length === 0 && (
            <p className="text-sm text-secondary-500 col-span-full text-center py-2">
              Nenhum filtro configurado (todos os dados serão incluídos)
            </p>
          )}
        </div>
      </div>

      {/* Recipients */}
      <div className="space-y-4">
        <h4 className="font-medium text-secondary-900 flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Destinatários
        </h4>
        <div className="flex gap-2">
          <Input
            type="email"
            value={recipientInput}
            onChange={(e) => setRecipientInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addRecipient())}
            placeholder="email@exemplo.com"
            className="flex-1"
          />
          <Button type="button" variant="secondary" onClick={addRecipient}>
            Adicionar
          </Button>
        </div>
        {formData.recipients.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.recipients.map((email) => (
              <Badge key={email} variant="secondary" className="flex items-center gap-1">
                <Mail className="h-3 w-3" />
                {email}
                <button type="button" onClick={() => removeRecipient(email)} className="ml-1 hover:text-danger-600">
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
        <Button type="button" variant="secondary" onClick={onCancel}>
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
              {initialData ? 'Atualizar' : 'Criar Agendamento'}
            </>
          )}
        </Button>
      </div>
    </form>
  )
}

import { Badge } from '@/components'