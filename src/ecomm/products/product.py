from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ecomm.core.database import get_db

from .models import Product
from .schemas import ProductCreate, ProductCreateResponse

router = APIRouter(prefix="/api/v1/product", tags=["Product"])

DbConn = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/add",
    response_model=ProductCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_product(
    product: ProductCreate,
    db: DbConn,
) -> ProductCreateResponse:
    db_product = Product(
        name=product.name,
        description=product.description,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    resp = ProductCreateResponse(
        id=db_product.id,
        name=db_product.name,
        description=db_product.description,
    )
    return resp
