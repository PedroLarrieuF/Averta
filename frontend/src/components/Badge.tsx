import { forwardRef, HTMLAttributes } from 'react'
import { cn } from '../utils/helpers'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'danger' | 'primary' | 'secondary'
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'secondary', children, ...props }, ref) => {
    const variantClasses = {
      success: 'badge-success',
      warning: 'badge-warning',
      danger: 'badge-danger',
      primary: 'badge-primary',
      secondary: 'badge-secondary',
    }

    return (
      <span
        ref={ref}
        className={cn('badge', variantClasses[variant], className)}
        {...props}
      >
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

// Convenience function for status badges
import { getStatusBadge, getSeverityBadge } from '../utils/helpers'

interface StatusBadgeProps {
  status: string
  type?: 'discrepancy' | 'contest' | 'document' | 'severity'
}

export function StatusBadge({ status, type = 'discrepancy' }: StatusBadgeProps) {
  if (type === 'severity') {
    const { variant, label } = getSeverityBadge(status)
    return <Badge variant={variant as BadgeProps['variant']}>{label}</Badge>
  }
  const { variant, label } = getStatusBadge(status)
  return <Badge variant={variant as BadgeProps['variant']}>{label}</Badge>
}