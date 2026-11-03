import { useEffect, useMemo } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { ContestCreateStepper, PageHeader, PageTitle, PageSubtitle, Button } from '@/components'
import toast from 'react-hot-toast'

export function ContestCreatePage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  // Get discrepancy IDs from URL params
  const discrepancyIdsParam = searchParams.get('discrepancyIds')
  const initialDiscrepancyIds = useMemo(
    () => (discrepancyIdsParam ? discrepancyIdsParam.split(',').filter(Boolean) : []),
    [discrepancyIdsParam]
  )

  const handleComplete = (contestId: string) => {
    toast.success('Contestação criada com sucesso!')
    navigate(`/contests/${contestId}`)
  }

  const handleCancel = () => {
    navigate('/contests')
  }

  // If coming from discrepancies page with selection, pre-fill
  useEffect(() => {
    if (initialDiscrepancyIds.length > 0) {
      toast.success(`${initialDiscrepancyIds.length} discrepância(s) selecionada(s) para contestação`)
    }
  }, [initialDiscrepancyIds])

  return (
    <div className="space-y-6">
      <PageHeader>
        <div>
          <PageTitle>Nova Contestação</PageTitle>
          <PageSubtitle>Selecione discrepâncias, revise e crie a contestação para envio à transportadora</PageSubtitle>
        </div>
        <Button variant="secondary" onClick={handleCancel}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </Button>
      </PageHeader>

      <div className="max-w-4xl mx-auto">
        <ContestCreateStepper
          initialDiscrepancyIds={initialDiscrepancyIds}
          onComplete={handleComplete}
          onCancel={handleCancel}
        />
      </div>
    </div>
  )
}