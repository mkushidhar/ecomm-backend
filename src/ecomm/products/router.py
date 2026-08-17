from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from .deps import ProductServiceDep
from .models import Product
from .schemas import ProductCreate, ProductListParams, ProductResponse

router = APIRouter(
    prefix="/api/v1/product",
    tags=["Product"],
)


@router.post(
    "/add",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    service: ProductServiceDep,
) -> Product:
    return await service.create_product(data)


@router.get(
    "/list",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
)
async def list_products(
    service: ProductServiceDep,
    params: Annotated[ProductListParams, Query()],
) -> list[Product]:
    return await service.list_products(skip=params.skip, limit=params.limit)


@router.get(
    "/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
async def get_product(
    id: UUID,
    service: ProductServiceDep,
) -> Product:
    product = await service.get_product(id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    id: UUID,
    service: ProductServiceDep,
) -> None:
    deleted = await service.delete_product(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
