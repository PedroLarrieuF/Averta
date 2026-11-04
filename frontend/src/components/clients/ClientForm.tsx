import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Modal, Switch } from '@/components'
import { Client } from '@/types'

function validateCNPJ(cnpj: string): boolean {
  const cleaned = cnpj.replace(/\D/g, '')
  if (cleaned.length !== 14) return false
  if (/^(\d)\1+$/.test(cleaned)) return false

  let sum = 0
  let weight = 2
  for (let i = 11; i >= 0; i--) {
    sum += parseInt(cleaned[i]) * weight
    weight = weight === 9 ? 2 : weight + 1
  }
  let digit = 11 - (sum % 11)
  if (digit >= 10) digit = 0
  if (parseInt(cleaned[12]) !== digit) return false

  sum = 0
  weight = 2
  for (let i = 12; i >= 0; i--) {
    sum += parseInt(cleaned[i]) * weight
    weight = weight === 9 ? 2 : weight + 1
  }
  digit = 11 - (sum % 11)
  if (digit >= 10) digit = 0
  return parseInt(cleaned[13]) === digit
}

function validateCPF(cpf: string): boolean {
  const cleaned = cpf.replace(/\D/g, '')
  if (cleaned.length !== 11) return false
  if (/^(\d)\1+$/.test(cleaned)) return false

  let sum = 0
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleaned[i]) * (10 - i)
  }
  let digit = 11 - (sum % 11)
  if (digit >= 10) digit = 0
  if (parseInt(cleaned[9]) !== digit) return false

  sum = 0
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleaned[i]) * (11 - i)
  }
  digit = 11 - (sum % 11)
  if (digit >= 10) digit = 0
  return parseInt(cleaned[10]) === digit
}

function validCNPJorCPF(value: string): boolean {
  const cleaned = value.replace(/\D/g, '')
  if (cleaned.length === 14) return validateCNPJ(cleaned)
  if (cleaned.length === 11) return validateCPF(cleaned)
  return false
}

const addressSchema = z.object({
  street: z.string().optional(),
  number: z.string().optional(),
  complement: z.string().optional(),
  neighborhood: z.string().optional(),
  city: z.string().optional(),
  state: z.string().length(2, 'UF deve ter 2 caracteres').optional(),
  zip: z.string().optional(),
})

export const clientSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  document: z.string().refine(validCNPJorCPF, 'CNPJ/CPF inválido'),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().optional(),
  address: addressSchema.optional(),
  status: z.enum(['ACTIVE', 'INACTIVE']),
})

export type ClientFormData = z.infer<typeof clientSchema>

interface ClientFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: ClientFormData) => Promise<void>
  client?: Client | null
  isLoading?: boolean
  title?: string
}

export function ClientForm({ open, onOpenChange, onSubmit, client, isLoading = false, title }: ClientFormProps) {
  const isEditing = !!client

  const form = useForm<ClientFormData>({
    resolver: zodResolver(clientSchema),
    defaultValues: {
      name: '',
      document: '',
      email: '',
      phone: '',
      address: {
        street: '',
        number: '',
        complement: '',
        neighborhood: '',
        city: '',
        state: '',
        zip: '',
      },
      status: 'ACTIVE',
    },
  })

  useEffect(() => {
    if (client) {
      form.reset({
        name: client.name,
        document: client.cnpj,
        email: client.email || '',
        phone: client.phone || '',
        address: {
          street: client.address || '',
          number: '',
          complement: '',
          neighborhood: '',
          city: client.city || '',
          state: client.state || '',
          zip: client.zipCode || '',
        },
        status: client.status || 'ACTIVE',
      })
    } else {
      form.reset({
        name: '',
        document: '',
        email: '',
        phone: '',
        address: {
          street: '',
          number: '',
          complement: '',
          neighborhood: '',
          city: '',
          state: '',
          zip: '',
        },
        status: 'ACTIVE',
      })
    }
  }, [client, form])

  const handleSubmit = async (data: ClientFormData) => {
    const submitData = {
      ...data,
      cnpj: data.document,
      zipCode: data.address?.zip,
    }
    await onSubmit(submitData as any)
  }

  const stateError = form.formState.errors.address?.state?.message

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={title || (isEditing ? 'Editar Cliente' : 'Novo Cliente')}
      size="lg"
      showClose
    >
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Nome *"
            placeholder="Nome do cliente"
            {...form.register('name')}
            error={form.formState.errors.name?.message}
          />
          <Input
            label="Documento (CNPJ/CPF) *"
            placeholder="00.000.000/0000-00"
            {...form.register('document')}
            error={form.formState.errors.document?.message}
            onChange={(e) => {
              const value = e.target.value.replace(/\D/g, '')
              let formatted = value
              if (value.length <= 11) {
                formatted = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
              } else {
                formatted = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5')
              }
              form.setValue('document', formatted, { shouldValidate: true })
            }}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Email"
            type="email"
            placeholder="cliente@exemplo.com"
            {...form.register('email')}
            error={form.formState.errors.email?.message}
          />
          <Input
            label="Telefone"
            placeholder="(00) 00000-0000"
            {...form.register('phone')}
          />
        </div>

        <div className="space-y-4 border-t border-secondary-200 pt-4">
          <h3 className="text-sm font-medium text-secondary-900">Endereço</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <Input
              label="Logradouro"
              placeholder="Rua, Avenida, etc."
              {...form.register('address.street')}
            />
            <Input
              label="Número"
              placeholder="123"
              {...form.register('address.number')}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <Input
              label="Complemento"
              placeholder="Apartamento, Sala, etc."
              {...form.register('address.complement')}
            />
            <Input
              label="Bairro"
              placeholder="Centro"
              {...form.register('address.neighborhood')}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <Input
              label="Cidade"
              placeholder="São Paulo"
              {...form.register('address.city')}
            />
            <Select {...form.register('address.state')}>
              <SelectTrigger>
                <SelectValue placeholder="UF" />
              </SelectTrigger>
              <SelectContent>
                {['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'].map((state) => (
                  <SelectItem key={state} value={state}>
                    {state}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {stateError && <p className="mt-1.5 text-sm text-danger-600" role="alert">{stateError}</p>}
            <Input
              label="CEP"
              placeholder="00000-000"
              {...form.register('address.zip')}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '')
                const formatted = value.length > 5 ? value.replace(/(\d{5})(\d{3})/, '$1-$2') : value
                form.setValue('address.zip', formatted)
              }}
            />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="flex items-center gap-3">
            <Switch
              {...form.register('status')}
              checked={form.watch('status') === 'ACTIVE'}
              onCheckedChange={(checked) => form.setValue('status', checked ? 'ACTIVE' : 'INACTIVE')}
              id="status"
            />
            <label htmlFor="status" className="text-sm font-medium text-secondary-700">
              Cliente ativo
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-secondary-200 pt-4">
          <Button
            type="button"
            variant="ghost"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancelar
          </Button>
          <Button type="submit" loading={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Salvando...
              </>
            ) : isEditing ? (
              'Atualizar'
            ) : (
              'Criar'
            )}
          </Button>
        </div>
      </form>
    </Modal>
  )
}