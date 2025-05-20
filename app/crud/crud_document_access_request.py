from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.document_access_request import DocumentAccessRequest
from app.schemas.document_access_request import DocumentAccessRequestCreate, DocumentAccessRequestUpdate
from app.core.enums import RequestStatusEnum

def get_document_access_request(db: Session, request_id: int) -> Optional[DocumentAccessRequest]:
    return db.query(DocumentAccessRequest).filter(DocumentAccessRequest.id == request_id).first()

def get_document_access_requests_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[DocumentAccessRequest]:
    return (
        db.query(DocumentAccessRequest)
        .filter(DocumentAccessRequest.user_id == user_id)
        .order_by(DocumentAccessRequest.request_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_document_access_requests_for_document(
    db: Session, document_id: int, skip: int = 0, limit: int = 100
) -> List[DocumentAccessRequest]:
    return (
        db.query(DocumentAccessRequest)
        .filter(DocumentAccessRequest.document_id == document_id)
        .order_by(DocumentAccessRequest.request_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
def get_pending_document_access_request(
    db: Session, *, user_id: int, document_id: int
) -> Optional[DocumentAccessRequest]:
    """Verifica si ya existe una solicitud PENDIENTE del usuario para ese documento."""
    return (
        db.query(DocumentAccessRequest)
        .filter(
            DocumentAccessRequest.user_id == user_id,
            DocumentAccessRequest.document_id == document_id,
            DocumentAccessRequest.status == RequestStatusEnum.PENDING,
        )
        .first()
    )

def get_approved_document_access_request(
    db: Session, *, user_id: int, document_id: int
) -> Optional[DocumentAccessRequest]:
    """Verifica si existe una solicitud APROBADA del usuario para ese documento."""
    return (
        db.query(DocumentAccessRequest)
        .filter(
            DocumentAccessRequest.user_id == user_id,
            DocumentAccessRequest.document_id == document_id,
            DocumentAccessRequest.status == RequestStatusEnum.APPROVED,
        )
        .first()
    )

def get_all_document_access_requests(
    db: Session, skip: int = 0, limit: int = 100, status: Optional[RequestStatusEnum] = None
) -> List[DocumentAccessRequest]:
    query = db.query(DocumentAccessRequest)
    if status:
        query = query.filter(DocumentAccessRequest.status == status)
    return query.order_by(DocumentAccessRequest.request_date.desc()).offset(skip).limit(limit).all()

def create_document_access_request(
    db: Session, *, obj_in: DocumentAccessRequestCreate, user_id: int
) -> DocumentAccessRequest:
    db_obj = DocumentAccessRequest(
        user_id=user_id,
        document_id=obj_in.document_id,
        reason=obj_in.reason
        # request_date y status tienen defaults
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_document_access_request(
    db: Session,
    *,
    db_obj: DocumentAccessRequest,
    obj_in: Union[DocumentAccessRequestUpdate, Dict[str, Any]]
) -> DocumentAccessRequest:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_document_access_request(db: Session, *, request_id: int) -> Optional[DocumentAccessRequest]:
    db_obj = db.query(DocumentAccessRequest).get(request_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj