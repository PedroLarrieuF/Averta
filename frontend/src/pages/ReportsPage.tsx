import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart2, Download, Calendar, ChevronLeft } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent, Button, PageHeader, PageTitle, PageSubtitle } from '@/components'
import { ReportDashboard, ReportFilters, ExportPanel, ScheduleList, ScheduleForm } from '@/components'
import { useReportDashboard, useExportPDF, useExportExcel, useReportSchedules, useCreateReportSchedule, useUpdateReportSchedule, useDeleteReportSchedule, ReportFilters as ReportFiltersType, ScheduleResponse, ScheduleRequest } from '@/hooks/useReports'

export function ReportsPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'dashboard' | 'export' | 'schedule'>('dashboard')
  const [filters, setFilters] = useState<Record<string, unknown>>({ period: '30d' })
  const [showScheduleForm, setShowScheduleForm] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<ScheduleResponse | null>(null)

  // Sync filters with URL
  const updateFilters = (newFilters: Record<string, unknown>) => {
    setFilters(newFilters)
    const params = new URLSearchParams()
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        params.set(key, String(value))
      }
    })
    // Update URL without navigation
    window.history.replaceState({}, '', `/reports?${params.toString()}`)
  }

  const clearFilters = () => {
    updateFilters({ period: '30d' })
  }

  const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== '' && v !== null && v !== '30d')

  // Dashboard data
  const { data: dashboardData, isLoading: isLoadingDashboard } = useReportDashboard(filters as ReportFiltersType)

  // Export mutations
  const exportPDF = useExportPDF(filters as ReportFiltersType)
  const exportExcel = useExportExcel(filters as ReportFiltersType)

  // Schedules
  const { data: schedules, isLoading: isLoadingSchedules, refetch: refetchSchedules } = useReportSchedules()
  const createSchedule = useCreateReportSchedule()
  const updateSchedule = useUpdateReportSchedule()
  const deleteSchedule = useDeleteReportSchedule()

  const handleExportPDF = async () => {
    const blob = await exportPDF.mutateAsync()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `relatorio-discrepancias-${new Date().toISOString().split('T')[0]}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const handleExportExcel = async () => {
    const blob = await exportExcel.mutateAsync()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `relatorio-discrepancias-${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const handleCreateSchedule = async (data: ScheduleRequest) => {
    await createSchedule.mutateAsync(data)
    refetchSchedules()
    setShowScheduleForm(false)
    setEditingSchedule(null)
  }

  const handleUpdateSchedule = async (data: Partial<ScheduleRequest>) => {
    if (!editingSchedule) return
    await updateSchedule.mutateAsync({ id: editingSchedule.id, data })
    refetchSchedules()
    setShowScheduleForm(false)
    setEditingSchedule(null)
  }

  const handleDeleteSchedule = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir este agendamento?')) return
    await deleteSchedule.mutateAsync(id)
    refetchSchedules()
  }

  const handleToggleSchedule = async (id: string, isActive: boolean) => {
    await updateSchedule.mutateAsync({ id, data: { is_active: isActive } })
    refetchSchedules()
  }

  const handlePreviewSchedule = (schedule: ScheduleResponse) => {
    // Navigate to export page with schedule's filters
    const params = new URLSearchParams()
    Object.entries(schedule.filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        params.set(key, String(value))
      }
    })
    params.set('format', schedule.format)
    navigate(`/reports/export?${params.toString()}`)
  }

  const handleEditSchedule = (schedule: ScheduleResponse) => {
    setEditingSchedule(schedule)
    setShowScheduleForm(true)
  }

  const handleNewSchedule = () => {
    setEditingSchedule(null)
    setShowScheduleForm(true)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader>
        <div>
          <PageTitle>Relatórios</PageTitle>
          <PageSubtitle>Dashboards, exportação e agendamento de relatórios automáticos</PageSubtitle>
        </div>
        <Button variant="secondary" onClick={() => navigate('/dashboard')}>
          <ChevronLeft className="h-4 w-4 mr-2" />
          Voltar ao Dashboard
        </Button>
      </PageHeader>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'dashboard' | 'export' | 'schedule')} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="dashboard">
            <BarChart2 className="h-4 w-4 mr-2" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="export">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </TabsTrigger>
          <TabsTrigger value="schedule">
            <Calendar className="h-4 w-4 mr-2" />
            Agendar
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          <ReportFilters
            filters={filters}
            onFiltersChange={updateFilters}
            onClearFilters={clearFilters}
            hasActiveFilters={hasActiveFilters}
          />
          <ReportDashboard data={dashboardData} isLoading={isLoadingDashboard} />
        </TabsContent>

        {/* Export Tab */}
        <TabsContent value="export" className="space-y-6">
          <ReportFilters
            filters={filters}
            onFiltersChange={updateFilters}
            onClearFilters={clearFilters}
            hasActiveFilters={hasActiveFilters}
          />
          <ExportPanel
            filters={filters}
            kpis={dashboardData?.kpis}
            onExportPDF={handleExportPDF}
            onExportExcel={handleExportExcel}
          />
        </TabsContent>

        {/* Schedule Tab */}
        <TabsContent value="schedule" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-medium text-secondary-900">Agendamentos de Relatórios</h3>
            <Button variant="primary" onClick={handleNewSchedule}>
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Novo Agendamento
            </Button>
          </div>

          <ScheduleList
            schedules={schedules ?? []}
            onEdit={handleEditSchedule}
            onToggle={handleToggleSchedule}
            onDelete={handleDeleteSchedule}
            onPreview={handlePreviewSchedule}
            isLoading={isLoadingSchedules}
          />

          {/* Schedule Form Modal */}
          {showScheduleForm && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
              <div className="w-full max-w-2xl max-h-[90vh] overflow-auto bg-white rounded-xl shadow-xl">
                <div className="p-6 border-b border-secondary-200 sticky top-0 bg-white z-10">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-secondary-900">
                      {editingSchedule ? 'Editar Agendamento' : 'Novo Agendamento'}
                    </h3>
                    <button
                      onClick={() => { setShowScheduleForm(false); setEditingSchedule(null); }}
                      className="p-2 text-secondary-400 hover:text-secondary-600"
                    >
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div className="p-6">
                  <ScheduleForm
                    initialData={editingSchedule}
                    onSubmit={editingSchedule ? handleUpdateSchedule : handleCreateSchedule}
                    onCancel={() => { setShowScheduleForm(false); setEditingSchedule(null); }}
                    isSubmitting={createSchedule.isPending || updateSchedule.isPending}
                  />
                </div>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}