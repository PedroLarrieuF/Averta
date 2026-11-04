import { memo } from 'react';
import { cn } from '@/utils/helpers';
import type { FreightTableColumn, FreightTableRow, CellType } from './types';
import { TextCellEditor } from './cell-editors/TextCellEditor';
import { NumberCellEditor } from './cell-editors/NumberCellEditor';
import { CurrencyCellEditor } from './cell-editors/CurrencyCellEditor';
import { SelectCellEditor } from './cell-editors/SelectCellEditor';
import { DateCellEditor } from './cell-editors/DateCellEditor';
import { BooleanCellEditor } from './cell-editors/BooleanCellEditor';

const formatCurrency = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) return '';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) return '';
  return new Intl.NumberFormat('pt-BR').format(value);
};

const formatDate = (value: string | Date | null | undefined): string => {
  if (!value) return '';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleDateString('pt-BR');
};

type CellValue = string | number | boolean | Date | null | undefined;

const formatCellValue = (value: CellValue, type: CellType, customFormat?: (value: CellValue) => string): string => {
  if (customFormat) return customFormat(value);
  if (value === null || value === undefined || value === '') return '';
  switch (type) {
    case 'currency':
      return formatCurrency(typeof value === 'number' ? value : Number(value));
    case 'number':
      return formatNumber(typeof value === 'number' ? value : Number(value));
    case 'date':
      return formatDate(value as string | Date);
    case 'boolean':
      return value ? 'Sim' : 'Não';
    default:
      return String(value);
  }
};

interface FreightTableCellProps {
  column: FreightTableColumn;
  row: FreightTableRow;
  isEditing: boolean;
  onStartEdit: () => void;
  onCommitEdit: (value: string | number | boolean | Date | null) => void;
  onCancelEdit: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  colIndex: number;
}

export const FreightTableCell = memo(function FreightTableCell({
  column,
  row,
  isEditing,
  onStartEdit,
  onCommitEdit,
  onCancelEdit,
  onKeyDown,
  colIndex,
}: FreightTableCellProps) {
  const value = row.data[column.id];
  const error = row.errors?.[column.id];

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancelEdit();
      return;
    }
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      return;
    }
    if (e.key === 'Tab') {
      return;
    }
    onKeyDown(e);
  };

  const handleDoubleClick = () => {
    if (column.editable) {
      onStartEdit();
    }
  };

  const renderEditor = () => {
    const baseProps = {
      value,
      onChange: onCommitEdit,
      onBlur: onCancelEdit,
      onKeyDown: handleKeyDown,
      row,
      autoFocus: true,
    };

    switch (column.type) {
      case 'text': {
        const col = { ...column, type: 'text' as const };
        return <TextCellEditor {...baseProps} column={col} />;
      }
      case 'number': {
        const col = { ...column, type: 'number' as const };
        return <NumberCellEditor {...baseProps} column={col} />;
      }
      case 'currency': {
        const col = { ...column, type: 'currency' as const };
        return <CurrencyCellEditor {...baseProps} column={col} />;
      }
      case 'select': {
        const col = { ...column, type: 'select' as const };
        return <SelectCellEditor {...baseProps} column={col} />;
      }
      case 'date': {
        const col = { ...column, type: 'date' as const };
        return <DateCellEditor {...baseProps} column={col} />;
      }
      case 'boolean': {
        const col = { ...column, type: 'boolean' as const };
        return <BooleanCellEditor {...baseProps} column={col} />;
      }
      default: {
        const col = { ...column, type: 'text' as const };
        return <TextCellEditor {...baseProps} column={col} />;
      }
    }
  };

  if (isEditing && column.editable) {
    return (
      <td className="relative p-0" tabIndex={-1}>
        {renderEditor()}
        {error && (
          <div className="absolute bottom-full left-0 right-0 mb-1 px-1 text-xs text-danger-600 bg-danger-50 border border-danger-200 rounded shadow z-10">
            {error}
          </div>
        )}
      </td>
    );
  }

  return (
    <td
      className={cn(
        'px-3 py-2 text-sm border-r border-secondary-100',
        column.align === 'right' && 'text-right',
        column.align === 'center' && 'text-center',
        error && 'text-danger-600 bg-danger-50',
        row.isNew && 'bg-primary-50',
        column.pinned === 'left' && 'bg-white sticky left-0 z-10 shadow-sm',
        column.pinned === 'right' && 'bg-white sticky right-0 z-10 shadow-sm'
      )}
      style={{ width: column.width, minWidth: column.minWidth, maxWidth: column.maxWidth }}
      onDoubleClick={handleDoubleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === 'F2') {
          e.preventDefault();
          if (column.editable) onStartEdit();
        } else if (e.key === 'ArrowRight' || e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
          onKeyDown(e);
        }
      }}
      tabIndex={0}
      role="gridcell"
      aria-colindex={colIndex + 1}
      aria-invalid={!!error}
      aria-describedby={error ? `${column.id}-error` : undefined}
    >
      {column.render ? column.render(value, row) : formatCellValue(value, column.type, column.format)}
      {error && <span id={`${column.id}-error`} className="sr-only">{error}</span>}
    </td>
  );
});

FreightTableCell.displayName = 'FreightTableCell';