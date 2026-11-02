export interface User {
  id: string
  email: string
  fullName: string
  role: Role
  status: string
  companyId: string
  clientId?: string
  avatarUrl?: string
  lastLoginAt?: string
  createdAt: string
}

export type Role = 'ADMIN' | 'MANAGER' | 'AUDITOR' | 'CLIENT'

export interface Company {
  id: string
  name: string
  cnpj: string
  email?: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zipCode?: string
  settings: CompanySettings
  createdAt: string
  updatedAt: string
}

export interface CompanySettings {
  autoApproveThreshold?: number
  defaultCurrency: string
  timezone: string
  notifications: {
    email: boolean
    push: boolean
    discrepancies: boolean
    contests: boolean
    documents: boolean
  }
}

export interface Client {
  id: string
  companyId: string
  name: string
  cnpj: string
  email?: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zipCode?: string
  contacts: ClientContact[]
  branches: ClientBranch[]
  createdAt: string
  updatedAt: string
}

export interface ClientContact {
  id: string
  name: string
  email: string
  phone?: string
  role: string
  isPrimary: boolean
}

export interface ClientBranch {
  id: string
  name: string
  code: string
  address?: string
  city?: string
  state?: string
  zipCode?: string
}

export interface Carrier {
  id: string
  companyId: string
  name: string
  cnpj: string
  email?: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zipCode?: string
  contacts: CarrierContact[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface CarrierContact {
  id: string
  name: string
  email: string
  phone?: string
  role: string
}

export interface Contract {
  id: string
  companyId: string
  clientId: string
  carrierId: string
  name: string
  number: string
  version: number
  status: ContractStatus
  startDate: string
  endDate?: string
  freightTable: FreightTableEntry[]
  createdAt: string
  updatedAt: string
}

export type ContractStatus = 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED'

export interface FreightTableEntry {
  id: string
  originCity: string
  originState: string
  destinationCity: string
  destinationState: string
  freightType: FreightType
  weightMin: number
  weightMax: number
  volumeMin?: number
  volumeMax?: number
  value: number
  valueType: 'FIXED' | 'PER_KG' | 'PER_VOLUME'
  icms?: number
  tolls?: number
}

export type FreightType = 'NORMAL' | 'EXPRESS' | 'FRACIONADO' | 'CARGA_FECHADA'

export interface Document {
  id: string
  companyId: string
  clientId?: string
  carrierId?: string
  type: DocumentType
  status: DocumentStatus
  fileName: string
  fileSize: number
  fileUrl?: string
  parsedData?: Record<string, unknown>
  errorMessage?: string
  processedAt?: string
  createdAt: string
  updatedAt: string
}

export type DocumentType = 'CTE' | 'NFE' | 'CTE_COMPLEMENTAR' | 'NFE_COMPLEMENTAR' | 'OTHER'
export type DocumentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'ARCHIVED'

export interface Discrepancy {
  id: string
  companyId: string
  documentId: string
  contractId?: string
  clientId?: string
  carrierId?: string
  type: DiscrepancyType
  severity: DiscrepancySeverity
  status: DiscrepancyStatus
  description: string
  expectedValue: number
  actualValue: number
  difference: number
  differencePercent: number
  fieldName: string
  suggestedAction?: string
  reviewedBy?: string
  reviewedAt?: string
  createdAt: string
  updatedAt: string
}

export type DiscrepancyType =
  | 'FREIGHT_VALUE'
  | 'ICMS'
  | 'TOLLS'
  | 'WEIGHT'
  | 'VOLUME'
  | 'DIMENSIONS'
  | 'DUPLICATE'
  | 'MISSING_DOCUMENT'
  | 'INVALID_CNPJ'
  | 'ROUTE_MISMATCH'
  | 'OTHER'

export type DiscrepancySeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type DiscrepancyStatus = 'OPEN' | 'IN_REVIEW' | 'CONTESTED' | 'APPROVED' | 'REJECTED' | 'PAID' | 'CLOSED'

export interface Contest {
  id: string
  companyId: string
  discrepancyId: string
  documentId: string
  carrierId: string
  status: ContestStatus
  title: string
  description: string
  requestedAmount: number
  offeredAmount?: number
  agreedAmount?: number
  evidenceFiles: ContestEvidence[]
  sentAt?: string
  acknowledgedAt?: string
  resolvedAt?: string
  expiresAt?: string
  createdAt: string
  updatedAt: string
}

export type ContestStatus = 'DRAFT' | 'SENT' | 'ACKNOWLEDGED' | 'NEGOTIATING' | 'ACCEPTED' | 'PARTIAL' | 'REJECTED' | 'EXPIRED'

export interface ContestEvidence {
  id: string
  fileName: string
  fileUrl: string
  fileSize: number
  type: string
}

export interface Notification {
  id: string
  userId: string
  type: NotificationType
  title: string
  message: string
  read: boolean
  actionUrl?: string
  metadata?: Record<string, unknown>
  createdAt: string
}

export type NotificationType = 'DISCREPANCY_FOUND' | 'CONTEST_UPDATE' | 'DOCUMENT_PROCESSED' | 'SYSTEM' | 'PAYMENT'

export interface DashboardKPIs {
  totalDiscrepancies: number
  openDiscrepancies: number
  contestedAmount: number
  recoveredAmount: number
  recoveryRate: number
  documentsProcessed: number
  documentsPending: number
  avgResolutionTime: number
  trends: {
    discrepancies: { date: string; count: number }[]
    recovered: { date: string; amount: number }[]
  }
}

export interface DiscrepancySummary {
  total: number
  by_status: Record<DiscrepancyStatus, number>
  by_severity: Record<DiscrepancySeverity, number>
  by_rule: Record<DiscrepancyType, number>
  total_recovered: number
  total_contested: number
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
}

export interface ApiError {
  message: string
  statusCode: number
  error?: string
  details?: Record<string, string[]>
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  user: User
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}

export interface RegisterRequest {
  email: string
  password: string
  fullName: string
  companyName: string
  companyCnpj: string
}

export interface RefreshTokenRequest {
  refreshToken: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}