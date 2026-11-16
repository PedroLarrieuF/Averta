// Contracts & Freight Tables Types
// Card #24: Contracts Page - CRUD + FreightTable Editor

export type ContractStatus = 'ACTIVE' | 'EXPIRED' | 'PENDING' | 'DRAFT' | 'CANCELLED';
export type FreightTableStatus = 'DRAFT' | 'ACTIVE' | 'ARCHIVED';
export type FreightModal = 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';
export type FreightType = 'NORMAL' | 'EXPRESS' | 'FRACIONADO' | 'CARGA_FECHADA';
export type FreightValueType = 'FIXED' | 'PER_KG' | 'PER_VOLUME';

export interface Contract {
  id: string;
  companyId: string;
  number: string;
  name: string;
  clientId: string;
  clientName?: string;
  client?: { id: string; name: string; cnpj: string };
  carrierId: string;
  carrierName?: string;
  carrier?: { id: string; name: string; cnpj: string };
  status: ContractStatus;
  version: number;
  startDate: string;
  endDate: string | null;
  successFeePct: number;
  description: string | null;
  freightTablesCount: number;
  documentsCount: number;
  discrepanciesCount: number;
  contestsCount: number;
  freightTables?: FreightTable[];
  createdAt: string;
  updatedAt: string;
}

export interface ContractListParams {
  page?: number;
  size?: number;
  search?: string;
  status?: ContractStatus;
  clientId?: string;
  carrierId?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface PaginatedContracts {
  data: Contract[];
  meta: {
    page: number;
    size: number;
    total: number;
    totalPages: number;
  };
}

export interface ContractListResponse extends PaginatedContracts {}

export interface ContractFilters {
  search?: string;
  status?: ContractStatus;
  clientId?: string;
  carrierId?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface ContractCreateRequest {
  number: string;
  name: string;
  clientId: string;
  carrierId: string;
  status: ContractStatus;
  version?: number;
  startDate: string;
  endDate: string | null;
  successFeePct: number;
  description?: string;
}

export interface ContractUpdateRequest extends Partial<ContractCreateRequest> {}

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

// Freight Table Types
export interface FreightTable {
  id: string;
  contractId: string;
  version: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo: string | null;
  rates: FreightRate[];
  entries?: FreightTableEntry[];
  createdAt: string;
  updatedAt: string;
}

export interface FreightRate {
  id: string;
  freightTableId: string;
  weightMin: number | null;
  weightMax: number | null;
  cubageMin: number | null;
  cubageMax: number | null;
  distanceMin: number | null;
  distanceMax: number | null;
  modal: FreightModal;
  ufOrigin: string | null;
  ufDest: string | null;
  ratePerKg: number | null;
  ratePerM3: number | null;
  ratePerKm: number | null;
  minimumValue: number | null;
}

export interface FreightRateInput extends Omit<FreightRate, 'id' | 'freightTableId'> {}

export interface CreateFreightTableData {
  contractId: string;
  version?: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo: string | null;
  rates: FreightRateInput[];
  entries?: FreightTableEntry[];
}

export interface UpdateFreightTableData {
  status?: FreightTableStatus;
  effectiveFrom?: string;
  effectiveTo?: string | null;
  rates?: FreightRateInput[];
  entries?: FreightTableEntry[];
}

export interface FreightTableListParams {
  contractId: string;
}

export interface FreightTableCreateRequest {
  contractId: string;
  version?: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo: string | null;
  rates: FreightRateInput[];
  entries?: FreightTableEntry[];
}

export interface FreightTableUpdateRequest {
  status?: FreightTableStatus;
  effectiveFrom?: string;
  effectiveTo?: string | null;
  rates?: FreightRateInput[];
  entries?: FreightTableEntry[];
}

export interface FreightTableActivateRequest {
  status: 'ACTIVE';
}

export interface FreightTableVersionResponse {
  id: string;
  contractId: string;
  version: number;
  status: FreightTableStatus;
  effectiveFrom: string;
  effectiveTo: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface SimpleSelectOption {
  id: string;
  name: string;
}

export const FREIGHT_MODALS: { value: FreightModal; label: string }[] = [
  { value: 'RODOVIARIO', label: 'Rodoviário' },
  { value: 'AEREO', label: 'Aéreo' },
  { value: 'MARITIMO', label: 'Marítimo' },
  { value: 'FERROVIARIO', label: 'Ferroviário' },
];

export const CONTRACT_STATUSES: { value: ContractStatus; label: string }[] = [
  { value: 'ACTIVE', label: 'Ativo' },
  { value: 'EXPIRED', label: 'Expirado' },
  { value: 'PENDING', label: 'Pendente' },
  { value: 'DRAFT', label: 'Rascunho' },
  { value: 'CANCELLED', label: 'Cancelado' },
];

export const FREIGHT_TABLE_STATUSES: { value: FreightTableStatus; label: string }[] = [
  { value: 'DRAFT', label: 'Rascunho' },
  { value: 'ACTIVE', label: 'Ativo' },
  { value: 'ARCHIVED', label: 'Arquivado' },
];

export const FREIGHT_TYPES: { value: FreightType; label: string }[] = [
  { value: 'NORMAL', label: 'Normal' },
  { value: 'EXPRESS', label: 'Expresso' },
  { value: 'FRACIONADO', label: 'Fracionado' },
  { value: 'CARGA_FECHADA', label: 'Carga Fechada' },
];

export const FREIGHT_VALUE_TYPES: { value: FreightValueType; label: string }[] = [
  { value: 'FIXED', label: 'Fixo' },
  { value: 'PER_KG', label: 'Por kg' },
  { value: 'PER_VOLUME', label: 'Por volume' },
];

export const BRAZILIAN_STATES = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
];