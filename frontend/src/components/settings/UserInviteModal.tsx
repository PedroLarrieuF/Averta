import { useState } from 'react'
import { X, UserPlus, Loader2, Mail, Shield } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Label, Modal } from '@/components'
import toast from 'react-hot-toast'

interface UserInviteModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: { email: string; role: 'ADMIN' | 'MANAGER' | 'AUDITOR' }) => Promise<void>
  isSubmitting?: boolean
}

const ROLE_OPTIONS = [
  { value: 'ADMIN', label: 'Administrador', description: 'Acesso total ao sistema' },
  { value: 'MANAGER', label: 'Gestor', description: 'Gerencia transportadoras, contratos e relatórios' },
  { value: 'AUDITOR', label: 'Auditor', description: 'Visualiza discrepâncias e relatórios' },
] as const

export function UserInviteModal({ open, onOpenChange, onSubmit, isSubmitting = false }: UserInviteModalProps) {
  const [formData, setFormData] = useState({ email: '', role: 'AUDITOR' as 'ADMIN' | 'MANAGER' | 'AUDITOR' })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return

    try {
      await onSubmit(formData)
      toast.success('Convite enviado com sucesso!')
      onOpenChange(false)
      setFormData({ email: '', role: 'AUDITOR' })
      setErrors({})
    } catch (_error) {
      toast.error('Erro ao enviar convite')
    }
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }))
    }
  }

  const handleClose = () => {
    onOpenChange(false)
    setFormData({ email: '', role: 'AUDITOR' })
    setErrors({})
  }

  return (
    <Modal
      open={open}
      onOpenChange={handleClose}
      title="Convidar Usuário"
      size="md"
      description="Preencha os dados para convidar um novo usuário"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className="block text-sm font-medium text-secondary-700">
            Email *
          </Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="usuario@empresa.com"
              error={errors.email}
              className="pl-10"
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="role" className="block text-sm font-medium text-secondary-700">
            Função *
          </Label>
          <Select value={formData.role} onValueChange={(value) => handleChange('role', value as 'ADMIN' | 'MANAGER' | 'AUDITOR')}>
            <SelectTrigger className={errors.role ? 'border-danger-500' : ''}>
              <SelectValue placeholder="Selecione uma função" />
            </SelectTrigger>
            <SelectContent>
              {ROLE_OPTIONS.map((role) => (
                <SelectItem key={role.value} value={role.value}>
                  <div className="flex items-start gap-3 py-2">
                    <Shield className="h-4 w-4 mt-0.5 text-primary-600 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-secondary-900">{role.label}</p>
                      <p className="text-xs text-secondary-500">{role.description}</p>
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.role && <p className="text-sm text-danger-600">{errors.role}</p>}
        </div>

        <div className="p-3 rounded-lg bg-secondary-50 border border-secondary-200">
          <p className="text-sm text-secondary-700">
            <strong>O que acontece:</strong> O usuário receberá um email com link para definir a senha e acessar o sistema.
            O convite expira em 7 dias.
          </p>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
          <Button type="button" variant="secondary" onClick={handleClose} disabled={isSubmitting}>
            <X className="h-4 w-4 mr-2" />
            Cancelar
          </Button>
          <Button type="submit" variant="primary" loading={isSubmitting} disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Enviando...
              </>
            ) : (
              <>
                <UserPlus className="h-4 w-4 mr-2" />
                Enviar Convite
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  )
}