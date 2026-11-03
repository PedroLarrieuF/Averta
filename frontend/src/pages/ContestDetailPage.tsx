import { useState } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, FileText, Download, MessageSquare, DollarSign, Send, Gavel, Clock, CheckCircle, AlertTriangle, XCircle, Calculator, X } from 'lucide-react'
import { useContest, useContestCommunications, useContestPayments, useSendContest, useGenerateContestPDF, useNegotiateContest, useAddContestCommunication, useRegisterPayment, useCalculateSuccessFee } from '@/hooks'
import { ContestTimeline, ContestItemTable, CommunicationThread, PaymentForm, SuccessFeeCalculator, ContestPDFViewer, PageHeader, PageTitle, PageSubtitle, Button, Badge, CardHeader, CardBody, Modal, Input, Textarea } from '@/components'
import { Contest, ContestStatus } from '@/types'
import { formatCurrency, formatDateTime, getStatusBadge, cn } from '@/utils/helpers'
import toast from 'react-hot-toast'

const statusFlow: ContestStatus[] = ['DRAFT', 'SENT', 'ACKNOWLEDGED', 'NEGOTIATING', 'ACCEPTED', 'PARTIAL', 'REJECTED']

interface NegotiationFormData {
  status: ContestStatus
  notes: string
  offeredAmount?: number
}

