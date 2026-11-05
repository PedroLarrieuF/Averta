import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { User } from '../store/auth-storage'
import { getUser, isAuthenticated, getAuthTokens, clearAuthTokens, setAuthTokens } from '../store/auth-storage'
import { hasRole, Role } from '../utils/helpers'
import { useDemo } from './demo-context'
import { demoApi } from '../services/demo-api'

const DEMO_MODE_KEY = 'averta_demo_mode'

function isDemoModeEnabled(): boolean {
  if (typeof window === 'undefined') return false
  return localStorage.getItem(DEMO_MODE_KEY) === 'true'
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  hasRole: (role: Role) => boolean
  hasAnyRole: (roles: Role[]) => boolean
}

interface RegisterData {
  email: string
  password: string
  fullName: string
  companyName: string
  companyCnpj: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { isDemoMode } = useDemo()

  const setUser = useCallback((userData: User | null) => {
    setUserState(userData)
    if (!userData) {
      clearAuthTokens()
    }
  }, [])

  const checkAuth = useCallback(async () => {
    // In demo mode, auto-login as demo user - check localStorage directly
    if (isDemoModeEnabled()) {
      try {
        const demoResponse = await demoApi.login('demo@averta.com', 'demo')
        const { user: demoUser, access_token, refresh_token, expires_in, token_type } = demoResponse

        const tokens = {
          accessToken: access_token,
          refreshToken: refresh_token,
          expiresIn: expires_in,
          tokenType: token_type,
        }

        setAuthTokens(tokens)
        setUser(demoUser)
      } catch (error) {
        console.error('Demo login failed:', error)
        setUser(null)
      }
      setIsLoading(false)
      return
    }

    // Normal authentication flow
    if (isAuthenticated()) {
      const storedUser = getUser()
      if (storedUser) {
        setUser(storedUser)
      }
    }
    setIsLoading(false)
  }, [isDemoMode])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (email: string, password: string) => {
    // In demo mode, use demo API - check localStorage directly to avoid race conditions
    if (isDemoModeEnabled()) {
      const demoResponse = await demoApi.login(email, password)
      const { user: userData, access_token, refresh_token, expires_in, token_type } = demoResponse

      const tokens = {
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresIn: expires_in,
        tokenType: token_type,
      }

      setAuthTokens(tokens)
      setUser(userData)
      return
    }

    // Normal login flow
    const response = await fetch(`${(import.meta as any).env?.VITE_API_URL || '/api/v1'}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Credenciais inválidas')
    }

    const data = await response.json()
    const { user: userData, access_token, refresh_token, expires_in, token_type } = data

    const tokens = {
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresIn: expires_in,
      tokenType: token_type,
    }

    setAuthTokens(tokens)
    setUser(userData)
  }

  const register = async (data: RegisterData) => {
    // In demo mode, use demo API - check localStorage directly to avoid race conditions
    if (isDemoModeEnabled()) {
      const demoResponse = await demoApi.register(data)
      const { user: userData, access_token, refresh_token, expires_in, token_type } = demoResponse

      const tokens = {
        accessToken: access_token,
        refreshToken: refresh_token,
        expiresIn: expires_in,
        tokenType: token_type,
      }

      setAuthTokens(tokens)
      setUser(userData)
      return
    }

    // Normal register flow
    const response = await fetch(`${(import.meta as any).env?.VITE_API_URL || '/api/v1'}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || 'Erro ao registrar')
    }

    const result = await response.json()
    const { user: userData, access_token, refresh_token, expires_in, token_type } = result

    const tokens = {
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresIn: expires_in,
      tokenType: token_type,
    }

    setAuthTokens(tokens)
    setUser(userData)
  }

  const logout = async () => {
    // In demo mode, just clear local state - check localStorage directly
    if (isDemoModeEnabled()) {
      setUser(null)
      return
    }

    // Normal logout flow
    try {
      const tokens = getAuthTokens()
      if (tokens?.refreshToken) {
        await fetch(`${(import.meta as any).env?.VITE_API_URL || '/api/v1'}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${tokens.accessToken}`,
          },
          body: JSON.stringify({ refreshToken: tokens.refreshToken }),
        })
      }
    } catch {
      // Ignore logout errors
    } finally {
      clearAuthTokens()
      setUser(null)
    }
  }

  const refreshUser = async () => {
    if (isDemoModeEnabled()) {
      const demoResponse = await demoApi.me()
      setUser(demoResponse)
      return
    }

    const storedUser = getUser()
    if (storedUser) {
      setUser(storedUser)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
        hasRole: (role: Role) => user ? hasRole(user.role as Role, role) : false,
        hasAnyRole: (roles: Role[]) => user ? roles.some((r) => hasRole(user.role as Role, r)) : false,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}