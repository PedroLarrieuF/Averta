const TOKEN_KEY = 'averta_tokens'
const USER_KEY = 'averta_user'

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  expiresIn: number
  tokenType: string
}

export interface User {
  id: string
  email: string
  fullName: string
  role: string
  status: string
  companyId: string
  clientId?: string
  avatarUrl?: string
  lastLoginAt?: string
  createdAt: string
}

export function getAuthTokens(): AuthTokens | null {
  try {
    const stored = localStorage.getItem(TOKEN_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch {
    return null
  }
}

export function setAuthTokens(tokens: AuthTokens): void {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens))
}

export function clearAuthTokens(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getUser(): User | null {
  try {
    const stored = localStorage.getItem(USER_KEY)
    if (!stored) return null
    return JSON.parse(stored)
  } catch {
    return null
  }
}

export function setUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function isAuthenticated(): boolean {
  const tokens = getAuthTokens()
  if (!tokens) return false

  // Check if access token is expired (with 30s buffer)
  const expiryTime = Date.now() + (tokens.expiresIn * 1000) - 30000
  return Date.now() < expiryTime
}

export async function refreshAccessToken(): Promise<string> {
  const tokens = getAuthTokens()
  if (!tokens?.refreshToken) {
    throw new Error('No refresh token available')
  }

  const response = await fetch(`${(import.meta as any).env?.VITE_API_URL || '/api/v1'}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken: tokens.refreshToken }),
  })

  if (!response.ok) {
    throw new Error('Failed to refresh token')
  }

  const data = await response.json()
  const newTokens: AuthTokens = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    expiresIn: data.expires_in,
    tokenType: data.token_type,
  }

  setAuthTokens(newTokens)
  return newTokens.accessToken
}