import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { queryKeys } from './useApi'
import type { Contest, PaginatedResponse } from '../types'

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

// Send contest (generate PDF and send to carrier)
export function useSendContest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.post<Contest>(`/contests/${id}/send`),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(data.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
    },
  })
}

// Generate contest PDF
export function useGenerateContestPDF() {
  return useMutation({
    mutationFn: (id: string) => apiClient.post<{ url: string }>(`/contests/${id}/pdf`),
  })
}

// Negotiate contest (update status, add notes, offered amount)
export function useNegotiateContest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { id: string; status: Contest['status']; notes?: string; offeredAmount?: number }) =>
      apiClient.patch<Contest>(`/contests/${data.id}/negotiate`, {
        status: data.status,
        notes: data.notes,
        offeredAmount: data.offeredAmount,
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(data.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
    },
  })
}

// Add communication to contest
export function useAddContestCommunication() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { contestId: string; type: 'INBOUND' | 'OUTBOUND'; subject: string; body: string; attachments?: string[] }) =>
      apiClient.post<{ id: string }>(`/contests/${data.contestId}/communications`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(variables.contestId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
    },
  })
}

// Get contest communications
export function useContestCommunications(contestId: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: [...queryKeys.contests.detail(contestId), 'communications'],
    queryFn: () => apiClient.get<PaginatedResponse<{
      id: string
      contestId: string
      type: 'INBOUND' | 'OUTBOUND'
      subject: string
      body: string
      attachments: Array<{ id: string; fileName: string; fileUrl: string; fileSize: number }>
      createdAt: string
    }>>(`/contests/${contestId}/communications`),
    enabled: options?.enabled ?? !!contestId,
  })
}

// Register payment
export function useRegisterPayment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { contestId: string; amount: number; paidAt: string; proofFile?: File; notes?: string }) => {
      const formData = new FormData()
      formData.append('amount', data.amount.toString())
      formData.append('paidAt', data.paidAt)
      if (data.notes) formData.append('notes', data.notes)
      if (data.proofFile) formData.append('proofFile', data.proofFile)
      return apiClient.post<{ id: string; successFee: number; netRecovery: number }>(`/contests/${data.contestId}/payments`, formData)
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(variables.contestId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
    },
  })
}

// Get contest payments
export function useContestPayments(contestId: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: [...queryKeys.contests.detail(contestId), 'payments'],
    queryFn: () => apiClient.get<PaginatedResponse<{
      id: string
      contestId: string
      amount: number
      successFee: number
      netRecovery: number
      paidAt: string
      proofUrl?: string
      notes?: string
      createdAt: string
    }>>(`/contests/${contestId}/payments`),
    enabled: options?.enabled ?? !!contestId,
  })
}

// Calculate success fee
export function useCalculateSuccessFee() {
  return useMutation({
    mutationFn: (data: { totalRecovered: number; successFeePct: number }) =>
      apiClient.post<{ successFee: number; netRecovery: number }>('/contests/calculate-fee', data),
  })
}

// Upload evidence file
export function useUploadContestEvidence() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { contestId: string; file: File; type: string }) => {
      const formData = new FormData()
      formData.append('file', data.file)
      formData.append('type', data.type)
      return apiClient.post<{ id: string; url: string }>(`/contests/${data.contestId}/evidence`, formData)
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(variables.contestId) })
    },
  })
}

// Delete evidence
export function useDeleteContestEvidence() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { contestId: string; evidenceId: string }) =>
      apiClient.delete(`/contests/${data.contestId}/evidence/${data.evidenceId}`),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(variables.contestId) })
    },
  })
}