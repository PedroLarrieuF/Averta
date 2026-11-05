import { useQuery, useMutation, useQueryClient, UseQueryOptions } from '@tanstack/react-query'
import { demoAwareApi } from '../services/api'
import type {
  User,
  Company,
  Client,
  ClientBranch,
  Carrier,
  CarrierBranch,
  Contract,
  Document,
  Discrepancy,
  Contest,
  Notification,
  DashboardKPIs,
  DiscrepancySummary,
  PaginatedResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RefreshTokenRequest,
  RefreshTokenResponse,
} from '../types'

// Query keys factory
export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  companies: {
    all: ['companies'] as const,
    detail: (id: string) => ['companies', id] as const,
    settings: (id: string) => ['companies', id, 'settings'] as const,
  },
  clients: {
    all: (params?: Record<string, unknown>) => ['clients', params] as const,
    detail: (id: string) => ['clients', id] as const,
    branches: (clientId: string) => ['clients', clientId, 'branches'] as const,
  },
  carriers: {
    all: (params?: Record<string, unknown>) => ['carriers', params] as const,
    detail: (id: string) => ['carriers', id] as const,
    branches: (carrierId: string) => ['carriers', carrierId, 'branches'] as const,
  },
  contracts: {
    all: (params?: Record<string, unknown>) => ['contracts', params] as const,
    detail: (id: string) => ['contracts', id] as const,
    versions: (id: string) => ['contracts', id, 'versions'] as const,
  },
  documents: {
    all: (params?: Record<string, unknown>) => ['documents', params] as const,
    detail: (id: string) => ['documents', id] as const,
  },
  discrepancies: {
    all: (params?: Record<string, unknown>) => ['discrepancies', params] as const,
    detail: (id: string) => ['discrepancies', id] as const,
    summary: (params?: Record<string, unknown>) => ['discrepancies', 'summary', params] as const,
  },
  contests: {
    all: (params?: Record<string, unknown>) => ['contests', params] as const,
    detail: (id: string) => ['contests', id] as const,
  },
  reports: {
    dashboard: ['reports', 'dashboard'] as const,
    discrepancies: (params?: Record<string, unknown>) => ['reports', 'discrepancies', params] as const,
    recovery: (params?: Record<string, unknown>) => ['reports', 'recovery', params] as const,
  },
  notifications: {
    all: (params?: Record<string, unknown>) => ['notifications', params] as const,
    unreadCount: ['notifications', 'unread-count'] as const,
  },
} as const

// Generic API functions
export const apiClient = {
  get: <T>(url: string, params?: Record<string, unknown>) =>
    demoAwareApi.get<T>(url, { params }).then((r) => r.data),
  post: <T>(url: string, data?: unknown) =>
    demoAwareApi.post<T>(url, data).then((r) => r.data),
  put: <T>(url: string, data?: unknown) =>
    demoAwareApi.put<T>(url, data).then((r) => r.data),
  patch: <T>(url: string, data?: unknown) =>
    demoAwareApi.patch<T>(url, data).then((r) => r.data),
  delete: <T>(url: string) =>
    demoAwareApi.delete<T>(url).then((r) => r.data),
}

// Auth hooks
export function useMe(options?: UseQueryOptions<User>) {
  return useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: () => apiClient.get<User>('/auth/me'),
    staleTime: 1000 * 60 * 5,
    ...options,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: LoginRequest) => apiClient.post<LoginResponse>('/auth/login', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
    },
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: RegisterRequest) => apiClient.post<LoginResponse>('/auth/register', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
    },
  })
}

export function useRefreshToken() {
  return useMutation({
    mutationFn: (data: RefreshTokenRequest) => apiClient.post<RefreshTokenResponse>('/auth/refresh', data),
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiClient.post('/auth/logout', {}),
    onSuccess: () => {
      queryClient.clear()
    },
  })
}

// Company hooks
export function useCompanies(options?: UseQueryOptions<PaginatedResponse<Company>>) {
  return useQuery({
    queryKey: queryKeys.companies.all,
    queryFn: () => apiClient.get<PaginatedResponse<Company>>('/companies'),
    ...options,
  })
}

export function useCompany(id: string, options?: UseQueryOptions<Company>) {
  return useQuery({
    queryKey: queryKeys.companies.detail(id),
    queryFn: () => apiClient.get<Company>(`/companies/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useUpdateCompany() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Company> }) =>
      apiClient.patch<Company>(`/companies/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.all })
    },
  })
}

// Client hooks
export function useClients(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Client>>) {
  return useQuery({
    queryKey: queryKeys.clients.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Client>>('/clients', params),
    ...options,
  })
}

