import { CheckCircle, Clock, FileText, Send, Users, XCircle, AlertTriangle, MessageSquare, DollarSign } from 'lucide-react'
import { Badge } from '@/components'
import { Contest, ContestStatus } from '@/types'
import { formatDateTime, getStatusBadge, cn } from '@/utils/helpers'

interface CommunicationMetadata {
  subject: string
  body: string
  type: 'INBOUND' | 'OUTBOUND'
  createdAt: string
}

interface PaymentMetadata {
  amount: number
  successFee: number
  netRecovery: number
  paidAt: string
}

interface TimelineEvent {
  id: string
  type: 'created' | 'pdf_generated' | 'sent' | 'acknowledged' | 'negotiating' | 'communication' | 'payment' | 'accepted' | 'partial' | 'rejected' | 'expired'
  title: string
  description: string
  timestamp: string
  metadata?: { communication: CommunicationMetadata } | { payment: PaymentMetadata }
  icon: React.ReactNode
  color: 'primary' | 'success' | 'warning' | 'danger' | 'secondary'
}

const statusEvents: Record<ContestStatus, TimelineEvent['type'][]> = {
  DRAFT: ['created'],
  SENT: ['created', 'pdf_generated', 'sent'],
  ACKNOWLEDGED: ['created', 'pdf_generated', 'sent', 'acknowledged'],
  NEGOTIATING: ['created', 'pdf_generated', 'sent', 'acknowledged', 'negotiating'],
  ACCEPTED: ['created', 'pdf_generated', 'sent', 'acknowledged', 'accepted'],
  PARTIAL: ['created', 'pdf_generated', 'sent', 'acknowledged', 'partial'],
  REJECTED: ['created', 'pdf_generated', 'sent', 'acknowledged', 'rejected'],
  EXPIRED: ['created', 'pdf_generated', 'sent', 'expired'],
}

const eventConfig: Record<TimelineEvent['type'], { title: string; description: string; icon: React.ReactNode; color: TimelineEvent['color'] }> = {
  created: { title: 'Contestação criada', description: 'Rascunho inicial salvo', icon: <FileText className="h-4 w-4" />, color: 'secondary' },
  pdf_generated: { title: 'PDF gerado', description: 'Carta de contestação gerada', icon: <FileText className="h-4 w-4" />, color: 'primary' },
  sent: { title: 'Enviada à transportadora', description: 'Carta enviada por email/portal', icon: <Send className="h-4 w-4" />, color: 'primary' },
  acknowledged: { title: 'Recebida pela transportadora', description: 'Confirmação de recebimento', icon: <CheckCircle className="h-4 w-4" />, color: 'success' },
  negotiating: { title: 'Em negociação', description: 'Contraproposta ou discussão iniciada', icon: <Users className="h-4 w-4" />, color: 'warning' },
  communication: { title: 'Nova comunicação', description: 'Mensagem trocada', icon: <MessageSquare className="h-4 w-4" />, color: 'primary' },
  payment: { title: 'Pagamento registrado', description: 'Valor recebido e success fee calculado', icon: <DollarSign className="h-4 w-4" />, color: 'success' },
  accepted: { title: 'Contestação aceita', description: 'Valor integral acordado', icon: <CheckCircle className="h-4 w-4" />, color: 'success' },
  partial: { title: 'Aceita parcialmente', description: 'Valor parcial acordado', icon: <AlertTriangle className="h-4 w-4" />, color: 'warning' },
  rejected: { title: 'Contestação rejeitada', description: 'Transportadora não aceitou', icon: <XCircle className="h-4 w-4" />, color: 'danger' },
  expired: { title: 'Contestação expirada', description: 'Prazo de resposta esgotado', icon: <Clock className="h-4 w-4" />, color: 'danger' },
}

interface ContestTimelineProps {
  contest: Contest
  communications?: Array<{
    id: string
    type: 'INBOUND' | 'OUTBOUND'
    subject: string
    body: string
    createdAt: string
  }>
  payments?: Array<{
    id: string
    amount: number
    successFee: number
    netRecovery: number
    paidAt: string
  }>
  className?: string
}

