import * as ToastPrimitive from '@radix-ui/react-toast'
import { X } from 'lucide-react'
import { cn } from '../utils/helpers'

interface ToastProps {
  title?: string
  description?: string
  variant?: 'default' | 'success' | 'warning' | 'danger'
  open?: boolean
  onOpenChange?: (open: boolean) => void
  duration?: number
  action?: React.ReactNode
  className?: string
}

const variantStyles = {
  default: 'border-secondary-200 bg-white',
  success: 'border-success-200 bg-success-50',
  warning: 'border-warning-200 bg-warning-50',
  danger: 'border-danger-200 bg-danger-50',
}

const variantTitleColors = {
  default: 'text-secondary-900',
  success: 'text-success-800',
  warning: 'text-warning-800',
  danger: 'text-danger-800',
}

export function Toast({
  title,
  description,
  variant = 'default',
  open = true,
  onOpenChange,
  duration = 5000,
  action,
  className,
}: ToastProps) {
  return (
    <ToastPrimitive.Root open={open} onOpenChange={onOpenChange} duration={duration}>
      <ToastPrimitive.Viewport className="fixed bottom-4 right-4 flex flex-col gap-2 z-50 w-[380px] max-w-[calc(100vw-2rem)]">
        <div
          className={cn(
            'flex items-start gap-3 rounded-lg border p-4 shadow-lg animate-in slide-in-from-bottom-full duration-300 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:slide-out-to-bottom-full data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=cancel]:translate-x-0 data-[swipe=end]:animate-out data-[swipe=end]:slide-out-to-right-full',
            variantStyles[variant],
            className
          )}
        >
          <div className="flex-1 space-y-1">
            {title && (
              <ToastPrimitive.Title className={cn('font-semibold', variantTitleColors[variant])}>
                {title}
              </ToastPrimitive.Title>
            )}
            {description && (
              <ToastPrimitive.Description className="text-sm opacity-90">
                {description}
              </ToastPrimitive.Description>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {action}
            <ToastPrimitive.Close asChild>
              <button
                className="rounded p-1 text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors"
                aria-label="Fechar"
              >
                <X className="h-4 w-4" />
              </button>
            </ToastPrimitive.Close>
          </div>
        </div>
      </ToastPrimitive.Viewport>
    </ToastPrimitive.Root>
  )
}

// Toast context for programmatic usage
import { createContext, useContext, useState, useCallback, ReactNode } from 'react'

interface ToastItem {
  id: string
  title?: string
  description?: string
  variant?: 'default' | 'success' | 'warning' | 'danger'
  duration?: number
  action?: ReactNode
}

interface ToastContextType {
  toasts: ToastItem[]
  addToast: (toast: Omit<ToastItem, 'id'>) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

export function ToastManager({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const addToast = useCallback((toast: Omit<ToastItem, 'id'>) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { ...toast, id }])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastPrimitive.Provider>
        <ToastPrimitive.Viewport className="fixed bottom-4 right-4 flex flex-col gap-2 z-50 w-[380px] max-w-[calc(100vw-2rem)]">
          {toasts.map((toast) => (
            <ToastPrimitive.Root key={toast.id} open={true} duration={toast.duration}>
              <div
                className={cn(
                  'flex items-start gap-3 rounded-lg border p-4 shadow-lg animate-in slide-in-from-bottom-full duration-300',
                  variantStyles[toast.variant || 'default']
                )}
              >
                <div className="flex-1 space-y-1">
                  {toast.title && (
                    <ToastPrimitive.Title className={cn('font-semibold', variantTitleColors[toast.variant || 'default'])}>
                      {toast.title}
                    </ToastPrimitive.Title>
                  )}
                  {toast.description && (
                    <ToastPrimitive.Description className="text-sm opacity-90">
                      {toast.description}
                    </ToastPrimitive.Description>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {toast.action}
                  <ToastPrimitive.Close asChild>
                    <button
                      className="rounded p-1 text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors"
                      onClick={() => removeToast(toast.id)}
                      aria-label="Fechar"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </ToastPrimitive.Close>
                </div>
              </div>
            </ToastPrimitive.Root>
          ))}
        </ToastPrimitive.Viewport>
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastManager')
  }
  return context
}