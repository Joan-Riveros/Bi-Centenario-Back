from typing import Any, Dict, Optional, Union, List
import os 
from pathlib import Path 

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_ 

from app.models.document import Document
from app.models.category import Category
from app.models.tag import Tag
from app.models.historical_event import HistoricalEvent
from app.models.document_access_request import DocumentAccessRequest 
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.core.enums import UserRole, RequestStatusEnum
from app.core.config import MEDIA_ROOT 
from app.models import User 


def get_document(db: Session, document_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[User],
    search_query: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    event_id: Optional[int] = None,
    uploader_id: Optional[int] = None,
    document_level: Optional[int] = None
) -> List[Document]:
    query = db.query(Document)

    # --- Filtros ---
    if search_query:
        search_terms = f"%{search_query.lower()}%"
        query = query.filter(
            or_(
                Document.title.ilike(search_terms),
                Document.author.ilike(search_terms),
                Document.short_description.ilike(search_terms),
                Document.tags.any(Tag.name.ilike(search_terms)) 
            )
        )
    if category_id:
        query = query.join(Document.categories).filter(Category.id == category_id)
    if tag_id:
        query = query.join(Document.tags).filter(Tag.id == tag_id)
    if event_id:
        query = query.join(Document.historical_events).filter(HistoricalEvent.id == event_id)
    if uploader_id:
        query = query.filter(Document.uploader_id == uploader_id)
    if document_level is not None: 
         query = query.filter(Document.document_level == document_level)

    # --- Control de Acceso ---
    if not current_user or current_user.role == UserRole.VISITANTE:
        # Visitantes y anonimos solo ven documentos publicos
        query = query.filter(Document.document_level == 1)
    elif current_user.role == UserRole.INVESTIGADOR:
        # Investigadores ven:
        # 1. Documentos publicos
        # 2. Sus propios documentos 
        # 3. Documentos restringidos para los que tienen una solicitud aprobada
        
        approved_access_subquery = (
            db.query(DocumentAccessRequest.document_id)
            .filter(
                DocumentAccessRequest.user_id == current_user.id,
                DocumentAccessRequest.status == RequestStatusEnum.APPROVED,
            )
            .subquery()
        )
        
        query = query.filter(
            or_(
                Document.document_level == 1, # Públicos
                Document.uploader_id == current_user.id, # Propios
                Document.id.in_(approved_access_subquery), # Con acceso aprobado
            )
        )

    return query.order_by(Document.upload_date.desc()).offset(skip).limit(limit).all()


def create_document( 
    db: Session,
    *,
    obj_in: DocumentCreate,
    uploader_id: int,
    file_path: str,
    cover_image_path: Optional[str] = None,
) -> Document:
    db_obj_data = obj_in.model_dump(exclude_unset=True, exclude={"category_ids", "tag_ids", "historical_event_ids"})
    
    db_obj = Document(
        **db_obj_data,
        uploader_id=uploader_id,
        file_path=file_path,
        cover_image_path=cover_image_path
    )

    if obj_in.category_ids:
        categories = db.query(Category).filter(Category.id.in_(obj_in.category_ids)).all()
        db_obj.categories = categories 

    if obj_in.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(obj_in.tag_ids)).all()
        db_obj.tags = tags

    if obj_in.historical_event_ids:
        events = db.query(HistoricalEvent).filter(HistoricalEvent.id.in_(obj_in.historical_event_ids)).all()
        db_obj.historical_events = events
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_document( 
    db: Session,
    *,
    db_obj: Document,
    obj_in: Union[DocumentUpdate, Dict[str, Any]],
) -> Document:
    if isinstance(obj_in, dict):
        update_data = obj_in
        category_ids = update_data.pop("category_ids", Ellipsis) 
        tag_ids = update_data.pop("tag_ids", Ellipsis)
        historical_event_ids = update_data.pop("historical_event_ids", Ellipsis)
    else:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"category_ids", "tag_ids", "historical_event_ids"})
        category_ids = obj_in.category_ids if hasattr(obj_in, 'category_ids') else Ellipsis
        tag_ids = obj_in.tag_ids if hasattr(obj_in, 'tag_ids') else Ellipsis
        historical_event_ids = obj_in.historical_event_ids if hasattr(obj_in, 'historical_event_ids') else Ellipsis

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    if category_ids is not Ellipsis: 
        if category_ids:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            db_obj.categories = categories
        else:
            db_obj.categories = []
    
    if tag_ids is not Ellipsis:
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_obj.tags = tags
        else:
            db_obj.tags = []

    if historical_event_ids is not Ellipsis:
        if historical_event_ids:
            events = db.query(HistoricalEvent).filter(HistoricalEvent.id.in_(historical_event_ids)).all()
            db_obj.historical_events = events
        else:
            db_obj.historical_events = []

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_document(db: Session, *, document_id: int) -> Optional[Document]:
    db_obj = db.query(Document).get(document_id)
    if db_obj:
        if db_obj.file_path:
            file_on_disk = MEDIA_ROOT / db_obj.file_path
            if file_on_disk.exists():
                try:
                    os.remove(file_on_disk)
                except OSError: 
                    pass 
        if db_obj.cover_image_path:
            cover_on_disk = MEDIA_ROOT / db_obj.cover_image_path
            if cover_on_disk.exists():
                try:
                    os.remove(cover_on_disk)
                except OSError:
                    pass
        
        db.delete(db_obj)
        db.commit()
    return db_obj