import { memo } from 'react';
import { Button } from '@/components/Button';
import { Plus, Copy, Trash2, RotateCcw, RotateCw, Download, Upload, Save, X, FileText } from 'lucide-react';
import type { FreightTableActions } from './types';

interface FreightTableToolbarProps {
  actions: FreightTableActions;
  rowCount: number;
  selectedCount: number;
  hasDraft: boolean;
  isSaving?: boolean;
  readOnly?: boolean;
  onSave: () => void;
  onCancel: () => void;
  onImport?: () => void;
  onExport?: () => void;
}

export const FreightTableToolbar = memo(function FreightTableToolbar({
  actions,
  rowCount,
  selectedCount,
  hasDraft,
  isSaving = false,
  readOnly = false,
  onSave,
  onCancel,
  onImport,
  onExport,
}: FreightTableToolbarProps) {
  if (readOnly) return null;

  return (
    <div className="flex flex-wrap items-center gap-3 p-4 border-b border-secondary-200 bg-secondary-50">
      {/* Row count & selection */}
      <div className="flex items-center gap-4 text-sm text-secondary-600">
        <span>{rowCount} linha{rowCount !== 1 ? 's' : ''}</span>
        {selectedCount > 0 && (
          <span className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full">
            {selectedCount} selecionada{selectedCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      <div className="flex-1" />

      {/* Row actions */}
      {!readOnly && (
        <div className="flex items-center gap-2" role="group" aria-label="Ações de linha">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => actions.addRow()}
            disabled={!actions.canUndo && !actions.canRedo}
            aria-label="Adicionar linha"
          >
            <Plus className="h-4 w-4 mr-1" />
            Adicionar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              // Duplicate selected row (first selected)
              // This would need selection integration
            }}
            disabled={selectedCount === 0}
            aria-label="Duplicar linha selecionada"
          >
            <Copy className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-danger-600 hover:bg-danger-50"
            onClick={() => {
              // Delete selected rows
            }}
            disabled={selectedCount === 0}
            aria-label="Excluir linhas selecionadas"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* History actions */}
      <div className="flex items-center gap-1 border-x border-secondary-200 px-3" role="group" aria-label="Histórico">
        <Button
          variant="ghost"
          size="sm"
          onClick={actions.undo}
          disabled={!actions.canUndo}
          aria-label="Desfazer (Ctrl+Z)"
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={actions.redo}
          disabled={!actions.canRedo}
          aria-label="Refazer (Ctrl+Y)"
        >
          <RotateCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Import/Export */}
      {(onImport || onExport) && (
        <div className="flex items-center gap-1 border-x border-secondary-200 px-3" role="group" aria-label="Importar/Exportar">
          {onImport && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onImport}
              aria-label="Importar CSV/Excel"
            >
              <Upload className="h-4 w-4 mr-1" />
              Importar
            </Button>
          )}
          {onExport && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onExport}
              aria-label="Exportar CSV/Excel"
            >
              <Download className="h-4 w-4 mr-1" />
              Exportar
            </Button>
          )}
        </div>
      )}

      {/* Draft indicator */}
      {hasDraft && (
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-warning-50 border border-warning-200">
          <span className="text-xs text-warning-700 flex items-center gap-1">
            <FileText className="h-3 w-3" />
            Rascunho salvo
          </span>
        </div>
      )}

      {/* Save/Cancel */}
      <div className="flex items-center gap-2 border-x border-secondary-200 px-3" role="group" aria-label="Salvar/Cancelar">
        <Button variant="secondary" size="sm" onClick={onCancel} disabled={isSaving}>
          <X className="h-4 w-4 mr-1" />
          Cancelar
        </Button>
        <Button variant="primary" size="sm" onClick={onSave} loading={isSaving} disabled={isSaving}>
          <Save className="h-4 w-4 mr-1" />
          Salvar
        </Button>
      </div>
    </div>
  );
});

FreightTableToolbar.displayName = 'FreightTableToolbar';