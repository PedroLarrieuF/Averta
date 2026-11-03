import { useState, useRef } from 'react'
import { Download, RotateCcw, Maximize, Minimize, FileText, AlertTriangle, CheckCircle, Loader2, X } from 'lucide-react'
import { Button, Badge, Modal } from '@/components'
import { formatDateTime, cn } from '@/utils/helpers'

interface ContestPDFViewerProps {
  contestId: string
  pdfUrl?: string
  contestTitle?: string
  onGeneratePDF: (id: string) => Promise<{ url: string }>
  onClose: () => void
  isOpen: boolean
  isGenerating?: boolean
}

export function ContestPDFViewer({ contestId, pdfUrl, contestTitle, onGeneratePDF, onClose, isOpen, isGenerating = false }: ContestPDFViewerProps) {
  const [pdfSrc, setPdfSrc] = useState<string | null>(pdfUrl || null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [scale, setScale] = useState(1)
  const [rotation, setRotation] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const handleGeneratePDF = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await onGeneratePDF(contestId)
      setPdfSrc(result.url)
    } catch (_err) {
      setError('Erro ao gerar PDF. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = () => {
    if (pdfSrc) {
      const link = document.createElement('a')
      link.href = pdfSrc
      link.download = `${contestTitle || 'contestacao'}-${contestId.slice(0, 8)}.pdf`
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handlePrint = () => {
    if (iframeRef.current) {
      iframeRef.current.contentWindow?.focus()
      iframeRef.current.contentWindow?.print()
    }
  }

  const zoomIn = () => setScale(prev => Math.min(prev + 0.25, 3))
  const zoomOut = () => setScale(prev => Math.max(prev - 0.25, 0.5))
  const resetZoom = () => { setScale(1); setRotation(0) }
  const rotate = () => setRotation(prev => (prev + 90) % 360)

  const handleIframeLoad = () => {
    setIsLoading(false)
    setError(null)
  }

  const handleIframeError = () => {
    setIsLoading(false)
    setError('Não foi possível carregar o PDF. O arquivo pode ter sido removido ou o link expirou.')
  }

  return (
    <Modal
      open={isOpen}
      onOpenChange={onClose}
      title=""
      size="full"
      showClose={false}
    >
      <div className="flex flex-col h-full max-h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-secondary-200 bg-white sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button onClick={onClose} className="p-2 rounded-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 transition-colors" aria-label="Fechar">
              <X className="h-5 w-5" />
            </button>
            <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
              <FileText className="h-6 w-6 text-primary-600" />
            </div>
            <div className="min-w-0">
              <h2 className="font-semibold text-secondary-900 truncate">{contestTitle || `Contestação ${contestId.slice(0, 8)}`}</h2>
              <p className="text-sm text-secondary-500">Visualização da carta de contestação</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {pdfSrc && (
              <>
                <Button variant="secondary" size="sm" onClick={handleDownload} className="hidden sm:flex">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
                <Button variant="secondary" size="sm" onClick={handlePrint} className="hidden sm:flex">
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v14a2 2 0 002 2h8a2 2 0 002-2v-4" /></svg>
                  Imprimir
                </Button>
              </>
            )}
            <div className="flex items-center gap-1 border-l border-secondary-200 pl-4 ml-2">
              <Button variant="ghost" size="sm" onClick={zoomOut} aria-label="Diminuir zoom" disabled={scale <= 0.5}>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" /></svg>
              </Button>
              <span className="text-sm font-mono text-secondary-600 w-16 text-center">{Math.round(scale * 100)}%</span>
              <Button variant="ghost" size="sm" onClick={zoomIn} aria-label="Aumentar zoom" disabled={scale >= 3}>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
              </Button>
              <Button variant="ghost" size="sm" onClick={resetZoom} aria-label="Resetar zoom">
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={rotate} aria-label="Rotacionar">
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setIsFullscreen(!isFullscreen)} aria-label={isFullscreen ? 'Sair tela cheia' : 'Tela cheia'}>
                {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="flex-1 overflow-auto bg-secondary-100 relative" style={{ transform: `scale(${scale}) rotate(${rotation}deg)`, transformOrigin: 'center center' }}>
          {(() => {
            if (!pdfSrc && !isGenerating && !isLoading) {
              return (
                <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                  <div className="w-24 h-24 rounded-full bg-primary-50 flex items-center justify-center mb-6">
                    <FileText className="h-12 w-12 text-primary-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-secondary-900 mb-2">PDF não gerado</h3>
                  <p className="text-secondary-500 mb-6 max-w-md">
                    A carta de contestação ainda não foi gerada. Clique no botão abaixo para gerar o PDF com os dados da contestação.
                  </p>
                  <Button variant="primary" size="lg" onClick={handleGeneratePDF} loading={isGenerating} disabled={isGenerating}>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    {isGenerating ? 'Gerando PDF...' : 'Gerar PDF da Contestação'}
                  </Button>
                  {isGenerating && (
                    <p className="text-sm text-secondary-500 mt-4">Aguarde enquanto o PDF é gerado no servidor...</p>
                  )}
                </div>
              )
            }
            if (error) {
              return (
                <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                  <div className="w-24 h-24 rounded-full bg-danger-50 flex items-center justify-center mb-6">
                    <AlertTriangle className="h-12 w-12 text-danger-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-secondary-900 mb-2">Erro ao carregar PDF</h3>
                  <p className="text-secondary-500 mb-6 max-w-md">{error}</p>
                  <div className="flex gap-3">
                    <Button variant="primary" onClick={() => { setError(null); setPdfSrc(pdfUrl || null); setIsLoading(true); }}>
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Tentar novamente
                    </Button>
                    <Button variant="secondary" onClick={handleGeneratePDF} loading={isGenerating} disabled={isGenerating}>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Regenerar PDF
                    </Button>
                  </div>
                </div>
              )
            }
            return (
              <>
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-10">
                    <div className="flex flex-col items-center gap-4">
                      <Loader2 className="h-12 w-12 text-primary-600 animate-spin" />
                      <p className="text-secondary-600">Carregando PDF...</p>
                    </div>
                  </div>
                )}
                <iframe
                  ref={iframeRef}
                  src={pdfSrc || ''}
                  className="w-full h-full min-h-[calc(100vh-200px)] border-0 bg-white shadow-lg"
                  onLoad={handleIframeLoad}
                  onError={handleIframeError}
                  title={`Contestação ${contestTitle || contestId}`}
                  style={{ display: pdfSrc ? 'block' : 'none' }}
                />
              </>
            )
          })()}
        </div>

        {/* Footer Status */}
        <div className="p-4 border-t border-secondary-200 bg-white flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-secondary-500">
            {pdfSrc && (
              <>
                <Badge variant="success" className="gap-1">
                  <CheckCircle className="h-3 w-3" />
                  PDF carregado
                </Badge>
                <span>Última atualização: {formatDateTime(new Date())}</span>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {pdfSrc && (
              <Button variant="secondary" size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={onClose}>
              Fechar
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  )
}

// Standalone PDF viewer component (non-modal)
export function ContestPDFEmbed({ pdfUrl, className, onLoad, onError }: { pdfUrl?: string; className?: string; onLoad?: () => void; onError?: () => void }) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  return (
    <div className={cn('relative', className)}>
      {isLoading && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-secondary-50 z-10">
          <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
        </div>
      )}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-secondary-50 z-10 p-4 text-center">
          <div className="space-y-2">
            <AlertTriangle className="mx-auto h-10 w-10 text-danger-500" />
            <p className="text-secondary-600">Erro ao carregar PDF</p>
            <Button variant="secondary" size="sm" onClick={() => { setError(false); setIsLoading(true); }}>
              Tentar novamente
            </Button>
          </div>
        </div>
      )}
      <iframe
        src={pdfUrl || ''}
        className={cn('w-full h-96 rounded-lg border border-secondary-200 bg-white', isLoading ? 'opacity-0' : 'opacity-100', error ? 'hidden' : 'block')}
        onLoad={() => { setIsLoading(false); setError(false); onLoad?.(); }}
        onError={() => { setIsLoading(false); setError(true); onError?.(); }}
        title="Contestação PDF"
      />
    </div>
  )
}