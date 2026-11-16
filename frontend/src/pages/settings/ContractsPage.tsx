import { useState } from 'react'
import { Search, Plus, FileText, MoreVertical, Edit, Trash2, Truck, Copy, History } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Badge, Card, CardBody, Table, Pagination, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, Tabs, TabsList, TabsTrigger, TabsContent } from '@/components'
import toast from 'react-hot-toast'
import { useAuth } from '@/store/auth-context'
import { useSettingsContracts, useCreateContract, useUpdateContract, useDeleteContract, useSettingsCarriers, useCreateContractVersion } from '@/hooks/useSettings'
import { useClients } from '@/hooks/useApi'
import { ContractForm } from '@/components/settings/ContractForm'
import { FreightTableEditor } from '@/components/settings/FreightTableEditor'
import { formatDate } from '@/utils/helpers'
import type { Contract, ContractStatus } from '@/types'

const STATUS_BADGES: Record<ContractStatus, 'success' | 'warning' | 'danger' | 'secondary'> = {
  DRAFT: 'secondary',
  ACTIVE: 'success',
  EXPIRED: 'warning',
  CANCELLED: 'danger',
  PENDING: 'warning',
}

const STATUS_LABELS: Record<ContractStatus, string> = {
  DRAFT: 'Rascunho',
  ACTIVE: 'Ativo',
  EXPIRED: 'Expirado',
  CANCELLED: 'Cancelado',
  PENDING: 'Pendente',
}

