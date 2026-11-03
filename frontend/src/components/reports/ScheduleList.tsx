import { useState } from 'react'
import { formatDateTime } from '@/utils/helpers'
import { Edit, Trash2, Pause, Play, Eye, Loader2 } from 'lucide-react'
import { Button, Badge, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components'
import { ScheduleResponse } from '@/hooks/useReports'

interface ScheduleListProps {
  schedules: ScheduleResponse[]
  onEdit: (schedule: ScheduleResponse) => void
  onToggle: (id: string, isActive: boolean) => Promise<void>
  onDelete: (id: string) => Promise<void>
  onPreview: (schedule: ScheduleResponse) => void
  isLoading?: boolean
}

const FORMAT_LABELS: Record<string, string> = {
  pdf: 'PDF',
  excel: 'Excel',
}

const DAY_LABELS = [
  'Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'
]

export function ScheduleList({ schedules, onEdit, onToggle, onDelete, onPreview, isLoading = false }: ScheduleListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-16 bg-secondary-100 rounded-lg" />
        <div className="h-16 bg-secondary-100 rounded-lg" />
        <div className="h-16 bg-secondary-100 rounded-lg" />
      </div>
    )
  }

  if (schedules.length === 0) {
    return (
      <div className="card p-12 text-center">
        <div className="mx-auto h-16 w-16 text-secondary-300 mb-4">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="h-16 w-16">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhum agendamento</h3>
        <p className="text-secondary-500 mb-4">Crie seu primeiro agendamento de relatório automático</p>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <div className="card-header border-b border-secondary-200">
        <h3 className="font-medium text-secondary-900">Agendamentos Configurados</h3>
      </div>
      <div className="divide-y divide-secondary-200">
        {schedules.map((schedule) => (
          <div key={schedule.id} className="p-4 hover:bg-secondary-50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-medium text-secondary-900 truncate">{schedule.name}</h4>
                  <Badge variant={schedule.is_active ? 'success' : 'secondary'}>
                    {schedule.is_active ? 'Ativo' : 'Pausado'}
                  </Badge>
                  <Badge variant="primary">{FORMAT_LABELS[schedule.format]}</Badge>
                </div>
                <div className="flex flex-wrap items-center gap-4 text-sm text-secondary-500">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-primary-500" />
                    {DAY_LABELS[schedule.day_of_week]} às {schedule.hour.toString().padStart(2, '0')}:00
                  </span>
                  <span>Destinatários: {schedule.recipients.length}</span>
                  {schedule.last_run_at && (
                    <span>Última execução: {formatDateTime(schedule.last_run_at)}</span>
                  )}
                  {schedule.next_run_at && (
                    <span className="text-primary-600 font-medium">Próxima: {formatDateTime(schedule.next_run_at)}</span>
                  )}
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {Object.entries(schedule.filters).map(([key, value]) => {
                    if (value === undefined || value === '' || value === null) return null
                    return (
                      <Badge key={key} variant="secondary" className="gap-1">
                        {key}: {String(value)}
                      </Badge>
                    )
                  })}
                </div>
              </div>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                    </svg>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={() => onPreview(schedule)}>
                    <Eye className="h-4 w-4 mr-2" />
                    Visualizar
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onEdit(schedule)}>
                    <Edit className="h-4 w-4 mr-2" />
                    Editar
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => onToggle(schedule.id, !schedule.is_active)}
                    className={schedule.is_active ? 'text-warning-600' : 'text-success-600'}
                  >
                    {schedule.is_active ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                    {schedule.is_active ? 'Pausar' : 'Ativar'}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => {
                      setDeletingId(schedule.id)
                      onDelete(schedule.id).finally(() => setDeletingId(null))
                    }}
                    disabled={deletingId === schedule.id}
                    className="text-danger-600"
                  >
                    {deletingId === schedule.id ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4 mr-2" />
                    )}
                    Excluir
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}