export function ContestTimeline({ contest, communications = [], payments = [], className }: ContestTimelineProps) {
  // Build timeline events from contest status and related data
  const baseEvents = statusEvents[contest.status] || ['created']
  const events: TimelineEvent[] = []

  // Add base status events
  baseEvents.forEach((type, index) => {
    const config = eventConfig[type]
    // Use contest timestamps where available
    let timestamp = contest.createdAt
    if (type === 'sent' && contest.sentAt) timestamp = contest.sentAt
    if (type === 'acknowledged' && contest.acknowledgedAt) timestamp = contest.acknowledgedAt
    if (type === 'accepted' || type === 'partial' || type === 'rejected') timestamp = contest.resolvedAt || contest.updatedAt

    events.push({
      id: `${type}-${index}`,
      type,
      title: config.title,
      description: config.description,
      timestamp,
      icon: config.icon,
      color: config.color,
    })
  })

  // Add communications
  communications.forEach((comm) => {
    events.push({
      id: `comm-${comm.id}`,
      type: 'communication',
      title: `${comm.type === 'INBOUND' ? 'Recebida' : 'Enviada'}: ${comm.subject}`,
      description: comm.body.substring(0, 100) + (comm.body.length > 100 ? '...' : ''),
      timestamp: comm.createdAt,
      icon: <MessageSquare className="h-4 w-4" />,
      color: 'primary',
      metadata: { communication: comm },
    })
  })

  // Add payments
  payments.forEach((payment) => {
    events.push({
      id: `payment-${payment.id}`,
      type: 'payment',
      title: `Pagamento recebido: ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(payment.amount)}`,
      description: `Success fee: ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(payment.successFee)} • Líquido: ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(payment.netRecovery)}`,
      timestamp: payment.paidAt,
      icon: <DollarSign className="h-4 w-4" />,
      color: 'success',
      metadata: { payment },
    })
  })

  // Sort by timestamp (newest first)
  events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

  return (
    <div className={cn('space-y-6', className)}>
      {events.map((event, index) => (
        <div key={event.id} className="relative flex gap-4">
          {/* Timeline line */}
          <div className="relative flex-shrink-0 w-6">
            <div className="absolute left-1/2 top-0 bottom-0 w-0.5" style={{ backgroundColor: index < events.length - 1 ? getColorClass(event.color) : 'transparent' }} />
            <div
              className={cn(
                'relative w-4 h-4 rounded-full border-4 flex-shrink-0 mx-auto',
                getBgColorClass(event.color)
              )}
            >
              {event.icon}
            </div>
          </div>

          {/* Event content */}
          <div className="flex-1 min-w-0 pt-1">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium text-secondary-900">{event.title}</h4>
                  <Badge variant={event.color === 'danger' ? 'danger' : event.color === 'warning' ? 'warning' : event.color === 'success' ? 'success' : event.color === 'primary' ? 'primary' : 'secondary'}>
                    {formatDateTime(event.timestamp)}
                  </Badge>
                </div>
                <p className="text-sm text-secondary-500 mt-1">{event.description}</p>
                {event.metadata && 'communication' in event.metadata && (
                  <div className="mt-2 p-3 rounded-lg bg-secondary-50 border border-secondary-200 text-sm">
                    <p className="font-medium text-secondary-900">{event.metadata.communication.subject}</p>
                    <p className="text-secondary-600 mt-1">{event.metadata.communication.body}</p>
                  </div>
                )}
                {event.metadata && 'payment' in event.metadata && (
                  <div className="mt-2 p-3 rounded-lg bg-success-50 border border-success-200 text-sm">
                    <div className="flex gap-4 text-sm">
                      <span>Valor: <span className="font-mono font-medium">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(event.metadata.payment.amount)}</span></span>
                      <span>Success Fee: <span className="font-mono font-medium">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(event.metadata.payment.successFee)}</span></span>
                      <span>Líquido: <span className="font-mono font-medium text-success-600">{new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(event.metadata.payment.netRecovery)}</span></span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Current status indicator */}
      <div className="relative flex gap-4 pt-2">
        <div className="relative flex-shrink-0 w-6">
          <div className="relative w-4 h-4 rounded-full border-4 flex-shrink-0 mx-auto" style={{ borderColor: getStatusColor(contest.status) }}>
            <div className="absolute inset-0 rounded-full" style={{ backgroundColor: getStatusColor(contest.status) }} />
          </div>
        </div>
        <div className="flex-1 pt-1">
          <div className="flex items-center gap-2">
            <span className="font-medium text-secondary-900">Status atual</span>
            <Badge variant={getStatusBadge(contest.status).variant as 'primary' | 'secondary' | 'danger' | 'success' | 'warning'}>
              {getStatusBadge(contest.status).label}
            </Badge>
          </div>
          <p className="text-sm text-secondary-500 mt-1">
            {getStatusDescription(contest.status)}
          </p>
        </div>
      </div>
    </div>
  )
}

function getColorClass(color: TimelineEvent['color']): string {
  switch (color) {
    case 'primary': return 'bg-primary-500'
    case 'success': return 'bg-success-500'
    case 'warning': return 'bg-warning-500'
    case 'danger': return 'bg-danger-500'
    default: return 'bg-secondary-300'
  }
}

function getBgColorClass(color: TimelineEvent['color']): string {
  switch (color) {
    case 'primary': return 'bg-primary-500 text-white border-primary-500'
    case 'success': return 'bg-success-500 text-white border-success-500'
    case 'warning': return 'bg-warning-500 text-white border-warning-500'
    case 'danger': return 'bg-danger-500 text-white border-danger-500'
    default: return 'bg-secondary-200 text-secondary-500 border-secondary-200'
  }
}

function getStatusColor(status: ContestStatus): string {
  const { variant } = getStatusBadge(status)
  switch (variant) {
    case 'badge-primary': return '#3b82f6'
    case 'badge-success': return '#22c55e'
    case 'badge-warning': return '#f59e0b'
    case 'badge-danger': return '#ef4444'
    default: return '#94a3b8'
  }
}

function getStatusDescription(status: ContestStatus): string {
  switch (status) {
    case 'DRAFT': return 'A contestação está em rascunho. Gere o PDF e envie para a transportadora.'
    case 'SENT': return 'A contestação foi enviada. Aguardando confirmação de recebimento.'
    case 'ACKNOWLEDGED': return 'A transportadora confirmou o recebimento. Aguardando resposta.'
    case 'NEGOTIATING': return 'Em processo de negociação. Contrapropostas podem ser registradas.'
    case 'ACCEPTED': return 'A contestação foi aceita integralmente. Registre o pagamento recebido.'
    case 'PARTIAL': return 'A contestação foi aceita parcialmente. Registre o pagamento acordado.'
    case 'REJECTED': return 'A contestação foi rejeitada pela transportadora.'
    case 'EXPIRED': return 'O prazo para resposta da transportadora expirou.'
    default: return ''
  }
}