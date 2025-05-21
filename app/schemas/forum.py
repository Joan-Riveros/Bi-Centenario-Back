from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserOutShort

# ---------- CATEGORY ----------

class ForumCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class ForumCategoryCreate(ForumCategoryBase):
    pass

class ForumCategoryOut(ForumCategoryBase):
    id: int
    model_config = {"from_attributes": True}


# ---------- TOPIC ----------

class ForumTopicBase(BaseModel):
    title: str
    content: str
    category_id: int

class ForumTopicCreate(ForumTopicBase):
    pass

class ForumTopicOut(ForumTopicBase):
    id: int
    author_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- POST----------

class ForumPostBase(BaseModel):
    content: str
    topic_id: int

class ForumPostCreate(ForumPostBase):
    pass

class ForumPostAuthorOut(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}

class ForumPostOut(ForumPostBase):
    id: int
    author_id: int
    created_at: datetime
    is_moderated: bool
    author: Optional[UserOutShort]

    model_config = {"from_attributes": True}