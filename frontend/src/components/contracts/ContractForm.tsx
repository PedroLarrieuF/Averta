// Contract Form Component
// Card #24: Contracts Page - CRUD + FreightTable Editor

import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';
import { Button, Input, Label, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Modal, Card, CardBody, CardFooter } from '../index';

export interface ContractFormData {
  number: string;
  client_id: string;
  carrier_id: string;
  status: 'ACTIVE' | 'EXPIRED' | 'PENDING';
  start_date: string;
  end_date?: string;
  success_fee_pct: string;
  description: string;
}

export const contractSchema = z.object({
  number: z.string().min(1, 'Número é obrigatório'),
  client_id: z.string().min(1, 'Cliente é obrigatório'),
  carrier_id: z.string().min(1, 'Transportadora é obrigatória'),
  status: z.enum(['ACTIVE', 'EXPIRED', 'PENDING']),
  start_date: z.string().min(1, 'Data de início é obrigatória'),
  end_date: z.string().optional(),
  success_fee_pct: z.string().refine((val) => {
    const num = parseFloat(val);
    return !isNaN(num) && num >= 0 && num <= 100;
  }, 'Success fee deve estar entre 0 e 100'),
  description: z.string().optional(),
}).refine((data) => {
  if (data.end_date) {
    return new Date(data.end_date) >= new Date(data.start_date);
  }
  return true;
}, {
  message: 'Data de fim deve ser posterior à data de início',
  path: ['end_date'],
});

interface ContractFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: any) => Promise<void>;
  clients: { id: string; name: string }[];
  carriers: { id: string; name: string }[];
  initialData?: Partial<ContractFormData> | null;
  isSubmitting?: boolean;
  title?: string;
}

const STATUS_OPTIONS = [
  { value: 'ACTIVE', label: 'Ativo' },
  { value: 'EXPIRED', label: 'Expirado' },
  { value: 'PENDING', label: 'Pendente' },
] as const;

export function ContractForm({
  open,
  onOpenChange,
  onSubmit,
  clients,
  carriers,
  initialData = null,
  isSubmitting = false,
  title = 'Novo Contrato',
}: ContractFormProps) {
  const form = useForm<ContractFormData>({
    resolver: zodResolver(contractSchema),
    defaultValues: {
      number: '',
      client_id: '',
      carrier_id: '',
      status: 'ACTIVE',
      start_date: '',
      end_date: '',
      success_fee_pct: '0',
      description: '',
      ...initialData,
    },
  });

  useEffect(() => {
    if (initialData) {
      form.reset({
        number: '',
        client_id: '',
        carrier_id: '',
        status: 'ACTIVE',
        start_date: '',
        end_date: '',
        success_fee_pct: '0',
        description: '',
        ...initialData,
      });
    } else {
      form.reset({
        number: '',
        client_id: '',
        carrier_id: '',
        status: 'ACTIVE',
        start_date: '',
        end_date: '',
        success_fee_pct: '0',
        description: '',
      });
    }
  }, [open, initialData, form]);

  const handleSubmit = async (data: ContractFormData) => {
    const submitData = {
      ...data,
      success_fee_pct: parseFloat(data.success_fee_pct),
      end_date: data.end_date || undefined,
    };
    await onSubmit(submitData);
    onOpenChange(false);
  };

  return (
    <Modal
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      size="lg"
    >
      <form onSubmit={form.handleSubmit(handleSubmit)}>
        <Card>
          <CardBody className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="number">Número do Contrato *</Label>
                <Input
                  id="number"
                  placeholder="Ex: CT-2024-001"
                  {...form.register('number')}
                />
                {form.formState.errors.number && (
                  <p className="text-sm text-danger-600">{form.formState.errors.number.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="status">Status *</Label>
                <Select
                  value={form.watch('status') as 'ACTIVE' | 'EXPIRED' | 'PENDING'}
                  onValueChange={(value: 'ACTIVE' | 'EXPIRED' | 'PENDING') => form.setValue('status', value)}
                >
                  <SelectTrigger id="status">
                    <SelectValue placeholder="Selecione o status" />
                  </SelectTrigger>
                  <SelectContent>
                    {STATUS_OPTIONS.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {form.formState.errors.status && (
                  <p className="text-sm text-danger-600">{form.formState.errors.status.message}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="client_id">Cliente *</Label>
                <Select
                  value={form.watch('client_id')}
                  onValueChange={(value) => form.setValue('client_id', value)}
                >
                  <SelectTrigger id="client_id">
                    <SelectValue placeholder="Selecione o cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map((client) => (
                      <SelectItem key={client.id} value={client.id}>
                        {client.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {form.formState.errors.client_id && (
                  <p className="text-sm text-danger-600">{form.formState.errors.client_id.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="carrier_id">Transportadora *</Label>
                <Select
                  value={form.watch('carrier_id')}
                  onValueChange={(value) => form.setValue('carrier_id', value)}
                >
                  <SelectTrigger id="carrier_id">
                    <SelectValue placeholder="Selecione a transportadora" />
                  </SelectTrigger>
                  <SelectContent>
                    {carriers.map((carrier) => (
                      <SelectItem key={carrier.id} value={carrier.id}>
                        {carrier.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {form.formState.errors.carrier_id && (
                  <p className="text-sm text-danger-600">{form.formState.errors.carrier_id.message}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="start_date">Data de Início *</Label>
                <Input
                  id="start_date"
                  type="date"
                  {...form.register('start_date')}
                />
                {form.formState.errors.start_date && (
                  <p className="text-sm text-danger-600">{form.formState.errors.start_date.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="end_date">Data de Fim</Label>
                <Input
                  id="end_date"
                  type="date"
                  {...form.register('end_date')}
                />
                {form.formState.errors.end_date && (
                  <p className="text-sm text-danger-600">{form.formState.errors.end_date.message}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="success_fee_pct">Success Fee % *</Label>
                <Input
                  id="success_fee_pct"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  placeholder="0.00"
                  {...form.register('success_fee_pct')}
                />
                {form.formState.errors.success_fee_pct && (
                  <p className="text-sm text-danger-600">{form.formState.errors.success_fee_pct.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="description">Descrição</Label>
              <Input
                id="description"
                placeholder="Descrição opcional do contrato..."
                {...form.register('description')}
              />
            </div>
          </CardBody>

          <CardFooter className="flex justify-end gap-2 p-4 border-t">
            <Button
              type="button"
              variant="secondary"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting || form.formState.isSubmitting}>
              {isSubmitting || form.formState.isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Salvando...
                </>
              ) : (
                'Salvar'
              )}
            </Button>
          </CardFooter>
        </Card>
      </form>
    </Modal>
  );
}