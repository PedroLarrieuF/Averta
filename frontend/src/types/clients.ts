import type { PaginatedResponse } from './common';

export interface ClientContact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: string;
  isPrimary: boolean;
}

export interface ClientBranch {
  id: string;
  clientId: string;
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain: boolean;
  // Backwards compatibility
  is_main?: boolean;
}

export interface Client {
  id: string;
  companyId: string;
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  contacts: ClientContact[];
  branches: ClientBranch[];
  status: 'ACTIVE' | 'INACTIVE';
  createdAt: string;
  updatedAt: string;
}

export type ClientListResponse = PaginatedResponse<Client>;

export interface ClientFilters {
  status?: 'ACTIVE' | 'INACTIVE';
  search?: string;
  city?: string;
  state?: string;
  page?: number;
  size?: number;
}

export interface ClientCreateRequest {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  contacts?: Omit<ClientContact, 'id'>[];
  branches?: Omit<ClientBranch, 'id' | 'clientId'>[];
}

export interface ClientUpdateRequest {
  name?: string;
  cnpj?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  status?: 'ACTIVE' | 'INACTIVE';
}

export interface ClientBranchCreateRequest {
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain: boolean;
}

export interface ClientBranchUpdateRequest {
  name?: string;
  code?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain?: boolean;
}

export interface ClientContactCreateRequest {
  name: string;
  email: string;
  phone?: string;
  role: string;
  isPrimary: boolean;
}

export interface ClientContactUpdateRequest {
  name?: string;
  email?: string;
  phone?: string;
  role?: string;
  isPrimary?: boolean;
}