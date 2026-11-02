import { ReactNode } from 'react'
import { cn } from '@/utils/helpers'

interface PageHeaderProps {
  children: ReactNode
  className?: string
}

export function PageHeader({ children, className }: PageHeaderProps) {
  return (
    <div className={cn('flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6', className)}>
      {children}
    </div>
  )
}

interface PageTitleProps {
  children: ReactNode
  className?: string
}

export function PageTitle({ children, className }: PageTitleProps) {
  return <h1 className={cn('text-2xl font-bold text-secondary-900', className)}>{children}</h1>
}

interface PageSubtitleProps {
  children: ReactNode
  className?: string
}

export function PageSubtitle({ children, className }: PageSubtitleProps) {
  return <p className={cn('text-secondary-500', className)}>{children}</p>
}