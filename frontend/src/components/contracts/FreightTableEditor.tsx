// Freight Table Editor Component
// Card #24: Contracts Page - CRUD + FreightTable Editor
// Main editor with tabs for different modals and the spreadsheet grid

import { useState, useMemo, useCallback, useEffect } from 'react';
import { Trash2, Save, Loader2, ArrowLeft } from 'lucide-react';
import { Button, Card, CardHeader, CardBody, Badge, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Input, Label, Modal, Tabs, TabsList, TabsTrigger, TabsContent, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, Alert, AlertTitle, AlertDescription } from '../index';
import { FreightTableGrid, type FreightRateRow } from './FreightTableGrid';
import { FreightTableVersionManager } from './FreightTableVersionManager';
import { useFreightTable, useCreateFreightTable, useUpdateFreightTable, useActivateFreightTable, useDeleteFreightTable } from '../../hooks/useContracts';
import type { FreightRateInput, FreightModal, CreateFreightTableData, UpdateFreightTableData, FreightTableStatus } from '../../types/contracts';
import { FREIGHT_MODALS } from '../../types/contracts';

export interface FreightTableEditorProps {
  contractId: string;
  freightTableId?: string;
  onClose: () => void;
  onSaved?: () => void;
}

const DEFAULT_RATE: Omit<FreightRateInput, 'modal'> = {
  weight_min: null,
  weight_max: null,
  cubage_min: null,
  cubage_max: null,
  distance_min: null,
  distance_max: null,
  uf_origin: null,
  uf_dest: null,
  rate_per_kg: null,
  rate_per_m3: null,
  rate_per_km: null,
  minimum_value: null,
};

