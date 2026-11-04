import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Modal, Switch } from '@/components'
import { Carrier } from '@/types'

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

function validCNPJ(value: string): boolean {
  const cleaned = value.replace(/\D/g, '')
  if (cleaned.length !== 14) return false
  return validateCNPJ(cleaned)
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

export const carrierSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  document: z.string().refine(validCNPJ, 'CNPJ inválido'),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().optional(),
  antt_registry: z.string().optional(),
  address: addressSchema.optional(),
  status: z.enum(['ACTIVE', 'INACTIVE']),
})

export type CarrierFormData = z.infer<typeof carrierSchema>

interface CarrierFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: CarrierFormData) => Promise<void>
  carrier?: Carrier | null
  isLoading?: boolean
  title?: string
}

export function CarrierForm({ open, onOpenChange, onSubmit, carrier, isLoading = false, title }: CarrierFormProps) {
  const isEditing = !!carrier

  const form = useForm<CarrierFormData>({
    resolver: zodResolver(carrierSchema),
    defaultValues: {
      name: '',
      document: '',
      email: '',
      phone: '',
      antt_registry: '',
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
    if (carrier) {
      form.reset({
        name: carrier.name,
        document: carrier.cnpj,
        email: carrier.email || '',
        phone: carrier.phone || '',
        antt_registry: carrier.antt_registry || '',
        address: {
          street: carrier.address || '',
          number: '',
          complement: '',
          neighborhood: '',
          city: carrier.city || '',
          state: carrier.state || '',
          zip: carrier.zipCode || '',
        },
        status: carrier.status || 'ACTIVE',
      })
    } else {
      form.reset({
        name: '',
        document: '',
        email: '',
        phone: '',
        antt_registry: '',
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
  }, [carrier, form])

  const handleSubmit = async (data: CarrierFormData) => {
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
      title={title || (isEditing ? 'Editar Transportadora' : 'Nova Transportadora')}
      size="lg"
      showClose
    >
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Nome *"
            placeholder="Nome da transportadora"
            {...form.register('name')}
            error={form.formState.errors.name?.message}
          />
          <Input
            label="CNPJ *"
            placeholder="00.000.000/0000-00"
            {...form.register('document')}
            error={form.formState.errors.document?.message}
            onChange={(e) => {
              const value = e.target.value.replace(/\D/g, '')
              let formatted = value
              if (value.length <= 14) {
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
            placeholder="transportadora@exemplo.com"
            {...form.register('email')}
            error={form.formState.errors.email?.message}
          />
          <Input
            label="Telefone"
            placeholder="(00) 00000-0000"
            {...form.register('phone')}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Registro ANTT"
            placeholder="Ex: 1234567"
            {...form.register('antt_registry')}
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
              Transportadora ativa
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