import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../Button'
import { Input } from '../Input'
import { ModalFooter } from '../Modal'
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogPortal,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
  AlertDialogAction,
} from '../Modal'

export const deleteAccountSchema = z.object({
  password: z.string().min(1, 'Senha obrigatória para confirmação'),
  confirm_text: z.literal('EXCLUIR'),
})

export type DeleteAccountFormData = z.infer<typeof deleteAccountSchema>

interface DangerZoneProps {
  onDeleteAccount: (password: string) => Promise<void>
  isDeleting?: boolean
}

export function DangerZone({ onDeleteAccount, isDeleting = false }: DangerZoneProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<DeleteAccountFormData>({
    resolver: zodResolver(deleteAccountSchema),
    defaultValues: {
      password: '',
      confirm_text: 'EXCLUIR',
    },
  })

  const handleDeleteSubmit = async (data: DeleteAccountFormData) => {
    await onDeleteAccount(data.password)
    reset()
  }

  return (
    <div className="card border-danger-200 bg-danger-50">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-danger-700 flex items-center gap-2">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Zona de Perigo
        </h3>
        <p className="text-sm text-danger-600 mt-1">
          Ações irreversíveis. Tenha certeza antes de prosseguir.
        </p>
      </div>
      <div className="card-body pt-0">
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="danger" className="w-full" disabled={isDeleting}>
              Excluir minha conta
            </Button>
          </AlertDialogTrigger>
          <AlertDialogPortal>
            <AlertDialogOverlay className="modal-overlay" />
            <AlertDialogContent className="modal-content max-w-md">
              <AlertDialogTitle className="modal-header">Excluir conta permanentemente</AlertDialogTitle>
              <AlertDialogDescription className="modal-body text-secondary-600">
                Esta ação não pode ser desfeita. Todos os seus dados, histórico de discrepâncias,
                contestações e configurações serão removidos permanentemente.
                <br /><br />
                Para confirmar, digite sua senha e a palavra <strong>EXCLUIR</strong> abaixo.
              </AlertDialogDescription>
              <form onSubmit={handleSubmit(handleDeleteSubmit)} className="space-y-4">
                <div className="space-y-4">
                  <Input
                    label="Senha atual"
                    type="password"
                    error={errors.password?.message}
                    {...register('password')}
                    placeholder="Digite sua senha para confirmar"
                    autoComplete="current-password"
                  />
                  <Input
                    label='Digite "EXCLUIR" para confirmar'
                    error={errors.confirm_text?.message}
                    {...register('confirm_text')}
                    placeholder="EXCLUIR"
                    autoComplete="off"
                  />
                </div>
                <ModalFooter className="gap-3">
                  <AlertDialogCancel>
                    <Button type="button" variant="ghost">Cancelar</Button>
                  </AlertDialogCancel>
                  <AlertDialogAction>
                    <Button type="submit" variant="danger" loading={isDeleting}>
                      Excluir permanentemente
                    </Button>
                  </AlertDialogAction>
                </ModalFooter>
              </form>
            </AlertDialogContent>
          </AlertDialogPortal>
        </AlertDialog>
      </div>
    </div>
  )
}