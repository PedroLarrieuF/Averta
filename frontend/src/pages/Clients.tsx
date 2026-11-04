import { useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Plus, Filter, Search } from 'lucide-react'
import {
  useClients,
  useCreateClient,
  useUpdateClient,
  useDeleteClient,
  useCreateBranch,
  useUpdateBranch,
  useDeleteBranch,
} from '@/hooks'
import {
  ClientsTable,
  ClientForm,
  ClientDetailModal,
  PageHeader,
  PageTitle,
  PageSubtitle,
  Button,
  Input,
} from '@/components'
import { Client } from '@/types'
import toast from 'react-hot-toast'

export function ClientsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  // Parse filters from URL
  const getInitialFilters = (): Record<string, unknown> => {
    const filters: Record<string, unknown> = {
      page: parseInt(searchParams.get('page') || '1', 10),
      size: parseInt(searchParams.get('size') || '20', 10),
    }
    if (searchParams.get('search')) filters.search = searchParams.get('search')
    if (searchParams.get('status')) filters.status = searchParams.get('status')
    if (searchParams.get('dateFrom')) filters.dateFrom = searchParams.get('dateFrom')
    if (searchParams.get('dateTo')) filters.dateTo = searchParams.get('dateTo')
    return filters
  }

  const [filters, setFilters] = useState<Record<string, unknown>>(getInitialFilters)
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)
  const [createFormOpen, setCreateFormOpen] = useState(false)
  const [editFormOpen, setEditFormOpen] = useState(false)
  const [editingClient, setEditingClient] = useState<Client | null>(null)

  // Sync filters with URL
  const updateFilters = useCallback((newFilters: Record<string, unknown>) => {
    setFilters(newFilters)
    const params = new URLSearchParams()
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        params.set(key, String(value))
      }
    })
    setSearchParams(params, { replace: true })
  }, [setSearchParams])

  const clearFilters = useCallback(() => {
    const newFilters = { page: 1, size: 20 }
    updateFilters(newFilters)
  }, [updateFilters])

  const hasActiveFilters = useCallback(() => {
    return !!(
      filters.search ||
      filters.status ||
      filters.dateFrom ||
      filters.dateTo
    )
  }, [filters])

  // Fetch data
  const { data: clientsData, isLoading: isLoadingClients, refetch: refetchClients } = useClients(filters)

  // Mutations
  const createClient = useCreateClient()
  const updateClient = useUpdateClient()
  const deleteClient = useDeleteClient()
  const createBranch = useCreateBranch()
  const updateBranch = useUpdateBranch()
  const deleteBranch = useDeleteBranch()

  const handleCreateSubmit = async (data: any) => {
    try {
      await createClient.mutateAsync(data)
      toast.success('Cliente criado com sucesso')
      setCreateFormOpen(false)
      refetchClients()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleEditSubmit = async (data: any) => {
    if (!editingClient) return
    try {
      await updateClient.mutateAsync({ id: editingClient.id, data })
      toast.success('Cliente atualizado com sucesso')
      setEditFormOpen(false)
      setEditingClient(null)
      refetchClients()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleDelete = async (client: Client) => {
    try {
      await deleteClient.mutateAsync(client.id)
      toast.success('Cliente excluído com sucesso')
      refetchClients()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleView = (client: Client) => {
    setSelectedClient(client)
  }

  const handleEdit = (client: Client) => {
    setEditingClient(client)
    setEditFormOpen(true)
  }

  const handleCloseDetail = () => {
    setSelectedClient(null)
  }

  const handleCloseCreateForm = () => {
    setCreateFormOpen(false)
  }

  const handleCloseEditForm = () => {
    setEditFormOpen(false)
    setEditingClient(null)
  }

  const handleBranchCreate = async (data: any) => {
    if (!selectedClient) return
    try {
      await createBranch.mutateAsync({ clientId: selectedClient.id, data })
      toast.success('Filial criada com sucesso')
      refetchClients()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleBranchUpdate = async (id: string, data: any) => {
    try {
      await updateBranch.mutateAsync({ id, data })
      toast.success('Filial atualizada com sucesso')
      refetchClients()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleBranchDelete = async (id: string) => {
    if (!selectedClient) return
    try {
      await deleteBranch.mutateAsync({ id, clientId: selectedClient.id })
      toast.success('Filial excluída com sucesso')
      refetchClients()
    } catch (error) {
      // Error handled by mutation
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div>
          <PageTitle>Clientes</PageTitle>
          <PageSubtitle>Cadastre e gerencie seus clientes e filiais</PageSubtitle>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" className="hidden sm:flex" onClick={() => {}}>
            <Filter className="h-4 w-4 mr-2" />
            Filtros
          </Button>
          <Button variant="primary" onClick={() => setCreateFormOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Cliente
          </Button>
        </div>
      </PageHeader>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
            <Input
              placeholder="Buscar por nome ou documento..."
              value={filters.search as string}
              onChange={(e) => updateFilters({ ...filters, search: e.target.value, page: 1 })}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filters.status as string}
              onChange={(e) => updateFilters({ ...filters, status: e.target.value || undefined, page: 1 })}
              className="input w-40"
            >
              <option value="">Todos os status</option>
              <option value="ACTIVE">Ativo</option>
              <option value="INACTIVE">Inativo</option>
            </select>
            {hasActiveFilters() && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Limpar filtros
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Clients Table */}
      <div className="card">
        <div className="card-body p-0">
          <ClientsTable
            clients={clientsData?.data ?? []}
            isLoading={isLoadingClients}
            pagination={clientsData?.meta}
            onPageChange={(page) => updateFilters({ ...filters, page })}
            onSizeChange={(size) => updateFilters({ ...filters, size, page: 1 })}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      </div>

      {/* Client Detail Modal */}
      {selectedClient && (
        <ClientDetailModal
          client={selectedClient}
          onClose={handleCloseDetail}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onBranchCreate={handleBranchCreate}
          onBranchUpdate={handleBranchUpdate}
          onBranchDelete={handleBranchDelete}
          isDeleting={deleteClient.isPending}
          isUpdating={updateClient.isPending}
          isCreatingBranch={createBranch.isPending}
          isUpdatingBranch={updateBranch.isPending}
          isDeletingBranch={deleteBranch.isPending}
        />
      )}

      {/* Create Client Form */}
      <ClientForm
        open={createFormOpen}
        onOpenChange={handleCloseCreateForm}
        onSubmit={handleCreateSubmit}
        isLoading={createClient.isPending}
        title="Novo Cliente"
      />

      {/* Edit Client Form */}
      <ClientForm
        open={editFormOpen}
        onOpenChange={handleCloseEditForm}
        onSubmit={handleEditSubmit}
        client={editingClient}
        isLoading={updateClient.isPending}
        title="Editar Cliente"
      />
    </div>
  )
}