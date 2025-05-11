from app.models.notification import Notification  
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.user import User
from app.models.forum import ForumCategory, ForumTopic, ForumPost
from app.schemas.forum import (
    ForumCategoryCreate, ForumCategoryOut,
    ForumTopicCreate, ForumTopicOut,
    ForumPostCreate, ForumPostOut
)
from app.core.security import get_current_user, require_role

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- CATEGORÍAS --------
@router.post("/categories/", response_model=ForumCategoryOut)
def create_category(
    category: ForumCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    db_category = ForumCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[ForumCategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(ForumCategory).all()


# -------- TEMAS --------
@router.post("/topics/", response_model=ForumTopicOut)
def create_topic(
    topic: ForumTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_topic = ForumTopic(**topic.dict(), author_id=current_user.id)
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    return new_topic

@router.get("/topics/", response_model=List[ForumTopicOut])
def get_topics(db: Session = Depends(get_db)):
    return db.query(ForumTopic).all()


# -------- RESPUESTAS --------
@router.post("/posts/", response_model=ForumPostOut)
def create_post(
    post: ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Crear la respuesta
    new_post = ForumPost(**post.dict(), author_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Buscar el tema correspondiente
    topic = db.query(ForumTopic).filter(ForumTopic.id == post.topic_id).first()

    # Crear notificación si el autor del post no es el autor del tema
    if topic and topic.author_id != current_user.id:
        notification = Notification(
            user_id=topic.author_id,
            message=f"{current_user.email} respondió a tu tema: {topic.title}"
        )
        db.add(notification)
        db.commit()

    return new_post


@router.get("/posts/", response_model=List[ForumPostOut])
def get_posts(db: Session = Depends(get_db)):
    return db.query(ForumPost).all()

@router.get("/search/topics", response_model=list[ForumTopicOut])
def search_topics(keyword: str, db: Session = Depends(get_db)):
    results = db.query(ForumTopic).filter(
        (ForumTopic.title.ilike(f"%{keyword}%")) |
        (ForumTopic.content.ilike(f"%{keyword}%"))  # ← CAMPO CORRECTO
    ).all()
    return results


@router.get("/search/responses", response_model=list[ForumPostOut])
def search_responses(keyword: str, db: Session = Depends(get_db)):
    results = db.query(ForumPost).filter(
        ForumPost.content.ilike(f"%{keyword}%")
    ).all()
    return results
