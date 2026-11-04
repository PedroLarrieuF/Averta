// Enums - Mirror Backend Prisma Schema
// Keep in sync with backend enum definitions

export type UserRole = 'ADMIN' | 'MANAGER' | 'AUDITOR' | 'CLIENT' | 'CARRIER';

export type UserStatus = 'ACTIVE' | 'INACTIVE' | 'PENDING' | 'INVITED';

export type DocumentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'ARCHIVED';

export type DocumentType = 'CTE' | 'NFE' | 'CTE_COMPLEMENTAR' | 'NFE_COMPLEMENTAR' | 'OTHER';

export type DiscrepancyStatus =
  | 'OPEN'
  | 'IN_REVIEW'
  | 'CONTESTED'
  | 'APPROVED'
  | 'REJECTED'
  | 'PAID'
  | 'CLOSED';

export type DiscrepancySeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

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
  | 'OTHER';

export type ContestStatus =
  | 'DRAFT'
  | 'SENT'
  | 'ACKNOWLEDGED'
  | 'NEGOTIATING'
  | 'ACCEPTED'
  | 'PARTIAL'
  | 'REJECTED'
  | 'EXPIRED';

export type ContestItemStatus = 'PENDING' | 'ACKNOWLEDGED' | 'NEGOTIATING' | 'ACCEPTED' | 'PARTIAL' | 'REJECTED';

export type NotificationType =
  | 'DISCREPANCY_FOUND'
  | 'CONTEST_UPDATE'
  | 'DOCUMENT_PROCESSED'
  | 'SYSTEM'
  | 'PAYMENT';

export type NotificationChannel = 'EMAIL' | 'IN_APP' | 'PUSH' | 'SMS';

export type FreightTableStatus = 'DRAFT' | 'ACTIVE' | 'ARCHIVED';

export type ContractStatus = 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED';

export type FreightType = 'NORMAL' | 'EXPRESS' | 'FRACIONADO' | 'CARGA_FECHADA';

export type ModalType = 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';

export type FreightValueType = 'FIXED' | 'PER_KG' | 'PER_VOLUME';