from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.schemas.forum import (
    ForumCategoryCreate, ForumCategoryOut,
    ForumTopicCreate, ForumTopicOut,
    ForumPostCreate, ForumPostOut
)
from app.core.enums import UserRole
from app.core.dependencies import get_current_user, require_role
from app.crud import crud_forum

router = APIRouter()

# -------- CATEGORÍAS --------
@router.post("/categories/", response_model=ForumCategoryOut, status_code=201)
def create_category_route(
    category_in: ForumCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR]))
):
    existing = crud_forum.get_forum_category_by_name(db, category_in.name)
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre")

    try:
        db_category = crud_forum.create_forum_category(db, category_in)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear la categoría")

@router.get("/categories/", response_model=List[ForumCategoryOut])
def get_categories_route(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return crud_forum.get_forum_categories(db=db, skip=skip, limit=limit)

# -------- TEMAS (TOPICS) --------
@router.post("/topics/", response_model=ForumTopicOut, status_code=201)
def create_topic_route(
    topic_in: ForumTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = crud_forum.get_forum_category_by_id(db, topic_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    try:
        db_topic = crud_forum.create_forum_topic(db, topic_in, current_user.id)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear el tema")

@router.get("/topics/", response_model=List[ForumTopicOut])
def get_topics_route(
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return crud_forum.get_forum_topics(db, category_id, skip, limit)

# -------- RESPUESTAS (POSTS) --------
@router.post("/posts/", response_model=ForumPostOut, status_code=201)
def create_post_route(
    post_in: ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    topic = crud_forum.get_forum_topic_by_id(db, post_in.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    try:
        db_post = crud_forum.create_forum_post_with_notification(db, post_in, current_user)
        db.commit()
        db.refresh(db_post)
        return db_post
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear la respuesta")

@router.get("/posts/", response_model=List[ForumPostOut])
def get_posts_route(
    topic_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    if topic_id:
        topic = crud_forum.get_forum_topic_by_id(db, topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Tema no encontrado")

    return crud_forum.get_forum_posts(db, topic_id, skip, limit)

# -------- BÚSQUEDA --------
@router.get("/search/topics", response_model=List[ForumTopicOut])
def search_topics_route(
    keyword: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    return crud_forum.search_forum_topics(db, keyword, skip, limit)

@router.get("/search/responses", response_model=List[ForumPostOut])
def search_responses_route(
    keyword: str = Query(..., min_length=3),
    topic_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    return crud_forum.search_forum_posts(db, keyword, topic_id, skip, limit)