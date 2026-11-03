import { useState } from 'react'
import { Send, MessageSquare, Paperclip, FileText, Download, ChevronDown, ChevronUp } from 'lucide-react'
import { Button, Input, Badge, Textarea } from '@/components'
import { formatDateTime, cn } from '@/utils/helpers'

interface Communication {
  id: string
  type: 'INBOUND' | 'OUTBOUND'
  subject: string
  body: string
  attachments: Array<{ id: string; fileName: string; fileUrl: string; fileSize: number }>
  createdAt: string
}

interface CommunicationThreadProps {
  communications: Communication[]
  isLoading?: boolean
  onAddCommunication: (data: { contestId: string; type: 'INBOUND' | 'OUTBOUND'; subject: string; body: string; attachments?: string[] }) => Promise<void>
  onDownloadAttachment: (url: string, fileName: string) => void
  canSend?: boolean
  contestId: string
}

export function CommunicationThread({ communications, isLoading = false, onAddCommunication, onDownloadAttachment, canSend = true, contestId }: CommunicationThreadProps) {
  const [showComposer, setShowComposer] = useState(false)
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [attachments, setAttachments] = useState<File[]>([])
  const [isSending, setIsSending] = useState(false)
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const handleSend = async () => {
    if (!subject.trim() || !body.trim()) return
    setIsSending(true)
    try {
      await onAddCommunication({ contestId, type: 'OUTBOUND', subject, body, attachments: [] })
      setSubject('')
      setBody('')
      setAttachments([])
      setShowComposer(false)
    } catch (_error) {
      // Error handled by hook
    } finally {
      setIsSending(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files)
      if (attachments.length + newFiles.length > 5) {
        // Could show toast here
        return
      }
      setAttachments([...attachments, ...newFiles])
    }
  }

  const removeAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index))
  }

  const toggleExpanded = (id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-20 bg-secondary-100 rounded-lg" />
        <div className="h-20 bg-secondary-100 rounded-lg" />
        <div className="h-20 bg-secondary-100 rounded-lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Composer */}
      {canSend && (
        <div className="space-y-4">
          <Button
            variant={showComposer ? 'primary' : 'secondary'}
            onClick={() => setShowComposer(!showComposer)}
            className="w-full justify-start"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            {showComposer ? 'Cancelar' : 'Nova Comunicação'}
          </Button>

          {showComposer && (
            <div className="space-y-4 p-4 rounded-lg border border-secondary-200 bg-secondary-50">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-secondary-700">Assunto *</label>
                <Input
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Assunto da mensagem"
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-secondary-700">Mensagem *</label>
                <Textarea
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Digite sua mensagem..."
                  rows={4}
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-secondary-700">Anexos (máx. 5)</label>
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="w-full text-sm text-secondary-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  disabled={attachments.length >= 5}
                />
                {attachments.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((file, index) => (
                      <Badge variant="secondary" className="flex items-center gap-1" key={index}>
                        <FileText className="h-3 w-3" />
                        {file.name} ({formatFileSize(file.size)})
                        <button type="button" onClick={() => removeAttachment(index)} className="ml-1 hover:text-danger-600">
                          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-secondary-200">
                <Button variant="secondary" onClick={() => setShowComposer(false)}>
                  Cancelar
                </Button>
                <Button variant="primary" onClick={handleSend} loading={isSending} disabled={!subject.trim() || !body.trim()}>
                  <Send className="h-4 w-4 mr-2" />
                  Enviar
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Communications List */}
      <div className="space-y-4">
        {communications.length === 0 && (
          <div className="p-8 text-center">
            <MessageSquare className="mx-auto h-12 w-12 text-secondary-300 mb-3" />
            <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhuma comunicação</h3>
            <p className="text-secondary-500">As mensagens trocadas com a transportadora aparecerão aqui</p>
          </div>
        )}

        {communications.map((comm) => {
          const isExpanded = expandedIds.has(comm.id)
          const isOutbound = comm.type === 'OUTBOUND'

          return (
            <div
              key={comm.id}
              className={cn(
                'rounded-lg border transition-colors',
                isOutbound ? 'border-primary-200 bg-primary-50' : 'border-secondary-200 bg-white'
              )}
            >
              <button
                type="button"
                className="p-4 flex items-start justify-between gap-4 cursor-pointer w-full text-left"
                onClick={() => toggleExpanded(comm.id)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleExpanded(comm.id); } }}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <Badge variant={isOutbound ? 'primary' : 'secondary'} className="text-xs">
                      {isOutbound ? 'Enviada' : 'Recebida'}
                    </Badge>
                    <h4 className="font-medium text-secondary-900 truncate">{comm.subject}</h4>
                    <span className="text-sm text-secondary-500 ml-auto whitespace-nowrap">
                      {formatDateTime(comm.createdAt)}
                    </span>
                  </div>
                  <p className={cn('text-secondary-600 truncate', !isExpanded && 'line-clamp-2')}>
                    {comm.body}
                  </p>
                  {comm.attachments.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {comm.attachments.map((att, idx) => (
                        <button
                          key={idx}
                          onClick={(e) => { e.stopPropagation(); onDownloadAttachment(att.fileUrl, att.fileName); }}
                          className="flex items-center gap-1 px-2 py-1 text-xs text-secondary-600 hover:text-primary-600 rounded bg-secondary-100 hover:bg-primary-50 transition-colors"
                        >
                          <Paperclip className="h-3 w-3" />
                          {att.fileName}
                          <Download className="h-3 w-3" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex-shrink-0">
                  {isExpanded ? <ChevronUp className="h-5 w-5 text-secondary-400" /> : <ChevronDown className="h-5 w-5 text-secondary-400" />}
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 border-t border-secondary-200 bg-secondary-50/50">
                  <div className="text-sm text-secondary-600 whitespace-pre-wrap">{comm.body}</div>
                  {comm.attachments.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-medium text-secondary-500 uppercase tracking-wide">Anexos</p>
                      {comm.attachments.map((att, idx) => (
                        <button
                          key={idx}
                          onClick={() => onDownloadAttachment(att.fileUrl, att.fileName)}
                          className="flex items-center justify-between w-full p-2 rounded border border-secondary-200 bg-white text-left hover:bg-secondary-50 transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-secondary-400" />
                            <span className="text-secondary-700">{att.fileName}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-secondary-400">{formatFileSize(att.fileSize)}</span>
                            <Download className="h-4 w-4 text-secondary-400 hover:text-primary-600" />
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}