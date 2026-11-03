import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { queryKeys } from './useApi'
import type { Discrepancy } from '../types'

const apiClient = {
  get: <T>(url: string, params?: Record<string, unknown>) =>
    api.get<T>(url, { params }).then((r) => r.data),
  post: <T>(url: string, data?: unknown) =>
    api.post<T>(url, data).then((r) => r.data),
  put: <T>(url: string, data?: unknown) =>
    api.put<T>(url, data).then((r) => r.data),
  patch: <T>(url: string, data?: unknown) =>
    api.patch<T>(url, data).then((r) => r.data),
  delete: <T>(url: string) =>
    api.delete<T>(url).then((r) => r.data),
}

// Bulk update discrepancies status (e.g., to IN_REVIEW)
export function useBulkUpdateDiscrepancyStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { ids: string[]; status: string }) =>
      apiClient.patch<Discrepancy[]>('/discrepancies/bulk-status', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.summary() })
    },
  })
}

// Review a single discrepancy with notes
export function useReviewDiscrepancy() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      apiClient.post<Discrepancy>(`/discrepancies/${id}/review`, { notes }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.summary() })
    },
  })
}

// Bulk review multiple discrepancies
export function useBulkReviewDiscrepancies() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { ids: string[]; notes?: string }) =>
      apiClient.post<Discrepancy[]>('/discrepancies/bulk-review', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.summary() })
    },
  })
}

// Create contest from selected discrepancies
export function useCreateContestFromDiscrepancies() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { discrepancyIds: string[]; title: string; description: string }) =>
      apiClient.post<{ contestId: string }>('/contests/from-discrepancies', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
    },
  })
}