export function useClient(id: string, options?: UseQueryOptions<Client>) {
  return useQuery({
    queryKey: queryKeys.clients.detail(id),
    queryFn: () => apiClient.get<Client>(`/clients/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useCreateClient() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Client>) => apiClient.post<Client>('/clients', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all() })
    },
  })
}

export function useUpdateClient() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Client> }) =>
      apiClient.patch<Client>(`/clients/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all() })
    },
  })
}

export function useDeleteClient() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/clients/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all() })
    },
  })
}

// Client Branch hooks
export function useClientBranches(clientId: string, options?: UseQueryOptions<ClientBranch[]>) {
  return useQuery({
    queryKey: queryKeys.clients.branches(clientId),
    queryFn: () => apiClient.get<ClientBranch[]>(`/clients/${clientId}/branches`),
    enabled: !!clientId,
    ...options,
  })
}

export function useCreateBranch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ clientId, data }: { clientId: string; data: Partial<ClientBranch> }) =>
      apiClient.post<ClientBranch>(`/clients/${clientId}/branches`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.branches(variables.clientId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.detail(variables.clientId) })
    },
  })
}

export function useUpdateBranch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ClientBranch> }) =>
      apiClient.patch<ClientBranch>(`/branches/${id}`, data),
    onSuccess: (_, _variables) => {
      // We need the clientId from the variables, but it's not in the mutation params
      // The API should return the updated branch with clientId, but if not, we'd need to pass it
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.all() })
    },
  })
}

export function useDeleteBranch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, clientId: _clientId }: { id: string; clientId: string }) =>
      apiClient.delete(`/branches/${id}`),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.branches(variables.clientId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.clients.detail(variables.clientId) })
    },
  })
}

// Carrier hooks
export function useCarriers(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Carrier>>) {
  return useQuery({
    queryKey: queryKeys.carriers.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Carrier>>('/carriers', params),
    ...options,
  })
}

export function useCarrier(id: string, options?: UseQueryOptions<Carrier>) {
  return useQuery({
    queryKey: queryKeys.carriers.detail(id),
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
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.all() })
    },
  })
}

export function useUpdateCarrier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Carrier> }) =>
      apiClient.patch<Carrier>(`/carriers/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.all() })
    },
  })
}

export function useDeleteCarrier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/carriers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.all() })
    },
  })
}

// Carrier Branch hooks
export function useCarrierBranches(carrierId: string, options?: UseQueryOptions<CarrierBranch[]>) {
  return useQuery({
    queryKey: queryKeys.carriers.branches(carrierId),
    queryFn: () => apiClient.get<CarrierBranch[]>(`/carriers/${carrierId}/branches`),
    enabled: !!carrierId,
    ...options,
  })
}

export function useCreateCarrierBranch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ carrierId, data }: { carrierId: string; data: Partial<CarrierBranch> }) =>
      apiClient.post<CarrierBranch>(`/carriers/${carrierId}/branches`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.branches(variables.carrierId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.detail(variables.carrierId) })
    },
  })
}

export function useUpdateCarrierBranch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CarrierBranch> }) =>
      apiClient.patch<CarrierBranch>(`/branches/${id}`, data),
    onSuccess: (_, _variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.all() })
    },
  })
}

export function useDeleteCarrierBranch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, carrierId: _carrierId }: { id: string; carrierId: string }) =>
      apiClient.delete(`/branches/${id}`),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.branches(variables.carrierId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.carriers.detail(variables.carrierId) })
    },
  })
}

// Contract hooks
export function useContracts(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Contract>>) {
  return useQuery({
    queryKey: queryKeys.contracts.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Contract>>('/contracts', params),
    ...options,
  })
}

export function useContract(id: string, options?: UseQueryOptions<Contract>) {
  return useQuery({
    queryKey: queryKeys.contracts.detail(id),
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
      queryClient.invalidateQueries({ queryKey: queryKeys.contracts.all() })
    },
  })
}

// Document hooks
export function useDocuments(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Document>>) {
  return useQuery({
    queryKey: queryKeys.documents.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Document>>('/documents', params),
    ...options,
  })
}

export function useDocument(id: string, options?: UseQueryOptions<Document>) {
  return useQuery({
    queryKey: queryKeys.documents.detail(id),
    queryFn: () => apiClient.get<Document>(`/documents/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (formData: FormData) => apiClient.post<Document>('/documents/upload', formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.documents.all() })
    },
  })
}

export function useReprocessDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.post<Document>(`/documents/${id}/reprocess`),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.documents.detail(data.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.documents.all() })
    },
  })
}

// Discrepancy hooks
export function useDiscrepancies(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Discrepancy>>) {
  return useQuery({
    queryKey: queryKeys.discrepancies.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Discrepancy>>('/discrepancies', params),
    ...options,
  })
}

