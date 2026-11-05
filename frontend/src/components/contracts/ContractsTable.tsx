// Contracts Table Component
// Card #24: Contracts Page - CRUD + FreightTable Editor

import { useMemo, useState } from 'react';
import { formatDate } from '../../utils/helpers';
import { MoreHorizontal, Edit, Trash2, Eye, Truck } from 'lucide-react';
import { Button, Table, Badge, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, Modal } from '../index';

export interface ContractsTableProps {
  contracts: any[];
  isLoading?: boolean;
  onView: (contract: any) => void;
  onEdit: (contract: any) => void;
  onDelete: (contract: any) => void;
  onManageFreightTables: (contract: any) => void;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

const STATUS_BADGE_VARIANTS: Record<string, 'success' | 'warning' | 'secondary'> = {
  ACTIVE: 'success',
  EXPIRED: 'secondary',
  PENDING: 'warning',
};

export function ContractsTable({
  contracts,
  isLoading = false,
  onView,
  onEdit,
  onDelete,
  onManageFreightTables,
  currentPage,
  pageSize,
  totalPages,
  totalItems,
  onPageChange,
  onPageSizeChange,
}: ContractsTableProps) {
  const [deleteTarget, setDeleteTarget] = useState<any>(null);

  const handleDeleteClick = (contract: any) => {
    setDeleteTarget(contract);
  };

  const confirmDelete = () => {
    if (deleteTarget) {
      onDelete(deleteTarget);
      setDeleteTarget(null);
    }
  };

  const columns = useMemo(() => [
    {
      key: 'number',
      header: 'Número',
      render: (contract: any) => (
        <span className="font-mono font-medium text-secondary-900">{contract.number}</span>
      ),
    },
    {
      key: 'client_name',
      header: 'Cliente',
      render: (contract: any) => (
        <div>
          <p className="font-medium text-secondary-900">{contract.client_name || '—'}</p>
          <p className="text-xs text-secondary-500 font-mono">{contract.client_id}</p>
        </div>
      ),
    },
    {
      key: 'carrier_name',
      header: 'Transportadora',
      render: (contract: any) => (
        <div>
          <p className="font-medium text-secondary-900">{contract.carrier_name || '—'}</p>
          <p className="text-xs text-secondary-500 font-mono">{contract.carrier_id}</p>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (contract: any) => (
        <Badge variant={STATUS_BADGE_VARIANTS[contract.status] || 'secondary'}>
          {contract.status}
        </Badge>
      ),
    },
    {
      key: 'vigencia',
      header: 'Vigência',
      render: (contract: any) => (
        <div className="text-sm">
          <p className="font-medium text-secondary-900">
            {formatDate(contract.start_date)}
          </p>
          <p className="text-secondary-500">
            {contract.end_date ? `até ${formatDate(contract.end_date)}` : 'Indeterminado'}
          </p>
        </div>
      ),
    },
    {
      key: 'success_fee_pct',
      header: 'Success Fee %',
      render: (contract: any) => (
        <span className="font-mono text-secondary-900">
          {contract.success_fee_pct.toFixed(2)}%
        </span>
      ),
    },
    {
      key: 'freight_tables_count',
      header: 'Tabelas',
      render: (contract: any) => (
        <Badge variant="secondary" className="text-xs">
          {contract.freight_tables_count || 0}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Criado em',
      render: (contract: any) => (
        <span className="text-sm text-secondary-500">
          {formatDate(contract.created_at)}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (contract: any) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onView(contract)}>
              <Eye className="h-4 w-4" />
              Visualizar
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onEdit(contract)}>
              <Edit className="h-4 w-4" />
              Editar
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onManageFreightTables(contract)}>
              <Truck className="h-4 w-4" />
              Gerenciar Tabelas de Frete
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleDeleteClick(contract)}
              className="text-danger-600 focus:text-danger-600"
              inset
            >
              <Trash2 className="h-4 w-4" />
              Excluir
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ], [onView, onEdit, onDelete, onManageFreightTables, deleteTarget]);

  return (
    <div>
      <Table
        columns={columns}
        data={contracts}
        keyField="id"
        isLoading={isLoading}
        emptyMessage="Nenhum contrato encontrado"
      />

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-secondary-500">
            Mostrando {(currentPage - 1) * pageSize + 1} a {Math.min(currentPage * pageSize, totalItems)} de {totalItems}
          </span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="input input-sm w-auto"
          >
            <option value={10}>10 por página</option>
            <option value={20}>20 por página</option>
            <option value={50}>50 por página</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage <= 1}
          >
            Anterior
          </Button>
          <span className="text-sm text-secondary-500 px-2">
            Página {currentPage} de {totalPages}
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
          >
            Próxima
          </Button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <Modal
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Excluir Contrato"
        description={deleteTarget ? `Tem certeza que deseja excluir o contrato "${deleteTarget.number}"? Esta ação não pode ser desfeita.` : ''}
      >
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={confirmDelete}>
            <Trash2 className="h-4 w-4" />
            Excluir
          </Button>
        </div>
      </Modal>
    </div>
  );
}