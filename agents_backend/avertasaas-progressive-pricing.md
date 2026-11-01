---
name: averta-saas-progressive-pricing
description: "Progressive pricing implementation (5% month 1, 10% month 2+) for AvertaSaaS success-fee model"
metadata:
  node_type: memory
  type: project
  originSessionId: a869b3f4-d5df-49d9-a9e0-c88017874c4c
  modified: 2026-11-01T17:06:21.591Z
---

# AvertaSaaS - Progressive Pricing Implementation

**Implemented**: 2026-11-01
**Status**: Complete, ready for testing

## Business Rule
- **Month 1** (first 30 days from contract start/progressive start date): **5%** success fee on recovered values
- **Month 2+** (day 30 onwards): **10%** success fee on recovered values
- **Fixed model** (default): Uses contract's `success_fee_pct` (e.g., 25%)

## Files Modified

### 1. Prisma Schema (`prisma/schema.prisma`)
- Added enum `PricingModel` (FIXED, PROGRESSIVE)
- Added to `Contract` model:
  - `pricingModel` (default: FIXED)
  - `progressiveStartDate` (DateTime?)
  - `progressiveMonth1Pct` (default: 5.0)
  - `progressiveMonth2Pct` (default: 10.0)
- Fixed enum defaults: `DocumentStatus` added UPLOADED, `DiscrepancyStatus` added DETECTED
- Fixed relation issues: User↔Client (ClientUser), ContestItem↔Payment (ContestItemPayments)
- Generator updated to `interface = "asyncio"` with `recursive_type_depth = 5`

### 2. Contracts Module
- **schemas.py**: Progressive fields in ContractCreate/Update/Response
- **service.py**: 
  - `_to_response()` includes progressive fields
  - `field_map` maps snake_case → camelCase
  - **New method**: `calculate_progressive_fee_pct(contract, reference_date)` - core logic

### 3. Contests Module  
- **schemas.py**: `pricing_model`, `progressive_month` in ContestResponse
- **service.py**:
  - Injected `ContractsService`
  - `create_contest()`: uses progressive calc if contract exists
  - `respond_contest()`: recalculates fee on carrier response
  - `_to_response()` (now async): fetches contract for pricing info
  - **New method**: `recalculate_success_fee(contest_id, company_id, reference_date)`
- **router.py**: `POST /contests/{id}/recalculate-fee`

### 4. Reports Module
- **schemas.py**: Progressive fields in RecoveryReportItem, SuccessFeeReportItem
- **service.py**: 
  - Injected `ContractsService`
  - `get_recovery_report()`, `get_success_fee_report()` include progressive info
  - Excel exports updated with new columns

### 5. Tasks/Celery
- **tasks/discrepancies.py**: `recalculate_progressive_success_fees` task (daily)
- **core/celery_app.py**: Beat schedule for daily execution

## Key Logic (ContractsService)
```python
def calculate_progressive_fee_pct(self, contract, reference_date=None):
    if contract.pricingModel == "FIXED":
        return contract.successFeePct
    
    start = contract.progressiveStartDate or contract.startDate
    days = (reference_date or utcnow) - start
    return contract.progressiveMonth1Pct if days < 30 else contract.progressiveMonth2Pct
```

## Testing Checklist
- [ ] `prisma db push` to apply migrations
- [ ] Create contract with `pricingModel: "PROGRESSIVE"`
- [ ] Create contest, verify 5% fee in month 1
- [ ] Wait/advance time, verify 10% fee in month 2+
- [ ] Test `POST /contests/{id}/recalculate-fee`
- [ ] Verify reports include progressive fields
- [ ] Verify Excel exports have new columns

## Related Memory
- [[avertasaas-project]] - Main project context