export function ContractsPage() {
  const { user, hasAnyRole } = useAuth()
  const canManage = user ? hasAnyRole(['ADMIN', 'MANAGER']) : false
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [page, setPage] = useState(1)
  const [showFormModal, setShowFormModal] = useState(false)
  const [showFreightTableModal, setShowFreightTableModal] = useState(false)
  const [editingContract, setEditingContract] = useState<Contract | null>(null)
  const [selectedContractForFreight, setSelectedContractForFreight] = useState<Contract | null>(null)
  const [activeTab, setActiveTab] = useState<string>('list')
  const pageSize = 10

  const { data, isLoading, refetch } = useSettingsContracts({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    limit: pageSize,
  })

  const { data: clients } = useClients({ limit: 1000 })
  const { data: carriers } = useSettingsCarriers({ limit: 1000 })

  const createContract = useCreateContract()
  const updateContract = useUpdateContract()
  const deleteContract = useDeleteContract()
  const createContractVersion = useCreateContractVersion()

  const handleOpenCreate = () => {
    setEditingContract(null)
    setShowFormModal(true)
  }

  const handleOpenEdit = (contract: Contract) => {
    setEditingContract(contract)
    setShowFormModal(true)
  }

  const handleOpenFreightTable = (contract: Contract) => {
    setSelectedContractForFreight(contract)
    setShowFreightTableModal(true)
  }

  const handleFormSubmit = async (data: Partial<Contract>) => {
    if (editingContract) {
      await updateContract.mutateAsync({ id: editingContract.id, data })
      toast.success('Contrato atualizado com sucesso!')
    } else {
      await createContract.mutateAsync(data)
      toast.success('Contrato criado com sucesso!')
    }
    setShowFormModal(false)
    setEditingContract(null)
    refetch()
  }

  const handleFreightTableSave = async (rules: Record<string, unknown>[]) => {
    if (!selectedContractForFreight) return
    await updateContract.mutateAsync({ id: selectedContractForFreight.id, data: { freightTables: rules as any } })
    toast.success('Tabela de frete atualizada!')
    setShowFreightTableModal(false)
    setSelectedContractForFreight(null)
    refetch()
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este contrato?')) return
    try {
      await deleteContract.mutateAsync(id)
      toast.success('Contrato excluído com sucesso!')
      refetch()
    } catch (_err) {
      toast.error('Erro ao excluir contrato')
    }
  }

  const handleCreateVersion = async (contractId: string) => {
    const name = prompt('Nome da nova versão:')
    if (!name) return
    try {
      await createContractVersion.mutateAsync({ contractId, data: { name } })
      toast.success('Nova versão criada!')
    } catch (_err) {
      toast.error('Erro ao criar versão')
    }
  }

  const filteredContracts = data?.data || []
  const totalPages = data?.meta?.totalPages || 1

  const columns = [
    {
      key: 'contract',
      header: 'Contrato',
      render: (c: Contract) => (
        <div>
          <p className="font-medium text-secondary-900">{c.name}</p>
          <p className="text-sm text-secondary-500 font-mono">{c.number}</p>
        </div>
      ),
    },
    {
      key: 'client',
      header: 'Cliente',
      render: (c: Contract) => {
        const client = clients?.data?.find(cl => cl.id === c.clientId)
        return <span className="text-sm text-secondary-500">{client?.name || c.clientId}</span>
      },
    },
    {
      key: 'carrier',
      header: 'Transportadora',
      render: (c: Contract) => {
        const carrier = carriers?.data?.find(cr => cr.id === c.carrierId)
        return <span className="text-sm text-secondary-500">{carrier?.name || c.carrierId}</span>
      },
    },
    {
      key: 'validity',
      header: 'Vigência',
      render: (c: Contract) => (
        <span className="text-sm text-secondary-500">
          {formatDate(c.startDate)} — {c.endDate ? formatDate(c.endDate) : 'Indeterminado'}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (c: Contract) => (
        <Badge variant={STATUS_BADGES[c.status] || 'secondary'}>
          {STATUS_LABELS[c.status] || c.status}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      className: 'text-right',
      render: (c: Contract) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem onClick={() => handleOpenEdit(c)} disabled={!canManage}>
              <Edit className="h-4 w-4 mr-2" />
              Editar
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleOpenFreightTable(c)}>
              <Truck className="h-4 w-4 mr-2" />
              Tabela de Frete
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleCreateVersion(c.id)} disabled={!canManage}>
              <Copy className="h-4 w-4 mr-2" />
              Nova Versão
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleDelete(c.id)}
              disabled={!canManage}
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Contratos</h1>
          <p className="text-secondary-500">Gerencie contratos e tabelas de frete</p>
        </div>
        {canManage && (
          <Button onClick={handleOpenCreate}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Contrato
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
                placeholder="Buscar por nome, número, cliente..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={(value) => { setStatusFilter(value); setPage(1); }}>
              <SelectTrigger><SelectValue placeholder="Todos os status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="DRAFT">Rascunho</SelectItem>
                <SelectItem value="ACTIVE">Ativo</SelectItem>
                <SelectItem value="EXPIRED">Expirado</SelectItem>
                <SelectItem value="CANCELLED">Cancelado</SelectItem>
                <SelectItem value="PENDING">Pendente</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardBody>
      </Card>

      {/* Contracts Table */}
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
        ) : filteredContracts.length === 0 ? (
          <div className="card p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-secondary-300 mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum contrato encontrado</h3>
            <p className="text-secondary-500 mb-4">
              {search || statusFilter ? 'Tente ajustar os filtros' : 'Cadastre o primeiro contrato'}
            </p>
            {canManage && !search && !statusFilter && (
              <Button onClick={handleOpenCreate}>
                <Plus className="h-4 w-4 mr-2" />
                Novo Contrato
              </Button>
            )}
          </div>
        ) : (
          <>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-2 border-b border-secondary-200">
                <TabsTrigger value="list" className="flex items-center justify-center gap-2">
                  <FileText className="h-4 w-4" />
                  Lista
                </TabsTrigger>
                <TabsTrigger value="versions" className="flex items-center justify-center gap-2">
                  <History className="h-4 w-4" />
                  Versões
                </TabsTrigger>
              </TabsList>

              <TabsContent value="list" className="p-4">
                <Table columns={columns} data={filteredContracts} keyField="id" isLoading={isLoading} />

                {/* Pagination */}
                {totalPages > 1 && (
                  <Pagination
                    currentPage={page}
                    totalPages={totalPages}
                    onPageChange={setPage}
                  />
                )}
              </TabsContent>

              <TabsContent value="versions" className="p-4">
                <p className="text-secondary-500 text-center py-8">
                  Selecione um contrato na aba "Lista" para ver suas versões
                </p>
              </TabsContent>
            </Tabs>
          </>
        )}
      </Card>

      {/* Contract Form Modal */}
      {showFormModal && (
        <ContractForm
          initialData={editingContract}
          clients={clients?.data || []}
          carriers={carriers?.data || []}
          onSubmit={handleFormSubmit}
          onCancel={() => { setShowFormModal(false); setEditingContract(null); }}
          isSubmitting={createContract.isPending || updateContract.isPending}
          mode={editingContract ? 'edit' : 'create'}
        />
      )}

      {/* Freight Table Modal */}
      {showFreightTableModal && selectedContractForFreight && (
        <FreightTableEditor
          initialRules={selectedContractForFreight?.freightTables as unknown as Record<string, unknown>[] || []}
          onSave={handleFreightTableSave}
          onCancel={() => { setShowFreightTableModal(false); setSelectedContractForFreight(null); }}
          isSubmitting={updateContract.isPending}
        />
      )}
    </div>
  )
}