import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Gavel, CheckCircle, AlertTriangle, XCircle, MessageSquare, DollarSign, Send, FileText, Download } from 'lucide-react'
import { useContest, useNegotiateContest, useAddContestCommunication, useRegisterPayment, useGenerateContestPDF, useSendContest } from '@/hooks'
import { PageHeader, PageTitle, PageSubtitle, Button, Badge, CardHeader, CardBody, Modal, Input, Textarea, PaymentForm } from '@/components'
import { Contest, ContestStatus } from '@/types'
import { formatCurrency, formatDateTime, getStatusBadge, cn } from '@/utils/helpers'
import toast from 'react-hot-toast'

const statusFlow: ContestStatus[] = ['DRAFT', 'SENT', 'ACKNOWLEDGED', 'NEGOTIATING', 'ACCEPTED', 'PARTIAL', 'REJECTED']

interface NegotiationFormData {
  status: ContestStatus
  notes: string
  offeredAmount?: number
}

// Helper Components
function KPICard({ label, value, icon: Icon, color }: { label: string; value: string; icon: React.ComponentType<{ className?: string }>; color: string }) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600 border-primary-200',
    secondary: 'bg-secondary-50 text-secondary-600 border-secondary-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    success: 'bg-success-50 text-success-600 border-success-200',
  }

  return (
    <div className={cn('p-4 rounded-xl border text-center', colorClasses[color as keyof typeof colorClasses] || colorClasses.primary)}>
      <div className="mx-auto w-12 h-12 rounded-lg flex items-center justify-center mb-3" style={{ backgroundColor: colorClasses[color as keyof typeof colorClasses]?.replace('bg-', '').replace('-50', '-100') || 'var(--color-primary-100)' }}>
        <Icon className="h-6 w-6" />
      </div>
      <p className="text-sm font-medium text-secondary-500">{label}</p>
      <p className="font-mono font-bold text-lg text-secondary-900 mt-1">{value}</p>
    </div>
  )
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center',
        active
          ? 'border-primary-500 text-primary-600'
          : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:bg-secondary-50'
      )}
    >
      {children}
    </button>
  )
}

