import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store/auth-context'
import { MainLayout } from './layouts/MainLayout'
import { AuthLayout } from './layouts/AuthLayout'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { Documents } from './pages/Documents'
import { DiscrepanciesPage } from './pages/DiscrepanciesPage'
import { ContestsPage } from './pages/ContestsPage'
import { ContestCreatePage } from './pages/ContestCreatePage'
import { ContestDetailPage } from './pages/ContestDetailPage'
import { ContestNegotiatePage } from './pages/ContestNegotiatePage'
import { ReportsPage } from './pages/ReportsPage'
import { ClientsPage } from './pages/Clients'
import { CarriersPage } from './pages/Carriers'
import { SettingsLayout } from './pages/settings/SettingsLayout'
import { CompanySettingsPage } from './pages/settings/CompanySettingsPage'
import { UsersPage } from './pages/settings/UsersPage'
import { CarriersPage as SettingsCarriersPage } from './pages/settings/CarriersPage'
import { ContractsPage } from './pages/settings/ContractsPage'
import { NotificationsPage } from './pages/settings/NotificationsPage'
import { Profile } from './pages/Profile'

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-50">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Public route wrapper (redirects authenticated users)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-50">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

// Placeholder pages for future implementation
function ComingSoon({ title, description }: { title: string; description: string }) {
  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">{title}</h1>
        <p className="page-subtitle">{description}</p>
      </div>
      <div className="card p-12 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center mb-4">
          <svg className="h-8 w-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-secondary-900 mb-2">Em desenvolvimento</h2>
        <p className="text-secondary-500 max-w-md mx-auto">
          Esta página está sendo desenvolvida. Volte em breve para ver as funcionalidades completas.
        </p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/clients" element={<ClientsPage />} />
        <Route path="/carriers" element={<CarriersPage />} />
        <Route path="/contracts" element={<ComingSoon title="Contratos" description="Crie e gerencie contratos com tabelas de frete versionadas" />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/discrepancies" element={<DiscrepanciesPage />} />
        <Route path="/contests" element={<ContestsPage />} />
        <Route path="/contests/create" element={<ContestCreatePage />} />
        <Route path="/contests/:id" element={<ContestDetailPage />} />
        <Route path="/contests/:id/negotiate" element={<ContestNegotiatePage />} />
        <Route path="/reports" element={<ReportsPage />} />

        {/* Settings routes with nested layout */}
        <Route element={<SettingsLayout />}>
          <Route path="/settings/company" element={<CompanySettingsPage />} />
          <Route path="/settings/users" element={<UsersPage />} />
          <Route path="/settings/carriers" element={<SettingsCarriersPage />} />
          <Route path="/settings/contracts" element={<ContractsPage />} />
          <Route path="/settings/notifications" element={<NotificationsPage />} />
        </Route>
        <Route path="/settings" element={<Navigate to="/settings/company" replace />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* Redirect root to dashboard or login */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}