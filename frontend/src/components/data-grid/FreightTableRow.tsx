import { memo } from 'react';
import { cn } from '@/utils/helpers';
import { FreightTableCell } from './FreightTableCell';
import type { FreightTableColumn, FreightTableRow as FreightTableRowType } from './types';

interface FreightTableRowProps {
  row: FreightTableRowType;
  columns: FreightTableColumn[];
  isSelected: boolean;
  isEditing: boolean;
  editingColumnId: string | null;
  onSelect: (multi?: boolean) => void;
  onStartEdit: (columnId: string) => void;
  onCommitEdit: (value: string | number | boolean | Date | null) => void;
  onCancelEdit: () => void;
  onKeyDown: (e: React.KeyboardEvent, columnId: string) => void;
  rowIndex: number;
}

export const FreightTableRow = memo(function FreightTableRow({
  row,
  columns,
  isSelected,
  isEditing,
  editingColumnId,
  onSelect,
  onStartEdit,
  onCommitEdit,
  onCancelEdit,
  onKeyDown,
  rowIndex,
}: FreightTableRowProps) {
  const handleKeyDown = (e: React.KeyboardEvent, columnId: string) => {
    onKeyDown(e, columnId);
  };

  return (
    <tr
      className={cn(
        'transition-colors',
        isSelected && 'bg-primary-50 border-l-4 border-primary-500',
        row.isNew && 'bg-primary-25',
        row.isDirty && 'border-b-2 border-primary-200'
      )}
      onClick={(e) => {
        if (!(e.target as HTMLElement).closest('input, select, button, [role="button"]')) {
          onSelect(e.shiftKey || e.ctrlKey || e.metaKey);
        }
      }}
      role="row"
      aria-selected={isSelected}
      aria-rowindex={rowIndex + 1}
    >
      {columns.map((column, colIndex) => (
        <FreightTableCell
          key={column.id}
          column={column}
          row={row}
          isEditing={isEditing && editingColumnId === column.id}
          onStartEdit={() => onStartEdit(column.id)}
          onCommitEdit={onCommitEdit}
          onCancelEdit={onCancelEdit}
          onKeyDown={(e) => handleKeyDown(e, column.id)}
          colIndex={colIndex}
        />
      ))}
    </tr>
  );
});

FreightTableRow.displayName = 'FreightTableRow';