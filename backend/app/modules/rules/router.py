"""Rules module router"""
from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import Optional, List, Dict, Any
from prisma import Prisma

from app.core.dependencies import (
    get_database,
    CurrentUserDep,
    RequireManager,
    RequireAuditor,
    CompanyIdDep,
    PaginationDep,
)
from app.core.rate_limit import api_limiter
from app.modules.rules.schemas import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
    RuleListResponse,
    RuleEngineStatus,
    RuleType,
    RuleSeverity,
)
from app.modules.rules.service import RulesService
from app.services.rules_engine_v2 import get_engine_instance, reload_engine_rules

router = APIRouter(prefix="/rules", tags=["Rules"])


def get_rules_service(db: Prisma = Depends(get_database)) -> RulesService:
    return RulesService(db)


@router.post(
    "",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create rule",
)
async def create_rule(
    data: RuleCreate,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    rules_service: RulesService = Depends(get_rules_service),
):
    """Create a new audit rule"""
    # Check if code already exists
    existing = await rules_service.get_rule_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="Rule code already exists")

    rule_data = data.model_dump()
    rule = await rules_service.create_rule(rule_data)

    # Reload engine rules
    await reload_engine_rules()

    return rule


@router.get(
    "",
    response_model=RuleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List rules",
)
@api_limiter
async def list_rules(
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    pagination: PaginationDep,
    is_active: Optional[bool] = Query(None),
    type: Optional[RuleType] = Query(None),
    search: Optional[str] = Query(None),
    rules_service: RulesService = Depends(get_rules_service),
):
    """List audit rules with filters"""
    result = await rules_service.list_rules(
        page=pagination.page,
        page_size=pagination.page_size,
        is_active=is_active,
        type=type.value if type else None,
        search=search,
    )
    return result


@router.get(
    "/engine-status",
    response_model=RuleEngineStatus,
    status_code=status.HTTP_200_OK,
    summary="Get rules engine status",
)
async def get_engine_status(
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
):
    """Get rules engine loading status and cache stats"""
    engine = get_engine_instance()

    if engine:
        cache_stats = await engine.get_cache_stats()
        rules_list = engine.list_rules()
        return RuleEngineStatus(
            rulesLoaded=len(rules_list),
            dbRules=len([r for r in rules_list if r.get("_db_version")]),
            builtinFallback=len([r for r in rules_list if not r.get("_db_version")]),
            cacheStats=cache_stats,
        )

    return RuleEngineStatus(
        rulesLoaded=0,
        dbRules=0,
        builtinFallback=0,
        cacheStats={},
    )


@router.post(
    "/reload",
    status_code=status.HTTP_200_OK,
    summary="Reload rules from database",
)
async def reload_rules(
    current_user: RequireManager,
    company_id: CompanyIdDep,
):
    """Force reload rules from database into engine"""
    engine = await reload_engine_rules()
    rules_list = engine.list_rules()
    return {
        "message": "Rules reloaded successfully",
        "rulesLoaded": len(rules_list),
    }


@router.get(
    "/{rule_id}",
    response_model=RuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get rule by ID",
)
@api_limiter
async def get_rule(
    rule_id: str,
    current_user: CurrentUserDep,
    company_id: CompanyIdDep,
    rules_service: RulesService = Depends(get_rules_service),
):
    """Get rule details"""
    rule = await rules_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.patch(
    "/{rule_id}",
    response_model=RuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Update rule",
)
async def update_rule(
    rule_id: str,
    data: RuleUpdate,
    current_user: RequireAuditor,
    company_id: CompanyIdDep,
    rules_service: RulesService = Depends(get_rules_service),
):
    """Update a rule (increments version)"""
    existing = await rules_service.get_rule(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    rule = await rules_service.update_rule(rule_id, update_data)

    # Reload engine rules
    await reload_engine_rules()

    return rule


@router.delete(
    "/{rule_id}",
    response_model=RuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete rule (soft delete)",
)
async def delete_rule(
    rule_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    rules_service: RulesService = Depends(get_rules_service),
):
    """Soft delete a rule (sets isActive=false, increments version)"""
    existing = await rules_service.get_rule(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = await rules_service.delete_rule(rule_id)

    # Reload engine rules
    await reload_engine_rules()

    return rule


@router.delete(
    "/{rule_id}/hard",
    response_model=RuleResponse,
    status_code=status.HTTP_200_OK,
    summary="Hard delete rule",
)
async def hard_delete_rule(
    rule_id: str,
    current_user: RequireManager,
    company_id: CompanyIdDep,
    rules_service: RulesService = Depends(get_rules_service),
):
    """Hard delete a rule (use with caution - permanent)"""
    existing = await rules_service.get_rule(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = await rules_service.hard_delete_rule(rule_id)

    # Reload engine rules
    await reload_engine_rules()

    return rule