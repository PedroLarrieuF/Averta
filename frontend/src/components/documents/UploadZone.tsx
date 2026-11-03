import { useCallback, useState, DragEvent, ChangeEvent } from 'react'
import { Upload, AlertCircle, CheckCircle } from 'lucide-react'
import { Button } from '@/components'
import { cn } from '@/utils/helpers'

interface UploadZoneProps {
  onUpload: (files: File[]) => void
  isLoading?: boolean
  acceptedFiles?: string[]
  maxFiles?: number
  maxFileSize?: number // in MB
}

export function UploadZone({
  onUpload,
  isLoading = false,
  acceptedFiles = ['.xml', '.XML'],
  maxFiles = 10,
  maxFileSize = 50,
}: UploadZoneProps) {
  const [isDragActive, setIsDragActive] = useState(false)
  const [errors, setErrors] = useState<string[]>([])

  const validateFiles = useCallback((files: FileList | File[]): File[] => {
    const fileArray = Array.from(files)
    const newErrors: string[] = []

    if (fileArray.length > maxFiles) {
      newErrors.push(`Máximo de ${maxFiles} arquivos por upload`)
    }

    const validFiles = fileArray.filter((file) => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase()
      const accepted = acceptedFiles.some((a) => a.toLowerCase() === ext)

      if (!accepted) {
        newErrors.push(`${file.name}: tipo não suportado (aceitos: ${acceptedFiles.join(', ')})`)
        return false
      }

      if (file.size > maxFileSize * 1024 * 1024) {
        newErrors.push(`${file.name}: arquivo muito grande (máx. ${maxFileSize}MB)`)
        return false
      }

      return true
    })

    setErrors(newErrors)
    return validFiles
  }, [acceptedFiles, maxFiles, maxFileSize])

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragActive(false)

      if (isLoading) return

      const validFiles = validateFiles(e.dataTransfer.files)
      if (validFiles.length > 0) {
        onUpload(validFiles)
      }
    },
    [isLoading, onUpload, validateFiles]
  )

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (!isLoading) setIsDragActive(true)
  }, [isLoading])

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
  }, [])

  const handleFileChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      if (isLoading) return

      const validFiles = validateFiles(e.target.files!)
      if (validFiles.length > 0) {
        onUpload(validFiles)
      }
      e.target.value = ''
    },
    [isLoading, onUpload, validateFiles]
  )

  return (
    <div className="relative">
      {/* Hidden file input */}
      <input
        type="file"
        multiple
        accept={acceptedFiles.join(',')}
        onChange={handleFileChange}
        className="hidden"
        id="file-upload"
        disabled={isLoading}
      />

      {/* Drop zone */}
      <div
        className={cn(
          'relative border-2 border-dashed rounded-xl p-6 text-center transition-all duration-200',
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-secondary-300 hover:border-primary-400 hover:bg-secondary-50',
          isLoading && 'opacity-50 pointer-events-none'
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && document.getElementById('file-upload')?.click()}
        aria-label="Área de upload de arquivos"
      >
        <div className="mx-auto w-12 h-12 rounded-full flex items-center justify-center mb-3">
          {isDragActive ? (
            <CheckCircle className="h-6 w-6 text-primary-600" />
          ) : (
            <Upload className="h-6 w-6 text-secondary-400" />
          )}
        </div>

        <p className="text-lg font-medium text-secondary-900 mb-1">
          {isDragActive ? 'Solte os arquivos aqui' : 'Arraste e solte XMLs aqui'}
        </p>

        <p className="text-secondary-500 text-sm mb-4">
          ou{' '}
          <Button
            variant="ghost"
            size="sm"
            className="p-0 h-auto text-primary-600 hover:text-primary-700"
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            clique para selecionar
          </Button>
        </p>

        <p className="text-xs text-secondary-400">
          Tipos aceitos: {acceptedFiles.map((f) => f.toUpperCase()).join(', ')} •
          Máx. {maxFiles} arquivos • Máx. {maxFileSize}MB cada
        </p>

        {errors.length > 0 && (
          <div className="mt-4 p-3 text-left bg-danger-50 border border-danger-200 rounded-lg">
            <div className="flex items-center gap-2 text-danger-700 mb-2">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">Erros de validação:</span>
            </div>
            <ul className="text-sm text-danger-600 space-y-1">
              {errors.map((error, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-danger-500" />
                  {error}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Upload progress */}
      {isLoading && (
        <div className="mt-4 p-4 bg-primary-50 border border-primary-200 rounded-lg">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary-500 border-t-transparent" />
            <div className="flex-1">
              <p className="font-medium text-primary-900">Enviando arquivos...</p>
              <p className="text-sm text-primary-700">Aguarde enquanto processamos seus documentos</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}