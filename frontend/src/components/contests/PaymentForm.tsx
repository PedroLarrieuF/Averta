import { useState } from 'react'
import { FileText, X, CheckCircle, DollarSign, Calculator, AlertTriangle } from 'lucide-react'
import { Button, Input, Modal } from '@/components'
import { formatCurrency } from '@/utils/helpers'

interface PaymentFormProps {
  contestId: string
  successFeePct: number
  agreedAmount?: number
  onSubmit: (data: { amount: number; paidAt: string; proofFile?: File; notes?: string }) => Promise<void>
  onClose: () => void
  isOpen: boolean
  isLoading?: boolean
}

export function PaymentForm({ contestId: _contestId, successFeePct, agreedAmount, onSubmit, onClose, isOpen, isLoading = false }: PaymentFormProps) {
  const [amount, setAmount] = useState('')
  const [paidAt, setPaidAt] = useState(new Date().toISOString().split('T')[0])
  const [proofFile, setProofFile] = useState<File | null>(null)
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const numericAmount = parseFloat(amount.replace(/[^0-9.,]/g, '').replace(',', '.')) || 0
  const successFee = numericAmount * (successFeePct / 100)
  const netRecovery = numericAmount - successFee

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!amount || numericAmount <= 0) return
    if (!paidAt) return

    setIsSubmitting(true)
    try {
      await onSubmit({ amount: numericAmount, paidAt, proofFile: proofFile || undefined, notes: notes || undefined })
      // Reset form
      setAmount('')
      setPaidAt(new Date().toISOString().split('T')[0])
      setProofFile(null)
      setNotes('')
    } catch (_error) {
      // Error handled by hook
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
      if (!allowedTypes.includes(file.type)) {
        // Could show toast
        return
      }
      // Validate size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        // Could show toast
        return
      }
      setProofFile(file)
    }
  }

  const removeProofFile = () => {
    setProofFile(null)
  }

  const formatAmountInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/[^0-9.,]/g, '')
    // Allow only one decimal separator
    const parts = value.split(',')
    if (parts.length > 2) {
      value = parts[0] + ',' + parts.slice(1).join('')
    }
    setAmount(value)
  }

  return (
    <Modal
      open={isOpen}
      onOpenChange={onClose}
      title="Registrar Pagamento Recebido"
      size="lg"
      showClose={true}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Success Fee Calculator Preview */}
        <div className="p-4 rounded-lg bg-secondary-50 border border-secondary-200">
          <div className="flex items-center gap-2 text-sm font-medium text-secondary-700 mb-3">
            <Calculator className="h-4 w-4" />
            Cálculo do Success Fee ({successFeePct}%)
          </div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 rounded-lg bg-white border border-secondary-200">
              <p className="text-xs text-secondary-500 uppercase tracking-wide">Valor Recebido</p>
              <p className="font-mono font-bold text-lg text-secondary-900 mt-1">{formatCurrency(numericAmount)}</p>
            </div>
            <div className="p-3 rounded-lg bg-white border border-secondary-200">
              <p className="text-xs text-secondary-500 uppercase tracking-wide">Success Fee</p>
              <p className="font-mono font-bold text-lg text-warning-600 mt-1">{formatCurrency(successFee)}</p>
            </div>
            <div className="p-3 rounded-lg bg-white border border-secondary-200">
              <p className="text-xs text-secondary-500 uppercase tracking-wide">Recuperação Líquida</p>
              <p className="font-mono font-bold text-lg text-success-600 mt-1">{formatCurrency(netRecovery)}</p>
            </div>
          </div>
          {agreedAmount && numericAmount > agreedAmount && (
            <p className="text-xs text-warning-600 mt-2 flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" />
              Valor excede o acordado ({formatCurrency(agreedAmount)})
            </p>
          )}
        </div>

        {/* Form Fields */}
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-secondary-700">Valor Recebido *</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400">R$</span>
              <Input
                type="text"
                value={amount}
                onChange={formatAmountInput}
                placeholder="0,00"
                className="pl-7 pr-3"
                required
                disabled={isSubmitting}
              />
            </div>
            <p className="text-xs text-secondary-500">Use vírgula para decimais. Ex: 1.234,56</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-secondary-700">Data do Pagamento *</label>
            <Input
              type="date"
              value={paidAt}
              onChange={(e) => setPaidAt(e.target.value)}
              required
              disabled={isSubmitting}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-secondary-700">Comprovante (PDF, JPG, PNG - máx. 10MB)</label>
            <div className="space-y-2">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                className="w-full text-sm text-secondary-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-secondary-100 file:text-secondary-700 hover:file:bg-secondary-200"
                disabled={isSubmitting}
              />
              {proofFile && (
                <div className="flex items-center justify-between p-2 rounded border border-secondary-200 bg-white">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-secondary-400" />
                    <span className="text-sm text-secondary-700">{proofFile.name}</span>
                    <span className="text-xs text-secondary-400">({(proofFile.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <button type="button" onClick={removeProofFile} className="p-1 text-secondary-400 hover:text-danger-600">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-secondary-700">Observações</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Observações opcionais sobre o pagamento..."
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-secondary-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={isSubmitting}
            />
          </div>
        </div>

        {/* Summary */}
        <div className="p-4 rounded-lg bg-primary-50 border border-primary-200">
          <div className="flex items-center gap-2 text-sm font-medium text-primary-900 mb-2">
            <CheckCircle className="h-4 w-4" />
            Resumo do Registro
          </div>
          <dl className="grid grid-cols-2 gap-2 text-sm">
            <dt className="text-secondary-600">Valor Bruto</dt>
            <dd className="font-mono font-medium text-secondary-900 text-right">{formatCurrency(numericAmount)}</dd>
            <dt className="text-secondary-600">Success Fee ({successFeePct}%)</dt>
            <dd className="font-mono font-medium text-warning-600 text-right">{formatCurrency(successFee)}</dd>
            <dt className="text-secondary-600">Recuperação Líquida</dt>
            <dd className="font-mono font-bold text-success-600 text-right">{formatCurrency(netRecovery)}</dd>
            <dt className="text-secondary-600">Data</dt>
            <dd className="font-medium text-secondary-900 text-right">{new Date(paidAt + 'T00:00:00').toLocaleDateString('pt-BR')}</dd>
          </dl>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" loading={isSubmitting || isLoading} disabled={!amount || numericAmount <= 0 || !paidAt || isSubmitting}>
            <DollarSign className="h-4 w-4 mr-2" />
            Registrar Pagamento
          </Button>
        </div>
      </form>
    </Modal>
  )
}