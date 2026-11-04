import { useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Plus, Filter, Search } from 'lucide-react'
import {
  useCarriers,
  useCreateCarrier,
  useUpdateCarrier,
  useDeleteCarrier,
  useCreateCarrierBranch,
  useUpdateCarrierBranch,
  useDeleteCarrierBranch,
} from '@/hooks'
import {
  CarriersTable,
  CarrierForm,
  CarrierDetailModal,
  PageHeader,
  PageTitle,
  PageSubtitle,
  Button,
  Input,
} from '@/components'
import { Carrier } from '@/types'
import toast from 'react-hot-toast'

export function CarriersPage() {
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
  const [selectedCarrier, setSelectedCarrier] = useState<Carrier | null>(null)
  const [createFormOpen, setCreateFormOpen] = useState(false)
  const [editFormOpen, setEditFormOpen] = useState(false)
  const [editingCarrier, setEditingCarrier] = useState<Carrier | null>(null)

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
  const { data: carriersData, isLoading: isLoadingCarriers, refetch: refetchCarriers } = useCarriers(filters)

  // Mutations
  const createCarrier = useCreateCarrier()
  const updateCarrier = useUpdateCarrier()
  const deleteCarrier = useDeleteCarrier()
  const createBranch = useCreateCarrierBranch()
  const updateBranch = useUpdateCarrierBranch()
  const deleteBranch = useDeleteCarrierBranch()

  const handleCreateSubmit = async (data: any) => {
    try {
      await createCarrier.mutateAsync(data)
      toast.success('Transportadora criada com sucesso')
      setCreateFormOpen(false)
      refetchCarriers()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleEditSubmit = async (data: any) => {
    if (!editingCarrier) return
    try {
      await updateCarrier.mutateAsync({ id: editingCarrier.id, data })
      toast.success('Transportadora atualizada com sucesso')
      setEditFormOpen(false)
      setEditingCarrier(null)
      refetchCarriers()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleDelete = async (carrier: Carrier) => {
    try {
      await deleteCarrier.mutateAsync(carrier.id)
      toast.success('Transportadora excluída com sucesso')
      refetchCarriers()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleView = (carrier: Carrier) => {
    setSelectedCarrier(carrier)
  }

  const handleEdit = (carrier: Carrier) => {
    setEditingCarrier(carrier)
    setEditFormOpen(true)
  }

  const handleCloseDetail = () => {
    setSelectedCarrier(null)
  }

  const handleCloseCreateForm = () => {
    setCreateFormOpen(false)
  }

  const handleCloseEditForm = () => {
    setEditFormOpen(false)
    setEditingCarrier(null)
  }

  const handleBranchCreate = async (data: any) => {
    if (!selectedCarrier) return
    try {
      await createBranch.mutateAsync({ carrierId: selectedCarrier.id, data })
      toast.success('Filial criada com sucesso')
      refetchCarriers()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleBranchUpdate = async (id: string, data: any) => {
    try {
      await updateBranch.mutateAsync({ id, data })
      toast.success('Filial atualizada com sucesso')
      refetchCarriers()
    } catch (error) {
      // Error handled by mutation
    }
  }

  const handleBranchDelete = async (id: string) => {
    if (!selectedCarrier) return
    try {
      await deleteBranch.mutateAsync({ id, carrierId: selectedCarrier.id })
      toast.success('Filial excluída com sucesso')
      refetchCarriers()
    } catch (error) {
      // Error handled by mutation
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div>
          <PageTitle>Transportadoras</PageTitle>
          <PageSubtitle>Cadastre e gerencie suas transportadoras e filiais</PageSubtitle>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" className="hidden sm:flex" onClick={() => {}}>
            <Filter className="h-4 w-4 mr-2" />
            Filtros
          </Button>
          <Button variant="primary" onClick={() => setCreateFormOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Transportadora
          </Button>
        </div>
      </PageHeader>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
            <Input
              placeholder="Buscar por nome, documento ou ANTT..."
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

      {/* Carriers Table */}
      <div className="card">
        <div className="card-body p-0">
          <CarriersTable
            carriers={carriersData?.data ?? []}
            isLoading={isLoadingCarriers}
            pagination={carriersData?.meta}
            onPageChange={(page) => updateFilters({ ...filters, page })}
            onSizeChange={(size) => updateFilters({ ...filters, size, page: 1 })}
            onView={handleView}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      </div>

      {/* Carrier Detail Modal */}
      {selectedCarrier && (
        <CarrierDetailModal
          carrier={selectedCarrier}
          onClose={handleCloseDetail}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onBranchCreate={handleBranchCreate}
          onBranchUpdate={handleBranchUpdate}
          onBranchDelete={handleBranchDelete}
          isDeleting={deleteCarrier.isPending}
          isUpdating={updateCarrier.isPending}
          isCreatingBranch={createBranch.isPending}
          isUpdatingBranch={updateBranch.isPending}
          isDeletingBranch={deleteBranch.isPending}
        />
      )}

      {/* Create Carrier Form */}
      <CarrierForm
        open={createFormOpen}
        onOpenChange={handleCloseCreateForm}
        onSubmit={handleCreateSubmit}
        isLoading={createCarrier.isPending}
        title="Nova Transportadora"
      />

      {/* Edit Carrier Form */}
      <CarrierForm
        open={editFormOpen}
        onOpenChange={handleCloseEditForm}
        onSubmit={handleEditSubmit}
        carrier={editingCarrier}
        isLoading={updateCarrier.isPending}
        title="Editar Transportadora"
      />
    </div>
  )
}