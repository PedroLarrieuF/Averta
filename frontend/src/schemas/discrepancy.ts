import { z } from 'zod';

// ============================================================================
// Enum Schemas
// ============================================================================

export const discrepancyStatusSchema = z.enum([
  'OPEN',
  'IN_REVIEW',
  'CONTESTED',
  'APPROVED',
  'REJECTED',
  'PAID',
  'CLOSED',
]);

export const discrepancySeveritySchema = z.enum([
  'LOW',
  'MEDIUM',
  'HIGH',
  'CRITICAL',
]);

export const discrepancyTypeSchema = z.enum([
  'FREIGHT_VALUE',
  'ICMS',
  'TOLLS',
  'WEIGHT',
  'VOLUME',
  'DIMENSIONS',
  'DUPLICATE',
  'MISSING_DOCUMENT',
  'INVALID_CNPJ',
  'ROUTE_MISMATCH',
  'OTHER',
]);

// ============================================================================
// Core Discrepancy Schemas
// ============================================================================

export const discrepancySchema = z.object({
  id: z.string().uuid(),
  companyId: z.string().uuid(),
  documentId: z.string().uuid(),
  contractId: z.string().uuid().optional(),
  clientId: z.string().uuid().optional(),
  carrierId: z.string().uuid().optional(),
  type: discrepancyTypeSchema,
  severity: discrepancySeveritySchema,
  status: discrepancyStatusSchema,
  description: z.string().min(1).max(1000),
  expectedValue: z.number(),
  actualValue: z.number(),
  difference: z.number(),
  differencePercent: z.number(),
  fieldName: z.string().min(1).max(255),
  suggestedAction: z.string().max(1000).optional(),
  reviewedBy: z.string().uuid().optional(),
  reviewedAt: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

// Paginated response schema
export const paginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    data: z.array(itemSchema),
    meta: z.object({
      total: z.number().int().nonnegative(),
      page: z.number().int().positive(),
      limit: z.number().int().positive(),
      totalPages: z.number().int().nonnegative(),
    }),
  });

export const discrepancyListResponseSchema = paginatedResponseSchema(discrepancySchema);

// ============================================================================
// Discrepancy Summary Schema
// ============================================================================

export const discrepancySummarySchema = z.object({
  total: z.number().int().nonnegative(),
  by_status: z.record(discrepancyStatusSchema, z.number().int().nonnegative()),
  by_severity: z.record(discrepancySeveritySchema, z.number().int().nonnegative()),
  by_rule: z.record(discrepancyTypeSchema, z.number().int().nonnegative()),
  total_recovered: z.number().nonnegative(),
  total_contested: z.number().nonnegative(),
});

// ============================================================================
// Request/Filter Schemas
// ============================================================================

export const discrepancyFiltersSchema = z.object({
  status: z.array(discrepancyStatusSchema).optional(),
  severity: z.array(discrepancySeveritySchema).optional(),
  rule_code: z.array(discrepancyTypeSchema).optional(),
  clientId: z.string().uuid().optional(),
  carrierId: z.string().uuid().optional(),
  contractId: z.string().uuid().optional(),
  documentId: z.string().uuid().optional(),
  dateFrom: z.string().datetime().optional(),
  dateTo: z.string().datetime().optional(),
  search: z.string().max(255).optional(),
  page: z.number().int().positive().optional().default(1),
  size: z.number().int().positive().max(100).optional().default(20),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).optional(),
});

export const discrepancyListParamsSchema = discrepancyFiltersSchema;

// ============================================================================
// Mutation Payload Schemas
// ============================================================================

export const bulkStatusPayloadSchema = z.object({
  ids: z.array(z.string().uuid()).min(1).max(1000),
  status: discrepancyStatusSchema,
});

export const reviewPayloadSchema = z.object({
  notes: z.string().max(2000).optional(),
});

export const bulkReviewPayloadSchema = z.object({
  ids: z.array(z.string().uuid()).min(1).max(1000),
  notes: z.string().max(2000).optional(),
});

export const createContestFromDiscrepanciesSchema = z.object({
  discrepancyIds: z.array(z.string().uuid()).min(1),
  title: z.string().min(1).max(255),
  description: z.string().min(1).max(5000),
});

// ============================================================================
// Create/Update Request Schemas
// ============================================================================

