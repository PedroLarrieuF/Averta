import type { ContestStatus } from './enums';
import type { Discrepancy } from './discrepancies';
import type { PaginatedResponse } from './common';

// Re-export enums for convenience
export type { ContestStatus } from './enums';

export interface ContestEvidence {
  id: string;
  fileName: string;
  fileUrl: string;
  fileSize: number;
  type: string;
  uploadedAt: string;
}

export interface Contest {
  id: string;
  companyId: string;
  discrepancyId: string;
  discrepancyIds?: string[];
  documentId: string;
  carrierId: string;
  status: ContestStatus;
  title: string;
  description: string;
  requestedAmount: number;
  offeredAmount?: number;
  agreedAmount?: number;
  evidenceFiles: ContestEvidence[];
  items?: Discrepancy[];
  sentAt?: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
  expiresAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ContestItem {
  id: string;
  contestId: string;
  discrepancyId: string;
  discrepancy?: Discrepancy;
  status: string;
  requestedAmount: number;
  offeredAmount?: number;
  agreedAmount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface ContestCommunication {
  id: string;
  contestId: string;
  authorId: string;
  authorName: string;
  authorRole: string;
  message: string;
  attachments: ContestEvidence[];
  isInternal: boolean;
  createdAt: string;
}

export interface ContestPayment {
  id: string;
  contestId: string;
  amount: number;
  paymentDate: string;
  paymentMethod: string;
  reference: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';
  createdAt: string;
}

export interface SuccessFeeCalculation {
  contractSuccessFeePct: number;
  totalRecovered: number;
  successFeeAmount: number;
  netAmount: number;
}

export type ContestListResponse = PaginatedResponse<Contest>;

export interface ContestCreateRequest {
  discrepancyIds: string[];
  carrierId: string;
  title: string;
  description: string;
  requestedAmount: number;
  evidenceFiles?: File[];
}

export interface ContestSendRequest {
  contestId: string;
}

export interface ContestNegotiateRequest {
  contestId: string;
  offeredAmount: number;
  message: string;
}

export interface ContestPaymentRequest {
  contestId: string;
  amount: number;
  paymentMethod: string;
  reference: string;
}

export interface ContestPDFResponse {
  url: string;
  expiresAt: string;
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

export interface ContestUpdateRequest {
  title?: string;
  description?: string;
  requestedAmount?: number;
}

export interface ContestAcknowledgeRequest {
  contestId: string;
}

export interface ContestResolveRequest {
  contestId: string;
  agreedAmount: number;
}