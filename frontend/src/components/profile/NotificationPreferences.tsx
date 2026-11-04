import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Switch } from '../Switch'
import { Card, CardHeader, CardBody } from '../Card'

export const notificationPreferencesSchema = z.object({
  email_enabled: z.boolean(),
  in_app_enabled: z.boolean(),
  weekly_report: z.boolean(),
  discrepancy_alerts: z.boolean(),
  contest_updates: z.boolean(),
})

export type NotificationPreferencesData = z.infer<typeof notificationPreferencesSchema>

interface NotificationPreferencesProps {
  initialData: NotificationPreferencesData
  onSubmit: (data: NotificationPreferencesData) => Promise<void>
  isSubmitting?: boolean
}

const preferences = [
  {
    key: 'email_enabled',
    label: 'Notificações por email',
    description: 'Receba emails para todas as notificações do sistema',
  },
  {
    key: 'in_app_enabled',
    label: 'Notificações no aplicativo',
    description: 'Veja notificações no sino de notificações no cabeçalho',
  },
  {
    key: 'weekly_report',
    label: 'Relatório semanal',
    description: 'Receba resumo semanal de discrepâncias e contestações',
  },
  {
    key: 'discrepancy_alerts',
    label: 'Alertas de discrepâncias',
    description: 'Seja notificado quando novas discrepâncias forem detectadas',
  },
  {
    key: 'contest_updates',
    label: 'Atualizações de contestações',
    description: 'Acompanhe o status das suas contestações em tempo real',
  },
] as const

export function NotificationPreferences({
  initialData,
  onSubmit,
  isSubmitting = false,
}: NotificationPreferencesProps) {
  const {
    register,
    handleSubmit,
    watch,
  } = useForm<NotificationPreferencesData>({
    resolver: zodResolver(notificationPreferencesSchema),
    defaultValues: initialData,
  })

  return (
    <Card>
      <CardHeader className="pb-2">
        <h3 className="text-lg font-semibold text-secondary-900">Preferências de Notificação</h3>
        <p className="text-sm text-secondary-500 mt-1">
          Configure como e quando você deseja ser notificado
        </p>
      </CardHeader>
      <CardBody className="pt-0">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {preferences.map((pref) => (
            <div
              key={pref.key}
              className="flex items-center justify-between py-3 border-b border-secondary-100 last:border-0"
            >
              <div className="flex-1">
                <label className="font-medium text-secondary-900">{pref.label}</label>
                <p className="text-sm text-secondary-500">{pref.description}</p>
              </div>
              <Switch
                {...register(pref.key)}
                checked={watch(pref.key)}
                disabled={isSubmitting}
              />
            </div>
          ))}
        </form>
      </CardBody>
    </Card>
  )
}