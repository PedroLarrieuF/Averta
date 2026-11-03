import { AlertTriangle, Gavel, X } from 'lucide-react'
import { Button, Badge } from '@/components'
import { cn } from '@/utils/helpers'

interface BulkActionBarProps {
  selectedCount: number
  onBulkReview: () => void
  onBulkContest: () => void
  onClearSelection: () => void
  isReviewing?: boolean
  isContesting?: boolean
}

export function BulkActionBar({
  selectedCount,
  onBulkReview,
  onBulkContest,
  onClearSelection,
  isReviewing,
  isContesting,
}: BulkActionBarProps) {
  if (selectedCount === 0) return null

  return (
    <div
      className={cn(
        'fixed bottom-0 left-0 right-0 z-50 animate-slide-up',
        'border-t border-secondary-200 bg-white shadow-lg'
      )}
      role="region"
      aria-label="Ações em lote"
    >
      <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Badge variant="primary" className="text-sm px-3 py-1">
              {selectedCount} selecionada{selectedCount > 1 ? 's' : ''}
            </Badge>
            <span className="text-sm text-secondary-600 hidden sm:block">
              A ação será aplicada a todos os itens selecionados
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              onClick={onBulkReview}
              loading={isReviewing}
              disabled={isContesting}
            >
              <AlertTriangle className="h-4 w-4 mr-2" />
              Revisar ({selectedCount})
            </Button>
            <Button
              variant="primary"
              onClick={onBulkContest}
              loading={isContesting}
              disabled={isReviewing}
            >
              <Gavel className="h-4 w-4 mr-2" />
              Contestar ({selectedCount})
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearSelection}
              className="ml-2"
            >
              <X className="h-4 w-4 mr-1" />
              Limpar
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}