export function ContestDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const viewPDF = searchParams.get('viewPDF') === 'true'

  // Fetch contest data
  const { data: contest, isLoading: isLoadingContest, refetch: refetchContest } = useContest(id!)
  const { data: communicationsData, isLoading: isLoadingComms, refetch: refetchComms } = useContestCommunications(id!)
  const { data: paymentsData, isLoading: isLoadingPayments, refetch: refetchPayments } = useContestPayments(id!)

  // Mutations
  const sendContest = useSendContest()
  const generatePDF = useGenerateContestPDF()
  const negotiateContest = useNegotiateContest()
  const addCommunication = useAddContestCommunication()
  const registerPayment = useRegisterPayment()
  const calculateFee = useCalculateSuccessFee()

  // UI State
  const [showPDFViewer, setShowPDFViewer] = useState(viewPDF)
  const [showNegotiateModal, setShowNegotiateModal] = useState(false)
  const [showCommunicationModal, setShowCommunicationModal] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [negotiationForm, setNegotiationForm] = useState<NegotiationFormData>({ status: 'NEGOTIATING', notes: '' })
  const [communicationForm, setCommunicationForm] = useState<{ subject: string; body: string; type: 'INBOUND' | 'OUTBOUND' }>({ subject: '', body: '', type: 'OUTBOUND' })
  const [activeTab, setActiveTab] = useState<'timeline' | 'items' | 'communications' | 'payments' | 'success-fee'>('timeline')

  // Get related data
  const communications = communicationsData?.data ?? []
  const payments = paymentsData?.data ?? []
  const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0)
  const totalNetRecovery = payments.reduce((sum, p) => sum + p.netRecovery, 0)

  const handleSend = async () => {
    if (!contest) return
    try {
      await sendContest.mutateAsync(contest.id)
      toast.success('Contestação enviada com sucesso!')
      await refetchContest()
      await refetchComms()
    } catch (_error) {
      toast.error('Erro ao enviar contestação')
    }
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

  const handleNegotiate = async () => {
    if (!contest) return
    try {
      await negotiateContest.mutateAsync({ id: contest.id, ...negotiationForm })
      toast.success('Negociação atualizada!')
      setShowNegotiateModal(false)
      setNegotiationForm({ status: 'NEGOTIATING', notes: '' })
      await refetchContest()
      await refetchComms()
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
      await refetchComms()
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
    await refetchPayments()
  }

  const handleCalculateFee = async (amount: number) => {
    try {
      const result = await calculateFee.mutateAsync({ totalRecovered: amount, successFeePct: 20 })
      return result
    } catch (_error) {
      toast.error('Erro ao calcular fee')
      return null
    }
  }

  const currentStatusIndex = statusFlow.indexOf(contest?.status || 'DRAFT')
  const canSend = contest?.status === 'DRAFT'
  const canNegotiate = ['SENT', 'ACKNOWLEDGED', 'NEGOTIATING'].includes(contest?.status || '')
  const canAddPayment = ['ACCEPTED', 'PARTIAL'].includes(contest?.status || '')
  const isFinal = ['ACCEPTED', 'PARTIAL', 'REJECTED', 'EXPIRED'].includes(contest?.status || '')

  if (isLoadingContest) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-secondary-100 rounded w-1/4" />
        <div className="h-4 bg-secondary-100 rounded w-1/2" />
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="h-24 bg-secondary-100 rounded-lg" />
          <div className="h-24 bg-secondary-100 rounded-lg" />
          <div className="h-24 bg-secondary-100 rounded-lg" />
          <div className="h-24 bg-secondary-100 rounded-lg" />
        </div>
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
          <FileText className="mx-auto h-16 w-16 text-secondary-300 mb-4" />
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
  const agreedAmount = contest.agreedAmount ?? contest.offeredAmount

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
          <PageSubtitle>{contest.description || 'Sem descrição'}</PageSubtitle>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="secondary" onClick={() => navigate('/contests')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          {!showPDFViewer && contest.status === 'DRAFT' && (
            <Button variant="secondary" onClick={handleGeneratePDF}>
              <FileText className="h-4 w-4 mr-2" />
              Gerar PDF
            </Button>
          )}
          {showPDFViewer && (
            <Button variant="secondary" onClick={() => setShowPDFViewer(false)}>
              <X className="h-4 w-4 mr-2" />
              Fechar PDF
            </Button>
          )}
          {canSend && (
            <Button variant="primary" onClick={handleSend} loading={sendContest.isPending}>
              <Send className="h-4 w-4 mr-2" />
              Enviar
            </Button>
          )}
          {canNegotiate && (
            <Button variant="secondary" onClick={() => { setNegotiationForm({ status: 'NEGOTIATING', notes: '' }); setShowNegotiateModal(true); }}>
              <Gavel className="h-4 w-4 mr-2" />
              Negociar
            </Button>
          )}
          {canAddPayment && (
            <Button variant="primary" onClick={() => setShowPaymentModal(true)}>
              <DollarSign className="h-4 w-4 mr-2" />
              Registrar Pagamento
            </Button>
          )}
          {!isFinal && (
            <Button variant="secondary" onClick={() => { setCommunicationForm({ subject: '', body: '', type: 'OUTBOUND' }); setShowCommunicationModal(true); }}>
              <MessageSquare className="h-4 w-4 mr-2" />
              Comunicação
            </Button>
          )}
        </div>
      </PageHeader>

      {/* PDF Viewer (top section when open) */}
      {showPDFViewer && (
        <ContestPDFViewer
          contestId={contest.id}
          pdfUrl={undefined}
          contestTitle={contest.title}
          onGeneratePDF={generatePDF.mutateAsync}
          onClose={() => setShowPDFViewer(false)}
          isOpen={true}
          isGenerating={generatePDF.isPending}
        />
      )}

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KPICard label="Solicitado" value={formatCurrency(contest.requestedAmount)} icon={DollarSign} color="primary" />
        <KPICard label="Oferecido" value={contest.offeredAmount ? formatCurrency(contest.offeredAmount) : '—'} icon={Gavel} color="warning" />
        <KPICard label="Acordado" value={agreedAmount ? formatCurrency(agreedAmount) : '—'} icon={CheckCircle} color="success" />
        <KPICard label="Total Pago" value={formatCurrency(totalPaid)} icon={DollarSign} color="primary" />
        <KPICard label="Recuperação Líquida" value={formatCurrency(totalNetRecovery)} icon={CheckCircle} color="success" />
      </div>

      {/* Status Progress */}
      <div className="card">
        <CardHeader>
          <h3 className="font-semibold text-secondary-900">Progresso do Workflow</h3>
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
                EXPIRED: <Clock className="h-4 w-4" />,
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

      {/* Main Content Tabs */}
      <div className="card">
        <div className="border-b border-secondary-200">
          <nav className="flex gap-1 px-4" aria-label="Abas da contestação">
            <TabButton active={activeTab === 'timeline'} onClick={() => setActiveTab('timeline')}>
              <Clock className="h-4 w-4 mr-2" /> Timeline
            </TabButton>
            <TabButton active={activeTab === 'items'} onClick={() => setActiveTab('items')}>
              <FileText className="h-4 w-4 mr-2" /> Itens ({contest.items?.length ?? 0})
            </TabButton>
            <TabButton active={activeTab === 'communications'} onClick={() => setActiveTab('communications')}>
              <MessageSquare className="h-4 w-4 mr-2" /> Comunicações ({communications.length})
            </TabButton>
            <TabButton active={activeTab === 'payments'} onClick={() => setActiveTab('payments')}>
              <DollarSign className="h-4 w-4 mr-2" /> Pagamentos ({payments.length})
            </TabButton>
            <TabButton active={activeTab === 'success-fee'} onClick={() => setActiveTab('success-fee')}>
              <Calculator className="h-4 w-4 mr-2" /> Success Fee
            </TabButton>
          </nav>
        </div>

        <CardBody className="p-0">
          {activeTab === 'timeline' && (
            <div className="p-6">
              <ContestTimeline
                contest={contest}
                communications={communications}
                payments={payments}
              />
            </div>
          )}

          {activeTab === 'items' && (
            <div className="p-6">
              <ContestItemTable
                discrepancies={contest.items ?? []}
                isLoading={isLoadingContest}
              />
            </div>
          )}

          {activeTab === 'communications' && (
            <div className="p-6">
              <CommunicationThread
                communications={communications}
                isLoading={isLoadingComms}
                onAddCommunication={async (data) => { await addCommunication.mutateAsync(data); }}
                onDownloadAttachment={(url, name) => {
                  const link = document.createElement('a')
                  link.href = url
                  link.download = name
                  link.target = '_blank'
                  document.body.appendChild(link)
                  link.click()
                  document.body.removeChild(link)
                }}
                canSend={!isFinal}
                contestId={contest.id}
              />
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="p-6">
              <PaymentList
                payments={payments}
                isLoading={isLoadingPayments}
                onRegisterPayment={() => setShowPaymentModal(true)}
                canAdd={canAddPayment}
              />
            </div>
          )}

          {activeTab === 'success-fee' && (
            <div className="p-6">
              <SuccessFeeCalculator
                successFeePct={20}
                agreedAmount={agreedAmount}
                initialAmount={agreedAmount || contest.requestedAmount}
                onAmountChange={handleCalculateFee}
                showDetails={true}
              />
            </div>
          )}
        </CardBody>
      </div>

      {/* Modals */}
      {showNegotiateModal && (
        <NegotiateModal
          contest={contest}
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

// Helper Components
function KPICard({ label, value, icon: Icon, color }: { label: string; value: string; icon: React.ComponentType<{ className?: string }>; color: string }) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    secondary: 'bg-secondary-50 text-secondary-600',
    warning: 'bg-warning-50 text-warning-600',
    success: 'bg-success-50 text-success-600',
  }

  return (
    <div className="p-4 rounded-xl border border-secondary-200 bg-white">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-secondary-500">{label}</p>
          <p className="text-xl font-bold text-secondary-900 mt-1">{value}</p>
        </div>
        <div className={cn('p-3 rounded-lg', colorClasses[color as keyof typeof colorClasses] || colorClasses.primary)}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
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

// Payment List Component
function PaymentList({ payments, isLoading, onRegisterPayment, canAdd }: { payments: any[]; isLoading: boolean; onRegisterPayment: () => void; canAdd: boolean }) {
  if (isLoading) {
    return <div className="animate-pulse h-32" />
  }

  if (payments.length === 0) {
    return (
      <div className="p-8 text-center">
        <DollarSign className="mx-auto h-12 w-12 text-secondary-300 mb-3" />
        <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum pagamento registrado</h3>
        <p className="text-secondary-500 mb-4">Registre pagamentos recebidos para calcular o success fee</p>
        {canAdd && (
          <Button variant="primary" onClick={onRegisterPayment}>
            <DollarSign className="h-4 w-4 mr-2" />
            Registrar Primeiro Pagamento
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {payments.map((payment) => (
        <div key={payment.id} className="p-4 rounded-lg border border-secondary-200 bg-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-success-50">
                <DollarSign className="h-5 w-5 text-success-600" />
              </div>
              <div>
                <p className="font-medium text-secondary-900">{formatCurrency(payment.amount)}</p>
                <p className="text-sm text-secondary-500">{formatDateTime(payment.paidAt)}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-right">
              <div>
                <p className="text-xs text-secondary-500">Success Fee</p>
                <p className="font-mono font-medium text-warning-600">{formatCurrency(payment.successFee)}</p>
              </div>
              <div>
                <p className="text-xs text-secondary-500">Líquido</p>
                <p className="font-mono font-bold text-success-600">{formatCurrency(payment.netRecovery)}</p>
              </div>
              {payment.proofUrl && (
                <button
                  onClick={() => {
                    const link = document.createElement('a')
                    link.href = payment.proofUrl
                    link.download = `comprovante-${payment.id.slice(0, 8)}.pdf`
                    link.target = '_blank'
                    document.body.appendChild(link)
                    link.click()
                    document.body.removeChild(link)
                  }}
                  className="p-2 rounded-lg text-secondary-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                  title="Download comprovante"
                >
                  <Download className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
          {payment.notes && (
            <p className="mt-2 text-sm text-secondary-600 pl-12">{payment.notes}</p>
          )}
        </div>
      ))}
    </div>
  )
}

// Negotiate Modal
function NegotiateModal({ contest, onClose, onSubmit, isLoading, form, setForm }: { contest: Contest; onClose: () => void; onSubmit: () => Promise<void>; isLoading: boolean; form: NegotiationFormData; setForm: React.Dispatch<React.SetStateAction<NegotiationFormData>> }) {
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

        <SuccessFeeCalculator
          successFeePct={20}
          agreedAmount={form.offeredAmount}
          initialAmount={form.offeredAmount || contest.requestedAmount}
          showDetails={true}
        />

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

// Communication Modal
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