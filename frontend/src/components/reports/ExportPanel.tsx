import { useState } from 'react'
import { Download, FileText, Table, Loader2 } from 'lucide-react'
import { Button } from '@/components'
import { formatCurrency } from '@/utils/helpers'
import toast from 'react-hot-toast'

interface ExportPanelProps {
  filters: Record<string, unknown>
  kpis?: {
    total_discrepancies: number
    total_recovered: number
    success_rate: number
    avg_resolution_days: number
  }
  onExportPDF: () => Promise<void>
  onExportExcel: () => Promise<void>
}

export function ExportPanel({ filters, kpis, onExportPDF, onExportExcel }: ExportPanelProps) {
  const [exportFormat, setExportFormat] = useState<'pdf' | 'excel'>('pdf')
  const [pdfExporting, setPdfExporting] = useState(false)
  const [excelExporting, setExcelExporting] = useState(false)

  const handleExport = async (format: 'pdf' | 'excel') => {
    try {
      if (format === 'pdf') {
        setPdfExporting(true)
        await onExportPDF()
        toast.success('PDF gerado e baixado com sucesso!')
      } else {
        setExcelExporting(true)
        await onExportExcel()
        toast.success('Excel gerado e baixado com sucesso!')
      }
    } catch (_error) {
      toast.error(`Erro ao gerar ${format.toUpperCase()}`)
    } finally {
      setPdfExporting(false)
      setExcelExporting(false)
    }
  }

  const activeFiltersCount = Object.values(filters).filter((v) => v !== undefined && v !== '' && v !== null).length

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="font-medium text-secondary-900 flex items-center gap-2">
          <Download className="h-5 w-5" />
          Exportar Relatório
        </h3>
      </div>
      <div className="card-body space-y-4">
        {/* Format Selector */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-secondary-700">Formato</label>
          <div className="flex gap-3">
            <Button
              variant={exportFormat === 'pdf' ? 'primary' : 'secondary'}
              onClick={() => setExportFormat('pdf')}
              className="flex-1"
            >
              <FileText className="h-4 w-4 mr-2" />
              PDF
            </Button>
            <Button
              variant={exportFormat === 'excel' ? 'primary' : 'secondary'}
              onClick={() => setExportFormat('excel')}
              className="flex-1"
            >
              <Table className="h-4 w-4 mr-2" />
              Excel
            </Button>
          </div>
        </div>

        {/* Filters Summary */}
        <div className="p-3 rounded-lg bg-secondary-50 border border-secondary-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-secondary-600">
              {activeFiltersCount > 0 ? (
                <>
                  <span className="font-medium">Filtros aplicados:</span>{' '}
                  {Object.entries(filters)
                    .filter(([, v]) => v !== undefined && v !== '' && v !== null)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(', ')}
                </>
              ) : (
                'Nenhum filtro aplicado (exportará todos os dados)'
              )}
            </span>
          </div>
        </div>

        {/* KPIs Preview */}
        {kpis && (
          <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-primary-50 border border-primary-100">
            <div>
              <p className="text-xs text-primary-700 uppercase tracking-wide">Total Discrepâncias</p>
              <p className="font-bold text-primary-900">{kpis.total_discrepancies}</p>
            </div>
            <div>
              <p className="text-xs text-primary-700 uppercase tracking-wide">Valor Recuperado</p>
              <p className="font-bold text-primary-900">{formatCurrency(kpis.total_recovered)}</p>
            </div>
            <div>
              <p className="text-xs text-primary-700 uppercase tracking-wide">Taxa de Sucesso</p>
              <p className="font-bold text-primary-900">{kpis.success_rate.toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-xs text-primary-700 uppercase tracking-wide">Tempo Médio</p>
              <p className="font-bold text-primary-900">{kpis.avg_resolution_days.toFixed(1)} dias</p>
            </div>
          </div>
        )}

        {/* Export Button */}
        <Button
          variant="primary"
          className="w-full py-3"
          onClick={() => handleExport(exportFormat)}
          loading={pdfExporting || excelExporting}
          disabled={pdfExporting || excelExporting}
        >
          {exportFormat === 'pdf' ? (
            <>
              {pdfExporting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Gerando PDF...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Baixar Relatório PDF
                </>
              )}
            </>
          ) : (
            <>
              {excelExporting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Gerando Excel...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Baixar Relatório Excel
                </>
              )}
            </>
          )}
        </Button>

        {/* Info Text */}
        <p className="text-xs text-secondary-500 text-center">
          {exportFormat === 'pdf'
            ? 'O PDF incluirá resumo executivo, gráficos e tabela de discrepâncias detalhada.'
            : 'O Excel terá múltiplas abas: Resumo, Detalhes, Gráficos e Filtros aplicados.'}
        </p>
      </div>
    </div>
  )
}