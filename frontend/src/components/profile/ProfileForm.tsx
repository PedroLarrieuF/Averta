import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../Button'
import { Input } from '../Input'
import { Modal, ModalBody, ModalFooter } from '../Modal'
import { Avatar } from '../Avatar'
import { getInitials } from '../../utils/helpers'

export const profileSchema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
})

export type ProfileFormData = z.infer<typeof profileSchema>

interface ProfileFormProps {
  initialData: ProfileFormData
  onSubmit: (data: ProfileFormData) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
}

export function ProfileForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: ProfileFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: initialData,
  })

  return (
    <Modal open={true} onOpenChange={onCancel} title="Editar Perfil">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <ModalBody className="space-y-4 p-6">
          <div className="flex items-center gap-4">
            <Avatar
              src={undefined}
              fallback={getInitials(initialData.name)}
              className="h-16 w-16"
            />
            <div className="flex-1">
              <label className="label">Avatar</label>
              <input
                type="file"
                accept="image/*"
                className="input mt-1"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    const reader = new FileReader()
                    reader.onloadend = () => {
                      // Handle avatar upload if needed
                    }
                    reader.readAsDataURL(file)
                  }
                }}
              />
              <p className="text-sm text-secondary-500 mt-1">
                JPG, PNG ou GIF. Máx. 2MB.
              </p>
            </div>
          </div>

          <Input
            label="Nome completo"
            error={errors.name?.message}
            {...register('name')}
            placeholder="Seu nome"
          />

          <Input
            label="Email"
            type="email"
            error={errors.email?.message}
            {...register('email')}
            placeholder="seu@email.com"
          />

          <Input
            label="Telefone"
            error={errors.phone?.message}
            {...register('phone')}
            placeholder="(11) 99999-9999"
          />
        </ModalBody>

        <ModalFooter className="gap-3">
          <Button type="button" variant="ghost" onClick={onCancel} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button type="submit" loading={isSubmitting}>
            Salvar alterações
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  )
}