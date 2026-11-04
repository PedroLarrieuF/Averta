// Form Types - Inferred from Zod Schemas
// Import schemas from components to infer types
// These types should match the Zod schemas in the respective component files

// From ProfileForm.tsx
export interface ProfileFormData {
  name: string;
  email: string;
  phone?: string;
}

// From ChangePasswordModal.tsx
export interface ChangePasswordFormData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

// From NotificationPreferences.tsx
export interface NotificationPreferencesFormData {
  email_enabled: boolean;
  in_app_enabled: boolean;
  weekly_report: boolean;
  discrepancy_alerts: boolean;
  contest_updates: boolean;
}

// From DangerZone.tsx
export interface DeleteAccountFormData {
  password: string;
  confirm_text: 'EXCLUIR';
}

// From ClientForm.tsx
export interface ClientFormData {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  contacts?: ClientContactFormData[];
  branches?: ClientBranchFormData[];
}

export interface ClientContactFormData {
  name: string;
  email: string;
  phone?: string;
  role: string;
  isPrimary: boolean;
}

export interface ClientBranchFormData {
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain: boolean;
}

// From CarrierForm.tsx
export interface CarrierFormData {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  anttRegistry?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  contacts?: CarrierContactFormData[];
  branches?: CarrierBranchFormData[];
}

export interface CarrierContactFormData {
  name: string;
  email: string;
  phone?: string;
  role: string;
}

export interface CarrierBranchFormData {
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  isMain: boolean;
  anttCode?: string;
}

// From ContractForm.tsx (Settings)
export interface ContractFormData {
  number: string;
  clientId: string;
  carrierId: string;
  name: string;
  status: 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED';
  startDate: string;
  endDate?: string;
  successFeePct: number;
  description?: string;
}

// From FreightTableEditor.tsx
export interface FreightRateFormData {
  id?: string;
  weightMin: number | null;
  weightMax: number | null;
  cubageMin: number | null;
  cubageMax: number | null;
  distanceMin: number | null;
  distanceMax: number | null;
  modal: 'RODOVIARIO' | 'AEREO' | 'MARITIMO' | 'FERROVIARIO';
  ufOrigin: string | null;
  ufDest: string | null;
  ratePerKg: number | null;
  ratePerM3: number | null;
  ratePerKm: number | null;
  minimumValue: number | null;
}

export interface FreightTableEntryFormData {
  id?: string;
  originCity: string;
  originState: string;
  destinationCity: string;
  destinationState: string;
  freightType: 'NORMAL' | 'EXPRESS' | 'FRACIONADO' | 'CARGA_FECHADA';
  weightMin: number;
  weightMax: number;
  volumeMin?: number;
  volumeMax?: number;
  value: number;
  valueType: 'FIXED' | 'PER_KG' | 'PER_VOLUME';
  icms?: number;
  tolls?: number;
}

// From ContestCreateStepper.tsx
export interface ContestCreateStep1Data {
  discrepancyIds: string[];
}

export interface ContestCreateStep2Data {
  carrierId: string;
  title: string;
  description: string;
  requestedAmount: number;
}

export interface ContestCreateStep3Data {
  evidenceFiles: File[];
}

export interface ContestCreateFormData {
  discrepancyIds: string[];
  carrierId: string;
  title: string;
  description: string;
  requestedAmount: number;
  evidenceFiles: File[];
}

// From CommunicationThread.tsx
export interface CommunicationFormData {
  message: string;
  isInternal: boolean;
  attachments?: File[];
}

// From PaymentForm.tsx
export interface PaymentFormData {
  amount: number;
  paymentMethod: string;
  reference: string;
}

// From Negotiate form
export interface NegotiateFormData {
  offeredAmount: number;
  message: string;
}

// From UserInviteModal.tsx
export interface UserInviteFormData {
  email: string;
  fullName: string;
  role: 'ADMIN' | 'MANAGER' | 'AUDITOR' | 'CLIENT';
  companyId?: string;
}

// From CompanySettingsPage.tsx
export interface CompanySettingsFormData {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  settings: CompanySettingsFormData;
}

export interface CompanySettingsFormData {
  autoApproveThreshold?: number;
  defaultCurrency: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    discrepancies: boolean;
    contests: boolean;
    documents: boolean;
  };
}

// From Settings pages
export interface SettingsCompanyFormData {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
}

export interface SettingsUserFormData {
  email: string;
  fullName: string;
  role: 'ADMIN' | 'MANAGER' | 'AUDITOR' | 'CLIENT';
  status: 'ACTIVE' | 'INACTIVE' | 'PENDING';
}

export interface SettingsCarrierFormData {
  name: string;
  cnpj: string;
  email?: string;
  phone?: string;
  anttRegistry?: string;
  address?: string;
  city?: string;
  state?: string;
  zipCode?: string;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface SettingsContractFormData {
  number: string;
  clientId: string;
  carrierId: string;
  name: string;
  status: 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED';
  startDate: string;
  endDate?: string;
  successFeePct: number;
  description?: string;
}

export interface SettingsNotificationFormData {
  email_enabled: boolean;
  in_app_enabled: boolean;
  weekly_report: boolean;
  discrepancy_alerts: boolean;
  contest_updates: boolean;
  push_enabled?: boolean;
  sms_enabled?: boolean;
}

// Login/Register (from Login.tsx, Register.tsx)
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  fullName: string;
  companyName: string;
  companyCnpj: string;
}