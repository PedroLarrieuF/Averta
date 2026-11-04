import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import type {
  FreightTableColumn,
  FreightTableRow,
  FreightTableSnapshot,
  FreightTableState,
  FreightTableActions,
  FreightTableProps,
} from './types';

const generateId = () => Math.random().toString(36).substring(2, 9);

const defaultColumnWidth = 150;
const minColumnWidth = 80;
const maxColumnWidth = 400;

export function useFreightTable(props: FreightTableProps) {
  const {
    columns: initialColumns,
    initialRows,
    onSave,
    onCancel,
    readOnly = false,
    maxRows = 1000,
    autoSave = false,
    autoSaveDelay = 30000,
  } = props;

  // Initialize state from props
  const getInitialColumns = useCallback((): FreightTableColumn[] => {
    return initialColumns.map((col) => ({
      ...col,
      width: col.width ?? defaultColumnWidth,
      minWidth: col.minWidth ?? minColumnWidth,
      maxWidth: col.maxWidth ?? maxColumnWidth,
      pinned: col.pinned ?? false,
      editable: col.editable ?? true,
      required: col.required ?? false,
      align: col.align ?? (col.type === 'number' || col.type === 'currency' ? 'right' : 'left'),
    }));
  }, [initialColumns]);

  const getInitialRows = useCallback((): FreightTableRow[] => {
    return initialRows.map((row) => ({
      ...row,
      id: row.id ?? generateId(),
      isNew: row.isNew ?? false,
      isDirty: row.isDirty ?? false,
      errors: row.errors ?? {},
    }));
  }, [initialRows]);

  const [columns, setColumns] = useState<FreightTableColumn[]>(getInitialColumns);
  const [rows, setRows] = useState<FreightTableRow[]>(getInitialRows);
  const [selection, setSelection] = useState<Set<string>>(new Set());
  const [editingCell, setEditingCell] = useState<{ rowId: string; columnId: string } | null>(null);
  const [history, setHistory] = useState<FreightTableSnapshot[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [columnOrder, setColumnOrder] = useState<string[]>(() => initialColumns.map((c) => c.id));
  const [columnVisibility, setColumnVisibility] = useState<Record<string, boolean>>(
    () => Object.fromEntries(initialColumns.map((c) => [c.id, true]))
  );
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>(
    () => Object.fromEntries(initialColumns.map((c) => [c.id, c.width ?? defaultColumnWidth]))
  );

  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isInitialMount = useRef(true);

  // Persistence functions (defined early for use in auto-save effect)
  const saveDraft = useCallback(() => {
    const draft = { rows, timestamp: Date.now() };
    localStorage.setItem('freight-table-draft', JSON.stringify(draft));
  }, [rows]);

  const loadDraft = useCallback(() => {
    const stored = localStorage.getItem('freight-table-draft');
    if (stored) {
      try {
        const { rows: draftRows } = JSON.parse(stored);
        setRows(draftRows.map((r: FreightTableRow) => ({ ...r, data: { ...r.data } })));
      } catch {
        // Invalid draft
      }
    }
  }, []);

  const clearDraft = useCallback(() => {
    localStorage.removeItem('freight-table-draft');
  }, []);

  // Update derived state when props change
  useEffect(() => {
    if (!isInitialMount.current) {
      setColumns(getInitialColumns());
      setRows(getInitialRows());
      setSelection(new Set());
      setEditingCell(null);
      setHistory([]);
      setHistoryIndex(-1);
    }
    isInitialMount.current = false;
  }, [initialColumns, initialRows, getInitialColumns, getInitialRows]);

  // Persist column widths
  useEffect(() => {
    setColumnWidths((prev) => {
      const updated = { ...prev };
      columns.forEach((col) => {
        if (!(col.id in updated)) {
          updated[col.id] = col.width ?? defaultColumnWidth;
        }
      });
      return updated;
    });
  }, [columns]);

  // Auto-save draft
  useEffect(() => {
    if (autoSave) {
      if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = setTimeout(() => {
        saveDraft();
      }, autoSaveDelay);
      return () => {
        if (autoSaveTimerRef.current) clearTimeout(autoSaveTimerRef.current);
      };
    }
  }, [rows, autoSave, autoSaveDelay, saveDraft]);

  // History management
  const pushHistory = useCallback((newRows: FreightTableRow[]) => {
    setHistory((prev) => {
      const nextIndex = historyIndex + 1;
      const newHistory = prev.slice(0, nextIndex);
      newHistory.push({ rows: newRows.map((r) => ({ ...r, data: { ...r.data } })), timestamp: Date.now() });
      // Limit history to 50 entries
      if (newHistory.length > 50) {
        return newHistory.slice(-50);
      }
      return newHistory;
    });
    setHistoryIndex((prev) => prev + 1);
  }, [historyIndex]);

  const captureSnapshot = useCallback((currentRows: FreightTableRow[]) => {
    pushHistory(currentRows);
  }, [pushHistory]);

  // Row actions
  const addRow = useCallback((initialData?: Record<string, any>) => {
    if (rows.length >= maxRows) return;
    const newRow: FreightTableRow = {
      id: generateId(),
      data: initialData ?? {},
      isNew: true,
      isDirty: true,
      errors: {},
    };
    setRows((prev) => [...prev, newRow]);
  }, [rows.length, maxRows]);

  const duplicateRow = useCallback((rowId: string) => {
    if (rows.length >= maxRows) return;
    setRows((prev) => {
      const index = prev.findIndex((r) => r.id === rowId);
      if (index === -1) return prev;
      const original = prev[index];
      const duplicated: FreightTableRow = {
        id: generateId(),
        data: { ...original.data },
        isNew: true,
        isDirty: true,
        errors: {},
      };
      return [...prev.slice(0, index + 1), duplicated, ...prev.slice(index + 1)];
    });
  }, [rows.length, maxRows]);

  const deleteRow = useCallback((rowId: string) => {
    setRows((prev) => prev.filter((r) => r.id !== rowId));
    setSelection((prev) => {
      const next = new Set(prev);
      next.delete(rowId);
      return next;
    });
  }, []);

  const reorderRows = useCallback((fromIndex: number, toIndex: number) => {
    setRows((prev) => {
      const newRows = [...prev];
      const [removed] = newRows.splice(fromIndex, 1);
      newRows.splice(toIndex, 0, removed);
      return newRows.map((r) => ({ ...r, isDirty: true }));
    });
  }, []);

  // Cell editing
  const startEdit = useCallback((rowId: string, columnId: string) => {
    if (readOnly) return;
    const column = columns.find((c) => c.id === columnId);
    if (!column?.editable) return;
    setEditingCell({ rowId, columnId });
  }, [columns, readOnly]);

  const commitEdit = useCallback(
    (rowId: string, columnId: string, value: any) => {
      setRows((prev) => {
        const newRows = prev.map((row) => {
          if (row.id !== rowId) return row;
          const column = columns.find((c) => c.id === columnId);
          let error: string | null = null;
          if (column?.validate) {
            error = column.validate(value, row);
          } else if (column?.required && (value === '' || value === null || value === undefined)) {
            error = 'Campo obrigatório';
          }
          return {
            ...row,
            data: { ...row.data, [columnId]: value },
            isDirty: true,
            errors: { ...row.errors, [columnId]: error ?? '' },
          };
        });
        captureSnapshot(newRows);
        return newRows;
      });
      setEditingCell(null);
    },
    [columns, captureSnapshot]
  );

  const cancelEdit = useCallback(() => {
    setEditingCell(null);
  }, []);

  // Column actions
  const setColumnWidth = useCallback((columnId: string, width: number) => {
    const column = columns.find((c) => c.id === columnId);
    const clampedWidth = Math.max(column?.minWidth ?? minColumnWidth, Math.min(column?.maxWidth ?? maxColumnWidth, width));
    setColumnWidths((prev) => ({ ...prev, [columnId]: clampedWidth }));
  }, [columns]);

  const reorderColumns = useCallback((fromIndex: number, toIndex: number) => {
    setColumnOrder((prev) => {
      const newOrder = [...prev];
      const [removed] = newOrder.splice(fromIndex, 1);
      newOrder.splice(toIndex, 0, removed);
      return newOrder;
    });
  }, []);

  const toggleColumnVisibility = useCallback((columnId: string) => {
    setColumnVisibility((prev) => ({ ...prev, [columnId]: !prev[columnId] }));
  }, []);

  const pinColumn = useCallback((columnId: string, position: 'left' | 'right' | false) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === columnId ? { ...col, pinned: position } : col
      )
    );
  }, []);

  // History actions
  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const snapshot = history[historyIndex - 1];
      setRows(snapshot.rows.map((r) => ({ ...r, data: { ...r.data } })));
      setHistoryIndex((prev) => prev - 1);
    }
  }, [history, historyIndex]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const snapshot = history[historyIndex + 1];
      setRows(snapshot.rows.map((r) => ({ ...r, data: { ...r.data } })));
      setHistoryIndex((prev) => prev + 1);
    }
  }, [history, historyIndex]);

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  // Selection
  const selectRow = useCallback((rowId: string, multi = false) => {
    setSelection((prev) => {
      const next: Set<string> = multi ? new Set(prev) : new Set();
      if (next.has(rowId)) {
        next.delete(rowId);
      } else {
        next.add(rowId);
      }
      return next;
    });
  }, []);

  const selectAll = useCallback(() => {
    const visibleColumns = columns.filter((c) => columnVisibility[c.id]);
    if (visibleColumns.length === 0) {
      setSelection(new Set());
      return;
    }
    const visibleRowIds = rows.map((r) => r.id);
    setSelection(new Set(visibleRowIds));
  }, [rows, columns, columnVisibility]);

  const clearSelection = useCallback(() => {
    setSelection(new Set());
  }, []);

  // Save action
  const handleSave = useCallback(async () => {
    const rowsToSave = rows.map((r) => ({ ...r, isDirty: false, isNew: false }));
    await onSave(rowsToSave);
    clearDraft();
    setRows(rowsToSave);
    captureSnapshot(rowsToSave);
  }, [rows, onSave, clearDraft, captureSnapshot]);

  const handleCancel = useCallback(() => {
    onCancel?.();
    clearDraft();
  }, [onCancel, clearDraft]);

  // Computed values
  const visibleColumns = useMemo(
    () => columns.filter((c) => columnVisibility[c.id]).sort((a, b) => columnOrder.indexOf(a.id) - columnOrder.indexOf(b.id)),
    [columns, columnVisibility, columnOrder]
  );

  const pinnedLeftColumns = useMemo(
    () => visibleColumns.filter((c) => c.pinned === 'left'),
    [visibleColumns]
  );

  const pinnedRightColumns = useMemo(
    () => visibleColumns.filter((c) => c.pinned === 'right'),
    [visibleColumns]
  );

  const centerColumns = useMemo(
    () => visibleColumns.filter((c) => !c.pinned),
    [visibleColumns]
  );

  const state: FreightTableState = {
    columns,
    rows,
    selection,
    editingCell,
    history,
    historyIndex,
    columnOrder,
    columnVisibility,
    columnWidths,
  };

  const actions: FreightTableActions = {
    addRow,
    duplicateRow,
    deleteRow,
    reorderRows,
    startEdit,
    commitEdit,
    cancelEdit,
    setColumnWidth,
    reorderColumns,
    toggleColumnVisibility,
    pinColumn,
    undo,
    redo,
    canUndo,
    canRedo,
    saveDraft,
    loadDraft,
    clearDraft,
    selectRow,
    selectAll,
    clearSelection,
  };

  return { state, actions, handleSave, handleCancel, visibleColumns, pinnedLeftColumns, pinnedRightColumns, centerColumns };
}