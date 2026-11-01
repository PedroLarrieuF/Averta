import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { User } from '../store/auth-storage'
import { getUser, isAuthenticated } from '../store/auth-storage'
import { hasRole, Role } from '../utils/helpers'

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
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuth = useCallback(async () => {
    if (isAuthenticated()) {
      const storedUser = getUser()
      if (storedUser) {
        setUser(storedUser)
      }
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (email: string, password: string) => {
    const response = await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/auth/login`, {
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

    localStorage.setItem('averta_tokens', JSON.stringify(tokens))
    localStorage.setItem('averta_user', JSON.stringify(userData))
    setUser(userData)
  }

  const register = async (data: RegisterData) => {
    const response = await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/auth/register`, {
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

    localStorage.setItem('averta_tokens', JSON.stringify(tokens))
    localStorage.setItem('averta_user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = async () => {
    try {
      const tokens = getAuthTokens()
      if (tokens?.refreshToken) {
        await fetch(`${import.meta.env.VITE_API_URL || '/api/v1'}/auth/logout`, {
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