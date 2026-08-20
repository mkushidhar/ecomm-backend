from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=5, max_length=20)
    description: str = Field(min_length=20)
    units: int = Field(default=0, ge=0)
    price: float = Field(ge=0)


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str
    units: int
    price: float
    created_at: datetime


class ProductListParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