export function ContestNegotiatePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  // Fetch contest data
  const { data: contest, isLoading: isLoadingContest, refetch: refetchContest } = useContest(id!)

  // Mutations
  const negotiateContest = useNegotiateContest()
  const addCommunication = useAddContestCommunication()
  const registerPayment = useRegisterPayment()
  const generatePDF = useGenerateContestPDF()
  const sendContest = useSendContest()

  // UI State
  const [activeTab, setActiveTab] = useState<'negotiate' | 'communications' | 'payments' | 'pdf'>('negotiate')
  const [showNegotiateModal, setShowNegotiateModal] = useState(false)
  const [showCommunicationModal, setShowCommunicationModal] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [showPDFViewer, setShowPDFViewer] = useState(false)
  const [negotiationForm, setNegotiationForm] = useState<NegotiationFormData>({ status: 'NEGOTIATING', notes: '' })
  const [communicationForm, setCommunicationForm] = useState<{ subject: string; body: string; type: 'INBOUND' | 'OUTBOUND' }>({ subject: '', body: '', type: 'OUTBOUND' })

  const currentStatusIndex = statusFlow.indexOf(contest?.status || 'DRAFT')
  const canSend = contest?.status === 'DRAFT'
  const canNegotiate = ['SENT', 'ACKNOWLEDGED', 'NEGOTIATING'].includes(contest?.status || '')
  const canAddPayment = ['ACCEPTED', 'PARTIAL'].includes(contest?.status || '')
  const isFinal = ['ACCEPTED', 'PARTIAL', 'REJECTED', 'EXPIRED'].includes(contest?.status || '')
  const agreedAmount = contest?.agreedAmount ?? contest?.offeredAmount

  const handleNegotiate = async () => {
    if (!contest) return
    try {
      await negotiateContest.mutateAsync({ id: contest.id, ...negotiationForm })
      toast.success('Negociação atualizada!')
      setShowNegotiateModal(false)
      setNegotiationForm({ status: 'NEGOTIATING', notes: '' })
      await refetchContest()
    } catch (_error) {
      toast.error('Erro ao atualizar negociação')
    }
  }

  const handleAddCommunication = async () => {
    if (!contest || !communicationForm.subject.trim() || !communicationForm.body.trim()) return
    try {
      await addCommunication.mutateAsync({ contestId: contest.id, ...communicationForm })
      toast.success('Comunicação registrada!')
      setShowCommunicationModal(false)
      setCommunicationForm({ subject: '', body: '', type: 'OUTBOUND' })
    } catch (_error) {
      toast.error('Erro ao registrar comunicação')
    }
  }

  const handleRegisterPayment = async (data: { amount: number; paidAt: string; proofFile?: File; notes?: string }) => {
    if (!contest) return
    await registerPayment.mutateAsync({ contestId: contest.id, ...data })
    toast.success('Pagamento registrado com sucesso!')
    setShowPaymentModal(false)
    await refetchContest()
  }

  const handleGeneratePDF = async () => {
    if (!contest) return
    try {
      await generatePDF.mutateAsync(contest.id)
      toast.success('PDF gerado com sucesso!')
      setShowPDFViewer(true)
    } catch (_error) {
      toast.error('Erro ao gerar PDF')
    }
  }

  const handleSend = async () => {
    if (!contest) return
    try {
      await sendContest.mutateAsync(contest.id)
      toast.success('Contestação enviada com sucesso!')
      await refetchContest()
    } catch (_error) {
      toast.error('Erro ao enviar contestação')
    }
  }

  if (isLoadingContest) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-secondary-100 rounded w-1/4" />
        <div className="h-4 bg-secondary-100 rounded w-1/2" />
        <div className="h-64 bg-secondary-100 rounded-lg" />
      </div>
    )
  }

  if (!contest) {
    return (
      <div className="space-y-6">
        <PageHeader>
          <div>
            <PageTitle>Contestação não encontrada</PageTitle>
            <PageSubtitle>A contestação solicitada não existe ou foi removida</PageSubtitle>
          </div>
        </PageHeader>
        <div className="card p-12 text-center">
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">Contestação não encontrada</h3>
          <p className="text-secondary-500 mb-6">A contestação solicitada não existe ou foi removida.</p>
          <Button variant="primary" onClick={() => navigate('/contests')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar para lista
          </Button>
        </div>
      </div>
    )
  }

  const { variant: statusVariant, label: statusLabel } = getStatusBadge(contest.status)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <PageTitle className="truncate">{contest.title}</PageTitle>
            <Badge variant={statusVariant as 'primary' | 'secondary' | 'danger' | 'success' | 'warning'}>
              {statusLabel}
            </Badge>
          </div>
          <PageSubtitle>Gerencie a negociação, comunicações e pagamentos desta contestação</PageSubtitle>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="secondary" onClick={() => navigate('/contests')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <Button variant="secondary" onClick={() => navigate(`/contests/${contest.id}`)}>
            Ver Detalhes Completos
          </Button>
          {!showPDFViewer && contest.status === 'DRAFT' && (
            <Button variant="secondary" onClick={handleGeneratePDF}>
              <FileText className="h-4 w-4 mr-2" />
              Gerar PDF
            </Button>
          )}
          {canSend && (
            <Button variant="primary" onClick={handleSend} loading={sendContest.isPending}>
              <Send className="h-4 w-4 mr-2" />
              Enviar
            </Button>
          )}
        </div>
      </PageHeader>

      {/* PDF Viewer */}
      {showPDFViewer && (
        <div className="fixed inset-0 z-50 bg-white">
          <div className="flex items-center justify-between p-4 border-b border-secondary-200 sticky top-0 bg-white z-10">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={() => setShowPDFViewer(false)}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <h3 className="font-semibold text-secondary-900">Visualização do PDF</h3>
            </div>
            <Button variant="primary" onClick={handleGeneratePDF} loading={generatePDF.isPending}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          </div>
          <iframe
            src={`${(import.meta as any).env.VITE_API_URL || '/api/v1'}/contests/${contest.id}/pdf`}
            className="w-full h-[calc(100vh-80px)] border-0"
            title={`Contestação ${contest.title}`}
          />
        </div>
      )}

      {/* Status Progress */}
      <div className="card">
        <CardHeader>
          <h3 className="font-semibold text-secondary-900">Status do Workflow</h3>
        </CardHeader>
        <CardBody>
          <div className="flex items-center gap-2 overflow-x-auto pb-4">
            {statusFlow.map((status, index) => {
              const isCompleted = index < currentStatusIndex
              const isCurrent = index === currentStatusIndex
              const stepLabels: Record<ContestStatus, string> = {
                DRAFT: 'Rascunho',
                SENT: 'Enviada',
                ACKNOWLEDGED: 'Recebida',
                NEGOTIATING: 'Negociando',
                ACCEPTED: 'Aceita',
                PARTIAL: 'Parcial',
                REJECTED: 'Rejeitada',
                EXPIRED: 'Expirada',
              }
              const stepIcons: Record<ContestStatus, React.ReactNode> = {
                DRAFT: <FileText className="h-4 w-4" />,
                SENT: <Send className="h-4 w-4" />,
                ACKNOWLEDGED: <CheckCircle className="h-4 w-4" />,
                NEGOTIATING: <Gavel className="h-4 w-4" />,
                ACCEPTED: <CheckCircle className="h-4 w-4" />,
                PARTIAL: <AlertTriangle className="h-4 w-4" />,
                REJECTED: <XCircle className="h-4 w-4" />,
                EXPIRED: <DollarSign className="h-4 w-4" />,
              }

              return (
                <div key={status} className="flex items-center flex-shrink-0">
                  <div className={cn(
                    'relative flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all',
                    isCompleted
                      ? 'bg-success-500 text-white'
                      : isCurrent
                      ? 'bg-primary-500 text-white ring-4 ring-primary-100'
                      : 'bg-secondary-200 text-secondary-500'
                  )}>
                    {isCompleted ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      stepIcons[status]
                    )}
                  </div>
                  <span className={cn(
                    'hidden sm:block whitespace-nowrap text-sm font-medium px-2',
                    isCompleted || isCurrent ? 'text-secondary-900' : 'text-secondary-400'
                  )}>
                    {stepLabels[status]}
                  </span>
                  {index < statusFlow.length - 1 && (
                    <div className={cn(
                      'w-20 h-0.5 mx-2 hidden sm:block',
                      index < currentStatusIndex ? 'bg-success-500' : 'bg-secondary-200'
                    )} />
                  )}
                </div>
              )
            })}
          </div>
        </CardBody>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Solicitado" value={formatCurrency(contest.requestedAmount)} icon={DollarSign} color="primary" />
        <KPICard label="Oferecido" value={contest.offeredAmount ? formatCurrency(contest.offeredAmount) : '—'} icon={Gavel} color="warning" />
        <KPICard label="Acordado" value={agreedAmount ? formatCurrency(agreedAmount) : '—'} icon={CheckCircle} color="success" />
        <KPICard label="Status" value={statusLabel} icon={Gavel} color={statusVariant.replace('badge-', '') as any} />
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-secondary-200">
          <nav className="flex gap-1 px-4" aria-label="Abas de negociação">
            <TabButton active={activeTab === 'negotiate'} onClick={() => setActiveTab('negotiate')}>
              <Gavel className="h-4 w-4 mr-2" /> Negociar
            </TabButton>
            <TabButton active={activeTab === 'communications'} onClick={() => setActiveTab('communications')}>
              <MessageSquare className="h-4 w-4 mr-2" /> Comunicações
            </TabButton>
            <TabButton active={activeTab === 'payments'} onClick={() => setActiveTab('payments')}>
              <DollarSign className="h-4 w-4 mr-2" /> Pagamentos
            </TabButton>
            <TabButton active={activeTab === 'pdf'} onClick={() => setActiveTab('pdf')}>
              <FileText className="h-4 w-4 mr-2" /> PDF
            </TabButton>
          </nav>
        </div>

        <CardBody className="p-6">
          {activeTab === 'negotiate' && (
            <NegotiateTab
              contest={contest}
              canNegotiate={canNegotiate}
              isFinal={isFinal}
              agreedAmount={agreedAmount}
              onOpenModal={() => { setNegotiationForm({ status: 'NEGOTIATING', notes: '' }); setShowNegotiateModal(true); }}
            />
          )}

          {activeTab === 'communications' && (
            <CommunicationsTab
              isFinal={isFinal}
              onOpenModal={() => { setCommunicationForm({ subject: '', body: '', type: 'OUTBOUND' }); setShowCommunicationModal(true); }}
            />
          )}

          {activeTab === 'payments' && (
            <PaymentsTab
              canAddPayment={canAddPayment}
              onOpenModal={() => setShowPaymentModal(true)}
            />
          )}

          {activeTab === 'pdf' && (
            <PDFTab
              contest={contest}
              onGeneratePDF={handleGeneratePDF}
              isGenerating={generatePDF.isPending}
            />
          )}
        </CardBody>
      </div>

      {/* Modals */}
      {showNegotiateModal && (
        <NegotiateModal
          onClose={() => setShowNegotiateModal(false)}
          onSubmit={handleNegotiate}
          isLoading={negotiateContest.isPending}
          form={negotiationForm}
          setForm={setNegotiationForm}
        />
      )}

      {showCommunicationModal && (
        <CommunicationModal
          onClose={() => setShowCommunicationModal(false)}
          onSubmit={handleAddCommunication}
          isLoading={addCommunication.isPending}
          form={communicationForm}
          setForm={setCommunicationForm}
        />
      )}

      {showPaymentModal && (
        <PaymentForm
          contestId={contest.id}
          successFeePct={20}
          agreedAmount={agreedAmount}
          onSubmit={handleRegisterPayment}
          onClose={() => setShowPaymentModal(false)}
          isOpen={true}
          isLoading={registerPayment.isPending}
        />
      )}
    </div>
  )
}

