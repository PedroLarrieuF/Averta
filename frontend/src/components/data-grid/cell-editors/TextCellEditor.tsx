import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import { cn } from '@/utils/helpers';
import type { CellEditorProps } from '../types';

export const TextCellEditor = forwardRef<HTMLInputElement | null, CellEditorProps>(
  ({ value, onChange, onBlur, onKeyDown, column, autoFocus }, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => inputRef.current!, []);

    useEffect(() => {
      if (autoFocus) {
        inputRef.current?.focus();
        inputRef.current?.select();
      }
    }, [autoFocus]);

    return (
      <input
        ref={inputRef}
        type="text"
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
        className={cn(
          'w-full px-2 py-1 text-sm border border-primary-500 rounded outline-none bg-white',
          column.required && 'bg-primary-50'
        )}
        placeholder={column.required ? 'Obrigatório' : ''}
        aria-label={column.header}
      />
    );
  }
);

TextCellEditor.displayName = 'TextCellEditor';