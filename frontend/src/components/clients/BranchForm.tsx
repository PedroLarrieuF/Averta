import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Modal, Switch } from '@/components'
import { ClientBranch } from '@/types'

const addressSchema = z.object({
  street: z.string().optional(),
  number: z.string().optional(),
  complement: z.string().optional(),
  neighborhood: z.string().optional(),
  city: z.string().optional(),
  state: z.string().length(2, 'UF deve ter 2 caracteres').optional(),
  zip: z.string().optional(),
})

export const branchSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  code: z.string().min(1, 'Código é obrigatório'),
  address: addressSchema.optional(),
  is_main: z.boolean(),
})

export type BranchFormData = z.infer<typeof branchSchema>

interface BranchFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: BranchFormData) => Promise<void>
  branch?: ClientBranch | null
  isLoading?: boolean
  title?: string
  existingCodes?: string[]
}

export function BranchForm({ open, onOpenChange, onSubmit, branch, isLoading = false, title, existingCodes = [] }: BranchFormProps) {
  const isEditing = !!branch

  const form = useForm<BranchFormData>({
    resolver: zodResolver(branchSchema),
    defaultValues: {
      name: '',
      code: '',
      address: {
        street: '',
        number: '',
        complement: '',
        neighborhood: '',
        city: '',
        state: '',
        zip: '',
      },
      is_main: false,
    },
  })

  useEffect(() => {
    if (branch) {
      form.reset({
        name: branch.name,
        code: branch.code,
        address: {
          street: branch.address || '',
          number: '',
          complement: '',
          neighborhood: '',
          city: branch.city || '',
          state: branch.state || '',
          zip: branch.zipCode || '',
        },
        is_main: branch.is_main || false,
      })
    } else {
      form.reset({
        name: '',
        code: '',
        address: {
          street: '',
          number: '',
          complement: '',
          neighborhood: '',
          city: '',
          state: '',
          zip: '',
        },
        is_main: false,
      })
    }
  }, [branch, form])

  const handleSubmit = async (data: BranchFormData) => {
    await onSubmit(data)
  }

  const codeError = existingCodes.includes(form.watch('code')) && !isEditing
    ? 'Este código já está em uso'
    : form.formState.errors.code?.message

  const stateError = form.formState.errors.address?.state?.message

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={title || (isEditing ? 'Editar Filial' : 'Nova Filial')}
      size="md"
      showClose
    >
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            label="Nome *"
            placeholder="Nome da filial"
            {...form.register('name')}
            error={form.formState.errors.name?.message}
          />
          <Input
            label="Código *"
            placeholder="Ex: SP01, RJ02"
            {...form.register('code')}
            error={codeError}
            onChange={(e) => form.setValue('code', e.target.value.toUpperCase(), { shouldValidate: true })}
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
              {...form.register('is_main')}
              id="is_main"
            />
            <label htmlFor="is_main" className="text-sm font-medium text-secondary-700">
              Filial principal
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