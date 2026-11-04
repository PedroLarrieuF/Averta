import { cn } from '../utils/helpers'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div className={cn('empty-state flex flex-col items-center text-center py-12 px-4', className)}>
      {icon && (
        <div className={cn('empty-state-icon mx-auto mb-4 text-secondary-400', 'h-16 w-16')}>
          {icon}
        </div>
      )}
      <h3 className={cn('empty-state-title text-lg font-semibold text-secondary-900 mb-2')}>
        {title}
      </h3>
      {description && (
        <p className={cn('empty-state-description text-secondary-500 max-w-md mb-6')}>
          {description}
        </p>
      )}
      {action && (
        <div className={cn('empty-state-action')}>
          {action}
        </div>
      )}
    </div>
  )
}

// Predefined empty states for common use cases
export function EmptyDiscrepancies({ onCreate }: { onCreate?: () => void }) {
  return (
    <EmptyState
      icon={
        <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      }
      title="Nenhuma discrepância encontrada"
      description="Não há discrepâncias para os filtros selecionados. Tente ajustar os filtros ou criar uma nova discrepância manualmente."
      action={onCreate && (
        <button
          className="btn btn-primary"
          onClick={onCreate}
        >
          Criar Discrepância
        </button>
      )}
    />
  )
}

export function EmptyDocuments({ onUpload }: { onUpload?: () => void }) {
  return (
    <EmptyState
      icon={
        <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      }
      title="Nenhum documento enviado"
      description="Comece enviando seus primeiros documentos (CTe, NFe) para análise de discrepâncias."
      action={onUpload && (
        <button
          className="btn btn-primary"
          onClick={onUpload}
        >
          Enviar Documentos
        </button>
      )}
    />
  )
}

export function EmptyContests({ onCreate }: { onCreate?: () => void }) {
  return (
    <EmptyState
      icon={
        <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      }
      title="Nenhuma contestação criada"
      description="Selecione discrepâncias na lista e clique em 'Contestar selecionadas' para iniciar uma nova contestação."
      action={onCreate && (
        <button
          className="btn btn-primary"
          onClick={onCreate}
        >
          Nova Contestação
        </button>
      )}
    />
  )
}

export function EmptySearch({ onClear }: { onClear?: () => void }) {
  return (
    <EmptyState
      icon={
        <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      }
      title="Nenhum resultado encontrado"
      description="Sua busca não retornou resultados. Tente ajustar os termos de busca ou limpar os filtros."
      action={onClear && (
        <button
          className="btn btn-secondary"
          onClick={onClear}
        >
          Limpar Filtros
        </button>
      )}
    />
  )
}

export function EmptyGeneric({ title, description, action }: { title: string; description?: string; action?: React.ReactNode }) {
  return (
    <EmptyState
      icon={
        <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      }
      title={title}
      description={description}
      action={action}
    />
  )
}