export const discrepancyCreateRequestSchema = z.object({
  documentId: z.string().uuid(),
  contractId: z.string().uuid().optional(),
  clientId: z.string().uuid().optional(),
  carrierId: z.string().uuid().optional(),
  type: discrepancyTypeSchema,
  severity: discrepancySeveritySchema,
  description: z.string().min(1).max(1000),
  expectedValue: z.number(),
  actualValue: z.number(),
  difference: z.number(),
  differencePercent: z.number(),
  fieldName: z.string().min(1).max(255),
  suggestedAction: z.string().max(1000).optional(),
});

export const discrepancyUpdateRequestSchema = z.object({
  severity: discrepancySeveritySchema.optional(),
  description: z.string().max(1000).optional(),
  expectedValue: z.number().optional(),
  actualValue: z.number().optional(),
  difference: z.number().optional(),
  differencePercent: z.number().optional(),
  fieldName: z.string().max(255).optional(),
  suggestedAction: z.string().max(1000).optional(),
});

// ============================================================================
// Inferred Types
// ============================================================================

export type DiscrepancySchema = z.infer<typeof discrepancySchema>;
export type DiscrepancyListResponseSchema = z.infer<typeof discrepancyListResponseSchema>;
export type DiscrepancySummarySchema = z.infer<typeof discrepancySummarySchema>;
export type DiscrepancyFiltersSchema = z.infer<typeof discrepancyFiltersSchema>;
export type DiscrepancyListParamsSchema = z.infer<typeof discrepancyListParamsSchema>;
export type BulkStatusPayloadSchema = z.infer<typeof bulkStatusPayloadSchema>;
export type ReviewPayloadSchema = z.infer<typeof reviewPayloadSchema>;
export type BulkReviewPayloadSchema = z.infer<typeof bulkReviewPayloadSchema>;
export type CreateContestFromDiscrepanciesSchema = z.infer<typeof createContestFromDiscrepanciesSchema>;
export type DiscrepancyCreateRequestSchema = z.infer<typeof discrepancyCreateRequestSchema>;
export type DiscrepancyUpdateRequestSchema = z.infer<typeof discrepancyUpdateRequestSchema>;

// ============================================================================
// Validation Helpers
// ============================================================================

/**
 * Validates a discrepancy object
 */
export function validateDiscrepancy(data: unknown) {
  return discrepancySchema.safeParse(data);
}

/**
 * Validates a discrepancy list response
 */
export function validateDiscrepancyList(data: unknown) {
  return discrepancyListResponseSchema.safeParse(data);
}

/**
 * Validates a discrepancy summary
 */
export function validateDiscrepancySummary(data: unknown) {
  return discrepancySummarySchema.safeParse(data);
}

/**
 * Validates discrepancy filters
 */
export function validateDiscrepancyFilters(data: unknown) {
  return discrepancyFiltersSchema.safeParse(data);
}

/**
 * Validates bulk status update payload
 */
export function validateBulkStatusPayload(data: unknown) {
  return bulkStatusPayloadSchema.safeParse(data);
}

/**
 * Validates review payload
 */
export function validateReviewPayload(data: unknown) {
  return reviewPayloadSchema.safeParse(data);
}

/**
 * Validates bulk review payload
 */
export function validateBulkReviewPayload(data: unknown) {
  return bulkReviewPayloadSchema.safeParse(data);
}

/**
 * Validates create contest from discrepancies payload
 */
export function validateCreateContestFromDiscrepancies(data: unknown) {
  return createContestFromDiscrepanciesSchema.safeParse(data);
}

/**
 * Validates discrepancy create request
 */
export function validateDiscrepancyCreateRequest(data: unknown) {
  return discrepancyCreateRequestSchema.safeParse(data);
}

/**
 * Validates discrepancy update request
 */
export function validateDiscrepancyUpdateRequest(data: unknown) {
  return discrepancyUpdateRequestSchema.safeParse(data);
}

// ============================================================================
// Schema Exports for Hook Form Resolvers
// ============================================================================

export const discrepancyFormSchema = discrepancyCreateRequestSchema;
export const discrepancyUpdateFormSchema = discrepancyUpdateRequestSchema;
export const bulkStatusFormSchema = bulkStatusPayloadSchema;
export const reviewFormSchema = reviewPayloadSchema;
export const bulkReviewFormSchema = bulkReviewPayloadSchema;
export const createContestFormSchema = createContestFromDiscrepanciesSchema;