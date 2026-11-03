import { useState, useEffect } from 'react'
import { Building2, Save, Loader2, Image, Upload, X, AlertCircle } from 'lucide-react'
import { Button, Input, Label, Card, CardHeader, CardBody, Badge } from '@/components'
import toast from 'react-hot-toast'
import { useAuth } from '@/store/auth-context'
import { useCompanySettings, useUpdateCompanySettings, useUploadCompanyLogo } from '@/hooks/useSettings'
import type { Company } from '@/types'

interface CompanySettings {
  defaultCurrency?: string
  timezone?: string
  autoApproveThreshold?: number
  notifications?: Record<string, boolean>
}

export function CompanySettingsPage() {
  const { user } = useAuth()
  const companyId = user?.companyId
  const [formData, setFormData] = useState<Partial<Company> & { settings?: CompanySettings }>({})
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const { data: company, isLoading, error } = useCompanySettings(companyId || '')

  const updateCompany = useUpdateCompanySettings()
  const uploadLogo = useUploadCompanyLogo()

  // Initialize form data from company
  useEffect(() => {
    if (company) {
      setFormData({
        name: company.name,
        cnpj: company.cnpj,
        email: company.email,
        phone: company.phone,
        address: company.address,
        city: company.city,
        state: company.state,
        zipCode: company.zipCode,
      })
      if (company.settings) {
        setFormData((prev) => ({ ...prev, settings: company.settings }))
      }
    }
  }, [company])

  const handleChange = (field: string, value: unknown) => {
    setFormData((prev: Partial<Company> & { settings?: CompanySettings }) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev: Record<string, string>) => ({ ...prev, [field]: '' }))
    }
  }

  const handleNestedChange = (parent: string, field: string, value: unknown) => {
    setFormData((prev: Partial<Company> & { settings?: CompanySettings }) => {
      const current = prev as Record<string, unknown>
      return {
        ...prev,
        [parent]: { ...((current[parent] as Record<string, unknown>) || {}), [field]: value },
      }
    })
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.name?.trim()) newErrors.name = 'Nome da empresa é obrigatório'
    if (!formData.cnpj?.trim()) newErrors.cnpj = 'CNPJ é obrigatório'
    else if (!/^\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}$/.test(String(formData.cnpj).replace(/[^\d]/g, ''))) {
      newErrors.cnpj = 'CNPJ inválido'
    }
    if (!formData.email?.trim()) newErrors.email = 'Email é obrigatório'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(formData.email))) newErrors.email = 'Email inválido'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm() || !companyId) return

    try {
      await updateCompany.mutateAsync({ companyId, data: formData })
      toast.success('Configurações salvas com sucesso!')
    } catch (_err) {
      toast.error('Erro ao salvar configurações')
    }
  }

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      toast.error('Arquivo deve ser uma imagem')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Imagem deve ter no máximo 5MB')
      return
    }

    setLogoFile(file)
    const reader = new FileReader()
    reader.onload = (event) => setLogoPreview(event.target?.result as string)
    reader.readAsDataURL(file)
  }

  const handleLogoSave = async () => {
    if (!logoFile || !companyId) return

    try {
      const formData = new FormData()
      formData.append('logo', logoFile)
      const result = await uploadLogo.mutateAsync({ companyId, formData })
      toast.success('Logo atualizada com sucesso!')
      setLogoPreview(result.logoUrl)
      setLogoFile(null)
    } catch (_err) {
      toast.error('Erro ao fazer upload da logo')
    }
  }

  const handleLogoRemove = () => {
    setLogoPreview(null)
    setLogoFile(null)
  }

  const formatCNPJ = (value: string) => {
    const numbers = value.replace(/\D/g, '')
    if (numbers.length <= 14) {
      return numbers
        .replace(/^(\d{2})(\d)/, '$1.$2')
        .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
        .replace(/\.(\d{3})(\d)/, '.$1/$2')
        .replace(/(\d{4})(\d)/, '$1-$2')
    }
    return value
  }

  const handleCNPJChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCNPJ(e.target.value)
    e.target.value = formatted
    handleChange('cnpj', formatted)
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-secondary-100 rounded w-1/4" />
        <div className="h-24 bg-secondary-100 rounded-xl" />
        <div className="h-24 bg-secondary-100 rounded-xl" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-12 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-danger-500 mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-1">Erro ao carregar empresa</h3>
        <p className="text-secondary-500">Tente recarregar a página</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Configurações da Empresa</h1>
          <p className="text-secondary-500">Gerencie os dados cadastrais e preferências da sua empresa</p>
        </div>
        <Badge variant="primary">{company?.settings?.defaultCurrency || 'BRL'}</Badge>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Logo Section */}
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-secondary-900 flex items-center gap-2">
              <Image className="h-5 w-5" />
              Logo da Empresa
            </h2>
          </CardHeader>
          <CardBody>
            <div className="flex items-center gap-6">
              <div className="relative w-32 h-32 flex-shrink-0">
                <div className="w-full h-full rounded-lg border-2 border-dashed border-secondary-300 flex items-center justify-center overflow-hidden bg-secondary-50">
                  {logoPreview ? (
                    <img src={logoPreview} alt="Logo preview" className="w-full h-full object-cover" />
                  ) : (
                    <div className="text-center text-secondary-400">
                      <Image className="mx-auto h-12 w-12 mb-2" />
                      <p className="text-sm">Nenhuma logo</p>
                    </div>
                  )}
                  {logoPreview && (
                    <button
                      type="button"
                      onClick={handleLogoRemove}
                      className="absolute top-1 right-1 p-1 bg-danger-500 text-white rounded-full hover:bg-danger-600 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
              <div className="flex-1 space-y-4">
                <label className="cursor-pointer">
                  <Button variant="secondary">
                    <Upload className="h-4 w-4 mr-2" />
                    {logoFile ? 'Substituir Logo' : 'Carregar Logo'}
                  </Button>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="hidden"
                  />
                </label>
                {logoFile && (
                  <Button variant="primary" type="button" onClick={handleLogoSave} loading={uploadLogo.isPending}>
                    <Save className="h-4 w-4 mr-2" />
                    Salvar Logo
                  </Button>
                )}
                <p className="text-sm text-secondary-500">
                  Formatos: PNG, JPG, SVG • Tamanho máximo: 5MB • Proporção recomendada: 1:1
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Basic Info */}
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-secondary-900 flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Dados Cadastrais
            </h2>
          </CardHeader>
          <CardBody className="space-y-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name" className="block text-sm font-medium text-secondary-700">
                  Razão Social *
                </Label>
                <Input
                  id="name"
                  value={formData.name || ''}
                  onChange={(e) => handleChange('name', e.target.value)}
                  placeholder="Nome da empresa"
                  error={errors.name}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cnpj" className="block text-sm font-medium text-secondary-700">
                  CNPJ *
                </Label>
                <Input
                  id="cnpj"
                  value={formData.cnpj || ''}
                  onChange={handleCNPJChange}
                  placeholder="00.000.000/0000-00"
                  maxLength={18}
                  error={errors.cnpj}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="block text-sm font-medium text-secondary-700">
                  Email *
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => handleChange('email', e.target.value)}
                  placeholder="contato@empresa.com"
                  error={errors.email}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone" className="block text-sm font-medium text-secondary-700">
                  Telefone
                </Label>
                <Input
                  id="phone"
                  value={formData.phone || ''}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  placeholder="(11) 99999-9999"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-secondary-200">
              <h3 className="font-medium text-secondary-900 mb-4">Endereço</h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div className="space-y-2">
                  <Label htmlFor="zipCode" className="block text-sm font-medium text-secondary-700">
                    CEP
                  </Label>
                  <Input
                    id="zipCode"
                    value={formData.zipCode || ''}
                    onChange={(e) => handleChange('zipCode', e.target.value)}
                    placeholder="00000-000"
                  />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Label htmlFor="address" className="block text-sm font-medium text-secondary-700">
                    Logradouro
                  </Label>
                  <Input
                    id="address"
                    value={formData.address || ''}
                    onChange={(e) => handleChange('address', e.target.value)}
                    placeholder="Rua, Avenida, etc."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="city" className="block text-sm font-medium text-secondary-700">
                    Cidade
                  </Label>
                  <Input
                    id="city"
                    value={formData.city || ''}
                    onChange={(e) => handleChange('city', e.target.value)}
                    placeholder="São Paulo"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state" className="block text-sm font-medium text-secondary-700">
                    Estado
                  </Label>
                  <Input
                    id="state"
                    value={formData.state || ''}
                    onChange={(e) => handleChange('state', e.target.value)}
                    placeholder="SP"
                    maxLength={2}
                  />
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Settings */}
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-secondary-900">Preferências do Sistema</h2>
          </CardHeader>
          <CardBody className="space-y-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="defaultCurrency" className="block text-sm font-medium text-secondary-700">
                  Moeda Padrão
                </Label>
                <Input
                  id="defaultCurrency"
                  value={formData.settings?.defaultCurrency || 'BRL'}
                  onChange={(e) => handleNestedChange('settings', 'defaultCurrency', e.target.value)}
                  placeholder="BRL"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="timezone" className="block text-sm font-medium text-secondary-700">
                  Fuso Horário
                </Label>
                <Input
                  id="timezone"
                  value={formData.settings?.timezone || 'America/Sao_Paulo'}
                  onChange={(e) => handleNestedChange('settings', 'timezone', e.target.value)}
                  placeholder="America/Sao_Paulo"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="autoApproveThreshold" className="block text-sm font-medium text-secondary-700">
                  Limite de Aprovação Automática (R$)
                </Label>
                <Input
                  id="autoApproveThreshold"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.settings?.autoApproveThreshold || ''}
                  onChange={(e) => handleNestedChange('settings', 'autoApproveThreshold', e.target.value ? Number(e.target.value) : undefined)}
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-secondary-200">
              <h3 className="font-medium text-secondary-900 mb-4">Notificações Padrão</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                {[
                  { key: 'email', label: 'Email', description: 'Receber notificações por email' },
                  { key: 'push', label: 'Push', description: 'Receber notificações push no navegador' },
                  { key: 'discrepancies', label: 'Discrepâncias', description: 'Alertas de novas discrepâncias' },
                  { key: 'contests', label: 'Contestações', description: 'Atualizações em contestações' },
                  { key: 'documents', label: 'Documentos', description: 'Status de processamento de documentos' },
                ].map((item) => (
                  <label key={item.key} className="flex items-center gap-3 p-3 rounded-lg border border-secondary-200 hover:bg-secondary-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.settings?.notifications?.[item.key as keyof typeof formData.settings.notifications] ?? true}
                      onChange={(e) => handleNestedChange('settings', 'notifications', {
                        ...formData.settings?.notifications,
                        [item.key]: e.target.checked,
                      })}
                      className="h-4 w-4 text-primary-600 rounded border-secondary-300 focus:ring-primary-500"
                    />
                    <div>
                      <p className="font-medium text-secondary-900">{item.label}</p>
                      <p className="text-sm text-secondary-500">{item.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-secondary-200">
          <Button type="button" variant="secondary" onClick={() => window.location.reload()}>
            <X className="h-4 w-4 mr-2" />
            Cancelar
          </Button>
          <Button type="submit" variant="primary" loading={updateCompany.isPending} disabled={updateCompany.isPending}>
            {updateCompany.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Salvando...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Salvar Configurações
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}