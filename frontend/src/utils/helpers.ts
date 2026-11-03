import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number, currency = 'BRL'): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value)
}

export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`
}

export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    ...options,
  })
}

export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'agora mesmo'
  if (diffMins < 60) return `${diffMins}min atrás`
  if (diffHours < 24) return `${diffHours}h atrás`
  if (diffDays < 7) return `${diffDays}d atrás`
  return formatDate(d)
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15)
}

export const ROLES = {
  ADMIN: 'ADMIN',
  MANAGER: 'MANAGER',
  AUDITOR: 'AUDITOR',
  CLIENT: 'CLIENT',
} as const

export type Role = (typeof ROLES)[keyof typeof ROLES]

export const ROLE_HIERARCHY: Record<Role, number> = {
  ADMIN: 4,
  MANAGER: 3,
  AUDITOR: 2,
  CLIENT: 1,
}

export function hasRole(userRole: Role, requiredRole: Role): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY[requiredRole]
}

export const DISCREPANCY_STATUS = {
  OPEN: 'OPEN',
  IN_REVIEW: 'IN_REVIEW',
  CONTESTED: 'CONTESTED',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
  PAID: 'PAID',
  CLOSED: 'CLOSED',
} as const

export const CONTEST_STATUS = {
  DRAFT: 'DRAFT',
  SENT: 'SENT',
  ACKNOWLEDGED: 'ACKNOWLEDGED',
  NEGOTIATING: 'NEGOTIATING',
  ACCEPTED: 'ACCEPTED',
  PARTIAL: 'PARTIAL',
  REJECTED: 'REJECTED',
  EXPIRED: 'EXPIRED',
} as const

export const DOCUMENT_STATUS = {
  PENDING: 'PENDING',
  PROCESSING: 'PROCESSING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  ARCHIVED: 'ARCHIVED',
} as const

export const DOCUMENT_TYPE = {
  CTE: 'CTE',
  NFE: 'NFE',
  CTE_COMPLEMENTAR: 'CTE_COMPLEMENTAR',
  NFE_COMPLEMENTAR: 'NFE_COMPLEMENTAR',
  OTHER: 'OTHER',
} as const

export function getStatusBadge(status: string): { variant: string; label: string } {
  const statusMap: Record<string, { variant: string; label: string }> = {
    // Discrepancy
    OPEN: { variant: 'badge-primary', label: 'Aberta' },
    IN_REVIEW: { variant: 'badge-warning', label: 'Em Análise' },
    CONTESTED: { variant: 'badge-warning', label: 'Contestada' },
    APPROVED: { variant: 'badge-success', label: 'Aprovada' },
    REJECTED: { variant: 'badge-danger', label: 'Rejeitada' },
    PAID: { variant: 'badge-success', label: 'Paga' },
    CLOSED: { variant: 'badge-secondary', label: 'Fechada' },
    // Contest
    DRAFT: { variant: 'badge-secondary', label: 'Rascunho' },
    SENT: { variant: 'badge-primary', label: 'Enviada' },
    ACKNOWLEDGED: { variant: 'badge-warning', label: 'Recebida' },
    NEGOTIATING: { variant: 'badge-warning', label: 'Negociando' },
    ACCEPTED: { variant: 'badge-success', label: 'Aceita' },
    PARTIAL: { variant: 'badge-warning', label: 'Parcial' },
    EXPIRED: { variant: 'badge-secondary', label: 'Expirada' },
    // Document
    PENDING: { variant: 'badge-secondary', label: 'Pendente' },
    PROCESSING: { variant: 'badge-primary', label: 'Processando' },
    COMPLETED: { variant: 'badge-success', label: 'Concluído' },
    FAILED: { variant: 'badge-danger', label: 'Falhou' },
    ARCHIVED: { variant: 'badge-secondary', label: 'Arquivado' },
  }
  return statusMap[status] || { variant: 'badge-secondary', label: status }
}

export function getSeverityBadge(severity: string): { variant: string; label: string } {
  const severityMap: Record<string, { variant: string; label: string }> = {
    LOW: { variant: 'badge-secondary', label: 'Baixa' },
    MEDIUM: { variant: 'badge-primary', label: 'Média' },
    HIGH: { variant: 'badge-warning', label: 'Alta' },
    CRITICAL: { variant: 'badge-danger', label: 'Crítica' },
  }
  return severityMap[severity] || { variant: 'badge-secondary', label: severity }
}