export function FreightTableEditor({
  contractId,
  freightTableId,
  onClose,
  onSaved,
}: FreightTableEditorProps) {
  const isEditing = !!freightTableId;
  const [activeModal, setActiveModal] = useState<FreightModal>('RODOVIARIO');
  const [rates, setRates] = useState<FreightRateRow[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [showVersionManager, setShowVersionManager] = useState(false);
  const [status, setStatus] = useState<FreightTableStatus>('DRAFT');
  const [effectiveFrom, setEffectiveFrom] = useState('');
  const [effectiveTo, setEffectiveTo] = useState('');
  const [version, setVersion] = useState(1);

  // Fetch existing freight table if editing
  const { data: freightTable, isLoading } = useFreightTable(freightTableId);

  const createMutation = useCreateFreightTable();
  const updateMutation = useUpdateFreightTable();
  const activateMutation = useActivateFreightTable();
  const deleteMutation = useDeleteFreightTable();

  // Initialize form data from existing freight table
  useEffect(() => {
    if (freightTable) {
      setActiveModal(freightTable.rates[0]?.modal || 'RODOVIARIO');
      setRates(freightTable.rates.map((r, i) => ({ ...r, id: r.id || `temp-${i}` })));
      setStatus(freightTable.status);
      setEffectiveFrom(freightTable.effective_from.split('T')[0]);
      setEffectiveTo(freightTable.effective_to ? freightTable.effective_to.split('T')[0] : '');
      setVersion(freightTable.version);
    } else if (!isEditing) {
      // New table - start with one empty rate per modal
      const initialRates = FREIGHT_MODALS.map((modal) => ({
        ...DEFAULT_RATE,
        modal: modal.value,
        id: `temp-${modal.value}`,
      }));
      setRates(initialRates);
      setEffectiveFrom(new Date().toISOString().split('T')[0]);
    }
  }, [freightTable, isEditing]);

  // Filter rates for active modal
  const otherModalRates = useMemo(() => {
    return rates.filter((r) => r.modal !== activeModal);
  }, [rates, activeModal]);

  const handleRateChange = useCallback((index: number, field: keyof FreightRateRow, value: any) => {
    setRates((prev) => {
      const newRates = [...prev];
      const rateIndex = prev.findIndex((r, i) => r.modal === activeModal && i === index);
      if (rateIndex >= 0) {
        newRates[rateIndex] = { ...newRates[rateIndex], [field]: value };
      }
      return newRates;
    });
  }, [activeModal]);

  const addRate = useCallback(() => {
    setRates((prev) => [...prev, { ...DEFAULT_RATE, modal: activeModal, id: `temp-${Date.now()}` }]);
  }, [activeModal]);

  const removeRate = useCallback((rateId: string) => {
    setRates((prev) => prev.filter((r) => r.id !== rateId));
  }, []);

  const duplicateRate = useCallback((rateId: string) => {
    setRates((prev) => {
      const rate = prev.find((r) => r.id === rateId);
      if (rate) {
        return [...prev, { ...rate, id: `temp-${Date.now()}` }];
      }
      return prev;
    });
  }, []);

  const copyRatesToModal = useCallback((targetModal: FreightModal) => {
    setRates((prev) => {
      const sourceRates = prev.filter((r) => r.modal === activeModal);
      const newRates = sourceRates.map((r, i) => ({
        ...r,
        modal: targetModal,
        id: `temp-${targetModal}-${i}-${Date.now()}`,
      }));
      return [...prev.filter((r) => r.modal !== targetModal), ...newRates];
    });
  }, [activeModal]);

  const getAllRatesForSubmit = useCallback((): FreightRateInput[] => {
    return rates.map(({ id, ...rate }) => rate);
  }, [rates]);

  const handleSave = async (activate = false) => {
    setIsSaving(true);
    try {
      const ratesData = getAllRatesForSubmit();
      const data: CreateFreightTableData | UpdateFreightTableData = {
        contract_id: contractId,
        status: activate ? 'ACTIVE' : status,
        effective_from: effectiveFrom,
        effective_to: effectiveTo || null,
        rates: ratesData,
      };

      if (isEditing && freightTableId) {
        await updateMutation.mutateAsync({ id: freightTableId, data });
      } else {
        await createMutation.mutateAsync(data);
      }

      if (activate && !isEditing) {
        // For new tables, we need to activate after creation
        // The create mutation returns the created table
      }

      onSaved?.();
      onClose();
    } catch (error) {
      console.error('Failed to save freight table:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!freightTableId) return;
    if (!confirm('Tem certeza que deseja excluir esta tabela de frete?')) return;
    try {
      await deleteMutation.mutateAsync(freightTableId);
      onSaved?.();
      onClose();
    } catch (error) {
      console.error('Failed to delete freight table:', error);
    }
  };

  const handleActivate = async () => {
    if (!freightTableId) return;
    try {
      await activateMutation.mutateAsync(freightTableId);
      onSaved?.();
      onClose();
    } catch (error) {
      console.error('Failed to activate freight table:', error);
    }
  };

  if (isLoading) {
    return (
      <Modal open={true} onOpenChange={onClose} title="Editor de Tabela de Frete" size="xl">
        <div className="flex items-center justify-center h-96">
          <Loader2 className="h-8 w-8 animate-spin text-secondary-400" />
        </div>
      </Modal>
    );
  }

  const unsavedChanges = isEditing && rates.length > 0;

  return (
    <Modal
      open={true}
      onOpenChange={onClose}
      title={isEditing ? `Editar Tabela v${version}` : 'Nova Tabela de Frete'}
      size="xl"
    >
      {/* Alert for unsaved changes */}
      {unsavedChanges && (
        <Alert className="mb-4" variant="warning">
          <AlertTitle>Alterações não salvas</AlertTitle>
          <AlertDescription>
            Você tem alterações pendentes. Salve antes de fechar ou mudar de aba.
          </AlertDescription>
        </Alert>
      )}

      {/* Header Actions */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Select value={activeModal} onValueChange={(value) => setActiveModal(value as FreightModal)}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {FREIGHT_MODALS.map((modal) => (
                <SelectItem key={modal.value} value={modal.value}>
                  {modal.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Badge variant={status === 'ACTIVE' ? 'success' : 'warning'}>
            {status}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={() => setShowVersionManager(true)}>
            Versões
          </Button>

          {!isEditing && (
            <Button variant="secondary" size="sm" onClick={() => handleSave(false)}>
              <Save className="h-4 w-4 mr-2" />
              Salvar Rascunho
            </Button>
          )}

          {isEditing && status === 'DRAFT' && (
            <Button variant="primary" size="sm" onClick={handleActivate} disabled={isSaving || activateMutation.isPending}>
              {activateMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : 'Ativar Tabela'}
            </Button>
          )}

          <Button variant="secondary" size="sm" onClick={() => handleSave(true)} disabled={isSaving}>
            {isSaving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : 'Salvar e Ativar'}
          </Button>

          {isEditing && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="text-danger-600 hover:text-danger-600">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleDelete} className="text-danger-600 focus:text-danger-600">
                  <Trash2 className="h-4 w-4" />
                  Excluir Tabela
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>

      {/* Effective Dates */}
      <Card className="mb-4">
        <CardHeader className="pb-2">
          <h3 className="text-sm font-medium text-secondary-900">Vigência</h3>
        </CardHeader>
        <CardBody className="pt-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="effective_from">Início da Vigência *</Label>
              <Input
                id="effective_from"
                type="date"
                value={effectiveFrom}
                onChange={(e) => setEffectiveFrom(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="effective_to">Fim da Vigência</Label>
              <Input
                id="effective_to"
                type="date"
                value={effectiveTo}
                onChange={(e) => setEffectiveTo(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="version">Versão</Label>
              <Input
                id="version"
                type="number"
                value={version}
                onChange={(e) => setVersion(Number(e.target.value))}
                min={1}
                disabled={isEditing}
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Modal Tabs */}
      <Tabs value={activeModal} onValueChange={(value) => setActiveModal(value as FreightModal)} className="mb-4">
        <TabsList className="grid w-full grid-cols-4">
          {FREIGHT_MODALS.map((modal) => (
            <TabsTrigger key={modal.value} value={modal.value}>
              {modal.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {FREIGHT_MODALS.map((modal) => (
          <TabsContent key={modal.value} value={modal.value} className="pt-0">
            <FreightTableGrid
              modal={modal.value}
              rates={rates.filter((r) => r.modal === modal.value)}
              onRateChange={(index, field, value) => handleRateChange(index, field, value)}
              onAddRate={addRate}
              onRemoveRate={removeRate}
              onDuplicateRate={duplicateRate}
              onCopyToModal={copyRatesToModal}
              availableModals={FREIGHT_MODALS.filter((m) => m.value !== modal.value).map((m) => m.value)}
              isReadOnly={false}
            />
          </TabsContent>
        ))}
      </Tabs>

      {/* Other modals summary */}
      {otherModalRates.length > 0 && (
        <Card className="mb-4">
          <CardHeader className="pb-2">
            <h3 className="text-sm font-medium text-secondary-900">Outras Modais ({otherModalRates.length} taxas)</h3>
          </CardHeader>
          <CardBody className="pt-0">
            <div className="flex flex-wrap gap-2">
              {FREIGHT_MODALS.filter((m) => m.value !== activeModal).map((modal) => {
                const count = rates.filter((r) => r.modal === modal.value).length;
                return count > 0 ? (
                  <Badge key={modal.value} variant="secondary" className="cursor-pointer hover:bg-secondary-200" onClick={() => setActiveModal(modal.value)}>
                    {modal.label} ({count})
                  </Badge>
                ) : null;
              })}
            </div>
          </CardBody>
        </Card>
      )}

      {/* Version Manager Modal */}
      <FreightTableVersionManager
        open={showVersionManager}
        onOpenChange={setShowVersionManager}
        contractId={contractId}
        currentTableId={freightTableId}
      />

      {/* Footer */}
      <div className="flex justify-end gap-2 pt-4 border-t">
        <Button variant="secondary" onClick={onClose} disabled={isSaving}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Fechar
        </Button>
        {!isEditing && (
          <Button variant="secondary" onClick={() => handleSave(false)} disabled={isSaving}>
            <Save className="h-4 w-4 mr-2" />
            Salvar Rascunho
          </Button>
        )}
        <Button onClick={() => handleSave(true)} disabled={isSaving} className="ml-auto">
          {isSaving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Salvando...
            </>
          ) : (
            <>
              Salvar e Ativar
            </>
          )}
        </Button>
      </div>
    </Modal>
  );
}