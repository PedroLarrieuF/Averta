"""Type stubs for Prisma ORM"""

from typing import Any, AsyncGenerator, TypeVar

T = TypeVar("T")


class Prisma:
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    def __getattr__(self, name: str) -> Any: ...


class PrismaError(Exception): ...


def get_prisma() -> AsyncGenerator[Prisma, None]: ...