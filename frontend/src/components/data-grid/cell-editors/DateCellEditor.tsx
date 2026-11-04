import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import { cn } from '@/utils/helpers';
import type { CellEditorProps } from '../types';

interface DateCellEditorProps extends CellEditorProps {
  column: {
    id: string;
    header: string;
    type: 'date';
    required?: boolean;
  };
}

const formatDateForInput = (date: string | Date | null | undefined): string => {
  if (!date) return '';
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  return d.toISOString().split('T')[0];
};

const parseDateInput = (value: string): string | null => {
  if (!value) return null;
  const d = new Date(value + 'T00:00:00');
  if (isNaN(d.getTime())) return null;
  return d.toISOString().split('T')[0];
};

export const DateCellEditor = forwardRef<HTMLInputElement | null, DateCellEditorProps>(
  ({ value, onChange, onBlur, onKeyDown, column, autoFocus }, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [displayValue, setDisplayValue] = useState(() => formatDateForInput(value));

    useImperativeHandle(ref, () => inputRef.current!, []);

    useEffect(() => {
      setDisplayValue(formatDateForInput(value));
    }, [value]);

    useEffect(() => {
      if (autoFocus) {
        inputRef.current?.focus();
        inputRef.current?.select();
      }
    }, [autoFocus]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setDisplayValue(val);
      onChange(parseDateInput(val));
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      const val = e.target.value;
      const parsed = parseDateInput(val);
      onChange(parsed);
      if (parsed) {
        setDisplayValue(parsed);
      }
      onBlur();
    };

    return (
      <input
        ref={inputRef}
        type="date"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        onKeyDown={onKeyDown}
        className={cn(
          'w-full px-2 py-1 text-sm border border-primary-500 rounded outline-none bg-white',
          column.required && 'bg-primary-50'
        )}
        aria-label={column.header}
      />
    );
  }
);

DateCellEditor.displayName = 'DateCellEditor';