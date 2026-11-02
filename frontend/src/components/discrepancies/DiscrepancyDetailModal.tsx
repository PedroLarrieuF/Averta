import { useEffect, useState } from 'react'
import { X, FileText, AlertTriangle, Gavel, DollarSign, Scale, Hash, Clock, ArrowRight, CheckCircle, XCircle } from 'lucide-react'
import { Modal, Badge, Button } from '@/components'
import { Discrepancy, DiscrepancySeverity, DiscrepancyStatus } from '@/types'
import { cn, formatCurrency, formatDateTime, getStatusBadge, getSeverityBadge } from '@/utils/helpers'

interface DiscrepancyDetailModalProps {
  discrepancy: Discrepancy
  onClose: () => void
  onReview: (id: string, notes?: string) => void
  onContest: (ids: string[]) => void
  isReviewing?: boolean
  isContesting?: boolean
}

const typeLabels: Record<string, string> = {
  FREIGHT_VALUE: 'Valor do Frete',
  ICMS: 'ICMS',
  TOLLS: 'Pedágios',
  WEIGHT: 'Peso',
  VOLUME: 'Volume',
  DIMENSIONS: 'Dimensões',
  DUPLICATE: 'Duplicado',
  MISSING_DOCUMENT: 'Documento Ausente',
  INVALID_CNPJ: 'CNPJ Inválido',
  ROUTE_MISMATCH: 'Rota Divergente',
  OTHER: 'Outro',
}

const severityLabels: Record<DiscrepancySeverity, string> = {
  LOW: 'Baixa',
  MEDIUM: 'Média',
  HIGH: 'Alta',
  CRITICAL: 'Crítica',
}

const statusLabels: Record<DiscrepancyStatus, string> = {
  OPEN: 'Aberta',
  IN_REVIEW: 'Em Análise',
  CONTESTED: 'Contestada',
  APPROVED: 'Aprovada',
  REJECTED: 'Rejeitada',
  PAID: 'Paga',
  CLOSED: 'Fechada',
}

const getBadgeVariant = (variant: string): 'primary' | 'secondary' | 'danger' | 'success' | 'warning' => {
  switch (variant) {
    case 'badge-primary': return 'primary'
    case 'badge-warning': return 'warning'
    case 'badge-danger': return 'danger'
    case 'badge-success': return 'success'
    default: return 'secondary'
  }
}

