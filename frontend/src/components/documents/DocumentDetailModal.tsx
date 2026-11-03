import { useEffect, useState } from 'react'
import { X, FileText, Download, RotateCw, AlertCircle, CheckCircle, Clock, DollarSign, Truck, MapPin, Package, Hash } from 'lucide-react'
import { Modal, Badge, Button } from '@/components'
import { Document, DocumentStatus, DocumentType } from '@/types'
import { cn, formatCurrency, formatNumber, formatDateTime, formatDate } from '@/utils/helpers'
import { Calendar } from 'lucide-react'

interface DocumentDetailModalProps {
  document: Document
  onClose: () => void
  onReprocess: (docId: string) => void
}

const typeLabels: Record<DocumentType, string> = {
  CTE: 'CT-e',
  NFE: 'NF-e',
  CTE_COMPLEMENTAR: 'CT-e Complementar',
  NFE_COMPLEMENTAR: 'NF-e Complementar',
  OTHER: 'Outro',
}

const statusLabels: Record<DocumentStatus, string> = {
  PENDING: 'Pendente',
  PROCESSING: 'Processando',
  COMPLETED: 'Concluído',
  FAILED: 'Falhou',
  ARCHIVED: 'Arquivado',
}

export function DocumentDetailModal({ document, onClose, onReprocess }: DocumentDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'parsed' | 'discrepancies'>('overview')

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  const parsedData = document.parsedData || {}

  const overviewFields = [
    { label: 'ID', value: document.id, icon: Hash },
    { label: 'Nome do arquivo', value: document.fileName, icon: FileText },
    { label: 'Tipo', value: typeLabels[document.type] || document.type, icon: FileText },
    { label: 'Status', value: statusLabels[document.status], icon: document.status === 'COMPLETED' ? CheckCircle : document.status === 'FAILED' ? AlertCircle : Clock, badge: true },
    { label: 'Tamanho', value: `${formatNumber(document.fileSize)} bytes`, icon: Package },
    { label: 'Criado em', value: formatDateTime(document.createdAt), icon: Clock },
    { label: 'Atualizado em', value: formatDateTime(document.updatedAt), icon: Clock },
    { label: 'Processado em', value: document.processedAt ? formatDateTime(document.processedAt) : '—', icon: Clock },
    { label: 'Transportadora', value: document.carrierId ? `ID: ${document.carrierId}` : 'Não informada', icon: Truck },
    { label: 'Cliente', value: document.clientId ? `ID: ${document.clientId}` : 'Não informado', icon: MapPin },
  ]

  const parsedFields = [
    { label: 'Chave de Acesso', key: 'accessKey', icon: Hash },
    { label: 'Número', key: 'number', icon: Hash },
    { label: 'Série', key: 'series', icon: Hash },
    { label: 'Data de Emissão', key: 'issueDate', icon: Calendar, format: 'date' },
    { label: 'Valor Total', key: 'totalValue', icon: DollarSign, format: 'currency' },
    { label: 'Valor do Frete', key: 'freightValue', icon: DollarSign, format: 'currency' },
    { label: 'ICMS', key: 'icmsValue', icon: DollarSign, format: 'currency' },
    { label: 'Pedágios', key: 'tollsValue', icon: DollarSign, format: 'currency' },
    { label: 'Peso (kg)', key: 'weight', icon: Package, format: 'number' },
    { label: 'Volume (m³)', key: 'volume', icon: Package, format: 'number' },
    { label: 'CNPJ Emitente', key: 'emitterCnpj', icon: Truck },
    { label: 'CNPJ Destinatário', key: 'receiverCnpj', icon: Truck },
    { label: 'UF Origem', key: 'originState', icon: MapPin },
    { label: 'UF Destino', key: 'destinationState', icon: MapPin },
    { label: 'Município Origem', key: 'originCity', icon: MapPin },
    { label: 'Município Destino', key: 'destinationCity', icon: MapPin },
    { label: 'CFOP', key: 'cfop', icon: Hash },
    { label: 'Modalidade', key: 'modality', icon: Truck },
  ]

  const renderValue = (value: unknown, format?: string) => {
    if (value === undefined || value === null || value === '') return '—'
    if (format === 'currency') return formatCurrency(Number(value))
    if (format === 'number') return formatNumber(Number(value))
    if (format === 'date') return formatDate(value as string)
    return String(value)
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
              <h2 className="text-xl font-semibold text-secondary-900">{document.fileName}</h2>
              <div className="flex items-center gap-3 mt-1">
                <Badge variant="secondary">{typeLabels[document.type] || document.type}</Badge>
                <Badge variant={getStatusVariant(document.status)}>
                  {statusLabels[document.status]}
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
          <nav className="flex gap-1" aria-label="Abas do documento">
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
              onClick={() => setActiveTab('parsed')}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2',
                activeTab === 'parsed'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50'
              )}
            >
              Dados Extraídos
            </button>
            <button
              onClick={() => setActiveTab('discrepancies')}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2',
                activeTab === 'discrepancies'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50'
              )}
            >
              Discrepâncias
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'overview' && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {overviewFields.map((field, i) => (
                <div key={i} className="space-y-1">
                  <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                    <field.icon className="h-3.5 w-3.5" aria-hidden="true" />
                    {field.label}
                  </label>
                  <div className="flex items-center gap-2">
                    {field.badge && field.label === 'Status' ? (
                      <Badge variant={getStatusVariant(document.status)}>
                        {statusLabels[document.status]}
                      </Badge>
                    ) : (
                      <span className="text-secondary-900">{field.value}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'parsed' && (
            <div className="space-y-4">
              {Object.keys(parsedData).length === 0 ? (
                <div className="p-8 text-center">
                  <FileText className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
                  <h3 className="text-lg font-medium text-secondary-900 mb-2">Nenhum dado extraído</h3>
                  <p className="text-secondary-500">O documento ainda não foi processado ou falhou no processamento</p>
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {parsedFields.map((field) => {
                    const value = parsedData[field.key as keyof typeof parsedData]
                    if (value === undefined || value === null || value === '') return null
                    return (
                      <div key={field.key} className="space-y-1">
                        <label className="flex items-center gap-1 text-xs font-medium text-secondary-500 uppercase tracking-wide">
                          <field.icon className="h-3.5 w-3.5" aria-hidden="true" />
                          {field.label}
                        </label>
                        <span className="text-secondary-900 font-mono text-sm">
                          {renderValue(value, field.format)}
                        </span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {activeTab === 'discrepancies' && (
            <div className="p-8 text-center">
              <AlertCircle className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">Discrepâncias vinculadas</h3>
              <p className="text-secondary-500 mb-6">
                As discrepâncias encontradas neste documento serão exibidas aqui após o processamento.
              </p>
              <Button variant="primary" onClick={() => { window.location.href = `/discrepancies?documentId=${document.id}`; onClose(); }}>
                Ver todas as discrepâncias
              </Button>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 border-t border-secondary-200 pt-4 mt-auto">
          {document.fileUrl && (
            <Button variant="secondary" onClick={() => window.open(document.fileUrl!, '_blank')}>
              <Download className="h-4 w-4 mr-2" />
              Baixar XML
            </Button>
          )}
          {document.status === 'FAILED' && (
            <Button
              variant="primary"
              onClick={() => onReprocess(document.id)}
            >
              <RotateCw className="h-4 w-4 mr-2" />
              Reprocessar
            </Button>
          )}
        </div>
      </div>
    </Modal>
  )
}

function getStatusVariant(status: DocumentStatus): 'success' | 'warning' | 'danger' | 'primary' | 'secondary' {
  switch (status) {
    case 'COMPLETED':
      return 'success'
    case 'PENDING':
      return 'warning'
    case 'PROCESSING':
      return 'primary'
    case 'FAILED':
      return 'danger'
    case 'ARCHIVED':
      return 'secondary'
    default:
      return 'secondary'
  }
}