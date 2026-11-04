import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import { cn } from '@/utils/helpers';
import type { CellEditorProps } from '../types';

interface CurrencyCellEditorProps extends CellEditorProps {
  column: {
    id: string;
    header: string;
    type: 'currency';
    required?: boolean;
    min?: number;
    max?: number;
    step?: number;
  };
}

const formatBRL = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) return '';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const parseBRL = (value: string): number | null => {
  if (!value) return null;
  const cleaned = value.replace(/[R$\s]/g, '').replace('.', '').replace(',', '.');
  const num = parseFloat(cleaned);
  return isNaN(num) ? null : num;
};

export const CurrencyCellEditor = forwardRef<HTMLInputElement | null, CurrencyCellEditorProps>(
  ({ value, onChange, onBlur, onKeyDown, column, autoFocus }, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [displayValue, setDisplayValue] = useState(() => formatBRL(value as number));

    useImperativeHandle(ref, () => inputRef.current!, []);

    useEffect(() => {
      setDisplayValue(formatBRL(value as number));
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
      if (val === '' || /^[R$\s]?\d*[.,]?\d*$/.test(val)) {
        onChange(parseBRL(val));
      }
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      const val = e.target.value;
      const parsed = parseBRL(val);
      if (parsed !== null) {
        if (column.min !== undefined && parsed < column.min) {
          onChange(column.min);
          setDisplayValue(formatBRL(column.min));
        } else if (column.max !== undefined && parsed > column.max) {
          onChange(column.max);
          setDisplayValue(formatBRL(column.max));
        } else {
          onChange(parsed);
          setDisplayValue(formatBRL(parsed));
        }
      } else {
        onChange(null);
        setDisplayValue('');
      }
      onBlur();
    };

    return (
      <div className="relative">
        <span className="absolute left-2 top-1/2 -translate-y-1/2 text-secondary-500 text-sm pointer-events-none">
          R$
        </span>
        <input
          ref={inputRef}
          type="text"
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onKeyDown={onKeyDown}
          className={cn(
            'w-full pl-6 pr-2 py-1 text-sm text-right border border-primary-500 rounded outline-none bg-white',
            column.required && 'bg-primary-50'
          )}
          placeholder={column.required ? '0,00' : ''}
          aria-label={column.header}
          inputMode="decimal"
          autoComplete="off"
        />
      </div>
    );
  }
);

CurrencyCellEditor.displayName = 'CurrencyCellEditor';