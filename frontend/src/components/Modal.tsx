import { forwardRef, ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import * as AlertDialog from '@radix-ui/react-alert-dialog'
import { cn } from '../utils/helpers'
import { Button } from './Button'
import { X } from 'lucide-react'

interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showClose?: boolean
}

export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
  size = 'md',
  showClose = true,
}: ModalProps) {
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-[90vw]',
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="modal-overlay" />
        <Dialog.Content className={cn('modal-content', sizeClasses[size])}>
          <div className="modal-header">
            <Dialog.Title className="modal-title">{title}</Dialog.Title>
            {showClose && (
              <Dialog.Close asChild>
                <button
                  className="p-1 rounded-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors"
                  aria-label="Fechar"
                >
                  <X className="h-5 w-5" />
                </button>
              </Dialog.Close>
            )}
          </div>
          {description && (
            <Dialog.Description className="px-6 py-2 text-sm text-secondary-500 border-b border-secondary-200">
              {description}
            </Dialog.Description>
          )}
          <Dialog.Close asChild>
            <div className="modal-body">{children}</div>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

interface ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  variant?: 'danger' | 'primary'
  loading?: boolean
}

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  onConfirm,
  variant = 'danger',
  loading = false,
}: ConfirmDialogProps) {
  return (
    <AlertDialog.Root open={open} onOpenChange={onOpenChange}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="modal-overlay" />
        <AlertDialog.Content className="modal-content max-w-md">
          <AlertDialog.Title className="modal-header">{title}</AlertDialog.Title>
          <AlertDialog.Description className="modal-body text-secondary-600">
            {description}
          </AlertDialog.Description>
          <div className="modal-footer">
            <AlertDialog.Cancel asChild>
              <Button variant="ghost" onClick={() => onOpenChange(false)} disabled={loading}>
                {cancelText}
              </Button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <Button variant={variant} onClick={onConfirm} loading={loading}>
                {confirmText}
              </Button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  )
}