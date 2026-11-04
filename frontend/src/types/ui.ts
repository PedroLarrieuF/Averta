import type {
  DiscrepancyStatus,
  DiscrepancySeverity,
  DiscrepancyType,
  DocumentStatus,
  DocumentType,
  ContestStatus,
} from './enums';

// UI State Types

export interface ModalState<T = unknown> {
  isOpen: boolean;
  data: T | null;
  mode: 'create' | 'edit' | 'view';
}

export interface ConfirmDialogState {
  isOpen: boolean;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'primary';
  onConfirm: () => void;
  loading?: boolean;
}

export interface ToastState {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  duration?: number;
  action?: React.ReactNode;
}

// Filter Types (re-exported for convenience)
export interface DiscrepancyFilters {
  status?: DiscrepancyStatus[];
  severity?: DiscrepancySeverity[];
  rule_code?: DiscrepancyType[];
  clientId?: string;
  carrierId?: string;
  contractId?: string;
  documentId?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  size?: number;
}

export interface DocumentFilters {
  status?: DocumentStatus[];
  documentType?: DocumentType[];
  clientId?: string;
  carrierId?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  size?: number;
}

export interface ContestFilters {
  status?: ContestStatus[];
  carrierId?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  size?: number;
}

export interface ClientFilters {
  status?: 'ACTIVE' | 'INACTIVE';
  search?: string;
  city?: string;
  state?: string;
  page?: number;
  size?: number;
}

export interface CarrierFilters {
  status?: 'ACTIVE' | 'INACTIVE';
  search?: string;
  city?: string;
  state?: string;
  page?: number;
  size?: number;
}

export interface ContractFilters {
  status?: 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED';
  clientId?: string;
  carrierId?: string;
  search?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  size?: number;
}

export interface ReportFilters {
  period?: '7d' | '30d' | '90d' | 'custom';
  dateFrom?: string;
  dateTo?: string;
  carrierIds?: string[];
  clientIds?: string[];
  ruleCodes?: string[];
  severity?: string[];
  status?: string[];
}

export interface NotificationFilters {
  read?: boolean;
  type?: string[];
  channel?: string[];
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  page?: number;
  size?: number;
}

// Table State (generic)
export interface TableState<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  sorting: {
    columnId: string;
    direction: 'asc' | 'desc';
  };
  filters: Record<string, unknown>;
}

// Select Options
export interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
}

export interface SimpleSelectOptions {
  clients: SelectOption[];
  carriers: SelectOption[];
  users: SelectOption[];
  contracts: SelectOption[];
}