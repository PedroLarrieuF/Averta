import { useState } from 'react'
import { Search, Mail, MoreVertical, Edit, Trash2, AlertCircle, CheckCircle, X, Send, UserPlus } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Label, Badge, Card, CardBody, Table, Pagination, Modal, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components'
import toast from 'react-hot-toast'
import { useAuth } from '@/store/auth-context'
import { useUsers, useUpdateUser, useDeleteUser, useInviteUser, useResendInvite } from '@/hooks/useSettings'
import { UserInviteModal } from '@/components/settings/UserInviteModal'
import { formatRelativeTime } from '@/utils/helpers'
import type { User, Role } from '@/types'

const ROLE_BADGES: Record<Role, 'primary' | 'success' | 'warning' | 'secondary' | 'danger'> = {
  ADMIN: 'danger',
  MANAGER: 'primary',
  AUDITOR: 'warning',
  CLIENT: 'secondary',
}

const ROLE_LABELS: Record<Role, string> = {
  ADMIN: 'Admin',
  MANAGER: 'Gestor',
  AUDITOR: 'Auditor',
  CLIENT: 'Cliente',
}

const STATUS_BADGES: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  ACTIVE: 'success',
  INACTIVE: 'secondary',
  PENDING: 'warning',
  INVITED: 'warning',
}

