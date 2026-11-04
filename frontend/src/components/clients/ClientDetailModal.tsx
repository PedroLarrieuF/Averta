import { useState } from 'react'
import { Edit, Trash2 } from 'lucide-react'
import { Button, StatusBadge, Modal, Tabs, TabsList, TabsTrigger, TabsContent, ConfirmDialog } from '@/components'
import { Client, ClientBranch } from '@/types'
import { formatDate } from '@/utils/helpers'
import { BranchesTable } from './BranchesTable'
import { BranchForm } from './BranchForm'

interface ClientDetailModalProps {
  client: Client | null
  onClose: () => void
  onEdit: (client: Client) => void
  onDelete: (client: Client) => void
  onBranchCreate: (data: any) => Promise<void>
  onBranchUpdate: (id: string, data: any) => Promise<void>
  onBranchDelete: (id: string) => Promise<void>
  isDeleting?: boolean
  isUpdating?: boolean
  isCreatingBranch?: boolean
  isUpdatingBranch?: boolean
  isDeletingBranch?: boolean
}

export function ClientDetailModal({
  client,
  onClose,
  onEdit,
  onDelete,
  onBranchCreate,
  onBranchUpdate,
  onBranchDelete,
  isDeleting = false,
  isUpdating = false,
  isCreatingBranch = false,
  isUpdatingBranch = false,
  isDeletingBranch = false,
}: ClientDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'branches'>('info')
  const [branchFormOpen, setBranchFormOpen] = useState(false)
  const [editingBranch, setEditingBranch] = useState<ClientBranch | null>(null)
  const [deleteBranchConfirm, setDeleteBranchConfirm] = useState<ClientBranch | null>(null)
  const [deleteClientConfirm, setDeleteClientConfirm] = useState(false)

  if (!client) return null

  const handleBranchSubmit = async (data: any) => {
    if (editingBranch) {
      await onBranchUpdate(editingBranch.id, data)
    } else {
      await onBranchCreate(data)
    }
    setBranchFormOpen(false)
    setEditingBranch(null)
  }

  const handleEditBranch = (branch: ClientBranch) => {
    setEditingBranch(branch)
    setBranchFormOpen(true)
  }

  const handleDeleteBranch = (branch: ClientBranch) => {
    setDeleteBranchConfirm(branch)
  }

  const confirmDeleteBranch = async () => {
    if (deleteBranchConfirm) {
      await onBranchDelete(deleteBranchConfirm.id)
      setDeleteBranchConfirm(null)
    }
  }

  const handleDeleteClient = () => {
    setDeleteClientConfirm(true)
  }

  return (
    <Modal
      open={true}
      onOpenChange={onClose}
      title={client.name}
      size="xl"
      showClose
    >
      <div className="space-y-6">
        {/* Client Info Header */}
        <div className="flex items-start justify-between gap-4 p-4 bg-secondary-50 rounded-lg">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-semibold text-secondary-900">{client.name}</h2>
              <StatusBadge status={client.status} />
            </div>
            <p className="text-sm text-secondary-500 font-mono">{formatCNPJCPF(client.cnpj)}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => onEdit(client)} disabled={isUpdating}>
              <Edit className="h-4 w-4 mr-2" />
              Editar
            </Button>
            <Button variant="ghost" className="text-danger-600" onClick={handleDeleteClient} disabled={isDeleting}>
              <Trash2 className="h-4 w-4 mr-2" />
              Excluir
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(value: string) => setActiveTab(value as 'info' | 'branches')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="info">Informações</TabsTrigger>
            <TabsTrigger value="branches">Filiais ({client.branches?.length || 0})</TabsTrigger>
          </TabsList>

          <TabsContent value="info" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label">Email</label>
                <p className="text-secondary-900">{client.email || <span className="text-secondary-400">—</span>}</p>
              </div>
              <div>
                <label className="label">Telefone</label>
                <p className="text-secondary-900">{client.phone || <span className="text-secondary-400">—</span>}</p>
              </div>
            </div>

            {client.address && (
              <div className="border-t border-secondary-200 pt-4">
                <h3 className="text-sm font-medium text-secondary-900 mb-3">Endereço</h3>
                <div className="grid gap-4 md:grid-cols-3 text-sm">
                  <div>
                    <label className="label">Logradouro</label>
                    <p className="text-secondary-900">{client.address || '—'}</p>
                  </div>
                  <div>
                    <label className="label">Cidade</label>
                    <p className="text-secondary-900">{client.city || '—'}</p>
                  </div>
                  <div>
                    <label className="label">UF</label>
                    <p className="text-secondary-900">{client.state || '—'}</p>
                  </div>
                  <div className="md:col-span-2">
                    <label className="label">CEP</label>
                    <p className="text-secondary-900">{client.zipCode || '—'}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="border-t border-secondary-200 pt-4">
              <h3 className="text-sm font-medium text-secondary-900 mb-3">Estatísticas</h3>
              <div className="grid gap-4 md:grid-cols-3 text-sm">
                <div>
                  <label className="label">Filiais</label>
                  <p className="text-2xl font-bold text-secondary-900">{client.branches?.length || 0}</p>
                </div>
                <div>
                  <label className="label">Contatos</label>
                  <p className="text-2xl font-bold text-secondary-900">{client.contacts?.length || 0}</p>
                </div>
                <div>
                  <label className="label">Criado em</label>
                  <p className="text-secondary-900">{formatDate(client.createdAt)}</p>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="branches">
            <BranchesTable
              branches={client.branches || []}
              onView={() => {}}
              onEdit={handleEditBranch}
              onDelete={handleDeleteBranch}
              onNewBranch={() => {
                setEditingBranch(null)
                setBranchFormOpen(true)
              }}
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* Branch Form Modal */}
      {branchFormOpen && (
        <BranchForm
          open
          onOpenChange={(open) => {
            if (!open) {
              setBranchFormOpen(false)
              setEditingBranch(null)
            }
          }}
          onSubmit={handleBranchSubmit}
          branch={editingBranch}
          isLoading={isCreatingBranch || isUpdatingBranch}
          title={editingBranch ? 'Editar Filial' : 'Nova Filial'}
          existingCodes={client.branches?.map((b) => b.code).filter((c) => c !== editingBranch?.code) || []}
        />
      )}

      {/* Delete Branch Confirm */}
      {deleteBranchConfirm && (
        <ConfirmDialog
          open
          onOpenChange={(open) => !open && setDeleteBranchConfirm(null)}
          title="Excluir filial"
          description={`Tem certeza que deseja excluir a filial "${deleteBranchConfirm.name}"?`}
          confirmText="Excluir"
          onConfirm={confirmDeleteBranch}
          variant="danger"
          loading={isDeletingBranch}
        />
      )}

      {/* Delete Client Confirm */}
      {deleteClientConfirm && (
        <ConfirmDialog
          open
          onOpenChange={(open) => !open && setDeleteClientConfirm(false)}
          title="Excluir cliente"
          description={`Tem certeza que deseja excluir o cliente "${client.name}"? Esta ação não pode ser desfeita e também removerá todas as filiais associadas.`}
          confirmText="Excluir"
          onConfirm={() => {
            onDelete(client)
            setDeleteClientConfirm(false)
            onClose()
          }}
          variant="danger"
          loading={isDeleting}
        />
      )}
    </Modal>
  )
}

function formatCNPJCPF(value: string): string {
  const cleaned = value.replace(/\D/g, '')
  if (cleaned.length === 14) {
    return cleaned.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
  }
  if (cleaned.length === 11) {
    return cleaned.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  }
  return value
}