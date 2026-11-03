"""Rules module service"""

from prisma.models import Rule as RuleModel

from prisma import Prisma


class RulesService:
    def __init__(self, db: Prisma):
        self.db = db

    async def create_rule(self, data: dict) -> RuleModel:
        """Create a new rule"""
        rule = await self.db.rule.create(data=data)
        return rule

    async def get_rule(self, rule_id: str) -> RuleModel | None:
        """Get rule by ID"""
        return await self.db.rule.find_unique(where={"id": rule_id})

    async def get_rule_by_code(self, code: str) -> RuleModel | None:
        """Get rule by code"""
        return await self.db.rule.find_unique(where={"code": code})

    async def list_rules(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: bool | None = None,
        type: str | None = None,
        search: str | None = None,
    ) -> dict:
        """List rules with pagination and filters"""
        where = {}
        if is_active is not None:
            where["isActive"] = is_active
        if type:
            where["type"] = type
        if search:
            where["OR"] = [
                {"code": {"contains": search, "mode": "insensitive"}},
                {"name": {"contains": search, "mode": "insensitive"}},
            ]

        total = await self.db.rule.count(where=where)
        rules = await self.db.rule.find_many(
            where=where,
            skip=(page - 1) * page_size,
            take=page_size,
            order={"code": "asc"},
        )

        return {
            "items": rules,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def update_rule(self, rule_id: str, data: dict) -> RuleModel:
        """Update a rule (increments version)"""
        existing = await self.db.rule.find_unique(where={"id": rule_id})
        if not existing:
            raise ValueError("Rule not found")

        update_data = data.copy()
        update_data["version"] = existing.version + 1

        rule = await self.db.rule.update(
            where={"id": rule_id},
            data=update_data,
        )
        return rule

    async def delete_rule(self, rule_id: str) -> RuleModel:
        """Delete a rule (soft delete by setting isActive=false)"""
        rule = await self.db.rule.update(
            where={"id": rule_id},
            data={"isActive": False, "version": {"increment": 1}},
        )
        return rule

    async def hard_delete_rule(self, rule_id: str) -> RuleModel:
        """Hard delete a rule (use with caution)"""
        return await self.db.rule.delete(where={"id": rule_id})

    async def get_active_rules(self) -> list[RuleModel]:
        """Get all active rules for engine loading"""
        return await self.db.rule.find_many(
            where={"isActive": True},
            order={"code": "asc"},
        )
