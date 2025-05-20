# app/schemas/category.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryInDBBase(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Category(CategoryInDBBase):
    pass