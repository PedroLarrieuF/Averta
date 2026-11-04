import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import { cn } from '@/utils/helpers';
import type { CellEditorProps } from '../types';

interface NumberCellEditorProps extends CellEditorProps {
  column: {
    id: string;
    header: string;
    type: 'number';
    required?: boolean;
    min?: number;
    max?: number;
    step?: number;
  };
}

export const NumberCellEditor = forwardRef<HTMLInputElement | null, NumberCellEditorProps>(
  ({ value, onChange, onBlur, onKeyDown, column, autoFocus }, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => inputRef.current!, []);

    useEffect(() => {
      if (autoFocus) {
        inputRef.current?.focus();
        inputRef.current?.select();
      }
    }, [autoFocus]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      if (val === '' || val === '-' || /^-?\d*\.?\d*$/.test(val)) {
        onChange(val === '' ? null : Number(val));
      }
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      const val = e.target.value;
      if (val !== '' && val !== '-') {
        const num = Number(val);
        if (column.min !== undefined && num < column.min) {
          onChange(column.min);
        } else if (column.max !== undefined && num > column.max) {
          onChange(column.max);
        } else {
          onChange(num);
        }
      } else {
        onChange(null);
      }
      onBlur();
    };

    return (
      <input
        ref={inputRef}
        type="number"
        value={value ?? ''}
        onChange={handleChange}
        onBlur={handleBlur}
        onKeyDown={onKeyDown}
        min={column.min}
        max={column.max}
        step={column.step ?? 'any'}
        className={cn(
          'w-full px-2 py-1 text-sm text-right border border-primary-500 rounded outline-none bg-white',
          column.required && 'bg-primary-50'
        )}
        placeholder={column.required ? '0' : ''}
        aria-label={column.header}
        inputMode="numeric"
      />
    );
  }
);

NumberCellEditor.displayName = 'NumberCellEditor';