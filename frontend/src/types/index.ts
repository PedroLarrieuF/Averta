// TypeScript Types Barrel Export
// Centralized re-exports for all domain types

// Enums (base types)
export * from './enums';

// Common utilities
export * from './common';

// Domain types - explicit exports to avoid conflicts
// Auth
export type { User, Role, UserStatus, LoginRequest, LoginResponse, RegisterRequest, RefreshTokenRequest, RefreshTokenResponse } from './auth';

// Clients
export type { Client, ClientContact, ClientBranch, ClientListResponse, ClientFilters, ClientCreateRequest, ClientUpdateRequest, ClientBranchCreateRequest, ClientBranchUpdateRequest, ClientContactCreateRequest, ClientContactUpdateRequest } from './clients';

// Carriers
export type { Carrier, CarrierContact, CarrierBranch, CarrierListResponse, CarrierFilters, CarrierCreateRequest, CarrierUpdateRequest, CarrierBranchCreateRequest, CarrierBranchUpdateRequest, CarrierContactCreateRequest, CarrierContactUpdateRequest } from './carriers';

// Contracts
export type { Contract, FreightTable, FreightRate, FreightTableEntry, ContractListResponse, ContractFilters, ContractCreateRequest, ContractUpdateRequest, FreightTableCreateRequest, FreightTableUpdateRequest, FreightTableActivateRequest, FreightTableVersionResponse } from './contracts';

// Documents
export type { Document, DocumentType, DocumentStatus, DocumentListResponse, DocumentFilters, DocumentCreateRequest, DocumentUpdateRequest } from './documents';

// Discrepancies
export type { Discrepancy, DiscrepancyType, DiscrepancySeverity, DiscrepancyStatus, DiscrepancyListResponse, DiscrepancyFilters, DiscrepancySummary, DiscrepancyCreateRequest, DiscrepancyUpdateRequest, DiscrepancyReviewRequest } from './discrepancies';

// Contests
export type { Contest, ContestStatus, ContestEvidence, ContestListResponse, ContestFilters, ContestCreateRequest, ContestUpdateRequest, ContestNegotiateRequest, ContestAcknowledgeRequest, ContestResolveRequest } from './contests';

// Reports
export type { DiscrepancySummary as ReportDiscrepancySummary, RecoveryReport, RecoveryReportFilters, CarrierPerformanceReport, CarrierPerformanceFilters } from './reports';

// Notifications
export type { Notification, NotificationType, NotificationChannel, NotificationListResponse, NotificationFilters, NotificationPreferences, NotificationPreferencesUpdateRequest, NotificationMarkReadRequest, NotificationMarkAllReadRequest, UnreadNotificationCountResponse } from './notifications';

// UI
export type { ModalState, ConfirmDialogState, ToastState, DiscrepancyFilters as UIDiscrepancyFilters, DocumentFilters as UIDocumentFilters, ContestFilters as UIContestFilters, ClientFilters as UIClientFilters, CarrierFilters as UICarrierFilters, ContractFilters as UIContractFilters, ReportFilters, NotificationFilters as UINotificationFilters, TableState, SelectOption, SimpleSelectOptions } from './ui';

// Forms
export type * from './forms';

// Legacy types for backwards compatibility with existing components
export interface Company {
  id: string;
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  settings: CompanySettings;
  createdAt: string;
  updatedAt: string;
}

export interface CompanySettings {
  autoApproveThreshold?: number;
  defaultCurrency: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    discrepancies: boolean;
    contests: boolean;
    documents: boolean;
  };
}

export type DashboardKPIs = {
  totalDiscrepancies: number;
  openDiscrepancies: number;
  contestedAmount: number;
  recoveredAmount: number;
  recoveryRate: number;
  documentsProcessed: number;
  documentsPending: number;
  avgResolutionTime: number;
  trends: {
    discrepancies: { date: string; count: number }[];
    recovered: { date: string; amount: number }[];
  };
};