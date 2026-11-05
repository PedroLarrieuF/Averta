import { useEffect, useRef } from 'react'
import { Card, CardHeader, CardBody } from '../../components'
import { ExternalLink, RefreshCw } from 'lucide-react'
import { Button } from '../../components'

export function DeveloperDocs() {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Load Scalar dynamically from CDN
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/@scalar/api-reference@latest'
    script.async = true
    script.onload = () => {
      // @ts-ignore - Scalar global
      if (window.Scalar) {
        // @ts-ignore
        window.Scalar.createApiReference('#scalar-docs', {
          spec: {
            url: '/openapi/v1.yaml',
          },
          theme: 'kepler',
          layout: 'modern',
          authentication: {
            preferredSecurityScheme: 'ApiKeyAuth',
            securitySchemes: {
              ApiKeyAuth: {
                type: 'apiKey',
                in: 'header',
                name: 'X-API-Key',
              },
            },
          },
          hideDownloadButton: false,
          hideModels: false,
          defaultHttpClient: { targetKey: 'fetch', clientKey: 'fetch' },
        })
      }
    }
    document.head.appendChild(script)

    return () => {
      document.head.removeChild(script)
      // @ts-ignore
      if (window.Scalar && window.Scalar.cleanup) {
        // @ts-ignore
        window.Scalar.cleanup()
      }
    }
  }, [])

  const handleRefresh = () => {
    if (containerRef.current) {
      containerRef.current.innerHTML = ''
      // Re-trigger the effect by remounting
      window.location.reload()
    }
  }

  return (
    <div className="space-y-6">
      <div className="page-header flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Documentação da API</h1>
          <p className="page-subtitle">Documentação interativa com Scalar - teste endpoints diretamente</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={handleRefresh} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Recarregar
          </Button>
          <Button variant="ghost" className="flex items-center gap-2">
            <ExternalLink className="h-4 w-4" />
            Abrir em Nova Aba
          </Button>
        </div>
      </div>

      <Card className="h-[calc(100vh-280px)] min-h-[600px] flex flex-col">
        <CardHeader className="flex items-center justify-between">
          <span>Referência da API (OpenAPI 3.1)</span>
          <span className="text-sm text-secondary-500">
            Powered by <a href="https://scalar.com" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Scalar</a>
          </span>
        </CardHeader>
        <CardBody className="flex-1 min-h-0 p-0">
          <div id="scalar-docs" ref={containerRef} className="w-full h-full" />
        </CardBody>
      </Card>

      {/* Fallback notice */}
      <div className="text-center text-sm text-secondary-500 p-4">
        <p>Se a documentação não carregar, verifique se o arquivo <code className="bg-secondary-100 px-1.5 rounded">/openapi/v1.yaml</code> está disponível.</p>
        <p className="mt-1">Em desenvolvimento, certifique-se de que o backend está servindo o spec em <code className="bg-secondary-100 px-1.5 rounded">http://localhost:8000/openapi/v1.yaml</code></p>
      </div>
    </div>
  )
}