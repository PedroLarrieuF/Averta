import { useState } from 'react'
import { useAuth } from '../store/auth-context'
import {
  useUserProfile,
  useUpdateUserProfile,
  useNotificationPreferences,
  useUpdateNotificationPreferences,
  useChangePassword,
  useDeleteAccount,
} from '../hooks'
import { PageHeader, PageTitle, PageSubtitle } from '../components/PageHeader'
import { Card, CardBody } from '../components/Card'
import { Button } from '../components/Button'
import { Alert, AlertTitle, AlertDescription } from '../components/Alert'
import {
  ProfileHeader,
  ProfileForm,
  ChangePasswordModal,
  NotificationPreferences,
  DangerZone,
  type ProfileFormData,
  type ChangePasswordFormData,
  type NotificationPreferencesData,
} from '../components/profile'
import { formatDate } from '../utils/helpers'

export function Profile() {
  const { isAuthenticated } = useAuth()

  // Fetch user profile
  const { data: profile, isLoading: isProfileLoading, refetch: refetchProfile } = useUserProfile()

  // Fetch notification preferences
  const { data: notifications } = useNotificationPreferences()

  // Mutations
  const updateProfileMutation = useUpdateUserProfile()
  const changePasswordMutation = useChangePassword()
  const updateNotifMutation = useUpdateNotificationPreferences()
  const deleteAccountMutation = useDeleteAccount()

  // Local state
  const [isPasswordOpen, setIsPasswordOpen] = useState(false)

  // Handlers
  const handleProfileSubmit = async (data: ProfileFormData) => {
    await updateProfileMutation.mutateAsync(data)
    refetchProfile()
  }

  const handlePasswordSubmit = async (data: ChangePasswordFormData) => {
    await changePasswordMutation.mutateAsync({
      current_password: data.current_password,
      new_password: data.new_password,
    })
    setIsPasswordOpen(false)
  }

  const handleNotifSubmit = async (data: NotificationPreferencesData) => {
    await updateNotifMutation.mutateAsync(data)
  }

  const handleDeleteAccount = async (password: string) => {
    await deleteAccountMutation.mutateAsync(password)
    // The auth context should handle logout after deletion
  }

  if (isProfileLoading) {
    return (
      <div className="space-y-6">
        <PageHeader>
          <PageTitle>Perfil</PageTitle>
          <PageSubtitle>Gerencie seu perfil e preferências</PageSubtitle>
        </PageHeader>
        <div className="card p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent mx-auto" />
        </div>
      </div>
    )
  }

  if (!profile || !isAuthenticated) {
    return (
      <div className="space-y-6">
        <PageHeader>
          <PageTitle>Perfil</PageTitle>
          <PageSubtitle>Gerencie seu perfil e preferências</PageSubtitle>
        </PageHeader>
        <Alert variant="destructive">
          <AlertTitle>Erro ao carregar perfil</AlertTitle>
          <AlertDescription>Não foi possível carregar seus dados. Tente recarregar a página.</AlertDescription>
        </Alert>
      </div>
    )
  }

  const initialProfileData: ProfileFormData = {
    name: profile.fullName,
    email: profile.email,
    phone: '', // User type doesn't have phone, use empty string
  }

  const initialNotifData: NotificationPreferencesData = {
    email_enabled: notifications?.email_enabled ?? true,
    in_app_enabled: notifications?.in_app_enabled ?? true,
    weekly_report: notifications?.weekly_report ?? true,
    discrepancy_alerts: notifications?.discrepancy_alerts ?? true,
    contest_updates: notifications?.contest_updates ?? true,
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <PageHeader>
        <PageTitle>Perfil</PageTitle>
        <PageSubtitle>Gerencie seu perfil, senha e preferências de notificação</PageSubtitle>
      </PageHeader>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Left column - Profile Header & Info */}
        <div className="md:col-span-2 space-y-6">
          <ProfileHeader />

          {/* Edit Profile Section */}
          <Card>
            <CardBody className="pt-0">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-secondary-900">Informações do Perfil</h3>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsPasswordOpen(true)} // This will be handled by ProfileForm's internal state
                  disabled={updateProfileMutation.isPending}
                >
                  Editar perfil
                </Button>
              </div>
              <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm text-secondary-500">Nome completo</dt>
                  <dd className="font-medium text-secondary-900">{profile.fullName}</dd>
                </div>
                <div>
                  <dt className="text-sm text-secondary-500">Email</dt>
                  <dd className="font-medium text-secondary-900">{profile.email}</dd>
                </div>
                <div>
                  <dt className="text-sm text-secondary-500">Empresa</dt>
                  <dd className="font-medium text-secondary-900">{profile.companyId ? `ID: ${profile.companyId}` : 'Não vinculado'}</dd>
                </div>
              </dl>
            </CardBody>
          </Card>

          {/* Notification Preferences */}
          <NotificationPreferences
            initialData={initialNotifData}
            onSubmit={handleNotifSubmit}
            isSubmitting={updateNotifMutation.isPending}
          />
        </div>

        {/* Right column - Security & Danger Zone */}
        <div className="space-y-6">
          {/* Change Password */}
          <Card>
            <CardBody className="pt-0">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-secondary-900">Segurança</h3>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsPasswordOpen(true)}
                  disabled={changePasswordMutation.isPending}
                >
                  Alterar senha
                </Button>
              </div>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between py-2 border-b border-secondary-100">
                  <span className="text-secondary-500">Última alteração</span>
                  <span className="font-medium text-secondary-900">
                    {profile.createdAt ? formatDate(profile.createdAt) : 'Nunca'}
                  </span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-secondary-500">Autenticação de dois fatores</span>
                  <span className="font-medium text-secondary-900">Não configurada</span>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Danger Zone */}
          <DangerZone
            onDeleteAccount={handleDeleteAccount}
            isDeleting={deleteAccountMutation.isPending}
          />
        </div>
      </div>

      {/* Modals */}
      <ProfileForm
        initialData={initialProfileData}
        onSubmit={handleProfileSubmit}
        onCancel={() => {}}
        isSubmitting={updateProfileMutation.isPending}
      />

      <ChangePasswordModal
        open={isPasswordOpen}
        onOpenChange={setIsPasswordOpen}
        onSubmit={handlePasswordSubmit}
        isSubmitting={changePasswordMutation.isPending}
      />
    </div>
  )
}