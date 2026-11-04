import type { PaginatedResponse } from './common';

// Dashboard KPIs
export interface DashboardKPIs {
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
}

export interface DiscrepancySummary {
  total: number;
  by_status: Record<string, number>;
  by_severity: Record<string, number>;
  by_rule: Record<string, number>;
  total_recovered: number;
  total_contested: number;
}

export interface RecoveryReport {
  id: string;
  period: string;
  totalDiscrepancies: number;
  totalContested: number;
  totalRecovered: number;
  recoveryRate: number;
  byCarrier: Array<{ carrierId: string; carrierName: string; count: number; recovered: number }>;
  byRule: Array<{ ruleCode: string; count: number; recovered: number }>;
  createdAt: string;
}

export interface RecoveryReportFilters {
  period?: '7d' | '30d' | '90d' | 'custom';
  dateFrom?: string;
  dateTo?: string;
  carrierIds?: string[];
  clientIds?: string[];
}

export interface CarrierPerformanceReport {
  carrierId: string;
  carrierName: string;
  totalDiscrepancies: number;
  totalContested: number;
  totalRecovered: number;
  recoveryRate: number;
  avgResolutionTime: number;
  topRules: Array<{ ruleCode: string; count: number; recovered: number }>;
}

export interface CarrierPerformanceFilters {
  carrierIds?: string[];
  dateFrom?: string;
  dateTo?: string;
}

export interface ReportsDashboardResponse {
  kpis: {
    total_documents: number;
    total_discrepancies: number;
    total_recovered: number;
    pending_contests: number;
    success_rate: number;
  };
  top_carriers: Array<{
    carrier_name: string;
    count: number;
    value: number;
  }>;
  top_rules: Array<{
    rule_code: string;
    count: number;
    total_difference: number;
  }>;
  time_series: Array<{
    date: string;
    discrepancies: number;
    recovered: number;
  }>;
}

export interface ScheduledReport {
  id: string;
  companyId: string;
  name: string;
  description?: string;
  format: 'PDF' | 'EXCEL';
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  dayOfWeek?: number;
  dayOfMonth?: number;
  hour: number;
  minute: number;
  filters: Record<string, unknown>;
  recipients: string[];
  isActive: boolean;
  lastRunAt?: string;
  nextRunAt?: string;
  createdAt: string;
  updatedAt: string;
}

export type ScheduledReportListResponse = PaginatedResponse<ScheduledReport>;

export interface ScheduledReportCreateRequest {
  name: string;
  description?: string;
  format: 'PDF' | 'EXCEL';
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  dayOfWeek?: number;
  dayOfMonth?: number;
  hour: number;
  minute: number;
  filters: Record<string, unknown>;
  recipients: string[];
  isActive: boolean;
}

export interface ScheduledReportUpdateRequest {
  name?: string;
  description?: string;
  format?: 'PDF' | 'EXCEL';
  frequency?: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  dayOfWeek?: number;
  dayOfMonth?: number;
  hour?: number;
  minute?: number;
  filters?: Record<string, unknown>;
  recipients?: string[];
  isActive?: boolean;
}

export interface ReportExportRequest {
  format: 'pdf' | 'excel';
  filters: Record<string, unknown>;
}

export interface ReportExportResponse {
  url: string;
  expiresAt: string;
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