import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'

interface DemoContextType {
  isDemoMode: boolean
  toggleDemoMode: () => void
  enableDemoMode: () => void
  disableDemoMode: () => void
}

const DemoContext = createContext<DemoContextType | undefined>(undefined)

const DEMO_MODE_KEY = 'averta_demo_mode'

export function DemoProvider({ children }: { children: ReactNode }) {
  const [isDemoMode, setIsDemoMode] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Load demo mode from localStorage on init
  useEffect(() => {
    const stored = localStorage.getItem(DEMO_MODE_KEY)
    if (stored === 'true') {
      setIsDemoMode(true)
    }
    setIsLoading(false)
  }, [])

  const toggleDemoMode = useCallback(() => {
    setIsDemoMode((prev) => {
      const newValue = !prev
      localStorage.setItem(DEMO_MODE_KEY, String(newValue))
      return newValue
    })
  }, [])

  const enableDemoMode = useCallback(() => {
    setIsDemoMode(true)
    localStorage.setItem(DEMO_MODE_KEY, 'true')
  }, [])

  const disableDemoMode = useCallback(() => {
    setIsDemoMode(false)
    localStorage.setItem(DEMO_MODE_KEY, 'false')
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-50">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <DemoContext.Provider value={{ isDemoMode, toggleDemoMode, enableDemoMode, disableDemoMode }}>
      {children}
    </DemoContext.Provider>
  )
}

export function useDemo() {
  const context = useContext(DemoContext)
  if (context === undefined) {
    throw new Error('useDemo must be used within a DemoProvider')
  }
  return context
}