// Contracts & Freight Tables Hooks
// Card #24: Contracts Page - CRUD + FreightTable Editor

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import type {
  Contract,
  ContractListParams,
  PaginatedContracts,
  ContractCreateRequest,
  ContractUpdateRequest,
  FreightTable,
  CreateFreightTableData,
  UpdateFreightTableData,
  SimpleSelectOption,
} from '../types/contracts';

// ============ CONTRACTS HOOKS ============

export function useContracts(params: ContractListParams = {}) {
  return useQuery({
    queryKey: ['contracts', params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params.page) searchParams.set('page', String(params.page));
      if (params.size) searchParams.set('size', String(params.size));
      if (params.search) searchParams.set('search', params.search);
      if (params.status) searchParams.set('status', params.status);
      if (params.clientId) searchParams.set('clientId', params.clientId);
      if (params.carrierId) searchParams.set('carrierId', params.carrierId);
      if (params.dateFrom) searchParams.set('dateFrom', params.dateFrom);
      if (params.dateTo) searchParams.set('dateTo', params.dateTo);

      const response = await api.get<PaginatedContracts>(`/contracts?${searchParams.toString()}`);
      return response.data;
    },
    placeholderData: (previousData) => previousData,
  });
}

export function useContract(id: string | undefined) {
  return useQuery({
    queryKey: ['contract', id],
    queryFn: async () => {
      if (!id) return null;
      const response = await api.get<Contract>(`/contracts/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ContractCreateRequest) => {
      const response = await api.post<Contract>('/contracts', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useUpdateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ContractUpdateRequest }) => {
      const response = await api.patch<Contract>(`/contracts/${id}`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
      queryClient.invalidateQueries({ queryKey: ['contract', id] });
    },
  });
}

export function useDeleteContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/contracts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

// ============ FREIGHT TABLES HOOKS ============

export function useFreightTables(contractId: string | undefined) {
  return useQuery({
    queryKey: ['freight-tables', contractId],
    queryFn: async () => {
      if (!contractId) return [];
      const response = await api.get<FreightTable[]>(`/contracts/${contractId}/freight-tables`);
      return response.data;
    },
    enabled: !!contractId,
  });
}

export function useFreightTable(id: string | undefined) {
  return useQuery({
    queryKey: ['freight-table', id],
    queryFn: async () => {
      if (!id) return null;
      const response = await api.get<FreightTable>(`/freight-tables/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateFreightTable() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateFreightTableData) => {
      const response = await api.post<FreightTable>(`/contracts/${data.contractId}/freight-tables`, data);
      return response.data;
    },
    onSuccess: (_, { contractId }) => {
      queryClient.invalidateQueries({ queryKey: ['freight-tables', contractId] });
    },
  });
}

export function useUpdateFreightTable() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateFreightTableData }) => {
      const response = await api.patch<FreightTable>(`/freight-tables/${id}`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['freight-table', id] });
      queryClient.invalidateQueries({ queryKey: ['freight-tables'] });
    },
  });
}

export function useActivateFreightTable() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<FreightTable>(`/freight-tables/${id}/activate`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['freight-table', id] });
      queryClient.invalidateQueries({ queryKey: ['freight-tables'] });
    },
  });
}

export function useDeleteFreightTable() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/freight-tables/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['freight-tables'] });
    },
  });
}

// ============ REFERENCE DATA HOOKS ============

export function useClientsSimple() {
  return useQuery({
    queryKey: ['clients', 'simple'],
    queryFn: async () => {
      const response = await api.get<SimpleSelectOption[]>('/clients?status=ACTIVE&size=100');
      return response.data.map((c) => ({ id: c.id, name: c.name }));
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCarriersSimple() {
  return useQuery({
    queryKey: ['carriers', 'simple'],
    queryFn: async () => {
      const response = await api.get<SimpleSelectOption[]>('/carriers?status=ACTIVE&size=100');
      return response.data.map((c) => ({ id: c.id, name: c.name }));
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}