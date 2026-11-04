import { useState } from 'react'
import { Eye, Edit, Trash2, Building2 } from 'lucide-react'
import { Table, Pagination, Column, StatusBadge, Button, ConfirmDialog } from '@/components'
import { Client } from '@/types'
import { formatDate } from '@/utils/helpers'

interface ClientsTableProps {
  clients: Client[]
  isLoading?: boolean
  pagination?: {
    page: number
    totalPages: number
    total: number
    limit: number
  }
  onPageChange: (page: number) => void
  onSizeChange: (size: number) => void
  onView: (client: Client) => void
  onEdit: (client: Client) => void
  onDelete: (client: Client) => void
}

export function ClientsTable({
  clients,
  isLoading = false,
  pagination,
  onPageChange,
  onSizeChange,
  onView,
  onEdit,
  onDelete,
}: ClientsTableProps) {
  const [deleteConfirm, setDeleteConfirm] = useState<Client | null>(null)

  const columns: Column<Client>[] = [
    {
      key: 'name',
      header: 'Nome',
      render: (row) => (
        <div>
          <p className="font-medium text-secondary-900">{row.name}</p>
          {row.branches && row.branches.length > 0 && (
            <p className="text-sm text-secondary-500 flex items-center gap-1">
              <Building2 className="h-3 w-3" />
              {row.branches.length} filial(is)
            </p>
          )}
        </div>
      ),
    },
    {
      key: 'cnpj',
      header: 'Documento',
      render: (row) => <span className="font-mono text-sm">{formatCNPJCPF(row.cnpj)}</span>,
    },
    {
      key: 'email',
      header: 'Email',
      render: (row) => row.email || <span className="text-secondary-400">—</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => <StatusBadge status={row.status} />,
    },
    {
      key: 'createdAt',
      header: 'Criado em',
      render: (row) => <span className="text-sm text-secondary-600">{formatDate(row.createdAt)}</span>,
      className: 'hidden md:table-cell',
    },
    {
      key: 'actions',
      header: 'Ações',
      className: 'w-48 text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onView(row)}
            aria-label={`Ver ${row.name}`}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit(row)}
            aria-label={`Editar ${row.name}`}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-danger-600 hover:bg-danger-50"
            onClick={() => setDeleteConfirm(row)}
            aria-label={`Excluir ${row.name}`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <Table
        columns={columns}
        data={clients}
        keyField="id"
        isLoading={isLoading}
        emptyMessage="Nenhum cliente encontrado"
      />
      {pagination && (
        <Pagination
          currentPage={pagination.page}
          totalPages={pagination.totalPages}
          totalItems={pagination.total}
          pageSize={pagination.limit}
          onPageChange={onPageChange}
          onPageSizeChange={onSizeChange}
          pageSizeOptions={[10, 20, 50, 100]}
        />
      )}
      {deleteConfirm && (
        <ConfirmDialog
          open
          onOpenChange={(open) => !open && setDeleteConfirm(null)}
          title="Excluir cliente"
          description={`Tem certeza que deseja excluir o cliente "${deleteConfirm.name}"? Esta ação não pode ser desfeita.`}
          confirmText="Excluir"
          onConfirm={() => {
            onDelete(deleteConfirm)
            setDeleteConfirm(null)
          }}
          variant="danger"
        />
      )}
    </div>
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