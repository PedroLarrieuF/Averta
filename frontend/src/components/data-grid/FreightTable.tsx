import { useState, useCallback, useEffect, useRef } from 'react';
import { cn } from '@/utils/helpers';
import { useFreightTable } from './useFreightTable';
import { FreightTableHeader } from './FreightTableHeader';
import { FreightTableRow } from './FreightTableRow';
import { FreightTableToolbar } from './FreightTableToolbar';
import type {
  FreightTableProps,
  FreightTableState,
} from './types';

interface FreightTableInternalState extends FreightTableState {
  sortedColumn: string | null;
  sortDirection: 'asc' | 'desc';
}

export function FreightTable({
  columns: initialColumns,
  initialRows,
  onSave,
  onCancel,
  readOnly = false,
  showToolbar = true,
  maxRows = 1000,
  autoSave = false,
  autoSaveDelay = 30000,
  rowKey = 'id',
}: FreightTableProps) {
  const {
    state,
    actions,
    handleSave,
    handleCancel,
    pinnedLeftColumns,
    pinnedRightColumns,
    centerColumns,
  } = useFreightTable({
    columns: initialColumns,
    initialRows,
    onSave,
    onCancel,
    readOnly,
    showToolbar,
    maxRows,
    autoSave,
    autoSaveDelay,
    rowKey,
  });

  // Local UI state - must be declared before useEffect that uses it
  const [sortedColumn, setSortedColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [isSaving, setIsSaving] = useState(false);
  const [hasDraft, setHasDraft] = useState(false);
  const [keyboardNavigation, setKeyboardNavigation] = useState<{ rowIndex: number; colIndex: number } | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  // We need to use useState for rows to allow sorting
  const [localState, setLocalState] = useState<FreightTableInternalState>({
    ...state,
    sortedColumn: null,
    sortDirection: 'asc',
  });

  // Sync with hook state
  useEffect(() => {
    setLocalState((prev) => ({
      ...prev,
      columns: state.columns,
      rows: state.rows,
      selection: state.selection,
      editingCell: state.editingCell,
      history: state.history,
      historyIndex: state.historyIndex,
      columnOrder: state.columnOrder,
      columnVisibility: state.columnVisibility,
      columnWidths: state.columnWidths,
    }));
  }, [state]);

  // Check for draft on mount
  useEffect(() => {
    const stored = localStorage.getItem('freight-table-draft');
    setHasDraft(!!stored);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle keyboard nav when not editing
      if (localState.editingCell) return;

      const visibleCols = [...pinnedLeftColumns, ...centerColumns, ...pinnedRightColumns];
      if (visibleCols.length === 0 || localState.rows.length === 0) return;

      let { rowIndex, colIndex } = keyboardNavigation ?? { rowIndex: 0, colIndex: 0 };

      switch (e.key) {
        case 'ArrowRight':
          e.preventDefault();
          colIndex = Math.min(colIndex + 1, visibleCols.length - 1);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          colIndex = Math.max(colIndex - 1, 0);
          break;
        case 'ArrowDown':
          e.preventDefault();
          rowIndex = Math.min(rowIndex + 1, localState.rows.length - 1);
          break;
        case 'ArrowUp':
          e.preventDefault();
          rowIndex = Math.max(rowIndex - 1, 0);
          break;
        case 'Home':
          e.preventDefault();
          colIndex = 0;
          break;
        case 'End':
          e.preventDefault();
          colIndex = visibleCols.length - 1;
          break;
        case 'PageDown':
          e.preventDefault();
          rowIndex = Math.min(rowIndex + 10, localState.rows.length - 1);
          break;
        case 'PageUp':
          e.preventDefault();
          rowIndex = Math.max(rowIndex - 10, 0);
          break;
        case 'Enter':
        case 'F2': {
          e.preventDefault();
          const col = visibleCols[colIndex];
          if (col?.editable) {
            actions.startEdit(localState.rows[rowIndex].id, col.id);
          }
          break;
        }
        case 'Escape': {
          actions.cancelEdit();
          setKeyboardNavigation(null);
          break;
        }
        case 'Tab': {
          if (e.shiftKey) {
            e.preventDefault();
            colIndex = colIndex > 0 ? colIndex - 1 : visibleCols.length - 1;
            if (colIndex === visibleCols.length - 1) {
              rowIndex = rowIndex > 0 ? rowIndex - 1 : localState.rows.length - 1;
            }
          } else {
            e.preventDefault();
            colIndex = colIndex < visibleCols.length - 1 ? colIndex + 1 : 0;
            if (colIndex === 0) {
              rowIndex = rowIndex < localState.rows.length - 1 ? rowIndex + 1 : 0;
            }
          }
          break;
        }
        case 'Delete':
        case 'Backspace': {
          if (!readOnly && keyboardNavigation) {
            e.preventDefault();
            const row = localState.rows[rowIndex];
            const col = visibleCols[colIndex];
            if (col?.editable) {
              actions.commitEdit(row.id, col.id, col.type === 'boolean' ? false : null);
            }
          }
          break;
        }
        default:
          return;
      }

      setKeyboardNavigation({ rowIndex, colIndex });
      // Scroll into view
      const cellSelector = `[data-row-index="${rowIndex}"][data-col-index="${colIndex}"]`;
      const cell = tableRef.current?.querySelector(cellSelector);
      cell?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    localState.editingCell,
    localState.rows,
    pinnedLeftColumns,
    centerColumns,
    pinnedRightColumns,
    keyboardNavigation,
    actions,
    readOnly,
  ]);

  // Handle sorting
  const handleSort = useCallback((columnId: string) => {
    const column = initialColumns.find((c) => c.id === columnId);
    if (!column) return;

    setSortedColumn((prev) => {
      setSortDirection((prevDir) => (prev === columnId && prevDir === 'asc' ? 'desc' : 'asc'));
      return columnId;
    });

    setLocalState((prev) => {
      const sortedRows = [...prev.rows].sort((a, b) => {
        const aVal = a.data[columnId];
        const bVal = b.data[columnId];
        const direction = sortedColumn === columnId && sortDirection === 'asc' ? -1 : 1;

        if (aVal === null || aVal === undefined) return 1 * direction;
        if (bVal === null || bVal === undefined) return -1 * direction;

        if (column.type === 'number' || column.type === 'currency') {
          return (Number(aVal) - Number(bVal)) * direction;
        }
        if (column.type === 'date') {
          return (new Date(aVal).getTime() - new Date(bVal).getTime()) * direction;
        }
        return String(aVal).localeCompare(String(bVal)) * direction;
      });
      return { ...prev, rows: sortedRows };
    });
  }, [initialColumns, sortedColumn, sortDirection]);

  // Handle cell edit commit
  const handleCommitEdit = useCallback((value: string | number | boolean | Date | null) => {
    if (localState.editingCell) {
      actions.commitEdit(localState.editingCell.rowId, localState.editingCell.columnId, value);
    }
  }, [localState.editingCell, actions]);

  // Handle cell edit start
  const handleStartEdit = useCallback((columnId: string) => {
    if (keyboardNavigation) {
      const row = localState.rows[keyboardNavigation.rowIndex];
      if (row) {
        actions.startEdit(row.id, columnId);
      }
    }
  }, [keyboardNavigation, localState.rows, actions]);

  // Handle cell edit cancel
  const handleCancelEdit = useCallback(() => {
    actions.cancelEdit();
  }, [actions]);

  // Handle key down in cell
  const handleCellKeyDown = useCallback((e: React.KeyboardEvent, columnId: string) => {
    const visibleCols = [...pinnedLeftColumns, ...centerColumns, ...pinnedRightColumns];
    const colIndex = visibleCols.findIndex((c) => c.id === columnId);
    const rowIndex = localState.rows.findIndex((r) => r.id === localState.editingCell?.rowId);

    if (e.key === 'Tab') {
      e.preventDefault();
      if (e.shiftKey) {
        // Previous cell
        let newCol = colIndex - 1;
        let newRow = rowIndex;
        if (newCol < 0) {
          newCol = visibleCols.length - 1;
          newRow = rowIndex > 0 ? rowIndex - 1 : localState.rows.length - 1;
        }
        if (newRow >= 0 && newRow < localState.rows.length) {
          const nextCol = visibleCols[newCol];
          if (nextCol?.editable) {
            actions.startEdit(localState.rows[newRow].id, nextCol.id);
          }
          setKeyboardNavigation({ rowIndex: newRow, colIndex: newCol });
        }
      } else {
        // Next cell
        let newCol = colIndex + 1;
        let newRow = rowIndex;
        if (newCol >= visibleCols.length) {
          newCol = 0;
          newRow = rowIndex < localState.rows.length - 1 ? rowIndex + 1 : 0;
        }
        if (newRow >= 0 && newRow < localState.rows.length) {
          const nextCol = visibleCols[newCol];
          if (nextCol?.editable) {
            actions.startEdit(localState.rows[newRow].id, nextCol.id);
          }
          setKeyboardNavigation({ rowIndex: newRow, colIndex: newCol });
        }
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      actions.cancelEdit();
      // Move to next row same column
      const nextRow = rowIndex < localState.rows.length - 1 ? rowIndex + 1 : 0;
      setKeyboardNavigation({ rowIndex: nextRow, colIndex });
      const nextCol = visibleCols[colIndex];
      if (nextCol?.editable && localState.rows[nextRow]) {
        actions.startEdit(localState.rows[nextRow].id, nextCol.id);
      }
    } else if (e.key === 'Escape') {
      actions.cancelEdit();
      setKeyboardNavigation({ rowIndex, colIndex });
    }
  }, [pinnedLeftColumns, centerColumns, pinnedRightColumns, localState.rows, localState.editingCell, actions]);

  // Handle row selection
  const handleRowSelect = useCallback((multi?: boolean) => {
    if (keyboardNavigation) {
      const row = localState.rows[keyboardNavigation.rowIndex];
      if (row) {
        actions.selectRow(row.id, multi);
      }
    }
  }, [keyboardNavigation, localState.rows, actions]);

  // Save handler
  const handleSaveClick = useCallback(async () => {
    setIsSaving(true);
    try {
      await handleSave();
      setHasDraft(false);
    } finally {
      setIsSaving(false);
    }
  }, [handleSave]);

  // Cancel handler
  const handleCancelClick = useCallback(() => {
    handleCancel();
    setHasDraft(false);
  }, [handleCancel]);

  // Import/Export handlers (placeholders)
  const handleImport = useCallback(() => {
    // TODO: Implement CSV/Excel import
    console.log('Import not implemented yet');
  }, []);

  const handleExport = useCallback(() => {
    // TODO: Implement CSV/Excel export
    console.log('Export not implemented yet');
  }, []);

  const selectedCount = localState.selection.size;

  // Render pinned left section
  const renderPinnedLeft = () => {
    if (pinnedLeftColumns.length === 0) return null;
    const width = pinnedLeftColumns.reduce((sum, c) => sum + (localState.columnWidths[c.id] ?? c.width ?? 150), 0);
    return (
      <div
        className="sticky left-0 z-10 overflow-hidden border-r border-secondary-200 bg-white"
        style={{ width, minWidth: width }}
        aria-hidden="true"
      >
        <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
          <table className="table w-full border-collapse" role="grid">
            <tbody>
              {localState.rows.map((row, rowIndex) => (
                <FreightTableRow
                  key={row.id}
                  row={row}
                  columns={pinnedLeftColumns}
                  isSelected={localState.selection.has(row.id)}
                  isEditing={localState.editingCell?.rowId === row.id}
                  editingColumnId={
                    localState.editingCell?.rowId === row.id ? localState.editingCell.columnId : null
                  }
                  onSelect={handleRowSelect}
                  onStartEdit={handleStartEdit}
                  onCommitEdit={handleCommitEdit}
                  onCancelEdit={handleCancelEdit}
                  onKeyDown={handleCellKeyDown}
                  rowIndex={rowIndex}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // Render center section
  const renderCenter = () => (
    <div className="flex-1 overflow-auto relative" role="grid">
      <table className="table w-full border-collapse min-w-max" role="presentation">
        <tbody>
          {localState.rows.map((row, rowIndex) => (
            <FreightTableRow
              key={row.id}
              row={row}
              columns={centerColumns}
              isSelected={localState.selection.has(row.id)}
              isEditing={localState.editingCell?.rowId === row.id}
              editingColumnId={
                localState.editingCell?.rowId === row.id ? localState.editingCell.columnId : null
              }
              onSelect={handleRowSelect}
              onStartEdit={handleStartEdit}
              onCommitEdit={handleCommitEdit}
              onCancelEdit={handleCancelEdit}
              onKeyDown={handleCellKeyDown}
              rowIndex={rowIndex}
            />
          ))}
        </tbody>
      </table>
      {localState.rows.length === 0 && centerColumns.length > 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-secondary-500 py-12">
          <div className="text-center">
            <p className="font-medium">Nenhum dado</p>
            <p className="text-sm">Clique em "Adicionar" para criar a primeira linha</p>
          </div>
        </div>
      )}
    </div>
  );

  // Render pinned right section
  const renderPinnedRight = () => {
    if (pinnedRightColumns.length === 0) return null;
    const width = pinnedRightColumns.reduce((sum, c) => sum + (localState.columnWidths[c.id] ?? c.width ?? 150), 0);
    return (
      <div
        className="sticky right-0 z-10 overflow-hidden border-l border-secondary-200 bg-white"
        style={{ width, minWidth: width }}
        aria-hidden="true"
      >
        <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
          <table className="table w-full border-collapse" role="grid">
            <tbody>
              {localState.rows.map((row, rowIndex) => (
                <FreightTableRow
                  key={row.id}
                  row={row}
                  columns={pinnedRightColumns}
                  isSelected={localState.selection.has(row.id)}
                  isEditing={localState.editingCell?.rowId === row.id}
                  editingColumnId={
                    localState.editingCell?.rowId === row.id ? localState.editingCell.columnId : null
                  }
                  onSelect={handleRowSelect}
                  onStartEdit={handleStartEdit}
                  onCommitEdit={handleCommitEdit}
                  onCancelEdit={handleCancelEdit}
                  onKeyDown={handleCellKeyDown}
                  rowIndex={rowIndex}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div
      ref={tableRef}
      className={cn('freight-table flex flex-col border border-secondary-200 rounded-lg bg-white', readOnly && 'read-only')}
      role="application"
      aria-label="Editor de Tabela de Frete"
    >
      {/* Toolbar */}
      {showToolbar && (
        <FreightTableToolbar
          actions={actions}
          rowCount={localState.rows.length}
          selectedCount={selectedCount}
          hasDraft={hasDraft}
          isSaving={isSaving}
          readOnly={readOnly}
          onSave={handleSaveClick}
          onCancel={handleCancelClick}
          onImport={handleImport}
          onExport={handleExport}
        />
      )}

      {/* Header */}
      <div className="flex overflow-hidden border-b border-secondary-200 bg-white">
        <FreightTableHeader
          pinnedLeftColumns={pinnedLeftColumns}
          pinnedRightColumns={pinnedRightColumns}
          centerColumns={centerColumns}
          columnWidths={localState.columnWidths}
          onSetColumnWidth={actions.setColumnWidth}
          onReorderColumns={actions.reorderColumns}
          onToggleVisibility={actions.toggleColumnVisibility}
          onPinColumn={actions.pinColumn}
          onSort={handleSort}
          sortedColumn={sortedColumn}
          sortDirection={sortDirection}
          columnVisibility={localState.columnVisibility}
        />
      </div>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden relative" style={{ minHeight: 300 }}>
        {renderPinnedLeft()}
        {renderCenter()}
        {renderPinnedRight()}
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-secondary-200 bg-secondary-50 text-xs text-secondary-500">
        <span>
          {localState.rows.length} linha{localState.rows.length !== 1 ? 's' : ''}
          {localState.rows.some((r) => r.isDirty) && ' • '}
          {localState.rows.filter((r) => r.isDirty).length} alterada{localState.rows.filter((r) => r.isDirty).length !== 1 ? 's' : ''}
          {localState.rows.some((r) => r.isNew) && ' • '}
          {localState.rows.filter((r) => r.isNew).length} nova{localState.rows.filter((r) => r.isNew).length !== 1 ? 's' : ''}
        </span>
        <span>
          {actions.canUndo ? '⌘Z Desfazer' : ''}
          {actions.canUndo && actions.canRedo ? ' • ' : ''}
          {actions.canRedo ? '⌘Y Refazer' : ''}
        </span>
      </div>
    </div>
  );
}

export type { FreightTableProps } from './types';
export type { FreightTableColumn, FreightTableRow } from './types';