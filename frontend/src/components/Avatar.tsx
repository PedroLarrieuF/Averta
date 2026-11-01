import { forwardRef, HTMLAttributes } from 'react'
import * as AvatarPrimitive from '@radix-ui/react-avatar'
import { cn } from '../utils/helpers'
import { User } from 'lucide-react'

interface AvatarProps extends HTMLAttributes<HTMLSpanElement> {
  src?: string | null
  alt?: string
  fallback?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export const Avatar = forwardRef<HTMLSpanElement, AvatarProps>(
  ({ className, src, alt, fallback, size = 'md', ...props }, ref) => {
    const sizeClasses = {
      sm: 'h-8 w-8 text-xs',
      md: 'h-10 w-10 text-sm',
      lg: 'h-12 w-12 text-base',
      xl: 'h-16 w-16 text-lg',
    }

    const fallbackText = fallback || alt?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '?'

    return (
      <AvatarPrimitive.Root
        ref={ref}
        className={cn('relative inline-flex shrink-0 overflow-hidden rounded-full', sizeClasses[size], className)}
        {...props}
      >
        <AvatarPrimitive.Image
          src={src || undefined}
          alt={alt || ''}
          className="aspect-square h-full w-full object-cover"
        />
        <AvatarPrimitive.Fallback className={cn('flex h-full w-full items-center justify-center rounded-full bg-secondary-100', sizeClasses[size])}>
          {src ? (
            <User className={cn('text-secondary-400', size === 'sm' && 'h-4 w-4', size === 'md' && 'h-5 w-5', size === 'lg' && 'h-6 w-6', size === 'xl' && 'h-8 w-8')} />
          ) : (
            <span className={cn('font-medium text-secondary-600')}>{fallbackText}</span>
          )}
        </AvatarPrimitive.Fallback>
      </AvatarPrimitive.Root>
    )
  }
)

Avatar.displayName = AvatarPrimitive.Root.displayName