import { ReactNode, HTMLAttributes } from 'react'
import { cn } from '../utils/helpers'

export interface Column<T> {
  key: string
  header: string
  render?: (row: T, index: number) => ReactNode
  className?: string
  headerClassName?: string
}

interface TableProps<T> extends HTMLAttributes<HTMLTableElement> {
  columns: Column<T>[]
  data: T[]
  keyField: keyof T | ((row: T) => string)
  rowClassName?: (row: T, index: number) => string
  emptyMessage?: string
  striped?: boolean
  hoverable?: boolean
  isLoading?: boolean
  onRowClick?: (row: T) => void
}

export function Table<T>({
  columns,
  data,
  keyField,
  rowClassName,
  emptyMessage = 'Nenhum registro encontrado',
  striped = true,
  hoverable = true,
  isLoading = false,
  onRowClick,
  className,
  children,
  ...props
}: TableProps<T>) {
  const getKey = typeof keyField === 'function' ? keyField : (row: T) => String(row[keyField])

  return (
    <div className={cn('table-container', className)}>
      <table className="table" {...props}>
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className={cn(column.headerClassName)}
                style={{ width: column.className?.includes('w-') ? undefined : 'auto' }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            columns.map((_, colIndex) => (
              <tr key={`loading-${colIndex}`}>
                <td colSpan={columns.length} className="px-4 py-8 text-center">
                  <div className="animate-pulse">
                    <div className="h-4 bg-secondary-200 rounded w-3/4 mx-auto" />
                  </div>
                </td>
              </tr>
            ))
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-secondary-500">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={getKey(row)}
                className={cn(
                  rowClassName?.(row, rowIndex),
                  striped && rowIndex % 2 === 1 && 'bg-secondary-50',
                  hoverable && 'hover:bg-secondary-50',
                  onRowClick && 'cursor-pointer'
                )}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column) => (
                  <td key={column.key} className={cn(column.className)}>
                    {column.render ? column.render(row, rowIndex) : String((row as Record<string, unknown>)[column.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
      {children}
    </div>
  )
}

interface PaginationProps {
  currentPage: number
  totalPages: number
  totalItems?: number
  pageSize?: number
  onPageChange: (page: number) => void
  onPageSizeChange?: (size: number) => void
  pageSizeOptions?: number[]
  showPageNumbers?: boolean
  maxPageNumbers?: number
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems: _totalItems,
  pageSize: _pageSize,
  onPageChange,
  onPageSizeChange: _onPageSizeChange,
  pageSizeOptions: _pageSizeOptions,
  showPageNumbers = true,
  maxPageNumbers = 5,
}: PaginationProps) {
  if (totalPages <= 1) return null

  const pages = []
  if (showPageNumbers) {
    const half = Math.floor(maxPageNumbers / 2)
    let start = Math.max(1, currentPage - half)
    let end = Math.min(totalPages, start + maxPageNumbers - 1)

    if (end - start + 1 < maxPageNumbers) {
      start = Math.max(1, end - maxPageNumbers + 1)
    }

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
  }

  return (
    <nav className="flex items-center justify-between px-4 py-3 border-t border-secondary-200" aria-label="Pagination">
      <div className="text-sm text-secondary-500">
        Página {currentPage} de {totalPages}
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="p-2 rounded-lg text-secondary-600 hover:bg-secondary-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Página anterior"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        {showPageNumbers && (
          <>
            {pages[0] > 1 && (
              <>
                <button
                  onClick={() => onPageChange(1)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                    currentPage === 1
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-600 hover:bg-secondary-100'
                  )}
                >
                  1
                </button>
                {pages[0] > 2 && (
                  <span className="px-2 text-secondary-400">...</span>
                )}
              </>
            )}
            {pages.map((page) => (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                  currentPage === page
                    ? 'bg-primary-600 text-white'
                    : 'text-secondary-600 hover:bg-secondary-100'
                )}
              >
                {page}
              </button>
            ))}
            {pages[pages.length - 1] < totalPages && (
              <>
                {pages[pages.length - 1] < totalPages - 1 && (
                  <span className="px-2 text-secondary-400">...</span>
                )}
                <button
                  onClick={() => onPageChange(totalPages)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
                    currentPage === totalPages
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-600 hover:bg-secondary-100'
                  )}
                >
                  {totalPages}
                </button>
              </>
            )}
          </>
        )}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="p-2 rounded-lg text-secondary-600 hover:bg-secondary-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Próxima página"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </nav>
  )
}