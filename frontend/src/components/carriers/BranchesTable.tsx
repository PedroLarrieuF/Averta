import { useState } from 'react'
import { Eye, Edit, Trash2, MapPin, Truck } from 'lucide-react'
import { Table, Column, Badge, Button, ConfirmDialog } from '@/components'

interface BranchesTableProps {
  branches: any[]
  isLoading?: boolean
  onView: (branch: any) => void
  onEdit: (branch: any) => void
  onDelete: (branch: any) => void
  onNewBranch: () => void
}

export function BranchesTable({ branches, isLoading = false, onView, onEdit, onDelete, onNewBranch }: BranchesTableProps) {
  const [deleteConfirm, setDeleteConfirm] = useState<any | null>(null)

  const columns: Column<any>[] = [
    {
      key: 'name',
      header: 'Nome',
      render: (row) => (
        <div>
          <p className="font-medium text-secondary-900">{row.name}</p>
          <p className="text-sm text-secondary-500 font-mono">{row.code}</p>
        </div>
      ),
    },
    {
      key: 'address',
      header: 'Endereço',
      render: (row) => {
        const parts = [row.address, row.city, row.state].filter(Boolean)
        return parts.length > 0 ? (
          <span className="text-sm text-secondary-600 flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {parts.join(', ')}
          </span>
        ) : (
          <span className="text-secondary-400">—</span>
        )
      },
    },
    {
      key: 'antt_code',
      header: 'Código ANTT',
      render: (row) => row.antt_code ? (
        <span className="font-mono text-sm bg-primary-50 text-primary-700 px-2 py-0.5 rounded">
          {row.antt_code}
        </span>
      ) : (
        <span className="text-secondary-400">—</span>
      ),
    },
    {
      key: 'is_main',
      header: 'Principal',
      render: (row) => (
        <Badge variant={row.is_main ? 'success' : 'secondary'}>
          {row.is_main ? 'Sim' : 'Não'}
        </Badge>
      ),
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
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-secondary-900">Filiais ({branches.length})</h3>
        <Button onClick={onNewBranch} size="sm">
          <Truck className="h-4 w-4 mr-1" />
          Nova Filial
        </Button>
      </div>
      <div className="card">
        <div className="card-body p-0">
          <Table
            columns={columns}
            data={branches}
            keyField="id"
            isLoading={isLoading}
            emptyMessage="Nenhuma filial cadastrada"
          />
        </div>
      </div>
      {deleteConfirm && (
        <ConfirmDialog
          open
          onOpenChange={(open) => !open && setDeleteConfirm(null)}
          title="Excluir filial"
          description={`Tem certeza que deseja excluir a filial "${deleteConfirm.name}"? Esta ação não pode ser desfeita.`}
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