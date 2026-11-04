import type { PaginatedResponse } from './common';

export interface CarrierContact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: string;
}

export interface CarrierBranch {
  id: string;
  carrierId: string;
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain: boolean;
  anttCode?: string;
  // Backwards compatibility
  is_main?: boolean;
  antt_code?: string;
}

export interface Carrier {
  id: string;
  companyId: string;
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  anttRegistry?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  contacts: CarrierContact[];
  branches: CarrierBranch[];
  status: 'ACTIVE' | 'INACTIVE';
  createdAt: string;
  updatedAt: string;
  // Backwards compatibility
  antt_registry?: string;
}

export type CarrierListResponse = PaginatedResponse<Carrier>;

export interface CarrierFilters {
  status?: 'ACTIVE' | 'INACTIVE';
  search?: string;
  city?: string;
  state?: string;
  page?: number;
  size?: number;
}

export interface CarrierCreateRequest {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  anttRegistry?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  contacts?: Omit<CarrierContact, 'id'>[];
  branches?: Omit<CarrierBranch, 'id' | 'carrierId'>[];
}

export interface CarrierUpdateRequest {
  name?: string;
  cnpj?: string;
  email?: string;
  phone?: string;
  anttRegistry?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  status?: 'ACTIVE' | 'INACTIVE';
}

export interface CarrierBranchCreateRequest {
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain: boolean;
  anttCode?: string;
}

export interface CarrierBranchUpdateRequest {
  name?: string;
  code?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain?: boolean;
  anttCode?: string;
}

export interface CarrierContactCreateRequest {
  name: string;
  email: string;
  phone?: string;
  role: string;
}

export interface CarrierContactUpdateRequest {
  name?: string;
  email?: string;
  phone?: string;
  role?: string;
}