export type CellType = 'text' | 'number' | 'currency' | 'select' | 'date' | 'boolean';

export interface FreightTableColumn {
  id: string;
  header: string;
  type: CellType;
  width?: number;
  minWidth?: number;
  maxWidth?: number;
  pinned?: 'left' | 'right' | false;
  editable?: boolean;
  required?: boolean;
  options?: { value: string; label: string }[]; // for select type
  format?: (value: any) => string; // custom formatter
  validate?: (value: any, row?: FreightTableRow) => string | null; // return error message
  render?: (value: any, row: FreightTableRow) => React.ReactNode; // custom cell render
  align?: 'left' | 'center' | 'right';
}

export interface FreightTableRow {
  id: string;
  data: Record<string, any>;
  isNew?: boolean;
  isDirty?: boolean;
  errors?: Record<string, string>;
}

export interface FreightTableSnapshot {
  rows: FreightTableRow[];
  timestamp: number;
}

export interface FreightTableState {
  columns: FreightTableColumn[];
  rows: FreightTableRow[];
  selection: Set<string>;
  editingCell: { rowId: string; columnId: string } | null;
  history: FreightTableSnapshot[];
  historyIndex: number;
  columnOrder: string[];
  columnVisibility: Record<string, boolean>;
  columnWidths: Record<string, number>;
}

export interface FreightTableActions {
  // Row actions
  addRow: (initialData?: Record<string, any>) => void;
  duplicateRow: (rowId: string) => void;
  deleteRow: (rowId: string) => void;
  reorderRows: (fromIndex: number, toIndex: number) => void;
  // Cell actions
  startEdit: (rowId: string, columnId: string) => void;
  commitEdit: (rowId: string, columnId: string, value: any) => void;
  cancelEdit: () => void;
  // Column actions
  setColumnWidth: (columnId: string, width: number) => void;
  reorderColumns: (fromIndex: number, toIndex: number) => void;
  toggleColumnVisibility: (columnId: string) => void;
  pinColumn: (columnId: string, position: 'left' | 'right' | false) => void;
  // History
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  // Persistence
  saveDraft: () => void;
  loadDraft: () => void;
  clearDraft: () => void;
  // Selection
  selectRow: (rowId: string, multi?: boolean) => void;
  selectAll: () => void;
  clearSelection: () => void;
}

export interface FreightTableProps {
  columns: FreightTableColumn[];
  initialRows: FreightTableRow[];
  onSave: (rows: FreightTableRow[]) => Promise<void>;
  onCancel?: () => void;
  readOnly?: boolean;
  showToolbar?: boolean;
  maxRows?: number;
  autoSave?: boolean;
  autoSaveDelay?: number;
  rowKey?: keyof FreightTableRow | ((row: FreightTableRow) => string);
}

export interface CellEditorProps {
  value: any;
  onChange: (value: any) => void;
  onBlur: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  column: FreightTableColumn;
  row: FreightTableRow;
  autoFocus?: boolean;
}