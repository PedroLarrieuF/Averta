import { useState } from 'react'
import { Search, Plus, Truck, MoreVertical, Loader2, Edit, Trash2, CheckCircle, X, ToggleLeft, ToggleRight, Building2 } from 'lucide-react'
import { Button, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Label, Badge, Card, CardBody, Table, Pagination, Modal, DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, Switch } from '@/components'
import toast from 'react-hot-toast'
import { useAuth } from '@/store/auth-context'
import { useSettingsCarriers, useCreateCarrier, useUpdateCarrier, useDeleteCarrier, useToggleCarrierStatus } from '@/hooks/useSettings'
import type { Carrier } from '@/types'

export function CarriersPage() {
  const { user, hasAnyRole } = useAuth()
  const canManage = user ? hasAnyRole(['ADMIN', 'MANAGER']) : false
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [page, setPage] = useState(1)
  const [showFormModal, setShowFormModal] = useState(false)
  const [editingCarrier, setEditingCarrier] = useState<Carrier | null>(null)
  const [formData, setFormData] = useState<Partial<Carrier>>({
    name: '',
    cnpj: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    isActive: true,
    contacts: [],
  })
  const [contactForm, setContactForm] = useState({ name: '', email: '', phone: '', role: '' })
  const pageSize = 10

  const { data, isLoading, refetch } = useSettingsCarriers({
    search: search || undefined,
    isActive: statusFilter === 'ACTIVE' ? true : statusFilter === 'INACTIVE' ? false : undefined,
    page,
    limit: pageSize,
  })

  const createCarrier = useCreateCarrier()
  const updateCarrier = useUpdateCarrier()
  const deleteCarrier = useDeleteCarrier()
  const toggleStatus = useToggleCarrierStatus()

  const resetForm = () => {
    setFormData({
      name: '',
      cnpj: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
      isActive: true,
      contacts: [],
    })
    setContactForm({ name: '', email: '', phone: '', role: '' })
  }

  const handleOpenCreate = () => {
    setEditingCarrier(null)
    resetForm()
    setShowFormModal(true)
  }

  const handleOpenEdit = (carrier: Carrier) => {
    setEditingCarrier(carrier)
    setFormData({
      name: carrier.name,
      cnpj: carrier.cnpj,
      email: carrier.email,
      phone: carrier.phone,
      address: carrier.address,
      city: carrier.city,
      state: carrier.state,
      zipCode: carrier.zipCode,
      isActive: carrier.isActive,
      contacts: [...carrier.contacts],
    })
    setContactForm({ name: '', email: '', phone: '', role: '' })
    setShowFormModal(true)
  }

  const validateForm = () => {
    if (!formData.name?.trim()) { toast.error('Nome é obrigatório'); return false }
    if (!formData.cnpj?.trim()) { toast.error('CNPJ é obrigatório'); return false }
    if (!formData.email?.trim()) { toast.error('Email é obrigatório'); return false }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) { toast.error('Email inválido'); return false }
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return

    const submitData = {
      ...formData,
      contacts: formData.contacts || [],
    }

    try {
      if (editingCarrier) {
        await updateCarrier.mutateAsync({ id: editingCarrier.id, data: submitData })
        toast.success('Transportadora atualizada com sucesso!')
      } else {
        await createCarrier.mutateAsync(submitData)
        toast.success('Transportadora criada com sucesso!')
      }
      setShowFormModal(false)
      refetch()
    } catch (_err) {
      toast.error('Erro ao salvar transportadora')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Tem certeza que deseja excluir esta transportadora?')) return
    try {
      await deleteCarrier.mutateAsync(id)
      toast.success('Transportadora excluída com sucesso!')
      refetch()
    } catch (_err) {
      toast.error('Erro ao excluir transportadora')
    }
  }

  const handleStatusToggle = async (id: string, isActive: boolean) => {
    try {
      await toggleStatus.mutateAsync({ id, isActive: !isActive })
      toast.success(`Transportadora ${!isActive ? 'ativada' : 'desativada'} com sucesso!`)
      refetch()
    } catch (_err) {
      toast.error('Erro ao alterar status')
    }
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
    setFormData((prev) => ({ ...prev, cnpj: formatted }))
  }

  const addContact = () => {
    if (!contactForm.name.trim() || !contactForm.email.trim()) {
      toast.error('Nome e email do contato são obrigatórios')
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactForm.email)) {
      toast.error('Email do contato inválido')
      return
    }
    setFormData((prev) => ({
      ...prev,
      contacts: [...(prev.contacts || []), { ...contactForm, id: crypto.randomUUID() }],
    }))
    setContactForm({ name: '', email: '', phone: '', role: '' })
  }

  const removeContact = (id: string) => {
    setFormData((prev) => ({
      ...prev,
      contacts: prev.contacts?.filter((c) => c.id !== id) || [],
    }))
  }

  const filteredCarriers = data?.data || []
  const totalPages = data?.meta?.totalPages || 1

  const columns = [
    {
      key: 'carrier',
      header: 'Transportadora',
      render: (c: Carrier) => (
        <div>
          <p className="font-medium text-secondary-900">{c.name}</p>
          {c.contacts && c.contacts.length > 0 && (
            <p className="text-sm text-secondary-500">{c.contacts.length} contato(s)</p>
          )}
        </div>
      ),
    },
    {
      key: 'cnpj',
      header: 'CNPJ',
      className: 'font-mono text-sm',
      render: (c: Carrier) => <span>{c.cnpj}</span>,
    },
    {
      key: 'contact',
      header: 'Contato',
      className: 'hidden sm:table-cell',
      render: (c: Carrier) => (
        <>
          {c.email && <p className="text-sm text-secondary-500">{c.email}</p>}
          {c.phone && <p className="text-sm text-secondary-500">{c.phone}</p>}
        </>
      ),
    },
    {
      key: 'location',
      header: 'Cidade/UF',
      className: 'hidden md:table-cell text-sm text-secondary-500',
      render: (c: Carrier) => <span>{c.city && c.state ? `${c.city}/${c.state}` : '—'}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (c: Carrier) => (
        <Badge variant={c.isActive ? 'success' : 'secondary'}>
          {c.isActive ? 'Ativa' : 'Inativa'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Ações',
      className: 'text-right',
      render: (c: Carrier) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={() => handleOpenEdit(c)} disabled={!canManage}>
              <Edit className="h-4 w-4 mr-2" />
              Editar
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleStatusToggle(c.id, c.isActive)}
              className={c.isActive ? 'text-warning-600' : 'text-success-600'}
            >
              {c.isActive ? (
                <>
                  <ToggleLeft className="h-4 w-4 mr-2" />
                  Desativar
                </>
              ) : (
                <>
                  <ToggleRight className="h-4 w-4 mr-2" />
                  Ativar
                </>
              )}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleDelete(c.id)}
              disabled={!canManage}
              className="text-danger-600"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Excluir
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Transportadoras</h1>
          <p className="text-secondary-500">Gerencie as transportadoras cadastradas</p>
        </div>
        {canManage && (
          <Button onClick={handleOpenCreate}>
            <Plus className="h-4 w-4 mr-2" />
            Nova Transportadora
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardBody className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="relative flex-1 min-w-[250px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
              <Input
                placeholder="Buscar por nome, CNPJ, email..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={(value) => { setStatusFilter(value); setPage(1); }}>
              <SelectTrigger><SelectValue placeholder="Todos os status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="ACTIVE">Ativas</SelectItem>
                <SelectItem value="INACTIVE">Inativas</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardBody>
      </Card>

      {/* Carriers Table */}
      <Card>
        {isLoading ? (
          <div className="animate-pulse p-8">
            <div className="h-10 bg-secondary-100 rounded" />
            <div className="space-y-3 mt-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-14 bg-secondary-100 rounded" />
              ))}
            </div>
          </div>
        ) : filteredCarriers.length === 0 ? (
          <div className="card p-12 text-center">
            <Truck className="mx-auto h-12 w-12 text-secondary-300 mb-4" />
            <h3 className="text-lg font-medium text-secondary-900 mb-1">Nenhuma transportadora encontrada</h3>
            <p className="text-secondary-500 mb-4">
              {search || statusFilter ? 'Tente ajustar os filtros' : 'Cadastre a primeira transportadora'}
            </p>
            {canManage && !search && !statusFilter && (
              <Button onClick={handleOpenCreate}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Transportadora
              </Button>
            )}
          </div>
        ) : (
          <>
            <Table columns={columns} data={filteredCarriers} keyField="id" isLoading={isLoading} />
            {totalPages > 1 && (
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            )}
          </>
        )}
      </Card>

      {/* Form Modal */}
      <Modal
        open={showFormModal}
        onOpenChange={(open) => { if (!open) { setShowFormModal(false); setEditingCarrier(null); } }}
        title={editingCarrier ? 'Editar Transportadora' : 'Nova Transportadora'}
        size="xl"
      >
        <form onSubmit={handleSubmit} className="flex-1 overflow-auto">
          <div className="p-6 pb-0 space-y-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name" className="block text-sm font-medium text-secondary-700">
                  Nome *
                </Label>
                <Input
                  id="name"
                  value={formData.name || ''}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Transportadora LTDA"
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
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="contato@transportadora.com"
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
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
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
                    onChange={(e) => setFormData({...formData, zipCode: e.target.value})}
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
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
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
                    onChange={(e) => setFormData({...formData, city: e.target.value})}
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
                    onChange={(e) => setFormData({...formData, state: e.target.value})}
                    placeholder="SP"
                    maxLength={2}
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-secondary-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-medium text-secondary-900 flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Contatos
                </h3>
              </div>

              {/* Add Contact Form */}
              <div className="grid gap-4 sm:grid-cols-4 mb-4 p-4 bg-secondary-50 rounded-lg">
                <div className="space-y-2 sm:col-span-2">
                  <Label className="block text-sm font-medium text-secondary-700">Nome *</Label>
                  <Input
                    value={contactForm.name}
                    onChange={(e) => setContactForm({...contactForm, name: e.target.value})}
                    placeholder="João Silva"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="block text-sm font-medium text-secondary-700">Email *</Label>
                  <Input
                    type="email"
                    value={contactForm.email}
                    onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                    placeholder="joao@transportadora.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="block text-sm font-medium text-secondary-700">Telefone</Label>
                  <Input
                    value={contactForm.phone}
                    onChange={(e) => setContactForm({...contactForm, phone: e.target.value})}
                    placeholder="(11) 99999-9999"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="block text-sm font-medium text-secondary-700">Cargo</Label>
                  <Input
                    value={contactForm.role}
                    onChange={(e) => setContactForm({...contactForm, role: e.target.value})}
                    placeholder="Gerente Comercial"
                  />
                </div>
                <div className="flex items-end">
                  <Button type="button" variant="primary" onClick={addContact} className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Adicionar
                  </Button>
                </div>
              </div>

              {/* Contacts List */}
              {formData.contacts && formData.contacts.length > 0 ? (
                <div className="space-y-2">
                  {formData.contacts.map((contact) => (
                    <div key={contact.id} className="flex items-center gap-3 p-3 bg-white border border-secondary-200 rounded-lg">
                      <div className="w-8 h-8 rounded-full bg-secondary-100 text-secondary-600 flex items-center justify-center text-sm font-medium">
                        {contact.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-secondary-900 truncate">{contact.name}</p>
                        <p className="text-sm text-secondary-500">{contact.email}</p>
                        {contact.phone && <p className="text-sm text-secondary-500">{contact.phone}</p>}
                        {contact.role && <p className="text-xs text-secondary-400">{contact.role}</p>}
                      </div>
                      <Button variant="ghost" size="sm" className="text-danger-600 hover:bg-danger-50" onClick={() => removeContact(contact.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-secondary-500 text-center py-4">Nenhum contato adicionado</p>
              )}
            </div>

            <div className="pt-4 border-t border-secondary-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Switch
                  id="isActive"
                  checked={formData.isActive}
                  onCheckedChange={(value) => setFormData({...formData, isActive: value})}
                />
                <Label htmlFor="isActive" className="text-sm font-medium text-secondary-700 cursor-pointer">
                  Transportadora ativa
                </Label>
              </div>
            </div>
          </div>

          <div className="p-6 border-t border-secondary-200 flex justify-end gap-3">
            <Button type="button" variant="secondary" onClick={() => { setShowFormModal(false); setEditingCarrier(null); }}>
              <X className="h-4 w-4 mr-2" />
              Cancelar
            </Button>
            <Button type="submit" variant="primary" loading={createCarrier.isPending || updateCarrier.isPending} disabled={createCarrier.isPending || updateCarrier.isPending}>
              {createCarrier.isPending || updateCarrier.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  {editingCarrier ? 'Atualizar' : 'Criar Transportadora'}
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}