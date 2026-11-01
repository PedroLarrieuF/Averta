"""Base module classes for consistent CRUD patterns"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from prisma import Prisma
from prisma.types import WhereUniqueInput, WhereInput, OrderByInput
from app.core.dependencies import PaginationParams, SortParams
from app.core.exceptions import NotFoundError
import structlog

logger = structlog.get_logger()

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType], ABC):
    """Base service with common CRUD operations"""

    def __init__(self, db: Prisma, model_name: str):
        self.db = db
        self.model_name = model_name
        self.model = getattr(db, model_name.lower())

    @abstractmethod
    def _to_response(self, model: ModelType) -> ResponseSchemaType:
        """Convert DB model to response schema"""
        pass

    async def get_by_id(self, id: str, company_id: str) -> ResponseSchemaType:
        """Get single record by ID with company scope"""
        model = await self.model.find_first(
            where={"id": id, "companyId": company_id}
        )
        if not model:
            raise NotFoundError(self.model_name, id)
        return self._to_response(model)

    async def list(
        self,
        company_id: str,
        pagination: PaginationParams,
        sort: SortParams,
        where: Optional[WhereInput] = None,
    ) -> tuple[List[ResponseSchemaType], int]:
        """List records with pagination, sorting, and filtering"""
        where_clause = {"companyId": company_id}
        if where:
            where_clause.update(where)

        order_by: OrderByInput = {}
        if sort.sort_by:
            order_by[sort.sort_by] = sort.sort_order

        total = await self.model.count(where=where_clause)
        records = await self.model.find_many(
            where=where_clause,
            skip=pagination.offset,
            take=pagination.limit,
            order=order_by or None,
        )

        return [self._to_response(r) for r in records], total

    async def create(self, data: CreateSchemaType, company_id: str) -> ResponseSchemaType:
        """Create new record"""
        create_data = data.model_dump(exclude_unset=True)
        create_data["companyId"] = company_id

        model = await self.model.create(data=create_data)
        logger.info(f"{self.model_name}_created", id=model.id, company_id=company_id)
        return self._to_response(model)

    async def update(
        self, id: str, data: UpdateSchemaType, company_id: str
    ) -> ResponseSchemaType:
        """Update record"""
        # Verify ownership
        await self.get_by_id(id, company_id)

        update_data = data.model_dump(exclude_unset=True)
        model = await self.model.update(
            where={"id": id},
            data=update_data,
        )
        logger.info(f"{self.model_name}_updated", id=id, company_id=company_id)
        return self._to_response(model)

    async def delete(self, id: str, company_id: str) -> None:
        """Delete record"""
        await self.get_by_id(id, company_id)
        await self.model.delete(where={"id": id})
        logger.info(f"{self.model_name}_deleted", id=id, company_id=company_id)

    async def exists(self, id: str, company_id: str) -> bool:
        """Check if record exists"""
        count = await self.model.count(where={"id": id, "companyId": company_id})
        return count > 0