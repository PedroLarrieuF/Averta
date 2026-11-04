// Common API Types
export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface ApiError {
  message: string;
  statusCode: number;
  error?: string;
  details?: Record<string, string[]>;
}

export interface PaginationParams {
  page?: number;
  size?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface FilterParams {
  search?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface SortingState {
  columnId: string;
  direction: 'asc' | 'desc';
}

export interface TableState<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  sorting: SortingState;
  filters: Record<string, unknown>;
}