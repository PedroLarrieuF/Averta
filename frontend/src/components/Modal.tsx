import { ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import * as AlertDialogPrimitive from '@radix-ui/react-alert-dialog'
import { cn } from '../utils/helpers'
import { Button } from './Button'
import { X } from 'lucide-react'

// Re-export AlertDialog primitives for direct use
// Note: @radix-ui/react-alert-dialog doesn't have Header/Footer components
export const AlertDialog = AlertDialogPrimitive.Root
export const AlertDialogTrigger = AlertDialogPrimitive.Trigger
export const AlertDialogPortal = AlertDialogPrimitive.Portal
export const AlertDialogOverlay = AlertDialogPrimitive.Overlay
export const AlertDialogContent = AlertDialogPrimitive.Content
export const AlertDialogTitle = AlertDialogPrimitive.Title
export const AlertDialogDescription = AlertDialogPrimitive.Description
export const AlertDialogCancel = AlertDialogPrimitive.Cancel
export const AlertDialogAction = AlertDialogPrimitive.Action

// Modal sub-components for compound pattern
interface ModalHeaderProps {
  children: ReactNode
  className?: string
}

export function ModalHeader({ children, className }: ModalHeaderProps) {
  return <div className={cn('modal-header', className)}>{children}</div>
}

interface ModalBodyProps {
  children: ReactNode
  className?: string
}

export function ModalBody({ children, className }: ModalBodyProps) {
  return <div className={cn('modal-body', className)}>{children}</div>
}

interface ModalFooterProps {
  children: ReactNode
  className?: string
}

export function ModalFooter({ children, className }: ModalFooterProps) {
  return <div className={cn('modal-footer', className)}>{children}</div>
}

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
          <ModalHeader>
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
          </ModalHeader>
          {description && (
            <Dialog.Description className="px-6 py-2 text-sm text-secondary-500 border-b border-secondary-200">
              {description}
            </Dialog.Description>
          )}
          <Dialog.Close asChild>
            <ModalBody>{children}</ModalBody>
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
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogPortal>
        <AlertDialogOverlay className="modal-overlay" />
        <AlertDialogContent className="modal-content max-w-md">
          <AlertDialogTitle className="modal-header">{title}</AlertDialogTitle>
          <AlertDialogDescription className="modal-body text-secondary-600">
            {description}
          </AlertDialogDescription>
          <ModalFooter className="gap-3">
            <AlertDialogCancel asChild>
              <Button variant="ghost" onClick={() => onOpenChange(false)} disabled={loading}>
                {cancelText}
              </Button>
            </AlertDialogCancel>
            <AlertDialogAction asChild>
              <Button variant={variant} onClick={onConfirm} loading={loading}>
                {confirmText}
              </Button>
            </AlertDialogAction>
          </ModalFooter>
        </AlertDialogContent>
      </AlertDialogPortal>
    </AlertDialog>
  )
}