export function UsersPage() {
  const { user, hasAnyRole } = useAuth()
  const canManageUsers = user ? hasAnyRole(['ADMIN', 'MANAGER']) : false
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [page, setPage] = useState(1)
  const [inviteModalOpen, setInviteModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [editFormData, setEditFormData] = useState<Partial<User>>({})
  const [editModalOpen, setEditModalOpen] = useState(false)
  const pageSize = 10

  const { data, isLoading, refetch } = useUsers({
    search: search || undefined,
    role: roleFilter || undefined,
    status: statusFilter || undefined,
    page,
    limit: pageSize,
  })

  const updateUser = useUpdateUser()
  const deleteUser = useDeleteUser()
  const inviteUser = useInviteUser()
  const resendInvite = useResendInvite()

  const handleInviteSubmit = async (data: { email: string; role: Role }) => {
    await inviteUser.mutateAsync({ ...data, companyId: user?.companyId || '' })
    refetch()
  }

  const handleEdit = (u: User) => {
    setEditingUser(u)
    setEditFormData({ role: u.role, status: u.status })
    setEditModalOpen(true)
  }

  const handleEditSubmit = async () => {
    if (!editingUser) return
    try {
      await updateUser.mutateAsync({ id: editingUser.id, data: editFormData })
      toast.success('Usuário atualizado com sucesso!')
      setEditModalOpen(false)
      setEditingUser(null)
      refetch()
    } catch (_err) {
      toast.error('Erro ao atualizar usuário')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return
    try {
      await deleteUser.mutateAsync(id)
      toast.success('Usuário excluído com sucesso!')
      refetch()
    } catch (_err) {
      toast.error('Erro ao excluir usuário')
    }
  }

  const handleResendInvite = async (id: string) => {
    try {
      await resendInvite.mutateAsync(id)
      toast.success('Convite reenviado!')
      refetch()
    } catch (_err) {
      toast.error('Erro ao reenviar convite')
    }
  }

  const handleStatusChange = (id: string, currentStatus: string) => {
    const newStatus = currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
    updateUser.mutate({ id, data: { status: newStatus } })
    refetch()
  }

  const columns = [
    {
      key: 'user',
      header: 'Usuário',
      render: (u: User) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-medium">
            {u.fullName?.charAt(0) || u.email.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-secondary-900">{u.fullName || 'Sem nome'}</p>
            <p className="text-sm text-secondary-500">{u.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'role',
      header: 'Função',
      render: (u: User) => (
        <Badge variant={ROLE_BADGES[u.role] || 'secondary'}>
          {ROLE_LABELS[u.role] || u.role}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (u: User) => (
        <Badge variant={STATUS_BADGES[u.status] || 'secondary'} className="capitalize">
          {u.status.toLowerCase()}
        </Badge>
      ),
    },
    {
      key: 'lastLogin',
      header: 'Último Acesso',
      className: 'hidden md:table-cell',
      render: (u: User) => (
        <span className="text-sm text-secondary-500">
          {u.lastLoginAt ? formatRelativeTime(u.lastLoginAt) : 'Nunca'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      className: 'text-right',
      render: (u: User) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={() => handleEdit(u)} disabled={!canManageUsers}>
              <Edit className="h-4 w-4 mr-2" />
              Editar
            </DropdownMenuItem>
            {u.status === 'INVITED' && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleResendInvite(u.id)}>
                  <Send className="h-4 w-4 mr-2" />
                  Reenviar Convite
                </DropdownMenuItem>
              </>
            )}
            {u.status !== 'INVITED' && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => handleStatusChange(u.id, u.status)}
                  className={u.status === 'ACTIVE' ? 'text-warning-600' : 'text-success-600'}
                >
                  {u.status === 'ACTIVE' ? (
                    <>
                      <AlertCircle className="h-4 w-4 mr-2" />
                      Desativar
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Ativar
                    </>
                  )}
                </DropdownMenuItem>
              </>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleDelete(u.id)}
              disabled={!canManageUsers || u.id === user?.id}
              className="text-danger-600"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Excluir
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ]

  const filteredUsers = data?.data || []
  const totalPages = data?.meta?.totalPages || 1

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Usuários</h1>
          <p className="text-secondary-500">Gerencie usuários e convites da empresa</p>
        </div>
        {canManageUsers && (
          <Button onClick={() => setInviteModalOpen(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Convidar Usuário
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardBody className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="relative flex-1 min-w-[250px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
              <Input
                placeholder="Buscar por nome, email..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="pl-10"
              />
            </div>
            <Select value={roleFilter} onValueChange={(value) => { setRoleFilter(value); setPage(1); }}>
              <SelectTrigger><SelectValue placeholder="Todas as funções" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todas as funções</SelectItem>
                <SelectItem value="ADMIN">Admin</SelectItem>
                <SelectItem value="MANAGER">Gestor</SelectItem>
                <SelectItem value="AUDITOR">Auditor</SelectItem>
                <SelectItem value="CLIENT">Cliente</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={(value) => { setStatusFilter(value); setPage(1); }}>
              <SelectTrigger><SelectValue placeholder="Todos os status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos os status</SelectItem>
                <SelectItem value="ACTIVE">Ativo</SelectItem>
                <SelectItem value="INACTIVE">Inativo</SelectItem>
                <SelectItem value="PENDING">Pendente</SelectItem>
                <SelectItem value="INVITED">Convidado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardBody>
      </Card>

      {/* Users Table */}
      <Card>
        {isLoading ? (
          <div className="animate-pulse p-8">
            <div className="h-10 bg-secondary-100 rounded" />
            <div className="space-y-3 mt-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-14 bg-secondary-100 rounded" />
              ))}
            </div>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="card p-12 text-center">
            <Mail className="mx-auto h-12 w-12 text-secondary-300 mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum usuário encontrado</h3>
            <p className="text-secondary-500 mb-4">
              {search || roleFilter || statusFilter ? 'Tente ajustar os filtros' : 'Comece convidando o primeiro usuário'}
            </p>
            {canManageUsers && !search && !roleFilter && !statusFilter && (
              <Button onClick={() => setInviteModalOpen(true)}>
                <UserPlus className="h-4 w-4 mr-2" />
                Convidar Usuário
              </Button>
            )}
          </div>
        ) : (
          <>
            <Table columns={columns} data={filteredUsers} keyField="id" isLoading={isLoading} />
            {totalPages > 1 && (
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            )}
          </>
        )}
      </Card>

      {/* Invite Modal */}
      <UserInviteModal
        open={inviteModalOpen}
        onOpenChange={setInviteModalOpen}
        onSubmit={handleInviteSubmit}
        isSubmitting={inviteUser.isPending}
      />

      {/* Edit User Modal */}
      <Modal
        open={editModalOpen}
        onOpenChange={(open) => { if (!open) { setEditingUser(null); setEditFormData({}) } }}
        title="Editar Usuário"
        size="md"
      >
        {editingUser && (
          <div className="space-y-4">
            <p className="text-sm text-secondary-500">{editingUser.email}</p>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Função</Label>
              <Select value={editFormData.role || editingUser.role} onValueChange={(value) => setEditFormData({...editFormData, role: value as Role})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="ADMIN">Admin</SelectItem>
                  <SelectItem value="MANAGER">Gestor</SelectItem>
                  <SelectItem value="AUDITOR">Auditor</SelectItem>
                  <SelectItem value="CLIENT">Cliente</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label className="block text-sm font-medium text-secondary-700">Status</Label>
              <Select value={editFormData.status || editingUser.status} onValueChange={(value) => setEditFormData({...editFormData, status: value})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="ACTIVE">Ativo</SelectItem>
                  <SelectItem value="INACTIVE">Inativo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
              <Button variant="secondary" onClick={() => { setEditModalOpen(false); setEditingUser(null); }}>
                <X className="h-4 w-4 mr-2" />
                Cancelar
              </Button>
              <Button variant="primary" onClick={handleEditSubmit} loading={updateUser.isPending}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Salvar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}