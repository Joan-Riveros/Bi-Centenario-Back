from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.upload_privilege_request import UploadPrivilegeRequest
from app.schemas.upload_privilege_request import UploadPrivilegeRequestCreate, UploadPrivilegeRequestUpdate
from app.core.enums import RequestStatusEnum

def get_upload_privilege_request(db: Session, request_id: int) -> Optional[UploadPrivilegeRequest]:
    return db.query(UploadPrivilegeRequest).filter(UploadPrivilegeRequest.id == request_id).first()

def get_upload_privilege_requests_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[UploadPrivilegeRequest]:
    return (
        db.query(UploadPrivilegeRequest)
        .filter(UploadPrivilegeRequest.user_id == user_id)
        .order_by(UploadPrivilegeRequest.request_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_pending_upload_request_by_user(db: Session, user_id: int) -> Optional[UploadPrivilegeRequest]:
    """Verifica si ya existe una solicitud PENDIENTE para este usuario."""
    return (
        db.query(UploadPrivilegeRequest)
        .filter(UploadPrivilegeRequest.user_id == user_id, UploadPrivilegeRequest.status == RequestStatusEnum.PENDING)
        .first()
    )

def get_all_upload_privilege_requests(
    db: Session, skip: int = 0, limit: int = 100, status: Optional[RequestStatusEnum] = None
) -> List[UploadPrivilegeRequest]:
    query = db.query(UploadPrivilegeRequest)
    if status:
        query = query.filter(UploadPrivilegeRequest.status == status)
    return query.order_by(UploadPrivilegeRequest.request_date.desc()).offset(skip).limit(limit).all()

def create_upload_privilege_request(
    db: Session, *, obj_in: UploadPrivilegeRequestCreate, user_id: int
) -> UploadPrivilegeRequest:
    db_obj = UploadPrivilegeRequest(
        user_id=user_id,
        title=obj_in.title,
        author=obj_in.author,
        short_description=obj_in.short_description,
        publisher=obj_in.publisher,
        isbn=obj_in.isbn,
        page_count=obj_in.page_count,
        is_scanned=obj_in.is_scanned if obj_in.is_scanned is not None else False,
        edition_details=obj_in.edition_details,
        proposed_document_level=obj_in.proposed_document_level,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_upload_privilege_request(
    db: Session,
    *,
    db_obj: UploadPrivilegeRequest,
    obj_in: Union[UploadPrivilegeRequestUpdate, Dict[str, Any]]
) -> UploadPrivilegeRequest:
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

def remove_upload_privilege_request(db: Session, *, request_id: int) -> Optional[UploadPrivilegeRequest]:
    db_obj = db.query(UploadPrivilegeRequest).get(request_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj