import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import { cn } from '@/utils/helpers';
import type { CellEditorProps } from '../types';

interface SelectCellEditorProps extends CellEditorProps {
  column: {
    id: string;
    header: string;
    type: 'select';
    required?: boolean;
    options?: { value: string; label: string }[];
  };
}

export const SelectCellEditor = forwardRef<HTMLSelectElement | null, SelectCellEditorProps>(
  ({ value, onChange, onBlur, onKeyDown, column, autoFocus }, ref) => {
    const selectRef = useRef<HTMLSelectElement>(null);

    useImperativeHandle(ref, () => selectRef.current!, []);

    useEffect(() => {
      if (autoFocus) {
        selectRef.current?.focus();
      }
    }, [autoFocus]);

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange(e.target.value || null);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLSelectElement>) => {
      onKeyDown(e);
      if (e.key === 'Enter') {
        e.stopPropagation();
      }
    };

    return (
      <select
        ref={selectRef}
        value={value ?? ''}
        onChange={handleChange}
        onBlur={onBlur}
        onKeyDown={handleKeyDown}
        className={cn(
          'w-full px-2 py-1 text-sm border border-primary-500 rounded outline-none bg-white',
          column.required && 'bg-primary-50'
        )}
        aria-label={column.header}
      >
        {!column.required && <option value="">Selecione...</option>}
        {column.options?.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    );
  }
);

SelectCellEditor.displayName = 'SelectCellEditor';