from uuid import UUID

from .models import Product
from .repository import ProductRepository
from .schemas import ProductCreate


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self.repo = repo

    async def create_product(
        self,
        data: ProductCreate,
    ) -> Product:
        product = Product(**data.model_dump())
        return await self.repo.create(product)

    async def get_product(
        self,
        product_id: UUID,
    ) -> Product | None:
        result = await self.repo.get_by_id(product_id)
        return result

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Product]:
        result = await self.repo.get_all(skip=skip, limit=limit)
        return result

    async def delete_product(
        self,
        product_id: UUID,
    ) -> bool:
        result = await self.repo.delete_by_id(id=product_id)
        return result
