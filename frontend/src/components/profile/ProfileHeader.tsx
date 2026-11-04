import { Avatar } from '../Avatar'
import { Badge } from '../Badge'
import { getInitials, getStatusBadge, formatDate, formatRelativeTime } from '../../utils/helpers'
import { useAuth } from '../../store/auth-context'
import { cn } from '../../utils/helpers'

interface ProfileHeaderProps {
  className?: string
}

export function ProfileHeader({ className }: ProfileHeaderProps) {
  const { user } = useAuth()

  if (!user) return null

  const roleBadge = getStatusBadge(user.role)

  return (
    <div className={cn('card p-6 space-y-6', className)}>
      <div className="flex items-center gap-4">
        <Avatar
          src={user.avatarUrl}
          fallback={getInitials(user.fullName)}
          className="h-20 w-20"
        />
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold text-secondary-900 truncate">
            {user.fullName}
          </h1>
          <p className="text-secondary-500 truncate">{user.email}</p>
          <div className="flex items-center gap-3 mt-2">
            <Badge variant={roleBadge.variant.replace('badge-', '') as 'primary' | 'secondary' | 'danger' | 'success' | 'warning'}>{roleBadge.label}</Badge>
            <span className="text-sm text-secondary-500">
              {user.companyId ? `Empresa: ${user.companyId}` : 'Sem empresa'}
            </span>
            {user.status && (
              <Badge variant="success">Ativo</Badge>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-secondary-200">
        <div>
          <p className="text-sm text-secondary-500">Criado em</p>
          <p className="font-medium text-secondary-900">
            {formatDate(user.createdAt)}
          </p>
        </div>
        <div>
          <p className="text-sm text-secondary-500">Último acesso</p>
          <p className="font-medium text-secondary-900">
            {user.lastLoginAt ? formatRelativeTime(user.lastLoginAt) : 'Nunca'}
          </p>
        </div>
        <div>
          <p className="text-sm text-secondary-500">Status</p>
          <p className="font-medium text-secondary-900 capitalize">{user.status?.toLowerCase() || 'ativo'}</p>
        </div>
      </div>
    </div>
  )
}