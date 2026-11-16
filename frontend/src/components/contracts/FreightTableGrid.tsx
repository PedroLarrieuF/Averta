// Freight Table Grid Component
// Card #24: Contracts Page - CRUD + FreightTable Editor
// Spreadsheet-like editable grid for freight rates

import { useMemo, useCallback, Fragment } from 'react';
import { Plus, Trash2, Copy, Edit2 } from 'lucide-react';
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '../index';
import { BRAZILIAN_STATES } from '../../types/contracts';

export interface FreightRateRow {
  id: string;
  modal: 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';
  weightMin: number | null;
  weightMax: number | null;
  cubageMin: number | null;
  cubageMax: number | null;
  distanceMin: number | null;
  distanceMax: number | null;
  ufOrigin: string | null;
  ufDest: string | null;
  ratePerKg: number | null;
  ratePerM3: number | null;
  ratePerKm: number | null;
  minimumValue: number | null;
}

interface FreightTableGridProps {
  modal: 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';
  rates: FreightRateRow[];
  onRateChange: (index: number, field: keyof FreightRateRow, value: any) => void;
  onAddRate: () => void;
  onRemoveRate: (rateId: string) => void;
  onDuplicateRate: (rateId: string) => void;
  onCopyToModal: (targetModal: 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO') => void;
  availableModals: ('RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO')[];
  isReadOnly?: boolean;
}

const MODAL_LABELS: Record<string, string> = {
  RODOVIARIO: 'Rodoviário',
  AEREO: 'Aéreo',
  MARITIMO: 'Marítimo',
  FERROVIARIO: 'Ferroviário',
};

const MODAL_FIELDS: Record<string, { key: keyof FreightRateRow; label: string; type: 'number' | 'select' | 'text'; step?: number; placeholder?: string; options?: { value: string; label: string }[] }[]> = {
  RODOVIARIO: [
    { key: 'ufOrigin', label: 'UF Origem', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'ufDest', label: 'UF Destino', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'weightMin', label: 'Peso Mín (kg)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'weightMax', label: 'Peso Máx (kg)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'cubageMin', label: 'Cubagem Mín (m³)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'cubageMax', label: 'Cubagem Máx (m³)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'ratePerKg', label: 'R$/kg', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'ratePerM3', label: 'R$/m³', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'minimumValue', label: 'Valor Mínimo', type: 'number', step: 0.01, placeholder: '0.00' },
  ],
  AEREO: [
    { key: 'ufOrigin', label: 'UF Origem', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'ufDest', label: 'UF Destino', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'weightMin', label: 'Peso Mín (kg)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'weightMax', label: 'Peso Máx (kg)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'cubageMin', label: 'Cubagem Mín (m³)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'cubageMax', label: 'Cubagem Máx (m³)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'ratePerKg', label: 'R$/kg', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'ratePerM3', label: 'R$/m³', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'minimumValue', label: 'Valor Mínimo', type: 'number', step: 0.01, placeholder: '0.00' },
  ],
  MARITIMO: [
    { key: 'ufOrigin', label: 'UF Origem', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'ufDest', label: 'UF Destino', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'weightMin', label: 'Peso Mín (kg)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'weightMax', label: 'Peso Máx (kg)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'cubageMin', label: 'Cubagem Mín (m³)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'cubageMax', label: 'Cubagem Máx (m³)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'ratePerKg', label: 'R$/kg', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'ratePerM3', label: 'R$/m³', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'minimumValue', label: 'Valor Mínimo', type: 'number', step: 0.01, placeholder: '0.00' },
  ],
  FERROVIARIO: [
    { key: 'ufOrigin', label: 'UF Origem', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'ufDest', label: 'UF Destino', type: 'select', options: BRAZILIAN_STATES.map((s) => ({ value: s, label: s })) },
    { key: 'distanceMin', label: 'Dist Mín (km)', type: 'number', step: 1, placeholder: '0' },
    { key: 'distanceMax', label: 'Dist Máx (km)', type: 'number', step: 1, placeholder: '∞' },
    { key: 'weightMin', label: 'Peso Mín (ton)', type: 'number', step: 0.01, placeholder: '0' },
    { key: 'weightMax', label: 'Peso Máx (ton)', type: 'number', step: 0.01, placeholder: '∞' },
    { key: 'ratePerKm', label: 'R$/km', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'ratePerKg', label: 'R$/ton', type: 'number', step: 0.01, placeholder: '0.00' },
    { key: 'minimumValue', label: 'Valor Mínimo', type: 'number', step: 0.01, placeholder: '0.00' },
  ],
};

export function FreightTableGrid({
  modal,
  rates,
  onRateChange,
  onAddRate,
  onRemoveRate,
  onDuplicateRate,
  onCopyToModal,
  availableModals,
  isReadOnly = false,
}: FreightTableGridProps) {
  const fields = useMemo(() => MODAL_FIELDS[modal] || [], [modal]);

  const handleInputChange = useCallback(
    (rateId: string, field: keyof FreightRateRow, value: any) => {
      const index = rates.findIndex((r) => r.id === rateId);
      if (index >= 0) {
        const numValue = value === '' ? null : value;
        onRateChange(index, field, numValue);
      }
    },
    [rates, onRateChange]
  );

  const handleSelectChange = useCallback(
    (rateId: string, field: keyof FreightRateRow, value: string) => {
      const index = rates.findIndex((r) => r.id === rateId);
      if (index >= 0) {
        onRateChange(index, field, value || null);
      }
    },
    [rates, onRateChange]
  );

  if (rates.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-secondary-500 mb-4">
          Nenhuma taxa cadastrada para <strong>{MODAL_LABELS[modal]}</strong>
        </p>
        <Button onClick={onAddRate} disabled={isReadOnly}>
          <Plus className="h-4 w-4 mr-2" />
          Adicionar Primeira Taxa
        </Button>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-secondary-200 bg-secondary-50">
            <th className="w-10 text-center p-2">#</th>
            {fields.map((field) => (
              <th key={field.key} className="p-2 text-left font-medium text-secondary-700 whitespace-nowrap">
                {field.label}
              </th>
            ))}
            <th className="w-36 text-center p-2 font-medium text-secondary-700">Ações</th>
          </tr>
        </thead>
        <tbody>
          {rates.map((rate, rowIndex) => (
            <Fragment key={rate.id}>
              <tr className="border-b border-secondary-100 hover:bg-secondary-50">
                <td className="p-2 text-center text-secondary-500 font-mono">
                  {rowIndex + 1}
                </td>
                {fields.map((field) => (
                  <td key={field.key} className="p-1.5">
                    {field.type === 'select' ? (
                      <Select
                        value={rate[field.key] as string}
                        onValueChange={(v) => handleSelectChange(rate.id, field.key, v)}
                        disabled={isReadOnly}
                      >
                        <SelectTrigger className="h-8 w-full">
                          <SelectValue placeholder={field.placeholder || '—'} />
                        </SelectTrigger>
                        <SelectContent>
                          {field.options?.map((opt) => (
                            <SelectItem key={opt.value} value={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <Input
                        type="number"
                        step={field.step || 'any'}
                        placeholder={field.placeholder}
                        value={rate[field.key] ?? ''}
                        onChange={(e) =>
                          handleInputChange(
                            rate.id,
                            field.key,
                            e.target.value === '' ? null : parseFloat(e.target.value)
                          )
                        }
                        disabled={isReadOnly}
                        className="h-8 text-sm"
                      />
                    )}
                  </td>
                ))}
                <td className="p-1.5 text-center">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" disabled={isReadOnly}>
                        <Edit2 className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onDuplicateRate(rate.id)} disabled={isReadOnly}>
                        <Copy className="h-4 w-4" />
                        Duplicar
                      </DropdownMenuItem>
                      {availableModals.length > 0 && (
                        <>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>
                            Copiar para...
                          </DropdownMenuItem>
                          {availableModals.map((targetModal) => (
                            <DropdownMenuItem
                              key={targetModal}
                              onClick={() => onCopyToModal(targetModal)}
                              disabled={isReadOnly}
                            >
                              {MODAL_LABELS[targetModal]}
                            </DropdownMenuItem>
                          ))}
                        </>
                      )}
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => onRemoveRate(rate.id)}
                        className="text-danger-600 focus:text-danger-600"
                        disabled={isReadOnly}
                      >
                        <Trash2 className="h-4 w-4" />
                        Excluir
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
              </tr>
            </Fragment>
          ))}
        </tbody>
      </table>

      <div className="mt-3 flex justify-end">
        <Button variant="secondary" size="sm" onClick={onAddRate} disabled={isReadOnly}>
          <Plus className="h-4 w-4 mr-2" />
          Adicionar Taxa
        </Button>
      </div>
    </div>
  );
}