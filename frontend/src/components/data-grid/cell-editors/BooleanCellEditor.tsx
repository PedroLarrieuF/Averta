import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import { cn } from '@/utils/helpers';
import type { CellEditorProps } from '../types';

interface BooleanCellEditorProps extends CellEditorProps {
  column: {
    id: string;
    header: string;
    type: 'boolean';
    required?: boolean;
  };
}

export const BooleanCellEditor = forwardRef<HTMLInputElement | null, BooleanCellEditorProps>(
  ({ value, onChange, onBlur, onKeyDown, column, autoFocus }, ref) => {
    const inputRef = useRef<HTMLInputElement>(null);

    useImperativeHandle(ref, () => inputRef.current!, []);

    useEffect(() => {
      if (autoFocus) {
        inputRef.current?.focus();
      }
    }, [autoFocus]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(e.target.checked);
    };

    return (
      <label className="flex items-center justify-center">
        <input
          ref={inputRef}
          type="checkbox"
          checked={value === true}
          onChange={handleChange}
          onBlur={onBlur}
          onKeyDown={onKeyDown}
          className={cn(
            'h-4 w-4 rounded border-secondary-300 text-primary-600 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 cursor-pointer',
            column.required && 'bg-primary-50'
          )}
          aria-label={column.header}
        />
      </label>
    );
  }
);

BooleanCellEditor.displayName = 'BooleanCellEditor';