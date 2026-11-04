import { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/utils/helpers';
import { ChevronUp, ChevronDown, Columns, Filter, GripVertical, Lock, Unlock } from 'lucide-react';
import type { FreightTableColumn } from './types';

interface FreightTableHeaderProps {
  pinnedLeftColumns: FreightTableColumn[];
  pinnedRightColumns: FreightTableColumn[];
  centerColumns: FreightTableColumn[];
  columnWidths: Record<string, number>;
  onSetColumnWidth: (columnId: string, width: number) => void;
  onReorderColumns: (fromIndex: number, toIndex: number) => void;
  onToggleVisibility: (columnId: string) => void;
  onPinColumn: (columnId: string, position: 'left' | 'right' | false) => void;
  onSort: (columnId: string) => void;
  sortedColumn: string | null;
  sortDirection: 'asc' | 'desc';
  columnVisibility: Record<string, boolean>;
  showColumnMenu?: boolean;
}

export function FreightTableHeader({
  pinnedLeftColumns,
  pinnedRightColumns,
  centerColumns,
  columnWidths,
  onSetColumnWidth,
  onReorderColumns,
  onToggleVisibility,
  onPinColumn,
  onSort,
  sortedColumn,
  sortDirection,
  columnVisibility,
  showColumnMenu = true,
}: FreightTableHeaderProps) {
  const [resizingColumn, setResizingColumn] = useState<string | null>(null);
  const [resizeStartX, setResizeStartX] = useState(0);
  const [resizeStartWidth, setResizeStartWidth] = useState(0);
  const [draggingColumn, setDraggingColumn] = useState<string | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null);
  const columnRefs = useRef<Record<string, HTMLTableHeaderCellElement>>({});
  const [columnMenuOpen, setColumnMenuOpen] = useState<string | null>(null);

  const handleMouseDown = (e: React.MouseEvent, column: FreightTableColumn) => {
    if ((e.target as HTMLElement).closest('.resize-handle')) {
      e.preventDefault();
      e.stopPropagation();
      setResizingColumn(column.id);
      setResizeStartX(e.clientX);
      setResizeStartWidth(columnWidths[column.id] ?? column.width ?? 150);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (resizingColumn) {
      const delta = e.clientX - resizeStartX;
      const newWidth = Math.max(80, resizeStartWidth + delta);
      onSetColumnWidth(resizingColumn, newWidth);
    }
  }, [resizingColumn, resizeStartX, resizeStartWidth, onSetColumnWidth]);

  const handleMouseUp = useCallback(() => {
    if (resizingColumn) {
      setResizingColumn(null);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }
  }, [resizingColumn]);

  useEffect(() => {
    if (resizingColumn) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [resizingColumn, handleMouseMove, handleMouseUp]);

  const handleDragStart = (e: React.DragEvent, column: FreightTableColumn) => {
    if (!column.editable) return;
    setDraggingColumn(column.id);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', column.id);
  };

  const handleDragOver = (e: React.DragEvent, column: FreightTableColumn) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (draggingColumn && draggingColumn !== column.id) {
      setDragOverColumn(column.id);
    }
  };

  const handleDragLeave = () => {
    setDragOverColumn(null);
  };

  const handleDrop = (e: React.DragEvent, targetColumn: FreightTableColumn) => {
    e.preventDefault();
    const draggedId = e.dataTransfer.getData('text/plain');
    if (!draggedId || draggedId === targetColumn.id) {
      setDraggingColumn(null);
      setDragOverColumn(null);
      return;
    }

    const allColumns = [...pinnedLeftColumns, ...centerColumns, ...pinnedRightColumns];
    const fromIndex = allColumns.findIndex((c) => c.id === draggedId);
    const toIndex = allColumns.findIndex((c) => c.id === targetColumn.id);

    if (fromIndex !== -1 && toIndex !== -1) {
      onReorderColumns(fromIndex, toIndex);
    }

    setDraggingColumn(null);
    setDragOverColumn(null);
  };

  const handleDragEnd = () => {
    setDraggingColumn(null);
    setDragOverColumn(null);
  };

  const renderHeaderCell = (column: FreightTableColumn) => {
    const isSorted = sortedColumn === column.id;
    const width = columnWidths[column.id] ?? column.width ?? 150;
    const isPinnedLeft = column.pinned === 'left';
    const isPinnedRight = column.pinned === 'right';
    const isDragging = draggingColumn === column.id;
    const isDragOver = dragOverColumn === column.id;

    return (
      <th
        ref={(el) => { columnRefs.current[column.id] = el!; }}
        key={column.id}
        className={cn(
          'relative px-3 py-2 text-xs font-semibold text-secondary-600 uppercase tracking-wider border-b-2 border-secondary-200 bg-white',
          'cursor-pointer select-none transition-colors',
          isSorted && 'bg-primary-50 text-primary-700',
          isPinnedLeft && 'sticky left-0 z-20 shadow-sm',
          isPinnedRight && 'sticky right-0 z-20 shadow-sm',
          isDragging && 'opacity-50',
          isDragOver && 'bg-primary-100'
        )}
        style={{ width, minWidth: column.minWidth, maxWidth: column.maxWidth }}
        onClick={() => onSort(column.id)}
        onMouseDown={(e) => handleMouseDown(e, column)}
        draggable={column.editable}
        onDragStart={(e) => handleDragStart(e, column)}
        onDragOver={(e) => handleDragOver(e, column)}
        onDragLeave={handleDragLeave}
        onDrop={(e) => handleDrop(e, column)}
        onDragEnd={handleDragEnd}
        role="columnheader"
        aria-sort={isSorted ? (sortDirection === 'asc' ? 'ascending' : 'descending') : 'none'}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSort(column.id);
          }
        }}
      >
        <div className="flex items-center gap-2">
          {column.editable && (
            <button
              className="p-1 rounded hover:bg-secondary-100 text-secondary-400 hover:text-secondary-600"
              onClick={(e) => { e.stopPropagation(); }}
              aria-label="Arrastar para reordenar"
              tabIndex={-1}
            >
              <GripVertical className="h-4 w-4" />
            </button>
          )}
          <span className="flex-1 truncate">{column.header}</span>
          {isSorted && (
            <span className="flex items-center">
              {sortDirection === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </span>
          )}
          {showColumnMenu && (
            <div className="relative">
              <button
                className="p-1 rounded hover:bg-secondary-100 text-secondary-400 hover:text-secondary-600"
                onClick={(e) => {
                  e.stopPropagation();
                  setColumnMenuOpen(columnMenuOpen === column.id ? null : column.id);
                }}
                aria-label="Opções da coluna"
                tabIndex={-1}
              >
                <Columns className="h-4 w-4" />
              </button>
              {columnMenuOpen === column.id && (
                <>
                  <button
                    className="fixed inset-0 z-40"
                    onClick={() => setColumnMenuOpen(null)}
                    onKeyDown={(e) => { if (e.key === 'Escape') setColumnMenuOpen(null); }}
                    aria-label="Fechar menu da coluna"
                    tabIndex={-1}
                  />
                  <div className="absolute right-0 top-full z-50 mt-1 min-w-[180px] rounded-lg border border-secondary-200 bg-white shadow-lg py-1">
                    <button
                      className={cn(
                        'w-full px-3 py-2 text-left text-sm text-secondary-700 hover:bg-secondary-50 flex items-center gap-2',
                        !columnVisibility[column.id] && 'opacity-50'
                      )}
                      onClick={(e) => { e.stopPropagation(); onToggleVisibility(column.id); setColumnMenuOpen(null); }}
                    >
                      <Filter className="h-4 w-4" />
                      {columnVisibility[column.id] ? 'Ocultar coluna' : 'Mostrar coluna'}
                    </button>
                    <div className="border-t border-secondary-100 my-1" />
                    <button
                      className="w-full px-3 py-2 text-left text-sm text-secondary-700 hover:bg-secondary-50 flex items-center gap-2"
                      onClick={(e) => { e.stopPropagation(); onPinColumn(column.id, 'left'); setColumnMenuOpen(null); }}
                      disabled={isPinnedLeft}
                    >
                      <Lock className={cn('h-4 w-4', isPinnedLeft ? 'text-primary-600' : 'text-secondary-400')} />
                      Fixar à esquerda
                    </button>
                    <button
                      className="w-full px-3 py-2 text-left text-sm text-secondary-700 hover:bg-secondary-50 flex items-center gap-2"
                      onClick={(e) => { e.stopPropagation(); onPinColumn(column.id, 'right'); setColumnMenuOpen(null); }}
                      disabled={isPinnedRight}
                    >
                      <Lock className={cn('h-4 w-4', isPinnedRight ? 'text-primary-600' : 'text-secondary-400')} />
                      Fixar à direita
                    </button>
                    <button
                      className="w-full px-3 py-2 text-left text-sm text-secondary-700 hover:bg-secondary-50 flex items-center gap-2"
                      onClick={(e) => { e.stopPropagation(); onPinColumn(column.id, false); setColumnMenuOpen(null); }}
                      disabled={!isPinnedLeft && !isPinnedRight}
                    >
                      <Unlock className="h-4 w-4" />
                      Desfixar
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
          <button
            className="resize-handle absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-primary-500"
            aria-label="Redimensionar coluna"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                // Could add keyboard resize handling here if needed
              }
            }}
          />
        </div>
      </th>
    );
  };

  return (
    <>
      {/* Pinned Left Headers */}
      <div className="sticky left-0 z-20" style={{ width: pinnedLeftColumns.reduce((sum, c) => sum + (columnWidths[c.id] ?? c.width ?? 150), 0) }}>
        <table className="table w-full border-collapse">
          <thead>
            <tr>
              {pinnedLeftColumns.map((col) => renderHeaderCell(col))}
            </tr>
          </thead>
        </table>
      </div>

      {/* Center Headers */}
      <div className="overflow-x-auto flex-1">
        <table className="table w-full border-collapse min-w-max">
          <thead>
            <tr>
              {centerColumns.map((col) => renderHeaderCell(col))}
            </tr>
          </thead>
        </table>
      </div>

      {/* Pinned Right Headers */}
      <div className="sticky right-0 z-20" style={{ width: pinnedRightColumns.reduce((sum, c) => sum + (columnWidths[c.id] ?? c.width ?? 150), 0) }}>
        <table className="table w-full border-collapse">
          <thead>
            <tr>
              {pinnedRightColumns.map((col) => renderHeaderCell(col))}
            </tr>
          </thead>
        </table>
      </div>
    </>
  );
}