// Tab Components
function NegotiateTab({ contest, canNegotiate, isFinal, agreedAmount, onOpenModal }: { contest: Contest; canNegotiate: boolean; isFinal: boolean; agreedAmount?: number; onOpenModal: () => void }) {
  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
        <h4 className="font-medium text-secondary-900 mb-4">Ações de Negociação</h4>
        <div className="space-y-3">
          {canNegotiate ? (
            <>
              <div className="flex items-center justify-between p-3 rounded-lg border border-secondary-200 bg-white">
                <div>
                  <p className="font-medium text-secondary-900">Atualizar Status</p>
                  <p className="text-sm text-secondary-500">Alterar status da negociação (ex: Aceita, Parcial, Rejeitada)</p>
                </div>
                <Button variant="primary" onClick={onOpenModal}>
                  <Gavel className="h-4 w-4 mr-2" />
                  Negociar
                </Button>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border border-secondary-200 bg-white">
                <div>
                  <p className="font-medium text-secondary-900">Registrar Comunicação</p>
                  <p className="text-sm text-secondary-500">Adicionar mensagem trocada com a transportadora</p>
                </div>
                <Button variant="secondary" onClick={() => {}}> {/* Will be handled by parent */}
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Comunicação
                </Button>
              </div>
            </>
          ) : isFinal ? (
            <div className="p-3 rounded-lg bg-secondary-100 border border-secondary-200 text-center">
              <p className="text-secondary-600">Esta contestação foi finalizada com status: <strong className="text-secondary-900">{getStatusBadge(contest.status).label}</strong></p>
            </div>
          ) : (
            <div className="p-3 rounded-lg bg-primary-50 border border-primary-200 text-center">
              <p className="text-secondary-600">A contestação está em <strong className="text-secondary-900">{getStatusBadge(contest.status).label}</strong>. Aguardando envio para a transportadora.</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-3">
        <QuickActionCard
          title="Valor Solicitado"
          value={formatCurrency(contest.requestedAmount)}
          icon={DollarSign}
          color="primary"
        />
        <QuickActionCard
          title="Valor Oferecido"
          value={contest.offeredAmount ? formatCurrency(contest.offeredAmount) : '—'}
          icon={Gavel}
          color="warning"
        />
        <QuickActionCard
          title="Valor Acordado"
          value={agreedAmount ? formatCurrency(agreedAmount) : '—'}
          icon={CheckCircle}
          color="success"
        />
      </div>

      {/* Success Fee Calculator */}
      <div className="p-4 rounded-lg border border-secondary-200 bg-white">
        <h4 className="font-medium text-secondary-900 mb-4">Calculadora de Success Fee</h4>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="p-3 rounded-lg bg-secondary-50 border border-secondary-200 text-center">
            <p className="text-xs text-secondary-500 uppercase tracking-wide">Success Fee (20%)</p>
            <p className="font-mono font-bold text-lg text-warning-600 mt-1">{formatCurrency((agreedAmount || contest.requestedAmount) * 0.2)}</p>
          </div>
          <div className="p-3 rounded-lg bg-secondary-50 border border-secondary-200 text-center">
            <p className="text-xs text-secondary-500 uppercase tracking-wide">Recuperação Líquida</p>
            <p className="font-mono font-bold text-lg text-success-600 mt-1">{formatCurrency((agreedAmount || contest.requestedAmount) * 0.8)}</p>
          </div>
          <div className="p-3 rounded-lg bg-secondary-50 border border-secondary-200 text-center">
            <p className="text-xs text-secondary-500 uppercase tracking-wide">Total Bruto</p>
            <p className="font-mono font-bold text-lg text-secondary-900 mt-1">{formatCurrency(agreedAmount || contest.requestedAmount)}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function CommunicationsTab({ isFinal, onOpenModal }: { isFinal: boolean; onOpenModal: () => void }) {
  // In a real implementation, this would fetch communications
  // For now, show placeholder
  return (
    <div className="space-y-4">
      {!isFinal && (
        <Button variant="primary" onClick={onOpenModal} className="w-full sm:w-auto">
          <MessageSquare className="h-4 w-4 mr-2" />
          Nova Comunicação
        </Button>
      )}
      <div className="p-8 text-center">
        <MessageSquare className="mx-auto h-12 w-12 text-secondary-300 mb-3" />
        <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhuma comunicação registrada</h3>
        <p className="text-secondary-500 mb-4">As mensagens trocadas com a transportadora aparecerão aqui</p>
        {!isFinal && (
          <Button variant="primary" onClick={onOpenModal}>
            <MessageSquare className="h-4 w-4 mr-2" />
            Registrar Primeira Comunicação
          </Button>
        )}
      </div>
    </div>
  )
}

function PaymentsTab({ canAddPayment, onOpenModal }: { canAddPayment: boolean; onOpenModal: () => void }) {
  // Placeholder - would use useContestPayments hook in real implementation
  return (
    <div className="space-y-4">
      {canAddPayment && (
        <Button variant="primary" onClick={onOpenModal} className="w-full sm:w-auto">
          <DollarSign className="h-4 w-4 mr-2" />
          Registrar Pagamento
        </Button>
      )}
      <div className="p-8 text-center">
        <DollarSign className="mx-auto h-12 w-12 text-secondary-300 mb-3" />
        <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum pagamento registrado</h3>
        <p className="text-secondary-500 mb-4">Registre pagamentos recebidos para calcular o success fee</p>
        {canAddPayment && (
          <Button variant="primary" onClick={onOpenModal}>
            <DollarSign className="h-4 w-4 mr-2" />
            Registrar Primeiro Pagamento
          </Button>
        )}
      </div>
    </div>
  )
}

function PDFTab({ contest, onGeneratePDF, isGenerating }: { contest: Contest; onGeneratePDF: () => void; isGenerating: boolean }) {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-lg border border-secondary-200 bg-white text-center">
        <div className="mx-auto w-20 h-20 rounded-full bg-primary-50 flex items-center justify-center mb-4">
          <FileText className="h-10 w-10 text-primary-600" />
        </div>
        <h3 className="text-xl font-semibold text-secondary-900 mb-2">Carta de Contestação</h3>
        <p className="text-secondary-500 mb-6 max-w-2xl mx-auto">
          Gere o PDF da carta de contestação formal para envio à transportadora. O documento incluirá todos os detalhes da contestação, valores, base legal e anexos.
        </p>
        <Button variant="primary" size="lg" onClick={onGeneratePDF} loading={isGenerating} disabled={isGenerating}>
          {isGenerating ? (
            <> <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg> Gerando PDF... </>)
          : (
            <> <FileText className="h-5 w-5 mr-2" /> Gerar PDF da Contestação </>
          )}
        </Button>
      </div>

      {contest.sentAt && (
        <div className="p-4 rounded-lg bg-success-50 border border-success-200">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-success-600" />
            <div>
              <p className="font-medium text-success-800">PDF já gerado anteriormente</p>
              <p className="text-sm text-success-600">Enviado em: {formatDateTime(contest.sentAt!)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Quick Action Card
function QuickActionCard({ title, value, icon: Icon, color }: { title: string; value: string; icon: React.ComponentType<{ className?: string }>; color: string }) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600 border-primary-200',
    secondary: 'bg-secondary-50 text-secondary-600 border-secondary-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    success: 'bg-success-50 text-success-600 border-success-200',
  }

  return (
    <div className={cn('p-4 rounded-xl border text-center', colorClasses[color as keyof typeof colorClasses] || colorClasses.primary)}>
      <div className="mx-auto w-12 h-12 rounded-lg flex items-center justify-center mb-3" style={{ backgroundColor: colorClasses[color as keyof typeof colorClasses]?.replace('bg-', '').replace('-50', '-100') || 'var(--color-primary-100)' }}>
        <Icon className="h-6 w-6" />
      </div>
      <p className="text-sm font-medium text-secondary-500">{title}</p>
      <p className="font-mono font-bold text-lg text-secondary-900 mt-1">{value}</p>
    </div>
  )
}

// Modals (reused from ContestDetailPage)
function NegotiateModal({ onClose, onSubmit, isLoading, form, setForm }: { onClose: () => void; onSubmit: () => Promise<void>; isLoading: boolean; form: NegotiationFormData; setForm: React.Dispatch<React.SetStateAction<NegotiationFormData>> }) {
  const nextStatuses: ContestStatus[] = ['ACKNOWLEDGED', 'NEGOTIATING', 'ACCEPTED', 'PARTIAL', 'REJECTED']

  return (
    <Modal open={true} onOpenChange={onClose} title="Negociar Contestação" size="lg">
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} className="space-y-6">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Novo Status *</label>
          <select
            value={form.status}
            onChange={(e) => setForm(prev => ({ ...prev, status: e.target.value as ContestStatus }))}
            className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            required
          >
            {nextStatuses.map(s => (
              <option key={s} value={s}>{getStatusBadge(s).label}</option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Valor Oferecido (opcional)</label>
          <Input
            type="number"
            step="0.01"
            value={form.offeredAmount?.toString() || ''}
            onChange={(e) => setForm(prev => ({ ...prev, offeredAmount: e.target.value ? parseFloat(e.target.value) : undefined }))}
            placeholder="0,00"
            className="w-full"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Observações</label>
          <Textarea
            value={form.notes}
            onChange={(e) => setForm(prev => ({ ...prev, notes: e.target.value }))}
            placeholder="Detalhes da negociação, contrapropostas, etc."
            rows={4}
          />
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" loading={isLoading}>
            Salvar Negociação
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function CommunicationModal({ onClose, onSubmit, isLoading, form, setForm }: { onClose: () => void; onSubmit: () => Promise<void>; isLoading: boolean; form: { subject: string; body: string; type: 'INBOUND' | 'OUTBOUND' }; setForm: React.Dispatch<React.SetStateAction<{ subject: string; body: string; type: 'INBOUND' | 'OUTBOUND' }>> }) {
  return (
    <Modal open={true} onOpenChange={onClose} title="Nova Comunicação" size="lg">
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }} className="space-y-6">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Tipo *</label>
          <select
            value={form.type}
            onChange={(e) => setForm(prev => ({ ...prev, type: e.target.value as 'INBOUND' | 'OUTBOUND' }))}
            className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="OUTBOUND">Enviada (nossa)</option>
            <option value="INBOUND">Recebida (transportadora)</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Assunto *</label>
          <Input
            value={form.subject}
            onChange={(e) => setForm(prev => ({ ...prev, subject: e.target.value }))}
            placeholder="Assunto da mensagem"
            required
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Mensagem *</label>
          <Textarea
            value={form.body}
            onChange={(e) => setForm(prev => ({ ...prev, body: e.target.value }))}
            placeholder="Conteúdo da mensagem..."
            rows={5}
            required
          />
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" loading={isLoading} disabled={!form.subject.trim() || !form.body.trim()}>
            Registrar Comunicação
          </Button>
        </div>
      </form>
    </Modal>
  )
}