import { ReactNode, useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../store/auth-context'
import { cn } from '../utils/helpers'
import { Avatar } from '../components'
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  Users,
  Truck,
  Settings,
  Menu,
  X,
  ChevronDown,
  Bell,
  LogOut,
  User as UserIcon,
  HelpCircle,
  BarChart2,
} from 'lucide-react'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuLabel } from '../components'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['ADMIN', 'MANAGER', 'AUDITOR', 'CLIENT'] },
  { name: 'Discrepâncias', href: '/discrepancies', icon: FileText, roles: ['ADMIN', 'MANAGER', 'AUDITOR'] },
  { name: 'Contestações', href: '/contests', icon: Briefcase, roles: ['ADMIN', 'MANAGER', 'AUDITOR'] },
  { name: 'Clientes', href: '/clients', icon: Users, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Transportadoras', href: '/carriers', icon: Truck, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Contratos', href: '/contracts', icon: FileText, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Documentos', href: '/documents', icon: FileText, roles: ['ADMIN', 'MANAGER', 'AUDITOR'] },
  { name: 'Relatórios', href: '/reports', icon: BarChart2, roles: ['ADMIN', 'MANAGER'] },
  { name: 'Configurações', href: '/settings', icon: Settings, roles: ['ADMIN', 'MANAGER'] },
]

export function MainLayout() {
  const { user, logout, hasAnyRole } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const filteredNav = navigation.filter((item) =>
    user && hasAnyRole(item.roles as any[])
  )

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-secondary-200 transform transition-transform duration-200 lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        aria-label="Menu principal"
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-secondary-200">
            <NavLink to="/dashboard" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-secondary-900">AvertaSaaS</span>
            </NavLink>
            <button
              className="lg:hidden p-2 rounded-lg text-secondary-500 hover:bg-secondary-100"
              onClick={() => setSidebarOpen(false)}
              aria-label="Fechar menu"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1" aria-label="Navegação principal">
            {filteredNav.map((item) => {
              const isActive = location.pathname === item.href ||
                (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'sidebar-link',
                    isActive && 'sidebar-link-active'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <item.icon className="h-5 w-5" aria-hidden="true" />
                  {item.name}
                </NavLink>
              )
            })}
          </nav>

          {/* User info at bottom */}
          <div className="p-4 border-t border-secondary-200">
            <div className="flex items-center gap-3">
              <Avatar
                src={user?.avatarUrl}
                alt={user?.fullName || 'Usuário'}
                fallback={user?.fullName}
                size="md"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-secondary-900 truncate">{user?.fullName}</p>
                <p className="text-xs text-secondary-500 truncate">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-30 bg-white border-b border-secondary-200">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6">
            <button
              className="lg:hidden p-2 rounded-lg text-secondary-500 hover:bg-secondary-100"
              onClick={() => setSidebarOpen(true)}
              aria-label="Abrir menu"
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex-1 lg:flex-none" />

            <div className="flex items-center gap-4">
              {/* Notifications */}
              <button
                className="relative p-2 rounded-lg text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700 transition-colors"
                aria-label="Notificações"
              >
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-danger-500" />
              </button>

              {/* User menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-secondary-100 transition-colors"
                    aria-label="Menu do usuário"
                  >
                    <Avatar
                      src={user?.avatarUrl}
                      alt={user?.fullName || 'Usuário'}
                      fallback={user?.fullName}
                      size="sm"
                    />
                    <span className="hidden sm:block text-sm font-medium text-secondary-700">
                      {user?.fullName}
                    </span>
                    <ChevronDown className="h-4 w-4 text-secondary-500 hidden sm:block" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel className="font-normal text-secondary-900">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">{user?.fullName}</span>
                      <span className="text-xs text-secondary-500">{user?.email}</span>
                      <Badge variant="secondary" className="mt-1 w-fit">{user?.role}</Badge>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <NavLink to="/profile" onClick={() => setUserMenuOpen(false)} className="w-full">
                      <UserIcon className="h-4 w-4" />
                      Perfil
                    </NavLink>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <NavLink to="/settings" onClick={() => setUserMenuOpen(false)} className="w-full">
                      <Settings className="h-4 w-4" />
                      Configurações
                    </NavLink>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <a href="#" className="w-full flex items-center gap-2">
                      <HelpCircle className="h-4 w-4" />
                      Ajuda
                    </a>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => logout()}
                    className="text-danger-600 focus:text-danger-600"
                    inset
                  >
                    <LogOut className="h-4 w-4" />
                    Sair
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}