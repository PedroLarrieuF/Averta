import { forwardRef, ReactNode } from 'react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { Check, Circle } from 'lucide-react'
import { cn } from '../utils/helpers'

export const DropdownMenuRoot = DropdownMenu.Root
export const DropdownMenuTrigger = DropdownMenu.Trigger
export const DropdownMenuPortal = DropdownMenu.Portal

interface DropdownMenuContentProps extends React.ComponentPropsWithoutRef<typeof DropdownMenu.Content> {
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
}

export const DropdownMenuContent = forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  ({ className, align = 'end', sideOffset = 4, children, ...props }, ref) => (
    <DropdownMenu.Portal>
      <DropdownMenu.Content
        ref={ref}
        className={cn(
          'z-50 min-w-[8rem] overflow-hidden rounded-md border border-secondary-200 bg-white p-1 text-secondary-900 shadow-md',
          className
        )}
        align={align}
        sideOffset={sideOffset}
        {...props}
      >
        {children}
      </DropdownMenu.Content>
    </DropdownMenu.Portal>
  )
)

DropdownMenuContent.displayName = DropdownMenu.Content.displayName

interface DropdownMenuItemProps extends React.ComponentPropsWithoutRef<typeof DropdownMenu.Item> {
  inset?: boolean
  shortcut?: string
  icon?: ReactNode
}

export const DropdownMenuItem = forwardRef<HTMLDivElement, DropdownMenuItemProps>(
  ({ className, inset, shortcut, icon, children, ...props }, ref) => (
    <DropdownMenu.Item
      ref={ref}
      className={cn(
        'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-secondary-100 focus:text-secondary-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        inset && 'pl-8',
        className
      )}
      {...props}
    >
      {icon && <span className="mr-2 h-4 w-4">{icon}</span>}
      {children}
      {shortcut && (
        <span className="ml-auto text-xs tracking-widest text-secondary-500">{shortcut}</span>
      )}
    </DropdownMenu.Item>
  )
)

DropdownMenuItem.displayName = DropdownMenu.Item.displayName

interface DropdownMenuCheckboxItemProps extends React.ComponentPropsWithoutRef<typeof DropdownMenu.CheckboxItem> {
  children: ReactNode
}

export const DropdownMenuCheckboxItem = forwardRef<HTMLDivElement, DropdownMenuCheckboxItemProps>(
  ({ className, children, checked, ...props }, ref) => (
    <DropdownMenu.CheckboxItem
      ref={ref}
      className={cn(
        'relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-secondary-100 focus:text-secondary-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        className
      )}
      checked={checked}
      {...props}
    >
      <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
        <DropdownMenu.ItemIndicator>
          <Check className="h-4 w-4" />
        </DropdownMenu.ItemIndicator>
      </span>
      {children}
    </DropdownMenu.CheckboxItem>
  )
)

DropdownMenuCheckboxItem.displayName = DropdownMenu.CheckboxItem.displayName

interface DropdownMenuRadioGroupProps extends React.ComponentPropsWithoutRef<typeof DropdownMenu.RadioGroup> {}

export const DropdownMenuRadioGroup = forwardRef<HTMLDivElement, DropdownMenuRadioGroupProps>(
  ({ className, children, ...props }, ref) => (
    <DropdownMenu.RadioGroup ref={ref} className={cn('', className)} {...props}>
      {children}
    </DropdownMenu.RadioGroup>
  )
)

DropdownMenuRadioGroup.displayName = DropdownMenu.RadioGroup.displayName

interface DropdownMenuRadioItemProps extends React.ComponentPropsWithoutRef<typeof DropdownMenu.RadioItem> {
  children: ReactNode
}

export const DropdownMenuRadioItem = forwardRef<HTMLDivElement, DropdownMenuRadioItemProps>(
  ({ className, children, ...props }, ref) => (
    <DropdownMenu.RadioItem
      ref={ref}
      className={cn(
        'relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none transition-colors focus:bg-secondary-100 focus:text-secondary-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        className
      )}
      {...props}
    >
      <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
        <DropdownMenu.ItemIndicator>
          <Circle className="h-2 w-2 fill-current" />
        </DropdownMenu.ItemIndicator>
      </span>
      {children}
    </DropdownMenu.RadioItem>
  )
)

DropdownMenuRadioItem.displayName = DropdownMenu.RadioItem.displayName

export const DropdownMenuLabel = forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof DropdownMenu.Label>>(
  ({ className, ...props }, ref) => (
    <DropdownMenu.Label
      ref={ref}
      className={cn('px-2 py-1.5 text-sm font-semibold text-secondary-900', className)}
      {...props}
    />
  )
)

DropdownMenuLabel.displayName = DropdownMenu.Label.displayName

export const DropdownMenuSeparator = forwardRef<HTMLDivElement, React.ComponentPropsWithoutRef<typeof DropdownMenu.Separator>>(
  ({ className, ...props }, ref) => (
    <DropdownMenu.Separator
      ref={ref}
      className={cn('-mx-1 my-1 h-px bg-secondary-100', className)}
      {...props}
    />
  )
)

DropdownMenuSeparator.displayName = DropdownMenu.Separator.displayName

export const DropdownMenuShortcut = ({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) => (
  <span className={cn('ml-auto text-xs tracking-widest text-secondary-500', className)} {...props} />
)