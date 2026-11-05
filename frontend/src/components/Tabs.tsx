import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '../utils/helpers'
import { forwardRef } from 'react'

// Tabs
export const Tabs = TabsPrimitive.Root

// TabsList
export const TabsList = forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List> & { className?: string }
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      'inline-flex h-10 items-center justify-center rounded-md bg-secondary-100 p-1 text-secondary-500',
      className
    )}
    {...props}
  />
))
TabsList.displayName = TabsPrimitive.List.displayName

// TabsTrigger
export const TabsTrigger = forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger> & { className?: string }
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all',
      'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
      'disabled:pointer-events-none disabled:opacity-50',
      'data-[state=active]:bg-white data-[state=active]:text-primary-600 data-[state=active]:shadow-sm',
      'data-[state=inactive]:text-secondary-600 hover:data-[state=inactive]:text-secondary-900 hover:data-[state=inactive]:bg-secondary-50',
      className
    )}
    {...props}
  />
))
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

// TabsContent
export const TabsContent = forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content> & { className?: string }
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      'mt-2 ring-offset-background focus:outline-none',
      'animate-in fade-in-0 zoom-in-95 data-[state=active]:animate-in data-[state=inactive]:animate-out',
      className
    )}
    {...props}
  />
))
TabsContent.displayName = TabsPrimitive.Content.displayName

// Export types
export type { TabsProps } from '@radix-ui/react-tabs'