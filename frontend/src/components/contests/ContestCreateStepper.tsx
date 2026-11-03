import { useState, useCallback } from 'react'
import { Check, FileText, Gavel, Eye, AlertTriangle, ArrowLeft, ArrowRight } from 'lucide-react'
import { Button, Input, Badge, CardHeader, CardBody, CardFooter } from '@/components'
import { Discrepancy } from '@/types'
import { formatCurrency, getSeverityBadge, getStatusBadge, cn } from '@/utils/helpers'
import { useDiscrepancies } from '@/hooks'
import toast from 'react-hot-toast'

interface ContestCreateStepperProps {
  initialDiscrepancyIds?: string[]
  onComplete: (contestId: string) => void
  onCancel: () => void
}

type Step = 1 | 2 | 3

const stepLabels: Record<Step, { label: string; description: string; icon: React.ReactNode }> = {
  1: {
    label: 'Selecionar Discrepâncias',
    description: 'Escolha as discrepâncias para incluir na contestação',
    icon: <AlertTriangle className="h-5 w-5" />,
  },
  2: {
    label: 'Revisar Contestação',
    description: 'Revise os detalhes e configure a contestação',
    icon: <FileText className="h-5 w-5" />,
  },
  3: {
    label: 'Confirmar e Criar',
    description: 'Confirme os dados e crie a contestação',
    icon: <Gavel className="h-5 w-5" />,
  },
}

