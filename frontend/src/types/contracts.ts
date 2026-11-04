import type { ContractStatus, FreightTableStatus, FreightType, ModalType, FreightValueType } from './enums';
import type { PaginatedResponse } from './common';
import type { Client } from './clients';
import type { Carrier } from './carriers';

export interface FreightRate {
  id: string;
  weightMin: number | null;
  weightMax: number | null;
  cubageMin: number | null;
  cubageMax: number | null;
  distanceMin: number | null;
  distanceMax: number | null;
  modal: ModalType;
  ufOrigin: string | null;
  ufDest: string | null;
  ratePerKg: number | null;
  ratePerM3: number | null;
  ratePerKm: number | null;
  minimumValue: number | null;
}

export interface FreightTableEntry {
  id: string;
  originCity: string;
  originState: string;
  destinationCity: string;
  destinationState: string;
  freightType: FreightType;
  weightMin: number;
  weightMax: number;
  volumeMin?: number;
  volumeMax?: number;
  value: number;
  valueType: FreightValueType;
  icms?: number;
  tolls?: number;
}

export interface FreightTable {
  id: string;
  contractId: string;
  version: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo: string | null;
  rates: FreightRate[];
  entries: FreightTableEntry[];
  createdAt: string;
  updatedAt: string;
}

export interface Contract {
  id: string;
  companyId: string;
  clientId: string;
  carrierId: string;
  name: string;
  number: string;
  version: number;
  status: ContractStatus;
  startDate: string;
  endDate?: string;
  successFeePct: number;
  description?: string;
  client?: Client;
  carrier?: Carrier;
  freightTables: FreightTable[];
  // Backwards compatibility
  freightTable?: FreightTableEntry[];
  createdAt: string;
  updatedAt: string;
}

export type ContractListResponse = PaginatedResponse<Contract>;

export interface ContractFilters {
  status?: ContractStatus;
  clientId?: string;
  carrierId?: string;
  search?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  size?: number;
}

export interface ContractCreateRequest {
  number: string;
  clientId: string;
  carrierId: string;
  name: string;
  status: ContractStatus;
  startDate: string;
  endDate?: string;
  successFeePct: number;
  description?: string;
}

export interface ContractUpdateRequest {
  number?: string;
  clientId?: string;
  carrierId?: string;
  name?: string;
  status?: ContractStatus;
  startDate?: string;
  endDate?: string;
  successFeePct?: number;
  description?: string;
}

export interface FreightTableCreateRequest {
  contractId: string;
  version: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo?: string;
  rates: Omit<FreightRate, 'id'>[];
  entries: Omit<FreightTableEntry, 'id'>[];
}

export interface FreightTableUpdateRequest {
  version?: number;
  status?: FreightTableStatus;
  effectiveFrom?: string;
  effectiveTo?: string;
  rates?: Omit<FreightRate, 'id'>[];
  entries?: Omit<FreightTableEntry, 'id'>[];
}

export interface FreightTableActivateRequest {
  freightTableId: string;
}

export interface FreightTableVersionResponse {
  id: string;
  version: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo: string | null;
  createdAt: string;
}