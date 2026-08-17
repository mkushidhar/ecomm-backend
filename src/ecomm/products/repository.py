from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Product


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_by_id(self, id: UUID) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int, limit: int) -> list[Product]:
        result = await self.db.execute(
            select(Product).order_by(Product.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def delete_by_id(self, id: UUID) -> bool:
        product = await self.get_by_id(id)
        if product is None:
            return False
        await self.db.delete(product)
        await self.db.commit()
        return True
