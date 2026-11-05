// Contract Detail Modal Component
// Card #24: Contracts Page - CRUD + FreightTable Editor

import { formatDate } from '../../utils/helpers';
import { Edit, Truck, X, FileText, Loader2, Plus } from 'lucide-react';
import { Button, Badge, Modal, Card, CardHeader, CardBody, Table } from '../index';

export interface FreightTableSummary {
  id: string;
  version: number;
  status: 'DRAFT' | 'ACTIVE' | 'ARCHIVED';
  effective_from: string;
  effective_to: string | null;
  rates_count: number;
  created_at: string;
}

interface ContractDetailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  contract: any | null;
  freightTables: FreightTableSummary[];
  isLoadingFreightTables?: boolean;
  onEdit: (contract: any) => void;
  onManageFreightTables: (contract: any) => void;
  onCreateFreightTable: (contractId: string) => void;
  onActivateFreightTable: (tableId: string) => void;
  onDeleteFreightTable: (tableId: string) => void;
}

const STATUS_BADGE_VARIANTS: Record<string, 'success' | 'warning' | 'secondary'> = {
  ACTIVE: 'success',
  EXPIRED: 'secondary',
  PENDING: 'warning',
  DRAFT: 'warning',
  ARCHIVED: 'secondary',
};

export function ContractDetailModal({
  open,
  onOpenChange,
  contract,
  freightTables,
  isLoadingFreightTables = false,
  onEdit,
  onManageFreightTables,
  onCreateFreightTable,
  onActivateFreightTable,
  onDeleteFreightTable,
}: ContractDetailModalProps) {
  if (!contract) return null;

  const handleClose = () => onOpenChange(false);

  const freightTableColumns = [
    {
      key: 'version',
      header: 'Versão',
      render: (ft: FreightTableSummary) => (
        <span className="font-mono font-medium text-secondary-900">v{ft.version}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (ft: FreightTableSummary) => (
        <Badge variant={STATUS_BADGE_VARIANTS[ft.status] || 'secondary'}>
          {ft.status}
        </Badge>
      ),
    },
    {
      key: 'effective_from',
      header: 'Vigência Início',
      render: (ft: FreightTableSummary) => (
        <span className="text-sm text-secondary-900">{formatDate(ft.effective_from)}</span>
      ),
    },
    {
      key: 'effective_to',
      header: 'Vigência Fim',
      render: (ft: FreightTableSummary) => (
        <span className="text-sm text-secondary-500">
          {ft.effective_to ? formatDate(ft.effective_to) : 'Indeterminado'}
        </span>
      ),
    },
    {
      key: 'rates_count',
      header: 'Taxas',
      render: (ft: FreightTableSummary) => (
        <span className="text-sm text-secondary-900">{ft.rates_count}</span>
      ),
    },
    {
      key: 'created_at',
      header: 'Criado em',
      render: (ft: FreightTableSummary) => (
        <span className="text-sm text-secondary-500">{formatDate(ft.created_at)}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      render: (ft: FreightTableSummary) => (
        <div className="flex items-center gap-1">
          {ft.status === 'DRAFT' && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onActivateFreightTable(ft.id)}
              className="h-8 px-2"
            >
              Ativar
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDeleteFreightTable(ft.id)}
            className="h-8 px-2 text-danger-600 hover:text-danger-600"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <Modal
      open={open}
      onOpenChange={handleClose}
      title={`Contrato: ${contract.number}`}
      size="xl"
    >
      <div className="space-y-6">
        {/* Contract Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-secondary-500">Status</p>
            </CardHeader>
            <CardBody>
              <Badge variant={STATUS_BADGE_VARIANTS[contract.status] || 'secondary'} className="text-lg px-3 py-1">
                {contract.status}
              </Badge>
            </CardBody>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-secondary-500">Cliente</p>
            </CardHeader>
            <CardBody>
              <p className="font-medium text-secondary-900">{contract.client_name || '—'}</p>
              <p className="text-xs text-secondary-500 font-mono">{contract.client_id}</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-secondary-500">Transportadora</p>
            </CardHeader>
            <CardBody>
              <p className="font-medium text-secondary-900">{contract.carrier_name || '—'}</p>
              <p className="text-xs text-secondary-500 font-mono">{contract.carrier_id}</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <p className="text-sm text-secondary-500">Success Fee</p>
            </CardHeader>
            <CardBody>
              <p className="font-mono font-medium text-secondary-900 text-lg">
                {contract.success_fee_pct.toFixed(2)}%
              </p>
            </CardBody>
          </Card>
        </div>

        {/* Additional Info */}
        <Card>
          <CardHeader className="pb-2">
            <h3 className="text-lg font-semibold text-secondary-900">Informações do Contrato</h3>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-secondary-500">Vigência</p>
                <p className="font-medium text-secondary-900">
                  {formatDate(contract.start_date)}
                  {contract.end_date ? ` a ${formatDate(contract.end_date)}` : ' (indeterminado)'}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-secondary-500">Criado em</p>
                <p className="font-medium text-secondary-900">{formatDate(contract.created_at)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-secondary-500">Atualizado em</p>
                <p className="font-medium text-secondary-900">{formatDate(contract.updated_at)}</p>
              </div>
            </div>

            {contract.description && (
              <div className="mt-4 space-y-1">
                <p className="text-sm text-secondary-500">Descrição</p>
                <p className="text-secondary-900">{contract.description}</p>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Freight Tables */}
        <div className="flex items-center justify-between">
          <CardHeader className="pb-0">
            <h3 className="text-lg font-semibold text-secondary-900">Tabelas de Frete</h3>
          </CardHeader>
          <Button onClick={() => onCreateFreightTable(contract.id)} size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Nova Tabela
          </Button>
        </div>

        <Card>
          <CardBody className="p-0">
            {isLoadingFreightTables ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-secondary-400" />
              </div>
            ) : freightTables.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-secondary-400">
                <FileText className="h-12 w-12 mb-4" />
                <p className="text-secondary-500">Nenhuma tabela de frete cadastrada</p>
                <p className="text-sm text-secondary-400">Clique em "Nova Tabela" para criar a primeira</p>
              </div>
            ) : (
              <Table
                columns={freightTableColumns}
                data={freightTables}
                keyField="id"
                isLoading={false}
                emptyMessage="Nenhuma tabela de frete encontrada"
              />
            )}
          </CardBody>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="secondary" onClick={handleClose}>
            Fechar
          </Button>
          <Button variant="secondary" onClick={() => { handleClose(); onEdit(contract); }}>
            <Edit className="h-4 w-4 mr-2" />
            Editar Contrato
          </Button>
          <Button onClick={() => { handleClose(); onManageFreightTables(contract); }}>
            <Truck className="h-4 w-4 mr-2" />
            Gerenciar Tabelas
          </Button>
        </div>
      </div>
    </Modal>
  );
}