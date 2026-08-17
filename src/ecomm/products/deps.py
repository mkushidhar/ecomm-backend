from typing import Annotated

from fastapi import Depends

from ecomm.core.database import DbConn

from .repository import ProductRepository
from .service import ProductService


def get_product_service(db: DbConn) -> ProductService:
    return ProductService(ProductRepository(db))


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
