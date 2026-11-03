import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'

// Types
export interface ReportFilters {
  period?: string
  dateFrom?: string
  dateTo?: string
  carrierId?: string
  clientId?: string
  status?: string
  ruleCode?: string
  severity?: string
}

export interface DashboardKPIs {
  total_discrepancies: number
  total_recovered: number
  success_rate: number
  avg_resolution_days: number
}

export interface TimeSeriesPoint {
  date: string
  count: number
  value: number
}

export interface TopCarrier {
  carrier_id: string
  carrier_name: string
  recovered: number
  count: number
}

export interface TopRule {
  rule_code: string
  count: number
  total_value: number
}

export interface SeverityDistribution {
  severity: string
  count: number
}

export interface DashboardResponse {
  kpis: DashboardKPIs
  time_series: TimeSeriesPoint[]
  top_carriers: TopCarrier[]
  top_rules: TopRule[]
  by_severity: SeverityDistribution[]
}

export interface ScheduleRequest {
  name: string
  frequency: 'weekly'
  day_of_week: number
  hour: number
  format: 'pdf' | 'excel'
  filters: ReportFilters
  recipients: string[]
}

export interface ScheduleResponse {
  id: string
  name: string
  frequency: 'weekly'
  day_of_week: number
  hour: number
  format: 'pdf' | 'excel'
  filters: ReportFilters
  recipients: string[]
  is_active: boolean
  created_at: string
  last_run_at?: string
  next_run_at?: string
}

// Query keys
export const reportKeys = {
  all: ['reports'] as const,
  dashboard: (filters: ReportFilters) => [...reportKeys.all, 'dashboard', filters] as const,
  schedules: () => [...reportKeys.all, 'schedules'] as const,
  schedule: (id: string) => [...reportKeys.all, 'schedule', id] as const,
}

// Dashboard hook
export function useReportDashboard(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: reportKeys.dashboard(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.set(key, value)
        }
      })
      const response = await api.get<DashboardResponse>(`/reports/dashboard?${params.toString()}`)
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Export hooks
export function useExportPDF(filters: ReportFilters = {}) {
  return useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.set(key, value)
        }
      })
      params.set('format', 'pdf')
      const response = await api.get(`/reports/pdf?${params.toString()}`, {
        responseType: 'blob',
      })
      return response.data
    },
  })
}

export function useExportExcel(filters: ReportFilters = {}) {
  return useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.set(key, value)
        }
      })
      params.set('format', 'excel')
      const response = await api.get(`/reports/excel?${params.toString()}`, {
        responseType: 'blob',
      })
      return response.data
    },
  })
}

// Schedule hooks
export function useReportSchedules() {
  return useQuery({
    queryKey: reportKeys.schedules(),
    queryFn: async () => {
      const response = await api.get<ScheduleResponse[]>('/reports/schedule')
      return response.data
    },
  })
}

export function useCreateReportSchedule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: ScheduleRequest) => {
      const response = await api.post<ScheduleResponse>('/reports/schedule', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() })
    },
  })
}

export function useUpdateReportSchedule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<ScheduleRequest> & { is_active?: boolean } }) => {
      const response = await api.patch<ScheduleResponse>(`/reports/schedule/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() })
    },
  })
}

export function useDeleteReportSchedule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/reports/schedule/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reportKeys.schedules() })
    },
  })
}