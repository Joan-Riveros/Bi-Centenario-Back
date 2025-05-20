# app/schemas/tag.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None

class TagInDBBase(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Tag(TagInDBBase):
    pass