import { Outlet, NavLink } from 'react-router-dom'
import { Building2, Users, Truck, FileText, Bell } from 'lucide-react'
import { cn } from '@/utils/helpers'
import { useAuth } from '@/store/auth-context'
import type { UserRole as Role } from '@/types'

const SETTINGS_NAV = [
  { path: 'company', label: 'Empresa', icon: Building2, roles: ['ADMIN'] as Role[] },
  { path: 'users', label: 'Usuários', icon: Users, roles: ['ADMIN', 'MANAGER'] as Role[] },
  { path: 'carriers', label: 'Transportadoras', icon: Truck, roles: ['ADMIN', 'MANAGER'] as Role[] },
  { path: 'contracts', label: 'Contratos', icon: FileText, roles: ['ADMIN', 'MANAGER'] as Role[] },
  { path: 'notifications', label: 'Notificações', icon: Bell, roles: ['ADMIN', 'MANAGER', 'AUDITOR', 'CLIENT'] as Role[] },
]

export function SettingsLayout() {
  const { user, hasAnyRole } = useAuth()

  const filteredNav = SETTINGS_NAV.filter((item) =>
    user ? hasAnyRole(item.roles) : false
  )

  return (
    <div className="flex h-full bg-secondary-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-secondary-200 flex flex-col">
        <div className="p-4 border-b border-secondary-200">
          <h2 className="font-semibold text-secondary-900">Configurações</h2>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {filteredNav.map((item) => (
            <NavLink
                key={item.path}
                to={`/settings/${item.path}`}
                className={({ isActive: active }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    active
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-secondary-600 hover:bg-secondary-100 hover:text-secondary-900'
                  )
                }
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                <span className="truncate">{item.label}</span>
              </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-secondary-200 text-xs text-secondary-500">
          Apenas administradores e gestores têm acesso a estas configurações.
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}