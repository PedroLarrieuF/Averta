import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { useAuth } from './store/auth-context'
import { MainLayout } from './layouts/MainLayout'
import { AuthLayout } from './layouts/AuthLayout'
import { SettingsLayout } from './pages/settings/SettingsLayout'
import { DeveloperLayout } from './layouts/DeveloperLayout'
import { PageSkeleton, PageSkeletonMinimal } from './components/PageSkeleton'

// Lazy load all pages for code splitting (named exports)
const lazyLoad = <T extends React.ComponentType<any>>(importFn: () => Promise<{ [key: string]: T }>, exportName: string) =>
  lazy(() => importFn().then((module) => ({ default: module[exportName] })))

const Login = lazyLoad(() => import('./pages/Login'), 'Login')
const Register = lazyLoad(() => import('./pages/Register'), 'Register')
const Dashboard = lazyLoad(() => import('./pages/Dashboard'), 'Dashboard')
const Documents = lazyLoad(() => import('./pages/Documents'), 'Documents')
const DiscrepanciesPage = lazyLoad(() => import('./pages/DiscrepanciesPage'), 'DiscrepanciesPage')
const ContractsPage = lazyLoad(() => import('./pages/Contracts'), 'ContractsPage')
const ContestsPage = lazyLoad(() => import('./pages/ContestsPage'), 'ContestsPage')
const ContestCreatePage = lazyLoad(() => import('./pages/ContestCreatePage'), 'ContestCreatePage')
const ContestDetailPage = lazyLoad(() => import('./pages/ContestDetailPage'), 'ContestDetailPage')
const ContestNegotiatePage = lazyLoad(() => import('./pages/ContestNegotiatePage'), 'ContestNegotiatePage')
const ReportsPage = lazyLoad(() => import('./pages/ReportsPage'), 'ReportsPage')
const ClientsPage = lazyLoad(() => import('./pages/Clients'), 'ClientsPage')
const CarriersPage = lazyLoad(() => import('./pages/Carriers'), 'CarriersPage')
const CompanySettingsPage = lazyLoad(() => import('./pages/settings/CompanySettingsPage'), 'CompanySettingsPage')
const UsersPage = lazyLoad(() => import('./pages/settings/UsersPage'), 'UsersPage')
const SettingsCarriersPage = lazyLoad(() => import('./pages/settings/CarriersPage'), 'CarriersPage')
const NotificationsPage = lazyLoad(() => import('./pages/settings/NotificationsPage'), 'NotificationsPage')
const Profile = lazyLoad(() => import('./pages/Profile'), 'Profile')
const DeveloperDashboard = lazyLoad(() => import('./pages/developer/DeveloperDashboard'), 'DeveloperDashboard')
const DeveloperDocs = lazyLoad(() => import('./pages/developer/DeveloperDocs'), 'DeveloperDocs')
const DeveloperKeys = lazyLoad(() => import('./pages/developer/DeveloperKeys'), 'DeveloperKeys')
const DeveloperAnalytics = lazyLoad(() => import('./pages/developer/DeveloperAnalytics'), 'DeveloperAnalytics')
const DeveloperWebhooks = lazyLoad(() => import('./pages/developer/DeveloperWebhooks'), 'DeveloperWebhooks')

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

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={
          <Suspense fallback={<PageSkeletonMinimal />}>
            <PublicRoute><Login /></PublicRoute>
          </Suspense>
        } />
        <Route path="/register" element={
          <Suspense fallback={<PageSkeletonMinimal />}>
            <PublicRoute><Register /></PublicRoute>
          </Suspense>
        } />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={
          <Suspense fallback={<PageSkeleton />}>
            <Dashboard />
          </Suspense>
        } />
        <Route path="/clients" element={
          <Suspense fallback={<PageSkeleton />}>
            <ClientsPage />
          </Suspense>
        } />
        <Route path="/carriers" element={
          <Suspense fallback={<PageSkeleton />}>
            <CarriersPage />
          </Suspense>
        } />
        <Route path="/contracts" element={
          <Suspense fallback={<PageSkeleton />}>
            <ContractsPage />
          </Suspense>
        } />
        <Route path="/documents" element={
          <Suspense fallback={<PageSkeleton />}>
            <Documents />
          </Suspense>
        } />
        <Route path="/discrepancies" element={
          <Suspense fallback={<PageSkeleton />}>
            <DiscrepanciesPage />
          </Suspense>
        } />
        <Route path="/contests" element={
          <Suspense fallback={<PageSkeleton />}>
            <ContestsPage />
          </Suspense>
        } />
        <Route path="/contests/create" element={
          <Suspense fallback={<PageSkeleton />}>
            <ContestCreatePage />
          </Suspense>
        } />
        <Route path="/contests/:id" element={
          <Suspense fallback={<PageSkeleton />}>
            <ContestDetailPage />
          </Suspense>
        } />
        <Route path="/contests/:id/negotiate" element={
          <Suspense fallback={<PageSkeleton />}>
            <ContestNegotiatePage />
          </Suspense>
        } />
        <Route path="/reports" element={
          <Suspense fallback={<PageSkeleton />}>
            <ReportsPage />
          </Suspense>
        } />

        {/* Settings routes with nested layout */}
        <Route element={<SettingsLayout />}>
          <Route path="/settings/company" element={
            <Suspense fallback={<PageSkeleton />}>
              <CompanySettingsPage />
            </Suspense>
          } />
          <Route path="/settings/users" element={
            <Suspense fallback={<PageSkeleton />}>
              <UsersPage />
            </Suspense>
          } />
          <Route path="/settings/carriers" element={
            <Suspense fallback={<PageSkeleton />}>
              <SettingsCarriersPage />
            </Suspense>
          } />
          <Route path="/settings/contracts" element={
            <Suspense fallback={<PageSkeleton />}>
              <ContractsPage />
            </Suspense>
          } />
          <Route path="/settings/notifications" element={
            <Suspense fallback={<PageSkeleton />}>
              <NotificationsPage />
            </Suspense>
          } />
        </Route>
        <Route path="/settings" element={<Navigate to="/settings/company" replace />} />
        <Route path="/profile" element={
          <Suspense fallback={<PageSkeleton />}>
            <Profile />
          </Suspense>
        } />

        {/* Developer Portal routes with nested layout */}
        <Route element={<DeveloperLayout />}>
          <Route path="/developer" element={
            <Suspense fallback={<PageSkeleton />}>
              <DeveloperDashboard />
            </Suspense>
          } />
          <Route path="/developer/docs" element={
            <Suspense fallback={<PageSkeleton />}>
              <DeveloperDocs />
            </Suspense>
          } />
          <Route path="/developer/keys" element={
            <Suspense fallback={<PageSkeleton />}>
              <DeveloperKeys />
            </Suspense>
          } />
          <Route path="/developer/keys/new" element={
            <Suspense fallback={<PageSkeleton />}>
              <DeveloperKeys />
            </Suspense>
          } />
          <Route path="/developer/analytics" element={
            <Suspense fallback={<PageSkeleton />}>
              <DeveloperAnalytics />
            </Suspense>
          } />
          <Route path="/developer/webhooks" element={
            <Suspense fallback={<PageSkeleton />}>
              <DeveloperWebhooks />
            </Suspense>
          } />
        </Route>
      </Route>

      {/* Redirect root to dashboard or login */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}