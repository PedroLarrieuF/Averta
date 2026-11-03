import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query'
import { apiClient } from './useApi'
import type { User, Carrier, Contract, Company, PaginatedResponse, Role } from '@/types'

// ============================================================================
// User Hooks
// ============================================================================

export function useUsers(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<User>>) {
  return useQuery({
    queryKey: ['users', params] as const,
    queryFn: () => apiClient.get<PaginatedResponse<User>>('/users', params),
    ...options,
  })
}

export function useUser(id: string, options?: UseQueryOptions<User>) {
  return useQuery({
    queryKey: ['users', id] as const,
    queryFn: () => apiClient.get<User>(`/users/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<User> & { password: string }) => apiClient.post<User>('/users', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      apiClient.patch<User>(`/users/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

export function useDeleteUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/users/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

export function useInviteUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { email: string; role: Role; companyId: string }) =>
      apiClient.post<User>('/users/invite', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

export function useResendInvite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.post(`/users/${id}/resend-invite`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

// ============================================================================
// Carrier Hooks
// ============================================================================

export function useSettingsCarriers(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Carrier>>) {
  return useQuery({
    queryKey: ['settings', 'carriers', params] as const,
    queryFn: () => apiClient.get<PaginatedResponse<Carrier>>('/carriers', params),
    ...options,
  })
}

export function useSettingsCarrier(id: string, options?: UseQueryOptions<Carrier>) {
  return useQuery({
    queryKey: ['settings', 'carriers', id] as const,
    queryFn: () => apiClient.get<Carrier>(`/carriers/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useCreateCarrier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Carrier>) => apiClient.post<Carrier>('/carriers', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'carriers'] })
    },
  })
}

export function useUpdateCarrier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Carrier> }) =>
      apiClient.patch<Carrier>(`/carriers/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'carriers', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['settings', 'carriers'] })
    },
  })
}

export function useDeleteCarrier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/carriers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'carriers'] })
    },
  })
}

export function useToggleCarrierStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      apiClient.patch<Carrier>(`/carriers/${id}`, { is_active: isActive }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'carriers', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['settings', 'carriers'] })
    },
  })
}

// ============================================================================
// Contract Hooks (Settings-specific)
// ============================================================================

export function useSettingsContracts(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Contract>>) {
  return useQuery({
    queryKey: ['settings', 'contracts', params] as const,
    queryFn: () => apiClient.get<PaginatedResponse<Contract>>('/contracts', params),
    ...options,
  })
}

export function useSettingsContract(id: string, options?: UseQueryOptions<Contract>) {
  return useQuery({
    queryKey: ['settings', 'contracts', id] as const,
    queryFn: () => apiClient.get<Contract>(`/contracts/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useCreateContract() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Contract>) => apiClient.post<Contract>('/contracts', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'contracts'] })
    },
  })
}

export function useUpdateContract() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Contract> }) =>
      apiClient.patch<Contract>(`/contracts/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'contracts', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['settings', 'contracts'] })
    },
  })
}

export function useDeleteContract() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/contracts/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'contracts'] })
    },
  })
}

export function useContractVersions(contractId: string, options?: UseQueryOptions<Contract[]>) {
  return useQuery({
    queryKey: ['settings', 'contracts', contractId, 'versions'] as const,
    queryFn: () => apiClient.get<Contract[]>(`/contracts/${contractId}/versions`),
    enabled: !!contractId,
    ...options,
  })
}

export function useCreateContractVersion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ contractId, data }: { contractId: string; data: Partial<Contract> }) =>
      apiClient.post<Contract>(`/contracts/${contractId}/versions`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'contracts', variables.contractId, 'versions'] })
      queryClient.invalidateQueries({ queryKey: ['settings', 'contracts'] })
    },
  })
}

// ============================================================================
// Company Settings Hooks
// ============================================================================

export function useCompanySettings(companyId: string, options?: UseQueryOptions<Company>) {
  return useQuery({
    queryKey: ['companies', companyId, 'settings'] as const,
    queryFn: () => apiClient.get<Company>(`/companies/${companyId}`),
    enabled: !!companyId,
    ...options,
  })
}

export function useUpdateCompanySettings() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ companyId, data }: { companyId: string; data: Partial<Company> }) =>
      apiClient.patch<Company>(`/companies/${companyId}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['companies', variables.companyId] })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
  })
}

export function useUploadCompanyLogo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ companyId, formData }: { companyId: string; formData: FormData }) =>
      apiClient.post<{ logoUrl: string }>(`/companies/${companyId}/logo`, formData),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['companies', variables.companyId] })
    },
  })
}

// ============================================================================
// Notification Settings Hooks
// ============================================================================

export interface NotificationPreferences {
  email: boolean
  push: boolean
  discrepancies: boolean
  contests: boolean
  documents: boolean
  payments: boolean
  reports: boolean
}

export function useNotificationPreferences(userId: string, options?: UseQueryOptions<NotificationPreferences>) {
  return useQuery({
    queryKey: ['users', userId, 'notification-preferences'] as const,
    queryFn: () => apiClient.get<NotificationPreferences>(`/users/${userId}/notification-preferences`),
    enabled: !!userId,
    ...options,
  })
}

export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: Partial<NotificationPreferences> }) =>
      apiClient.patch<NotificationPreferences>(`/users/${userId}/notification-preferences`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['users', variables.userId, 'notification-preferences'] })
    },
  })
}

export interface NotificationTemplate {
  id: string
  type: string
  channel: 'email' | 'push'
  subject: string
  body: string
  variables: string[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export function useNotificationTemplates(options?: UseQueryOptions<NotificationTemplate[]>) {
  return useQuery({
    queryKey: ['notification-templates'] as const,
    queryFn: () => apiClient.get<NotificationTemplate[]>('/notification-templates'),
    ...options,
  })
}

export function useUpdateNotificationTemplate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<NotificationTemplate> }) =>
      apiClient.patch<NotificationTemplate>(`/notification-templates/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-templates'] })
    },
  })
}

// ============================================================================
// Freight Table Hooks
// ============================================================================

export interface FreightTableVersion {
  id: string
  contractId: string
  version: number
  name: string
  rules: Record<string, unknown>[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export function useFreightTableVersions(contractId: string, options?: UseQueryOptions<FreightTableVersion[]>) {
  return useQuery({
    queryKey: ['contracts', contractId, 'freight-table-versions'] as const,
    queryFn: () => apiClient.get<FreightTableVersion[]>(`/contracts/${contractId}/freight-table-versions`),
    enabled: !!contractId,
    ...options,
  })
}

export function useCreateFreightTableVersion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ contractId, data }: { contractId: string; data: { name: string; rules: Record<string, unknown>[] } }) =>
      apiClient.post<FreightTableVersion>(`/contracts/${contractId}/freight-table-versions`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['contracts', variables.contractId, 'freight-table-versions'] })
    },
  })
}

export function useUpdateFreightTableVersion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FreightTableVersion> }) =>
      apiClient.patch<FreightTableVersion>(`/freight-table-versions/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts', '', 'freight-table-versions'] })
    },
  })
}

export function useActivateFreightTableVersion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.post(`/freight-table-versions/${id}/activate`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts', '', 'freight-table-versions'] })
    },
  })
}

export function useValidateFreightTableRules() {
  return useMutation({
    mutationFn: (rules: Record<string, unknown>[]) =>
      apiClient.post<{ valid: boolean; errors: string[] }>('/freight-table-rules/validate', { rules }),
  })
}