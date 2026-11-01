import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getAuthTokens,
  setAuthTokens,
  clearAuthTokens,
  getUser,
  setUser,
  isAuthenticated,
  AuthTokens,
  User,
} from './auth-storage'

const mockTokens: AuthTokens = {
  accessToken: 'mock-access-token',
  refreshToken: 'mock-refresh-token',
  expiresIn: 900,
  tokenType: 'bearer',
}

const mockUser: User = {
  id: 'user-123',
  email: 'test@averta.com',
  fullName: 'Test User',
  role: 'ADMIN',
  status: 'ACTIVE',
  companyId: 'company-456',
  createdAt: '2024-01-01T00:00:00Z',
}

describe('auth-storage', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2024-06-15T12:00:00'))
  })

  afterEach(() => {
    localStorage.clear()
    vi.useRealTimers()
  })

  describe('getAuthTokens', () => {
    it('returns null when no tokens stored', () => {
      expect(getAuthTokens()).toBeNull()
    })

    it('returns parsed tokens when valid', () => {
      localStorage.setItem('averta_tokens', JSON.stringify(mockTokens))
      expect(getAuthTokens()).toEqual(mockTokens)
    })

    it('returns null when JSON is invalid', () => {
      localStorage.setItem('averta_tokens', 'invalid json')
      expect(getAuthTokens()).toBeNull()
    })
  })

  describe('setAuthTokens', () => {
    it('stores tokens in localStorage', () => {
      setAuthTokens(mockTokens)
      expect(localStorage.getItem('averta_tokens')).toBe(JSON.stringify(mockTokens))
    })

    it('overwrites existing tokens', () => {
      setAuthTokens(mockTokens)
      const newTokens = { ...mockTokens, accessToken: 'new-token' }
      setAuthTokens(newTokens)
      expect(getAuthTokens()).toEqual(newTokens)
    })
  })

  describe('clearAuthTokens', () => {
    it('removes both tokens and user', () => {
      localStorage.setItem('averta_tokens', JSON.stringify(mockTokens))
      localStorage.setItem('averta_user', JSON.stringify(mockUser))

      clearAuthTokens()

      expect(localStorage.getItem('averta_tokens')).toBeNull()
      expect(localStorage.getItem('averta_user')).toBeNull()
    })
  })

  describe('getUser', () => {
    it('returns null when no user stored', () => {
      expect(getUser()).toBeNull()
    })

    it('returns parsed user when valid', () => {
      localStorage.setItem('averta_user', JSON.stringify(mockUser))
      expect(getUser()).toEqual(mockUser)
    })

    it('returns null when JSON is invalid', () => {
      localStorage.setItem('averta_user', 'invalid json')
      expect(getUser()).toBeNull()
    })
  })

  describe('setUser', () => {
    it('stores user in localStorage', () => {
      setUser(mockUser)
      expect(localStorage.getItem('averta_user')).toBe(JSON.stringify(mockUser))
    })

    it('overwrites existing user', () => {
      setUser(mockUser)
      const newUser = { ...mockUser, email: 'new@test.com' }
      setUser(newUser)
      expect(getUser()).toEqual(newUser)
    })
  })

  describe('isAuthenticated', () => {
    it('returns false when no tokens', () => {
      expect(isAuthenticated()).toBe(false)
    })

    it('returns false when token expired', () => {
      const expiredTokens = { ...mockTokens, expiresIn: 0 }
      localStorage.setItem('averta_tokens', JSON.stringify(expiredTokens))
      expect(isAuthenticated()).toBe(false)
    })

    it('returns true when token valid', () => {
      localStorage.setItem('averta_tokens', JSON.stringify(mockTokens))
      expect(isAuthenticated()).toBe(true)
    })

    it('returns false when token expires within 30 seconds', () => {
      const nearExpiryTokens = { ...mockTokens, expiresIn: 20 } // 20 seconds
      localStorage.setItem('averta_tokens', JSON.stringify(nearExpiryTokens))
      // Buffer is 30 seconds, so 20 < 30 = should return false
      expect(isAuthenticated()).toBe(false)
    })

    it('returns true when token expires in more than 30 seconds', () => {
      const validTokens = { ...mockTokens, expiresIn: 60 } // 60 seconds
      localStorage.setItem('averta_tokens', JSON.stringify(validTokens))
      expect(isAuthenticated()).toBe(true)
    })
  })
})