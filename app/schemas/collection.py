from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from .user import UserOut

class UserOut(BaseModel): 
    id: int
    nombre: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class DocumentMinimal(BaseModel): 
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None

class CollectionCreate(CollectionBase):
    document_ids: Optional[List[int]] = None

class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    document_ids: Optional[List[int]] = None

class CollectionInDBBase(CollectionBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class Collection(CollectionInDBBase): 
    owner: UserOut 
    documents: List[DocumentMinimal] = [] 