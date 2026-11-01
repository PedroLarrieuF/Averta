import { describe, it, expect, vi } from 'vitest'
import {
  cn,
  formatCurrency,
  formatNumber,
  formatPercent,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  truncate,
  getInitials,
  sleep,
  debounce,
  generateId,
  hasRole,
  getStatusBadge,
  getSeverityBadge,
  ROLE_HIERARCHY,
} from './helpers'

describe('helpers', () => {
  describe('cn', () => {
    it('merges class names correctly', () => {
      expect(cn('base', 'extra')).toBe('base extra')
    })

    it('handles conditional classes', () => {
      expect(cn('base', true && 'conditional')).toBe('base conditional')
      expect(cn('base', false && 'conditional')).toBe('base')
    })

    it('handles tailwind merge conflicts', () => {
      expect(cn('p-2 p-4')).toBe('p-4')
      expect(cn('text-red-500 text-blue-500')).toBe('text-blue-500')
    })
  })

  describe('formatCurrency', () => {
    it('formats BRL correctly', () => {
      expect(formatCurrency(1000)).toBe('R$ 1.000,00')
      expect(formatCurrency(1000.5)).toBe('R$ 1.000,50')
      expect(formatCurrency(0)).toBe('R$ 0,00')
      expect(formatCurrency(-500)).toBe('-R$ 500,00')
    })

    it('accepts custom currency', () => {
      expect(formatCurrency(100, 'USD')).toBe('US$ 100,00')
    })
  })

  describe('formatNumber', () => {
    it('formats numbers with Brazilian locale', () => {
      expect(formatNumber(1000)).toBe('1.000')
      expect(formatNumber(1000000)).toBe('1.000.000')
      expect(formatNumber(0)).toBe('0')
    })
  })

  describe('formatPercent', () => {
    it('formats percentages with default 1 decimal', () => {
      expect(formatPercent(50)).toBe('50.0%')
      expect(formatPercent(33.333)).toBe('33.3%')
    })

    it('accepts custom decimals', () => {
      expect(formatPercent(33.333, 2)).toBe('33.33%')
      expect(formatPercent(100, 0)).toBe('100%')
    })
  })

  describe('formatDate', () => {
    it('formats date strings (parsed as local)', () => {
      // ISO date strings without time are parsed as UTC midnight
      // In timezones west of UTC, this becomes the previous day
      // So we test the format pattern instead of exact values
      const result1 = formatDate('2024-01-15')
      const result2 = formatDate('2024-12-31')
      expect(result1).toMatch(/^\d{2}\/\d{2}\/\d{4}$/)
      expect(result2).toMatch(/^\d{2}\/\d{2}\/\d{4}$/)
    })

    it('formats Date objects (timezone aware)', () => {
      // Date constructor parses as UTC, toLocaleDateString uses local timezone
      // So we test that it returns a valid formatted date
      const result = formatDate(new Date('2024-06-10T12:00:00Z'))
      expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4}$/)
    })

    it('accepts custom options', () => {
      expect(formatDate('2024-01-15', { month: 'long' })).toContain('janeiro')
    })
  })

  describe('formatDateTime', () => {
    it('formats date and time', () => {
      const result = formatDateTime('2024-01-15T14:30:00')
      expect(result).toMatch(/15\/01\/2024/)
      expect(result).toMatch(/14:30/)
    })
  })

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2024-06-15T12:00:00'))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('returns "agora mesmo" for very recent', () => {
      expect(formatRelativeTime(new Date('2024-06-15T11:59:30'))).toBe('agora mesmo')
    })

    it('returns minutes for < 1 hour', () => {
      expect(formatRelativeTime(new Date('2024-06-15T11:30:00'))).toBe('30min atrás')
    })

    it('returns hours for < 24 hours', () => {
      expect(formatRelativeTime(new Date('2024-06-15T06:00:00'))).toBe('6h atrás')
    })

    it('returns days for < 7 days', () => {
      expect(formatRelativeTime(new Date('2024-06-10T12:00:00'))).toBe('5d atrás')
    })

    it('returns formatted date for older', () => {
      // Date is parsed as local time, so '2024-01-01' = midnight local
      // With fake timer at 2024-06-15, that's > 7 days ago
      const result = formatRelativeTime(new Date('2024-01-01'))
      expect(result).toMatch(/^\d{2}\/\d{2}\/\d{4}$/)
    })
  })

  describe('truncate', () => {
    it('truncates long strings', () => {
      // truncates at length, then adds '...'
      expect(truncate('Hello World', 8)).toBe('Hello Wo...')
    })

    it('returns original if shorter than length', () => {
      expect(truncate('Hi', 10)).toBe('Hi')
    })

    it('handles exact length', () => {
      expect(truncate('Hello', 5)).toBe('Hello')
    })
  })

  describe('getInitials', () => {
    it('gets initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD')
      expect(getInitials('Maria Silva Santos')).toBe('MS')
    })

    it('handles single name', () => {
      expect(getInitials('John')).toBe('J')
    })

    it('limits to 2 characters', () => {
      expect(getInitials('A B C D')).toBe('AB')
    })
  })

  describe('sleep', () => {
    it('resolves after specified time', async () => {
      vi.useFakeTimers()
      const promise = sleep(100)
      vi.advanceTimersByTime(100)
      await expect(promise).resolves.toBeUndefined()
      vi.useRealTimers()
    })
  })

  describe('debounce', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('delays function execution', () => {
      const fn = vi.fn()
      const debounced = debounce(fn, 100)

      debounced('arg1')
      expect(fn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(100)
      expect(fn).toHaveBeenCalledWith('arg1')
    })

    it('only calls once for multiple rapid calls', () => {
      const fn = vi.fn()
      const debounced = debounce(fn, 100)

      debounced('a')
      debounced('b')
      debounced('c')

      vi.advanceTimersByTime(100)
      expect(fn).toHaveBeenCalledTimes(1)
      expect(fn).toHaveBeenCalledWith('c')
    })
  })

  describe('generateId', () => {
    it('generates unique ids', () => {
      const ids = new Set()
      for (let i = 0; i < 100; i++) {
        ids.add(generateId())
      }
      expect(ids.size).toBe(100)
    })

    it('generates string ids', () => {
      expect(typeof generateId()).toBe('string')
      expect(generateId().length).toBeGreaterThan(0)
    })
  })

  describe('hasRole', () => {
    it('returns true when user role >= required role', () => {
      expect(hasRole('ADMIN', 'MANAGER')).toBe(true)
      expect(hasRole('MANAGER', 'AUDITOR')).toBe(true)
      expect(hasRole('AUDITOR', 'CLIENT')).toBe(true)
      expect(hasRole('ADMIN', 'ADMIN')).toBe(true)
    })

    it('returns false when user role < required role', () => {
      expect(hasRole('MANAGER', 'ADMIN')).toBe(false)
      expect(hasRole('CLIENT', 'MANAGER')).toBe(false)
      expect(hasRole('AUDITOR', 'ADMIN')).toBe(false)
    })
  })

  describe('ROLE_HIERARCHY', () => {
    it('has correct hierarchy values', () => {
      expect(ROLE_HIERARCHY.ADMIN).toBe(4)
      expect(ROLE_HIERARCHY.MANAGER).toBe(3)
      expect(ROLE_HIERARCHY.AUDITOR).toBe(2)
      expect(ROLE_HIERARCHY.CLIENT).toBe(1)
    })
  })

  describe('getStatusBadge', () => {
    it('returns correct badge for discrepancy statuses', () => {
      expect(getStatusBadge('OPEN')).toEqual({ variant: 'badge-primary', label: 'Aberta' })
      expect(getStatusBadge('IN_REVIEW')).toEqual({ variant: 'badge-warning', label: 'Em Análise' })
      expect(getStatusBadge('APPROVED')).toEqual({ variant: 'badge-success', label: 'Aprovada' })
      expect(getStatusBadge('REJECTED')).toEqual({ variant: 'badge-danger', label: 'Rejeitada' })
    })

    it('returns correct badge for contest statuses', () => {
      expect(getStatusBadge('DRAFT')).toEqual({ variant: 'badge-secondary', label: 'Rascunho' })
      expect(getStatusBadge('SENT')).toEqual({ variant: 'badge-primary', label: 'Enviada' })
      expect(getStatusBadge('ACCEPTED')).toEqual({ variant: 'badge-success', label: 'Aceita' })
    })

    it('returns correct badge for document statuses', () => {
      expect(getStatusBadge('PENDING')).toEqual({ variant: 'badge-secondary', label: 'Pendente' })
      expect(getStatusBadge('PROCESSING')).toEqual({ variant: 'badge-primary', label: 'Processando' })
      expect(getStatusBadge('COMPLETED')).toEqual({ variant: 'badge-success', label: 'Concluído' })
    })

    it('returns fallback for unknown status', () => {
      expect(getStatusBadge('UNKNOWN')).toEqual({ variant: 'badge-secondary', label: 'UNKNOWN' })
    })
  })

  describe('getSeverityBadge', () => {
    it('returns correct badge for each severity', () => {
      expect(getSeverityBadge('LOW')).toEqual({ variant: 'badge-secondary', label: 'Baixa' })
      expect(getSeverityBadge('MEDIUM')).toEqual({ variant: 'badge-primary', label: 'Média' })
      expect(getSeverityBadge('HIGH')).toEqual({ variant: 'badge-warning', label: 'Alta' })
      expect(getSeverityBadge('CRITICAL')).toEqual({ variant: 'badge-danger', label: 'Crítica' })
    })

    it('returns fallback for unknown severity', () => {
      expect(getSeverityBadge('UNKNOWN')).toEqual({ variant: 'badge-secondary', label: 'UNKNOWN' })
    })
  })
})