export function useDiscrepancy(id: string, options?: UseQueryOptions<Discrepancy>) {
  return useQuery({
    queryKey: queryKeys.discrepancies.detail(id),
    queryFn: () => apiClient.get<Discrepancy>(`/discrepancies/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useDiscrepancySummary(params?: Record<string, unknown>, options?: UseQueryOptions<DiscrepancySummary>) {
  return useQuery({
    queryKey: queryKeys.discrepancies.summary(params),
    queryFn: () => apiClient.get<DiscrepancySummary>('/discrepancies/summary', params),
    ...options,
  })
}

export function useUpdateDiscrepancy() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Discrepancy> }) =>
      apiClient.patch<Discrepancy>(`/discrepancies/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.summary() })
    },
  })
}

export function useBulkUpdateDiscrepancies() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { ids: string[]; updates: Partial<Discrepancy> }) =>
      apiClient.patch<Discrepancy[]>('/discrepancies/bulk', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.summary() })
    },
  })
}

// Contest hooks
export function useContests(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Contest>>) {
  return useQuery({
    queryKey: queryKeys.contests.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Contest>>('/contests', params),
    ...options,
  })
}

export function useContest(id: string, options?: UseQueryOptions<Contest>) {
  return useQuery({
    queryKey: queryKeys.contests.detail(id),
    queryFn: () => apiClient.get<Contest>(`/contests/${id}`),
    enabled: !!id,
    ...options,
  })
}

export function useCreateContest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<Contest>) => apiClient.post<Contest>('/contests', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.discrepancies.all() })
    },
  })
}

export function useUpdateContest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Contest> }) =>
      apiClient.patch<Contest>(`/contests/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.contests.all() })
    },
  })
}

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

export function useGenerateContestPDF() {
  return useMutation({
    mutationFn: (id: string) => apiClient.post<{ url: string }>(`/contests/${id}/pdf`),
  })
}

// Report hooks
export function useDashboardKPIs(options?: UseQueryOptions<DashboardKPIs>) {
  return useQuery({
    queryKey: queryKeys.reports.dashboard,
    queryFn: () => apiClient.get<DashboardKPIs>('/reports/dashboard'),
    staleTime: 1000 * 60 * 5,
    ...options,
  })
}

export function useDiscrepancyReport(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: queryKeys.reports.discrepancies(params),
    queryFn: () => apiClient.get('/reports/discrepancies', params),
  })
}

export function useRecoveryReport(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: queryKeys.reports.recovery(params),
    queryFn: () => apiClient.get('/reports/recovery', params),
  })
}

export function useExportReport(type: 'pdf' | 'excel', params?: Record<string, unknown>) {
  return useMutation({
    mutationFn: () => apiClient.get<{ url: string }>(`/reports/export/${type}`, params),
  })
}

// Notification hooks
export function useNotifications(params?: Record<string, unknown>, options?: UseQueryOptions<PaginatedResponse<Notification>>) {
  return useQuery({
    queryKey: queryKeys.notifications.all(params),
    queryFn: () => apiClient.get<PaginatedResponse<Notification>>('/notifications', params),
    ...options,
  })
}

export function useUnreadNotificationCount(options?: UseQueryOptions<number>) {
  return useQuery({
    queryKey: queryKeys.notifications.unreadCount,
    queryFn: () => apiClient.get<number>('/notifications/unread-count'),
    refetchInterval: 30000,
    ...options,
  })
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.patch(`/notifications/${id}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.unreadCount })
    },
  })
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiClient.patch('/notifications/read-all'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all() })
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.unreadCount })
    },
  })
}

// User Profile hooks
export function useUserProfile(options?: UseQueryOptions<User>) {
  return useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => apiClient.get<User>('/users/me'),
    staleTime: 1000 * 60 * 5,
    ...options,
  })
}

export function useUpdateUserProfile() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.patch<User>('/users/me', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] })
    },
  })
}

// Notification Preferences hooks
export interface NotificationPreferences {
  email_enabled: boolean
  in_app_enabled: boolean
  weekly_report: boolean
  discrepancy_alerts: boolean
  contest_updates: boolean
}

export function useNotificationPreferences(options?: UseQueryOptions<NotificationPreferences>) {
  return useQuery({
    queryKey: ['notifications', 'preferences'],
    queryFn: () => apiClient.get<NotificationPreferences>('/notifications/preferences'),
    staleTime: 1000 * 60 * 5,
    ...options,
  })
}

export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: Partial<NotificationPreferences>) =>
      apiClient.patch<NotificationPreferences>('/notifications/preferences', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications', 'preferences'] })
    },
  })
}

// Auth hooks - Change Password
export function useChangePassword() {
  return useMutation({
    mutationFn: (data: { current_password: string; new_password: string }) =>
      apiClient.post('/auth/change-password', data),
  })
}

// Delete Account
export function useDeleteAccount() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (password: string) =>
      apiClient.post('/users/me/delete', { password }),
    onSuccess: () => {
      queryClient.clear()
    },
  })
}