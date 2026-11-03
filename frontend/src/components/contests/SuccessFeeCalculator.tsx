import { useState, useEffect } from 'react'
import { Calculator, DollarSign, TrendingUp, TrendingDown, AlertTriangle, Info } from 'lucide-react'
import { Badge, Input } from '@/components'
import { formatCurrency, formatPercent, cn } from '@/utils/helpers'

interface SuccessFeeCalculatorProps {
  successFeePct: number
  agreedAmount?: number
  initialAmount?: number
  onAmountChange?: (amount: number) => void
  className?: string
  showDetails?: boolean
}

export function SuccessFeeCalculator({
  successFeePct,
  agreedAmount,
  initialAmount = 0,
  onAmountChange,
  className,
  showDetails = true,
}: SuccessFeeCalculatorProps) {
  const [amount, setAmount] = useState(initialAmount)
  const [isEditing, setIsEditing] = useState(false)

  const successFee = amount * (successFeePct / 100)
  const netRecovery = amount - successFee
  const isPartial = agreedAmount !== undefined && amount < agreedAmount
  const isOver = agreedAmount !== undefined && amount > agreedAmount

  useEffect(() => {
    setAmount(initialAmount)
  }, [initialAmount])

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/[^0-9.,]/g, '')
    const parts = value.split(',')
    if (parts.length > 2) {
      value = parts[0] + ',' + parts.slice(1).join('')
    }
    const numericValue = parseFloat(value.replace(',', '.')) || 0
    setAmount(numericValue)
    onAmountChange?.(numericValue)
  }

  const formatInputValue = (val: number) => {
    return val.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }

  if (!showDetails) {
    // Compact version
    return (
      <div className={cn('flex items-center gap-4', className)}>
        <div className="flex items-center gap-2 p-3 rounded-lg bg-secondary-50 border border-secondary-200">
          <Calculator className="h-5 w-5 text-secondary-500" />
          <div>
            <p className="text-xs text-secondary-500">Success Fee</p>
            <p className="font-mono font-bold text-warning-600">{formatCurrency(successFee)}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 p-3 rounded-lg bg-success-50 border border-success-200">
          <DollarSign className="h-5 w-5 text-success-600" />
          <div>
            <p className="text-xs text-success-700">Líquido</p>
            <p className="font-mono font-bold text-success-600">{formatCurrency(netRecovery)}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Input Amount */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-secondary-700 flex items-center gap-2">
          Valor Total Recuperado
          {agreedAmount && (
            <Badge variant={isOver ? 'warning' : isPartial ? 'secondary' : 'success'} className="text-xs">
              {isOver ? 'Acima do acordado' : isPartial ? 'Abaixo do acordado' : 'Conforme acordado'}
            </Badge>
          )}
        </label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400 text-lg font-medium">R$</span>
          <Input
            type="text"
            value={formatInputValue(amount)}
            onChange={handleAmountChange}
            onFocus={() => setIsEditing(true)}
            onBlur={() => setIsEditing(false)}
            placeholder="0,00"
            className="pl-7 pr-3 text-lg font-mono"
            disabled={agreedAmount !== undefined && !isEditing}
          />
        </div>
        {agreedAmount && !isEditing && (
          <p className="text-xs text-secondary-500">Valor acordado: <span className="font-mono font-medium">{formatCurrency(agreedAmount)}</span></p>
        )}
      </div>

      {/* Calculation Breakdown */}
      <div className="grid gap-4 sm:grid-cols-3">
        {/* Gross Amount */}
        <div className={cn(
          'p-4 rounded-xl border text-center transition-colors',
          isEditing ? 'border-primary-300 bg-primary-50' : 'border-secondary-200 bg-white'
        )}>
          <div className="flex items-center justify-center gap-2 mb-2">
            <DollarSign className="h-5 w-5 text-secondary-500" />
            <span className="text-xs font-medium text-secondary-500 uppercase tracking-wide">Valor Bruto</span>
          </div>
          <p className="font-mono font-bold text-2xl text-secondary-900">{formatCurrency(amount)}</p>
          {agreedAmount && (
            <p className={cn('text-xs mt-1', isOver ? 'text-warning-600' : isPartial ? 'text-danger-600' : 'text-success-600')}>
              {isOver ? (
                <> <TrendingUp className="h-3 w-3 inline mr-1" /> +{formatCurrency(amount - agreedAmount)} acima do acordado </> )
              : isPartial ? (
                <> <TrendingDown className="h-3 w-3 inline mr-1" /> -{formatCurrency(agreedAmount - amount)} abaixo do acordado </> )
              : (
                <> <span className="h-3 w-3 inline mr-1" /> Conforme acordado </>
              )}
            </p>
          )}
        </div>

        {/* Success Fee */}
        <div className="p-4 rounded-xl border border-warning-200 bg-warning-50 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Calculator className="h-5 w-5 text-warning-600" />
            <span className="text-xs font-medium text-warning-700 uppercase tracking-wide">Success Fee</span>
          </div>
          <p className="font-mono font-bold text-2xl text-warning-600">{formatCurrency(successFee)}</p>
          <p className="text-xs text-warning-700 mt-1">{formatPercent(successFeePct)} do valor bruto</p>
        </div>

        {/* Net Recovery */}
        <div className="p-4 rounded-xl border border-success-200 bg-success-50 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <DollarSign className="h-5 w-5 text-success-600" />
            <span className="text-xs font-medium text-success-700 uppercase tracking-wide">Recuperação Líquida</span>
          </div>
          <p className="font-mono font-bold text-2xl text-success-600">{formatCurrency(netRecovery)}</p>
          <p className="text-xs text-success-700 mt-1">Valor para o cliente</p>
        </div>
      </div>

      {/* Details Panel */}
      {showDetails && agreedAmount && (
        <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
          <div className="flex items-start gap-3">
            <Info className="h-5 w-5 text-secondary-400 mt-0.5 flex-shrink-0" />
            <div className="space-y-2 text-sm text-secondary-600">
              <p>
                <strong className="text-secondary-900">Acordado:</strong> {formatCurrency(agreedAmount)}
                {' '}
                <Badge variant={isOver ? 'warning' : isPartial ? 'danger' : 'success'} className="ml-2">
                  {isOver ? `${formatPercent(((amount - agreedAmount) / agreedAmount) * 100)} acima` : isPartial ? `${formatPercent(((agreedAmount - amount) / agreedAmount) * 100)} abaixo` : 'Exato'}
                </Badge>
              </p>
              <p>
                <strong className="text-secondary-900">Success Fee no acordado:</strong> {formatCurrency(agreedAmount * (successFeePct / 100))}
              </p>
              <p>
                <strong className="text-secondary-900">Líquido no acordado:</strong> {formatCurrency(agreedAmount * (1 - successFeePct / 100))}
              </p>
              {isOver && (
                <p className="text-warning-600 flex items-center gap-1">
                  <AlertTriangle className="h-4 w-4" />
                  Valor excede o acordado. O success fee será calculado sobre o valor total recebido.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Formula Reference */}
      {showDetails && (
        <details className="group">
          <summary className="flex items-center gap-2 text-sm text-secondary-500 cursor-pointer p-2 rounded-lg hover:bg-secondary-100 transition-colors">
            <Calculator className="h-4 w-4" />
            Ver fórmula de cálculo
            <svg className="ml-auto h-4 w-4 text-secondary-400 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </summary>
          <div className="p-4 bg-secondary-50 rounded-lg border border-secondary-200 mt-2 text-sm text-secondary-600 space-y-2 font-mono">
            <p>success_fee = valor_bruto × (success_fee_pct / 100)</p>
            <p>recuperação_líquida = valor_bruto - success_fee</p>
            <p className="text-secondary-900">Exemplo: {formatCurrency(amount)} × {formatPercent(successFeePct)} = {formatCurrency(successFee)} (fee) → {formatCurrency(netRecovery)} (líquido)</p>
          </div>
        </details>
      )}
    </div>
  )
}

// Compact inline version for tables/lists
export function SuccessFeeCalculatorInline({ amount, successFeePct, className }: { amount: number; successFeePct: number; className?: string }) {
  const successFee = amount * (successFeePct / 100)
  const netRecovery = amount - successFee

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="text-right">
        <p className="text-xs text-secondary-500">Bruto</p>
        <p className="font-mono font-medium text-secondary-900">{formatCurrency(amount)}</p>
      </div>
      <div className="w-px h-8 bg-secondary-200" />
      <div className="text-right">
        <p className="text-xs text-warning-600">Fee ({formatPercent(successFeePct)})</p>
        <p className="font-mono font-medium text-warning-600">{formatCurrency(successFee)}</p>
      </div>
      <div className="w-px h-8 bg-secondary-200" />
      <div className="text-right">
        <p className="text-xs text-success-600">Líquido</p>
        <p className="font-mono font-bold text-success-600">{formatCurrency(netRecovery)}</p>
      </div>
    </div>
  )
}