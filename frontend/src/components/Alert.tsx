import { cn } from '../utils/helpers'

interface AlertProps {
  variant?: 'default' | 'destructive' | 'success' | 'warning'
  className?: string
  children: React.ReactNode
}

export function Alert({ variant = 'default', className, children }: AlertProps) {
  const variants = {
    default: 'bg-blue-50 text-blue-800 border-blue-200',
    destructive: 'bg-red-50 text-red-800 border-red-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  }

  return (
    <div
      className={cn(
        'relative flex w-full items-center gap-4 rounded-lg border p-4',
        variants[variant],
        className
      )}
      role="alert"
    >
      <div className="flex-1">{children}</div>
    </div>
  )
}

interface AlertTitleProps {
  className?: string
  children: React.ReactNode
}

export function AlertTitle({ className, children }: AlertTitleProps) {
  return (
    <h4 className={cn('mb-1 font-medium leading-none', className)}>
      {children}
    </h4>
  )
}

interface AlertDescriptionProps {
  className?: string
  children: React.ReactNode
}

export function AlertDescription({ className, children }: AlertDescriptionProps) {
  return (
    <div className={cn('text-sm opacity-90', className)}>
      {children}
    </div>
  )
}