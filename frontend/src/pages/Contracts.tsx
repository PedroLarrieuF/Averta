// Contracts Page - Main Route
// Card #24: Contracts Page - CRUD + FreightTable Editor

import { useState, useCallback, useMemo } from 'react';
import { Search, Plus } from 'lucide-react';
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Card, CardBody, PageHeader, PageTitle, PageSubtitle } from '@/components';
import { ContractsTable, ContractForm, ContractDetailModal, FreightTableEditor } from '@/components/contracts';
import { useContracts, useCreateContract, useUpdateContract, useDeleteContract, useFreightTables, useActivateFreightTable, useDeleteFreightTable, useClientsSimple, useCarriersSimple } from '@/hooks/useContracts';
import type { Contract, ContractStatus } from '@/types/contracts';
import type { FreightTableSummary } from '@/components/contracts/ContractDetailModal';
import toast from 'react-hot-toast';

export function ContractsPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ContractStatus | ''>('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [showFormModal, setShowFormModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showFreightTableModal, setShowFreightTableModal] = useState(false);
  const [editingContract, setEditingContract] = useState<Contract | null>(null);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [selectedContractForFreight, setSelectedContractForFreight] = useState<Contract | null>(null);
  const [editingFreightTableId, setEditingFreightTableId] = useState<string | undefined>(undefined);

  const { data, isLoading, refetch } = useContracts({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    size: pageSize,
  });

  const { data: clients } = useClientsSimple();
  const { data: carriers } = useCarriersSimple();

  const createContract = useCreateContract();
  const updateContract = useUpdateContract();
  const deleteContract = useDeleteContract();

  // Freight tables hooks
  const activateFreightTable = useActivateFreightTable();
  const deleteFreightTable = useDeleteFreightTable();

  // Load freight tables for the selected contract in detail modal
  const { data: freightTablesData, isLoading: isLoadingFreightTables } = useFreightTables(
    selectedContract?.id
  );

  // Convert FreightTable[] to FreightTableSummary[] for the detail modal
  const freightTables = useMemo<FreightTableSummary[]>(() => {
    return (freightTablesData || []).map((ft) => ({
      id: ft.id,
      version: ft.version,
      status: ft.status,
      effective_from: ft.effective_from,
      effective_to: ft.effective_to,
      rates_count: ft.rates.length,
      created_at: ft.created_at,
    }));
  }, [freightTablesData]);

  const handleOpenCreate = useCallback(() => {
    setEditingContract(null);
    setShowFormModal(true);
  }, []);

  const handleOpenEdit = useCallback((contract: Contract) => {
    setEditingContract(contract);
    setShowFormModal(true);
  }, []);

  const handleView = useCallback((contract: Contract) => {
    setSelectedContract(contract);
    setShowDetailModal(true);
  }, []);

  const handleManageFreightTables = useCallback((contract: Contract) => {
    setSelectedContractForFreight(contract);
    setShowFreightTableModal(true);
    setEditingFreightTableId(undefined);
  }, []);

  const handleCreateFreightTable = useCallback((contractId: string) => {
    setSelectedContractForFreight({ id: contractId } as Contract);
    setShowFreightTableModal(true);
    setEditingFreightTableId(undefined);
  }, []);

  const handleActivateFreightTable = useCallback(async (tableId: string) => {
    try {
      await activateFreightTable.mutateAsync(tableId);
      toast.success('Tabela ativada com sucesso!');
      refetch();
    } catch (error) {
      toast.error('Erro ao ativar tabela');
    }
  }, [activateFreightTable, refetch]);

  const handleDeleteFreightTable = useCallback(async (tableId: string) => {
    if (!confirm('Tem certeza que deseja excluir esta tabela de frete?')) return;
    try {
      await deleteFreightTable.mutateAsync(tableId);
      toast.success('Tabela excluída com sucesso!');
      refetch();
    } catch (error) {
      toast.error('Erro ao excluir tabela');
    }
  }, [deleteFreightTable, refetch]);

  const handleFormSubmit = async (data: any) => {
    try {
      if (editingContract) {
        await updateContract.mutateAsync({ id: editingContract.id, data });
        toast.success('Contrato atualizado com sucesso!');
      } else {
        await createContract.mutateAsync(data);
        toast.success('Contrato criado com sucesso!');
      }
      setShowFormModal(false);
      setEditingContract(null);
      refetch();
    } catch (error) {
      toast.error('Erro ao salvar contrato');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este contrato?')) return;
    try {
      await deleteContract.mutateAsync(id);
      toast.success('Contrato excluído com sucesso!');
      refetch();
    } catch (error) {
      toast.error('Erro ao excluir contrato');
    }
  };

  const contracts = data?.data || [];
  const totalPages = data?.meta?.total_pages || 1;
  const totalItems = data?.meta?.total || 0;

  // Transform contracts for the table
  const tableContracts = contracts.map((c) => ({
    ...c,
    client_name: c.client_name,
    carrier_name: c.carrier_name,
    freight_tables_count: c.freight_tables_count,
  }));

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <PageTitle>Contratos</PageTitle>
        <PageSubtitle>Gerencie contratos e tabelas de frete versionadas</PageSubtitle>
      </PageHeader>

      {/* Filters */}
      <Card>
        <CardBody className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="relative flex-1 min-w-[250px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
              <Input
                placeholder="Buscar por número, cliente, transportadora..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="pl-10"
              />
            </div>
            <Select
              value={statusFilter}
              onValueChange={(value) => { setStatusFilter(value as ContractStatus | ''); setPage(1); }}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Todos os status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="ACTIVE">Ativo</SelectItem>
                <SelectItem value="EXPIRED">Expirado</SelectItem>
                <SelectItem value="PENDING">Pendente</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardBody>
      </Card>

      {/* Contracts Table */}
      <Card>
        <div className="flex items-center justify-between p-4 border-b border-secondary-200">
          <h2 className="text-lg font-semibold text-secondary-900">Lista de Contratos</h2>
          <Button onClick={handleOpenCreate}>
            <Plus className="h-4 w-4 mr-2" />
            Novo Contrato
          </Button>
        </div>

        <CardBody className="p-0">
          <ContractsTable
            contracts={tableContracts}
            isLoading={isLoading}
            onView={handleView}
            onEdit={handleOpenEdit}
            onDelete={handleDelete}
            onManageFreightTables={handleManageFreightTables}
            currentPage={page}
            pageSize={pageSize}
            totalPages={totalPages}
            totalItems={totalItems}
            onPageChange={setPage}
            onPageSizeChange={() => {}}
          />
        </CardBody>
      </Card>

      {/* Contract Form Modal */}
      {showFormModal && (
        <ContractForm
          open={showFormModal}
          onOpenChange={setShowFormModal}
          onSubmit={handleFormSubmit}
          clients={clients || []}
          carriers={carriers || []}
          initialData={editingContract ? {
            number: editingContract.number,
            client_id: editingContract.client_id,
            carrier_id: editingContract.carrier_id,
            status: editingContract.status,
            start_date: editingContract.start_date.split('T')[0],
            end_date: editingContract.end_date?.split('T')[0] || '',
            success_fee_pct: editingContract.success_fee_pct.toString(),
            description: editingContract.description || '',
          } : null}
          isSubmitting={createContract.isPending || updateContract.isPending}
          title={editingContract ? 'Editar Contrato' : 'Novo Contrato'}
        />
      )}

      {/* Contract Detail Modal */}
      {showDetailModal && selectedContract && (
        <ContractDetailModal
          open={showDetailModal}
          onOpenChange={setShowDetailModal}
          contract={selectedContract}
          freightTables={freightTables || []}
          isLoadingFreightTables={isLoadingFreightTables}
          onEdit={handleOpenEdit}
          onManageFreightTables={handleManageFreightTables}
          onCreateFreightTable={handleCreateFreightTable}
          onActivateFreightTable={handleActivateFreightTable}
          onDeleteFreightTable={handleDeleteFreightTable}
        />
      )}

      {/* Freight Table Editor Modal */}
      {showFreightTableModal && selectedContractForFreight && (
        <FreightTableEditor
          contractId={selectedContractForFreight.id}
          freightTableId={editingFreightTableId}
          onClose={() => {
            setShowFreightTableModal(false);
            setSelectedContractForFreight(null);
            setEditingFreightTableId(undefined);
          }}
          onSaved={() => refetch()}
        />
      )}
    </div>
  );
}