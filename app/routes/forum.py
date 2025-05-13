from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.core.enums import UserRole

from app.db.session import get_db 

from app.models.user import User

from app.schemas.forum import (
    ForumCategoryCreate, ForumCategoryOut,
    ForumTopicCreate, ForumTopicOut,
    ForumPostCreate, ForumPostOut
)
from app.core.dependencies import get_current_user
from app.core.dependencies import require_role 


from app.crud import crud_forum

router = APIRouter()

# -------- CATEGORIAS --------
@router.post(
    "/categories/",
    response_model=ForumCategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoria del foro (Solo Admin)"
)

def create_category_route( 
    category_in: ForumCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMINISTRADOR])) 
):
    existing_category = crud_forum.get_forum_category_by_name(db, name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una categoria con este nombre"
        )
    
    db_category = crud_forum.create_forum_category(db=db, category_in=category_in)
    try:
        db.commit()
        db.refresh(db_category)
    except IntegrityError: 
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Ocurrio un error al crear la categoria"
        )
    return db_category

@router.get(
    "/categories/",
    response_model=List[ForumCategoryOut],
    summary="Obtener lista de categorias del foro"
)
def get_categories_route( 
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Nimero de items a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Numero maximo de items a retornar")
):
    return crud_forum.get_forum_categories(db=db, skip=skip, limit=limit)

# -------- TEMAS --------
@router.post(
    "/topics/",
    response_model=ForumTopicOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo tema (hilo) en el foro"
)
def create_topic_route( 
    topic_in: ForumTopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    category = crud_forum.get_forum_category_by_name(db, name="dummy") # Un get_category_by_id vendria bien
    # O mejor, que crud_forum.create_forum_topic maneje esto o devuelva error si category_id es invalido ojo
    # Por simplicidad, asumiremo que category_id es valido o el DB lo rechazara.
    
    db_topic = crud_forum.create_forum_topic(db=db, topic_in=topic_in, author_id=current_user.id)
    if db_topic is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    try:
        db.commit()
        db.refresh(db_topic)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear el tema Verifica que la categoria exista"
        )
    return db_topic

@router.get(
    "/topics/",
    response_model=List[ForumTopicOut],
    summary="Obtener lista de temas (hilos) del foro"
)
def get_topics_route( 
    category_id: Optional[int] = Query(None, description="Filtrar temas por ID de categoria"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Numero de items a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Numero maximo de items a retornar")
):
    return crud_forum.get_forum_topics(
        db=db, category_id=category_id, skip=skip, limit=limit
    )

# -------- RESPUESTAS --------
@router.post(
    "/posts/",
    response_model=ForumPostOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva respuesta a un tema"
)
def create_post_route( 
    post_in: ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    topic = crud_forum.get_forum_topic_by_id(db, topic_id=post_in.topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tema con ID {post_in.topic_id} no encontrado")

    db_post = crud_forum.create_forum_post_with_notification(
        db=db, post_in=post_in, author=current_user
    )
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la respuesta"
        )
    
    db.refresh(db_post) 
    return db_post

@router.get(
    "/posts/",
    response_model=List[ForumPostOut],
    summary="Obtener lista de respuestas (posts)"
)
def get_posts_route( 
    topic_id: Optional[int] = Query(None, description="Filtrar respuestas por ID de tema"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Numero de items a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Numero maximo de tems a retornar")
):
    if topic_id is not None:
        topic = crud_forum.get_forum_topic_by_id(db, topic_id=topic_id)
        if not topic:
             # Opcion 1: Devolver lista vacia
            # return []
            # Opcion 2: Devolver 404 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tema con ID {topic_id} no encontrado")

    return crud_forum.get_forum_posts(
        db=db, topic_id=topic_id, skip=skip, limit=limit
    )

# -------- BUSQUEDA --------
@router.get(
    "/search/topics",
    response_model=List[ForumTopicOut],
    summary="Buscar temas  por palabra clave"
)
def search_topics_route(
    keyword: str = Query(..., min_length=3, description="Palabra clave para buscar en titulos y contenido de temas"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Numero de items a saltar"),
    limit: int = Query(10, ge=1, le=50, description="Numero maximo de items a retornar")
):
    return crud_forum.search_forum_topics(db=db, keyword=keyword, skip=skip, limit=limit)

@router.get(
    "/search/responses",
    response_model=List[ForumPostOut],
    summary="Buscar respuestas por palabra clave"
)
def search_responses_route(
    keyword: str = Query(..., min_length=3, description="Palabra clave para buscar en el contenido de las respuestas"),
    topic_id: Optional[int] = Query(None, description="Opcional: ID del tema para acotar la busqueda"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Numero de items a saltar"),
    limit: int = Query(10, ge=1, le=50, description="Numero maximo de items a retornar")
):
    return crud_forum.search_forum_posts(
        db=db, keyword=keyword, topic_id=topic_id, skip=skip, limit=limit
    )