export function DiscrepancyDetailModal({
  discrepancy,
  onClose,
  onReview,
  onContest,
  isReviewing,
  isContesting,
}: DiscrepancyDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'evidence' | 'actions'>('overview')
  const [reviewNotes, _setReviewNotes] = useState('')

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  const handleReview = () => {
    onReview(discrepancy.id, reviewNotes)
  }

  const handleContest = () => {
    onContest([discrepancy.id])
  }

  return (
    <Modal
      open={true}
      onOpenChange={onClose}
      title=""
      size="xl"
      showClose={false}
    >
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-secondary-200 pb-4 mb-4">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-secondary-100 flex items-center justify-center flex-shrink-0">
              <FileText className="h-6 w-6 text-secondary-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-secondary-900">
                {typeLabels[discrepancy.type] || discrepancy.type}
              </h2>
              <div className="flex items-center gap-3 mt-1">
                <Badge variant={getBadgeVariant(getSeverityBadge(discrepancy.severity).variant)}>
                  {severityLabels[discrepancy.severity]}
                </Badge>
                <Badge variant={getBadgeVariant(getStatusBadge(discrepancy.status).variant)}>
                  {statusLabels[discrepancy.status]}
                </Badge>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors"
            aria-label="Fechar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-secondary-200 mb-4">
          <nav className="flex gap-1" aria-label="Abas da discrepância">
            <button
              onClick={() => setActiveTab('overview')}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2',
                activeTab === 'overview'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50'
              )}
            >
              Visão Geral
            </button>
            <button
              onClick={() => setActiveTab('evidence')}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2',
                activeTab === 'evidence'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50'
              )}
            >
              Evidências
            </button>
            <button
              onClick={() => setActiveTab('actions')}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2',
                activeTab === 'actions'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50'
              )}
            >
              Ações
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Values Comparison */}
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
                  <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                    <DollarSign className="h-3.5 w-3.5" aria-hidden="true" />
                    Valor Esperado
                  </label>
                  <p className="text-2xl font-bold text-secondary-900 font-mono mt-1">
                    {formatCurrency(discrepancy.expectedValue)}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
                  <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                    <DollarSign className="h-3.5 w-3.5" aria-hidden="true" />
                    Valor Atual
                  </label>
                  <p className="text-2xl font-bold text-secondary-900 font-mono mt-1">
                    {formatCurrency(discrepancy.actualValue)}
                  </p>
                </div>
                <div className={cn(
                  'p-4 rounded-lg border font-mono',
                  discrepancy.difference > 0
                    ? 'bg-danger-50 border-danger-200'
                    : 'bg-success-50 border-success-200'
                )}>
                  <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                    <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                    Diferença
                  </label>
                  <p className={cn('text-2xl font-bold mt-1', discrepancy.difference > 0 ? 'text-danger-600' : 'text-success-600')}>
                    {discrepancy.difference > 0 ? '+' : ''}{formatCurrency(discrepancy.difference)}
                  </p>
                  <p className="text-sm text-secondary-500 mt-1">
                    {discrepancy.differencePercent.toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Details Grid */}
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[
                  { label: 'ID', value: discrepancy.id, icon: Hash },
                  { label: 'Regra', value: typeLabels[discrepancy.type] || discrepancy.type, icon: FileText },
                  { label: 'Descrição', value: discrepancy.description, icon: FileText },
                  { label: 'Severidade', value: severityLabels[discrepancy.severity], icon: AlertTriangle, badge: getSeverityBadge(discrepancy.severity) },
                  { label: 'Status', value: statusLabels[discrepancy.status], icon: discrepancy.status === 'APPROVED' || discrepancy.status === 'PAID' || discrepancy.status === 'CLOSED' ? CheckCircle : AlertTriangle, badge: getStatusBadge(discrepancy.status) },
                  { label: 'Criada em', value: formatDateTime(discrepancy.createdAt), icon: Clock },
                  { label: 'Atualizada em', value: formatDateTime(discrepancy.updatedAt), icon: Clock },
                  { label: 'Revisada em', value: discrepancy.reviewedAt ? formatDateTime(discrepancy.reviewedAt) : '—', icon: Clock },
                  { label: 'Documento ID', value: discrepancy.documentId, icon: FileText },
                  { label: 'Contrato ID', value: discrepancy.contractId || '—', icon: Scale },
                  { label: 'Transportadora', value: discrepancy.carrierId || 'Não informada', icon: Hash },
                  { label: 'Ação Sugerida', value: discrepancy.suggestedAction || '—', icon: Gavel },
                ].map((field, i) => (
                  <div key={i} className="space-y-1">
                    <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                      <field.icon className="h-3.5 w-3.5" aria-hidden="true" />
                      {field.label}
                    </label>
                    <div className="flex items-center gap-2">
                      {field.badge ? (
                        <Badge variant={getBadgeVariant(field.badge.variant)}>
                          {field.badge.label}
                        </Badge>
                      ) : (
                        <span className="text-secondary-900 font-mono text-sm truncate max-w-xs">{field.value}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Suggested Action */}
              {discrepancy.suggestedAction && (
                <div className="p-4 rounded-lg bg-primary-50 border border-primary-200">
                  <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                    <Gavel className="h-3.5 w-3.5" aria-hidden="true" />
                    Ação Sugerida
                  </label>
                  <p className="text-secondary-900 mt-1">{discrepancy.suggestedAction}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'evidence' && (
            <div className="space-y-6">
              <div className="p-8 text-center">
                <FileText className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
                <h3 className="text-lg font-medium text-secondary-900 mb-2">Evidências Detalhadas</h3>
                <p className="text-secondary-500">
                  As evidências detalhadas (caminhos XML, valores esperados/encontrados) serão exibidas aqui
                  quando a API retornar esses dados no campo 'evidence'.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'actions' && (
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
                <h3 className="text-lg font-medium text-secondary-900 mb-4">Ações Disponíveis</h3>
                <div className="space-y-3">
                  {discrepancy.status === 'OPEN' && (
                    <>
                      <div className="flex items-center justify-between p-3 rounded-lg border border-secondary-200 bg-white">
                        <div>
                          <p className="font-medium text-secondary-900">Revisar Discrepância</p>
                          <p className="text-sm text-secondary-500">Marca como em análise e permite adicionar observações</p>
                        </div>
                        <Button
                          variant="primary"
                          onClick={handleReview}
                          loading={isReviewing}
                        >
                          <AlertTriangle className="h-4 w-4 mr-2" />
                          Revisar
                        </Button>
                      </div>
                      <div className="flex items-center justify-between p-3 rounded-lg border border-secondary-200 bg-white">
                        <div>
                          <p className="font-medium text-secondary-900">Contestar Discrepância</p>
                          <p className="text-sm text-secondary-500">Inicia processo de contestação com a transportadora</p>
                        </div>
                        <Button
                          variant="secondary"
                          onClick={handleContest}
                          loading={isContesting}
                        >
                          <Gavel className="h-4 w-4 mr-2" />
                          Contestar
                        </Button>
                      </div>
                    </>
                  )}
                  {discrepancy.status === 'IN_REVIEW' && (
                    <div className="flex items-center justify-between p-3 rounded-lg border border-secondary-200 bg-white">
                      <div>
                        <p className="font-medium text-secondary-900">Finalizar Revisão</p>
                        <p className="text-sm text-secondary-500">Aprovar ou rejeitar a discrepância após análise</p>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="primary" size="sm">
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Aprovar
                        </Button>
                        <Button variant="danger" size="sm">
                          <XCircle className="h-4 w-4 mr-2" />
                          Rejeitar
                        </Button>
                      </div>
                    </div>
                  )}
                  {discrepancy.status === 'CONTESTED' && (
                    <div className="flex items-center justify-between p-3 rounded-lg border border-secondary-200 bg-white">
                      <div>
                        <p className="font-medium text-secondary-900">Acompanhar Contestação</p>
                        <p className="text-sm text-secondary-500">Ver status e negociar com a transportadora</p>
                      </div>
                      <Button variant="primary" size="sm">
                        <ArrowRight className="h-4 w-4 mr-2" />
                        Ver Contestação
                      </Button>
                    </div>
                  )}
                  {['APPROVED', 'REJECTED', 'PAID', 'CLOSED'].includes(discrepancy.status) && (
                    <div className="p-3 rounded-lg bg-secondary-100 border border-secondary-200">
                      <p className="text-sm text-secondary-600 text-center">
                        Esta discrepância já foi finalizada com status: <strong>{statusLabels[discrepancy.status]}</strong>
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Review Notes */}
              {discrepancy.reviewedAt && (
                <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
                  <label className="text-xs font-medium text-secondary-500 uppercase tracking-wide mb-1 block">
                    Observações da Revisão
                  </label>
                  <p className="text-secondary-900">{discrepancy.description || 'Sem observações'}</p>
                  <p className="text-xs text-secondary-500 mt-1">
                    Revisado por: {discrepancy.reviewedBy || 'Sistema'} em {formatDateTime(discrepancy.reviewedAt!)}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 border-t border-secondary-200 pt-4 mt-auto">
          {discrepancy.status === 'OPEN' && (
            <>
              <Button variant="secondary" onClick={handleContest} loading={isContesting}>
                <Gavel className="h-4 w-4 mr-2" />
                Contestar
              </Button>
              <Button variant="primary" onClick={handleReview} loading={isReviewing}>
                <AlertTriangle className="h-4 w-4 mr-2" />
                Revisar
              </Button>
            </>
          )}
          <Button variant="ghost" onClick={onClose}>
            Fechar
          </Button>
        </div>
      </div>
    </Modal>
  )
}