import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../Button'
import { Input } from '../Input'
import { Modal, ModalBody, ModalFooter } from '../Modal'

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, 'Senha atual obrigatória'),
    new_password: z.string().min(8, 'Nova senha deve ter pelo menos 8 caracteres'),
    confirm_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Senhas não coincidem',
    path: ['confirm_password'],
  })

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

interface ChangePasswordModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: ChangePasswordFormData) => Promise<void>
  isSubmitting?: boolean
}

export function ChangePasswordModal({
  open,
  onOpenChange,
  onSubmit,
  isSubmitting = false,
}: ChangePasswordModalProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
  })

  const newPassword = watch('new_password')

  const getPasswordStrength = (password: string): { score: number; label: string; color: string } => {
    let score = 0
    if (password.length >= 8) score++
    if (/[A-Z]/.test(password)) score++
    if (/[a-z]/.test(password)) score++
    if (/[0-9]/.test(password)) score++
    if (/[^A-Za-z0-9]/.test(password)) score++

    const labels = ['Muito fraca', 'Fraca', 'Média', 'Forte', 'Muito forte']
    const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500']

    return {
      score,
      label: labels[score] || labels[0],
      color: colors[score] || colors[0],
    }
  }

  const strength = getPasswordStrength(newPassword)

  const handleClose = () => {
    onOpenChange(false)
  }

  return (
    <Modal open={open} onOpenChange={handleClose} title="Alterar Senha">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <ModalBody className="space-y-4 p-6">
          <Input
            label="Senha atual"
            type="password"
            error={errors.current_password?.message}
            {...register('current_password')}
            placeholder="Digite sua senha atual"
            autoComplete="current-password"
          />

          <div className="space-y-2">
            <Input
              label="Nova senha"
              type="password"
              error={errors.new_password?.message}
              {...register('new_password')}
              placeholder="Digite a nova senha"
              autoComplete="new-password"
            />
            {newPassword && (
              <div className="space-y-1">
                <div className="h-2 bg-secondary-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${strength.color} transition-all duration-300`}
                    style={{ width: `${(strength.score / 5) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-secondary-500">
                  Força da senha: <span className="font-medium">{strength.label}</span>
                </p>
              </div>
            )}
            <p className="text-xs text-secondary-500">
              Mínimo 8 caracteres. Use maiúsculas, minúsculas, números e símbolos.
            </p>
          </div>

          <Input
            label="Confirmar nova senha"
            type="password"
            error={errors.confirm_password?.message}
            {...register('confirm_password')}
            placeholder="Confirme a nova senha"
            autoComplete="new-password"
          />
        </ModalBody>

        <ModalFooter className="gap-3">
          <Button type="button" variant="ghost" onClick={handleClose} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button type="submit" loading={isSubmitting}>
            Alterar senha
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  )
}