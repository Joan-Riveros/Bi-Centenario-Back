from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ---------- CATEGORY ----------

class ForumCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class ForumCategoryCreate(ForumCategoryBase):
    pass

class ForumCategoryOut(ForumCategoryBase):
    id: int

    class Config:
        from_attributes = True


# ---------- TOPIC (HILO) ----------

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

    class Config:
        from_attributes = True


# ---------- POST (RESPUESTA) ----------

class ForumPostBase(BaseModel):
    content: str
    topic_id: int

class ForumPostCreate(ForumPostBase):
    pass

class ForumPostOut(ForumPostBase):
    id: int
    author_id: int
    created_at: datetime
    is_moderated: bool

    class Config:
        from_attributes = True
