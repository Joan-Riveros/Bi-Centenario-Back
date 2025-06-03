from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
import datetime


class UserOutShort(BaseModel): 
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    text_content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    document_id: int
    parent_comment_id: Optional[int] = None 

class CommentUpdate(BaseModel):
    text_content: Optional[str] = Field(None, min_length=1)

class CommentInDBBase(CommentBase):
    id: int
    created_at: datetime.datetime
    user_id: int
    document_id: int
    parent_comment_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class Comment(CommentInDBBase): 
    commenter: UserOutShort 
    replies: List['Comment'] = Field(default_factory=list)

