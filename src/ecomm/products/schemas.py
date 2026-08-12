from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=5, max_length=20)
    description: str = Field(min_length=20)


class ProductCreateResponse(BaseModel):
    id: UUID
    name: str
    description: str