export function ContestCreateStepper({ initialDiscrepancyIds = [], onComplete, onCancel }: ContestCreateStepperProps) {
  const [currentStep, setCurrentStep] = useState<Step>(1)
  const [selectedDiscrepancyIds, setSelectedDiscrepancyIds] = useState<string[]>(initialDiscrepancyIds)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Fetch selected discrepancies for review step
  const { data: discrepanciesData, isLoading: isLoadingDiscrepancies } = useDiscrepancies({
    ids: selectedDiscrepancyIds.join(','),
    size: 100,
  })

  const discrepancies = discrepanciesData?.data ?? []
  const totalRequestedAmount = discrepancies.reduce((sum, d) => sum + d.difference, 0)

  const handleNext = useCallback(() => {
    if (currentStep === 1 && selectedDiscrepancyIds.length === 0) {
      toast.error('Selecione pelo menos uma discrepância')
      return
    }
    if (currentStep === 2 && !title.trim()) {
      toast.error('Informe um título para a contestação')
      return
    }
    if (currentStep < 3) {
      setCurrentStep((s) => (s + 1) as Step)
    }
  }, [currentStep, selectedDiscrepancyIds, title])

  const handleBack = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep((s) => (s - 1) as Step)
    }
  }, [currentStep])

  const handleSubmit = async () => {
    if (selectedDiscrepancyIds.length === 0) {
      toast.error('Nenhuma discrepância selecionada')
      return
    }
    if (!title.trim()) {
      toast.error('Título é obrigatório')
      return
    }

    setIsSubmitting(true)
    try {
      // This would call the API to create the contest
      // For now, we'll simulate and call onComplete
      // In real implementation, this would use useCreateContestFromDiscrepancies hook
      const mockContestId = `contest-${Date.now()}`
      toast.success('Contestação criada com sucesso!')
      onComplete(mockContestId)
    } catch (_error) {
      toast.error('Erro ao criar contestação')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDiscrepancySelectionChange = (ids: string[]) => {
    setSelectedDiscrepancyIds(ids)
  }

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <div className="flex items-center justify-between">
        {([1, 2, 3] as Step[]).map((step) => (
          <div key={step} className="flex items-center">
            <div
              className={cn(
                'flex items-center justify-center w-10 h-10 rounded-full text-sm font-medium transition-all',
                currentStep > step
                  ? 'bg-success-500 text-white'
                  : currentStep === step
                  ? 'bg-primary-500 text-white'
                  : 'bg-secondary-200 text-secondary-500'
              )}
            >
              {currentStep > step ? (
                <Check className="h-5 w-5" />
              ) : (
                step
              )}
            </div>
            {step < 3 && (
              <div
                className={cn(
                  'w-24 h-0.5 mx-2',
                  currentStep > step ? 'bg-success-500' : 'bg-secondary-200'
                )}
              />
            )}
            <div className="hidden sm:block w-32 text-center">
              <p className={cn('text-sm font-medium', currentStep >= step ? 'text-secondary-900' : 'text-secondary-500')}>
                {stepLabels[step].label}
              </p>
              <p className={cn('text-xs', currentStep >= step ? 'text-secondary-500' : 'text-secondary-400')}>
                {stepLabels[step].description}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="card">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary-50 text-primary-600">
              {stepLabels[currentStep].icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-secondary-900">{stepLabels[currentStep].label}</h3>
              <p className="text-sm text-secondary-500">{stepLabels[currentStep].description}</p>
            </div>
          </div>
        </CardHeader>

        <CardBody className="py-4">
          {currentStep === 1 && (
            <DiscrepancySelectionStep
              selectedIds={selectedDiscrepancyIds}
              onSelectionChange={handleDiscrepancySelectionChange}
              isLoading={isLoadingDiscrepancies}
            />
          )}

          {currentStep === 2 && (
            <ReviewStep
              discrepancies={discrepancies}
              totalAmount={totalRequestedAmount}
              title={title}
              setTitle={setTitle}
              description={description}
              setDescription={setDescription}
              isLoading={isLoadingDiscrepancies}
            />
          )}

          {currentStep === 3 && (
            <ConfirmStep
              discrepancies={discrepancies}
              totalAmount={totalRequestedAmount}
              title={title}
              description={description}
            />
          )}
        </CardBody>

        <CardFooter className="flex justify-between pt-4 border-t border-secondary-200">
          {currentStep === 1 && (
            <Button variant="secondary" onClick={onCancel}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
          )}
          {currentStep > 1 && (
            <Button variant="secondary" onClick={handleBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar
            </Button>
          )}
          {currentStep < 3 && (
            <Button variant="primary" onClick={handleNext}>
              Próximo
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}
          {currentStep === 3 && (
            <Button variant="primary" onClick={handleSubmit} loading={isSubmitting}>
              <Check className="h-4 w-4 mr-2" />
              Criar Contestação
            </Button>
          )}
        </CardFooter>
      </div>
    </div>
  )
}

// Step 1: Select Discrepancies
function DiscrepancySelectionStep({
  selectedIds,
  onSelectionChange,
  isLoading,
}: {
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  isLoading: boolean
}) {
  const { data: allDiscrepanciesData } = useDiscrepancies({ status: 'OPEN', size: 100 })
  const allDiscrepancies = allDiscrepanciesData?.data ?? []

  if (isLoading) {
    return <div className="animate-pulse h-64" />
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-secondary-500">
          {selectedIds.length} de {allDiscrepancies.length} discrepâncias selecionadas
        </p>
        {selectedIds.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => onSelectionChange([])}>
            Limpar seleção
          </Button>
        )}
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {allDiscrepancies.map((discrepancy) => {
          const isSelected = selectedIds.includes(discrepancy.id)
          const { variant: severityVariant, label: severityLabel } = getSeverityBadge(discrepancy.severity)
          const { variant: statusVariant, label: statusLabel } = getStatusBadge(discrepancy.status)

          return (
            <label
              key={discrepancy.id}
              className={cn(
                'flex items-center gap-4 p-3 rounded-lg border transition-colors cursor-pointer',
                isSelected
                  ? 'bg-primary-50 border-primary-200'
                  : 'bg-white border-secondary-200 hover:bg-secondary-50'
              )}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                  const newIds = e.target.checked
                    ? [...selectedIds, discrepancy.id]
                    : selectedIds.filter((id) => id !== discrepancy.id)
                  onSelectionChange(newIds)
                }}
                className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500 h-4 w-4"
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-secondary-900 truncate">{discrepancy.description}</span>
                  <Badge variant={severityVariant as 'primary' | 'secondary' | 'danger' | 'success' | 'warning'} className="text-xs">
                    {severityLabel}
                  </Badge>
                  <Badge variant={statusVariant as 'primary' | 'secondary' | 'danger' | 'success' | 'warning'} className="text-xs">
                    {statusLabel}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-sm text-secondary-500 mt-1">
                  <span>Valor esperado: <span className="font-mono font-medium text-secondary-900">{formatCurrency(discrepancy.expectedValue)}</span></span>
                  <span>Valor atual: <span className="font-mono font-medium text-secondary-900">{formatCurrency(discrepancy.actualValue)}</span></span>
                  <span className={discrepancy.difference > 0 ? 'text-danger-600' : 'text-success-600'}>
                    Diferença: {discrepancy.difference > 0 ? '+' : ''}{formatCurrency(discrepancy.difference)}
                  </span>
                </div>
              </div>
            </label>
          )
        })}
      </div>

      {allDiscrepancies.length === 0 && (
        <div className="p-8 text-center">
          <AlertTriangle className="mx-auto h-12 w-12 text-secondary-300 mb-3" />
          <p className="text-secondary-500">Nenhuma discrepância aberta disponível para seleção</p>
        </div>
      )}
    </div>
  )
}

// Step 2: Review
function ReviewStep({
  discrepancies,
  totalAmount,
  title,
  setTitle,
  description,
  setDescription,
  isLoading,
}: {
  discrepancies: Discrepancy[]
  totalAmount: number
  title: string
  setTitle: (v: string) => void
  description: string
  setDescription: (v: string) => void
  isLoading: boolean
}) {
  if (isLoading) {
    return <div className="animate-pulse h-64" />
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Título da Contestação *</label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ex: Contestação de fretes interestaduais - Janeiro 2024"
            required
          />
        </div>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Valor Total Solicitado</label>
          <div className="p-3 rounded-lg bg-secondary-50 border border-secondary-200 font-mono text-xl font-bold text-secondary-900">
            {formatCurrency(totalAmount)}
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-secondary-700">Descrição</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Descreva os fundamentos da contestação, referências legais, etc."
          rows={4}
          className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      <div className="border-t border-secondary-200 pt-4">
        <h4 className="font-medium text-secondary-900 mb-3">Discrepâncias Incluídas ({discrepancies.length})</h4>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {discrepancies.map((d) => (
            <div key={d.id} className="flex items-center justify-between p-3 rounded-lg bg-secondary-50 border border-secondary-200">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-secondary-900 truncate">{d.description}</p>
                <p className="text-sm text-secondary-500">{d.type} • Diferença: {formatCurrency(d.difference)}</p>
              </div>
              <span className="font-mono font-medium text-secondary-900">{formatCurrency(d.difference)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Step 3: Confirm
function ConfirmStep({
  discrepancies,
  totalAmount,
  title,
  description,
}: {
  discrepancies: Discrepancy[]
  totalAmount: number
  title: string
  description: string
}) {
  return (
    <div className="space-y-6">
      <div className="p-4 rounded-lg bg-primary-50 border border-primary-200">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary-100 text-primary-600">
            <Eye className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-medium text-primary-900">Revise os dados antes de confirmar</h4>
            <p className="text-sm text-primary-700">A contestação será criada em status "Rascunho" e poderá ser editada antes do envio.</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1">Título</label>
          <p className="text-secondary-900">{title}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-1">Descrição</label>
          <p className="text-secondary-900 whitespace-pre-wrap">{description || 'Sem descrição'}</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200 text-center">
            <p className="text-sm text-secondary-500">Discrepâncias</p>
            <p className="text-2xl font-bold text-secondary-900">{discrepancies.length}</p>
          </div>
          <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200 text-center">
            <p className="text-sm text-secondary-500">Valor Total</p>
            <p className="text-2xl font-bold text-secondary-900 font-mono">{formatCurrency(totalAmount)}</p>
          </div>
          <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200 text-center">
            <p className="text-sm text-secondary-500">Status Inicial</p>
            <p className="text-2xl font-bold text-secondary-900">Rascunho</p>
          </div>
        </div>
      </div>

      <div className="border-t border-secondary-200 pt-4">
        <h4 className="font-medium text-secondary-900 mb-3">Discrepâncias</h4>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {discrepancies.map((d) => (
            <div key={d.id} className="flex items-center justify-between p-2 rounded bg-secondary-50">
              <span className="text-sm text-secondary-700 truncate max-w-[300px]">{d.description}</span>
              <span className="font-mono font-medium text-secondary-900">{formatCurrency(d.difference)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}