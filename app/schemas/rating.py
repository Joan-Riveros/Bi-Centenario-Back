from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class UserOutShort(BaseModel): 
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class RatingBase(BaseModel):
    document_id: int
    score: int = Field(..., ge=1, le=5) 

class RatingCreate(RatingBase):

    pass

class RatingUpdate(BaseModel):
    score: Optional[int] = Field(None, ge=1, le=5)

class RatingInDBBase(RatingBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class Rating(RatingInDBBase): 
    rater: UserOutShort 
