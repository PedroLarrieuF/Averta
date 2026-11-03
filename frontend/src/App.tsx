import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store/auth-context'
import { MainLayout } from './layouts/MainLayout'
import { AuthLayout } from './layouts/AuthLayout'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { Documents } from './pages/Documents'
import { DiscrepanciesPage } from './pages/DiscrepanciesPage'

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

function Contests() {
  return <ComingSoon title="Contestações" description="Acompanhe o fluxo completo de contestações com transportadoras" />
}

function Clients() {
  return <ComingSoon title="Clientes" description="Cadastre e gerencie seus clientes e filiais" />
}

function Carriers() {
  return <ComingSoon title="Transportadoras" description="Gerencie transportadoras e seus contatos" />
}

function Contracts() {
  return <ComingSoon title="Contratos" description="Crie e gerencie contratos com tabelas de frete versionadas" />
}

function Reports() {
  return <ComingSoon title="Relatórios" description="Dashboards, KPIs e exportação PDF/Excel" />
}

function Settings() {
  return <ComingSoon title="Configurações" description="Configurações da empresa, usuários e preferências" />
}

function Profile() {
  return <ComingSoon title="Perfil" description="Gerencie seu perfil e preferências" />
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
        <Route path="/discrepancies" element={<DiscrepanciesPage />} />
        <Route path="/contests" element={<Contests />} />
        <Route path="/clients" element={<Clients />} />
        <Route path="/carriers" element={<Carriers />} />
        <Route path="/contracts" element={<Contracts />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      {/* Redirect root to dashboard or login */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}