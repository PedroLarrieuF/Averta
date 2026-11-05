import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { getAuthTokens, clearAuthTokens, refreshAccessToken } from '../store/auth-storage'
import { demoApi } from './demo-api'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api/v1'

// Create the base axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = getAuthTokens()
    if (tokens?.accessToken) {
      config.headers.Authorization = `Bearer ${tokens.accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await refreshAccessToken()
        processQueue(null, newToken)
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        clearAuthTokens()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

// ===== DEMO API INTERCEPTOR =====
// This interceptor checks if we're in demo mode and routes calls to demoApi

// We need a way to check demo mode from outside React context
// We'll use localStorage directly for this check
function isDemoModeEnabled(): boolean {
  if (typeof window === 'undefined') return false
  return localStorage.getItem('averta_demo_mode') === 'true'
}

// Map axios endpoints to demoApi functions
const demoEndpointMap: Record<string, (...args: any[]) => Promise<any>> = {
  // Auth
  'POST:/auth/login': demoApi.login,
  'POST:/auth/register': demoApi.register,
  'POST:/auth/refresh': demoApi.refresh,
  'POST:/auth/logout': demoApi.logout,
  'GET:/auth/me': demoApi.me,

  // Companies
  'GET:/settings/companies': demoApi.getCompanies,
  'GET:/settings/companies/:id': demoApi.getCompany,
  'POST:/settings/companies': demoApi.createCompany,
  'PATCH:/settings/companies/:id': demoApi.updateCompany,
  'DELETE:/settings/companies/:id': demoApi.deleteCompany,

  // Users
  'GET:/settings/users': demoApi.getUsers,
  'GET:/settings/users/:id': demoApi.getUser,
  'POST:/settings/users': demoApi.createUser,
  'PATCH:/settings/users/:id': demoApi.updateUser,
  'DELETE:/settings/users/:id': demoApi.deleteUser,

  // Carriers
  'GET:/settings/carriers': demoApi.getCarriers,
  'GET:/settings/carriers/:id': demoApi.getCarrier,
  'POST:/settings/carriers': demoApi.createCarrier,
  'PATCH:/settings/carriers/:id': demoApi.updateCarrier,
  'DELETE:/settings/carriers/:id': demoApi.deleteCarrier,

  // Clients
  'GET:/settings/clients': demoApi.getClients,
  'GET:/settings/clients/:id': demoApi.getClient,
  'POST:/settings/clients': demoApi.createClient,
  'PATCH:/settings/clients/:id': demoApi.updateClient,
  'DELETE:/settings/clients/:id': demoApi.deleteClient,

  // Contracts
  'GET:/settings/contracts': demoApi.getContracts,
  'GET:/settings/contracts/:id': demoApi.getContract,
  'POST:/settings/contracts': demoApi.createContract,
  'PATCH:/settings/contracts/:id': demoApi.updateContract,
  'DELETE:/settings/contracts/:id': demoApi.deleteContract,

  // Documents
  'GET:/documents': demoApi.getDocuments,
  'GET:/documents/:id': demoApi.getDocument,
  'POST:/documents/upload': demoApi.uploadDocument,
  'POST:/documents/:id/reprocess': demoApi.reprocessDocument,

  // Discrepancies
  'GET:/discrepancies': demoApi.getDiscrepancies,
  'GET:/discrepancies/summary': demoApi.getDiscrepancySummary,
  'GET:/discrepancies/:id': demoApi.getDiscrepancy,
  'PATCH:/discrepancies/bulk-status': demoApi.bulkUpdateStatus,
  'POST:/discrepancies/:id/review': demoApi.reviewDiscrepancy,
  'POST:/discrepancies/bulk-review': demoApi.bulkReviewDiscrepancies,
  'POST:/contests/from-discrepancies': demoApi.createContestFromDiscrepancies,

  // Contests
  'GET:/contests': demoApi.getContests,
  'GET:/contests/:id': demoApi.getContest,
  'POST:/contests': demoApi.createContest,
  'POST:/contests/:id/send': demoApi.sendContest,
  'PATCH:/contests/:id/negotiate': demoApi.negotiateContest,

  // Payments
  'POST:/contests/:id/payments': (contestId: string, data: any) => demoApi.createPayment(contestId, data),

  // Reports
  'GET:/reports/dashboard': demoApi.getDashboardReport,
  'GET:/reports/dashboard-full': demoApi.getReportsDashboard,
  'GET:/reports/pdf': demoApi.getPDFReport,
  'GET:/reports/excel': demoApi.getExcelReport,
  'GET:/reports/recovery': demoApi.getRecoveryReport,
  'GET:/reports/carrier-performance': demoApi.getCarrierPerformanceReport,
  'POST:/reports/schedule': demoApi.createSchedule,
  'GET:/reports/schedule': demoApi.getScheduledReports,
  'GET:/reports/schedule/:id': demoApi.getScheduledReport,
  'PATCH:/reports/schedule/:id': demoApi.updateSchedule,
  'DELETE:/reports/schedule/:id': demoApi.deleteSchedule,

  // Notifications
  'GET:/settings/notifications': demoApi.getNotifications,
  'PATCH:/settings/notifications': demoApi.updateNotifications,
}

// Helper to normalize URL for matching
function normalizeUrl(url: string): string {
  // Remove query params
  const path = url.split('?')[0]
  // Replace UUIDs and IDs with :id placeholder
  return path.replace(/\/[a-f0-9-]{36}/g, '/:id').replace(/\/\d+/g, '/:id')
}

// Helper to extract params from URL
function extractParams(url: string, normalizedUrl: string): Record<string, string> {
  const params: Record<string, string> = {}
  const urlParts = url.split('/')
  const normParts = normalizedUrl.split('/')

  for (let i = 0; i < normParts.length; i++) {
    if (normParts[i] === ':id' && urlParts[i]) {
      params.id = urlParts[i]
    }
  }
  return params
}

// Create a demo-aware axios instance
export const createDemoAwareApi = () => {
  const demoApiInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 30000,
  })

  // Request interceptor - check demo mode first, short-circuit if enabled
  demoApiInstance.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      // If in demo mode, handle with demo API and short-circuit the request
      if (isDemoModeEnabled()) {
        const method = config.method?.toUpperCase() || 'GET'
        const url = config.url || ''
        const normalizedUrl = normalizeUrl(url)
        const key = `${method}:${normalizedUrl}`

        const demoHandler = demoEndpointMap[key]
        if (demoHandler) {
          try {
            // Extract params from URL
            const params = extractParams(url, normalizedUrl)
            const data = config.data

            // Call demo API with appropriate arguments
            let result: any
            if (method === 'GET') {
              // For GET, use query params
              const searchParams = new URLSearchParams(config.params)
              const page = parseInt(searchParams.get('page') || '1')
              const size = parseInt(searchParams.get('size') || '20')
              const queryParams: any = { page, size }
              searchParams.forEach((value, key) => {
                if (key !== 'page' && key !== 'size') {
                  queryParams[key] = value
                }
              })
              result = await demoHandler(queryParams)
            } else if (method === 'POST' && url.includes('/upload')) {
              // File upload
              result = await demoHandler(data?.get?.('file') || data)
            } else if (params.id) {
              // Has ID param
              if (method === 'POST' && url.includes('/send')) {
                result = await demoHandler(params.id)
              } else if (method === 'POST' && url.includes('/reprocess')) {
                result = await demoHandler(params.id)
              } else if (method === 'POST' && url.includes('/payments')) {
                result = await demoHandler(params.id, data)
              } else if (method === 'POST' && url.includes('/review')) {
                result = await demoHandler(params.id, data?.status, data?.review_notes)
              } else if (method === 'PATCH' && url.includes('/negotiate')) {
                result = await demoHandler(params.id, data)
              } else if (method === 'PATCH') {
                result = await demoHandler(params.id, data)
              } else if (method === 'DELETE') {
                result = await demoHandler(params.id)
              } else {
                result = await demoHandler(params.id)
              }
            } else {
              // No ID param
              result = await demoHandler(data)
            }

            // Attach mock response to config for response interceptor
            ;(config as any).__mockResponse = {
              data: result,
              status: 200,
              statusText: 'OK',
              headers: {},
              config,
            }
            // Cancel the real request by throwing a special error
            throw { __demoMock: true, response: (config as any).__mockResponse }
          } catch (demoError) {
            if ((demoError as any).__demoMock) {
              throw demoError
            }
            console.error('Demo API error:', demoError)
            throw { __demoMock: true, response: {
              data: { message: 'Demo API error', error: String(demoError) },
              status: 500,
              statusText: 'Internal Server Error',
              headers: {},
              config,
            } }
          }
        }
      }

      // Normal request - add auth token
      const tokens = getAuthTokens()
      if (tokens?.accessToken) {
        config.headers.Authorization = `Bearer ${tokens.accessToken}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor - handle demo mock responses and token refresh
  demoApiInstance.interceptors.response.use(
    (response) => response,
    async (error: any) => {
      // Handle demo mock responses
      if (error?.__demoMock && error.response) {
        return error.response
      }

      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

      // In demo mode, demo handler handles everything, so we shouldn't get errors
      // But just in case, don't try token refresh in demo mode
      if (isDemoModeEnabled()) {
        return Promise.reject(error)
      }

      // Normal error handling (token refresh, etc.)
      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject })
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              return demoApiInstance(originalRequest)
            })
            .catch((err) => Promise.reject(err))
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          const newToken = await refreshAccessToken()
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return demoApiInstance(originalRequest)
        } catch (refreshError) {
          processQueue(refreshError as Error, null)
          clearAuthTokens()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    }
  )

  return demoApiInstance
}

// Export the demo-aware API instance
export const demoAwareApi = createDemoAwareApi()

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    if (error.response?.data?.detail) {
      return error.response.data.detail
    }
    if (error.message) {
      return error.message
    }
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'Ocorreu um erro inesperado'
}

export default api