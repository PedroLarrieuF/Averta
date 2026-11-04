import type {
  DiscrepancyStatus,
  DiscrepancySeverity,
  DiscrepancyType,
} from './enums';
import type { PaginatedResponse } from './common';

// Re-export enums for convenience
export type { DiscrepancyType, DiscrepancySeverity, DiscrepancyStatus } from './enums';

export interface Discrepancy {
  id: string;
  companyId: string;
  documentId: string;
  contractId?: string;
  clientId?: string;
  carrierId?: string;
  type: DiscrepancyType;
  severity: DiscrepancySeverity;
  status: DiscrepancyStatus;
  description: string;
  expectedValue: number;
  actualValue: number;
  difference: number;
  differencePercent: number;
  fieldName: string;
  suggestedAction?: string;
  reviewedBy?: string;
  reviewedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DiscrepancySummary {
  total: number;
  by_status: Record<DiscrepancyStatus, number>;
  by_severity: Record<DiscrepancySeverity, number>;
  by_rule: Record<DiscrepancyType, number>;
  total_recovered: number;
  total_contested: number;
}

export type DiscrepancyListResponse = PaginatedResponse<Discrepancy>;

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

export interface DiscrepancyBulkUpdateRequest {
  ids: string[];
  status: DiscrepancyStatus;
}

export interface DiscrepancyReviewRequest {
  notes: string;
}

export interface DiscrepancyReviewResponse {
  discrepancy: Discrepancy;
  message: string;
}

export interface DiscrepancyCreateRequest {
  documentId: string;
  contractId?: string;
  clientId?: string;
  carrierId?: string;
  type: DiscrepancyType;
  severity: DiscrepancySeverity;
  description: string;
  expectedValue: number;
  actualValue: number;
  difference: number;
  differencePercent: number;
  fieldName: string;
  suggestedAction?: string;
}

export interface DiscrepancyUpdateRequest {
  severity?: DiscrepancySeverity;
  description?: string;
  expectedValue?: number;
  actualValue?: number;
  difference?: number;
  differencePercent?: number;
  fieldName?: string;
  suggestedAction?: string;
}