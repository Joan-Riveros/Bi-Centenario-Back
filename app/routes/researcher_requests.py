from typing import List, Optional 

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import dependencies 

router = APIRouter(
    tags=["Researcher Requests"], 
)


@router.post(
    "/requests/upload-privilege/", 
    response_model=schemas.UploadPrivilegeRequest, 
    status_code=status.HTTP_201_CREATED, 
    summary="Proponer un nuevo documento para subida (Investigador)"
)
def create_document_proposal_by_researcher(
    *,
    db: Session = Depends(dependencies.get_db),
    proposal_in: schemas.UploadPrivilegeRequestCreate, 
    current_user: models.User = Depends(dependencies.require_researcher_user) 
):
    """
    Permite a un investigador proponer la metadata y el archivo 
    """

    existing_pending_request = crud.upload_privilege_request.get_pending_upload_request_by_user_and_title(
        db, user_id=current_user.id, title=proposal_in.title
    )
    if existing_pending_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una propuesta pendiente con este titulo",
        )


    if proposal_in.category_ids:
        for cat_id in proposal_in.category_ids:
            if not crud.category.get_category(db, category_id=cat_id): 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria con id {cat_id} no encontrada")
    
    if proposal_in.tag_ids:
        for tag_id in proposal_in.tag_ids:
            if not crud.tag.get_tag(db, tag_id=tag_id): 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag con id {tag_id} no encontrado")
    
    if proposal_in.historical_event_ids:
        for event_id in proposal_in.historical_event_ids:
            if not crud.historical_event.get_historical_event(db, historical_event_id=event_id): 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evento historico con id {event_id} no encontrado")


    return crud.upload_privilege_request.create_upload_privilege_request(
        db=db, obj_in=proposal_in, user_id=current_user.id
    )

@router.get(
    "/requests/upload-privilege/mine", 
    response_model=List[schemas.UploadPrivilegeRequest], 
    summary="Listar mis propuestas de subida de documentos (Investigador)"
)
def read_my_upload_privilege_requests(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.require_researcher_user) 
):
    """
    Obtiene la lista de todas las propuestas de subida de documentos
    """

    return crud.upload_privilege_request.get_upload_privilege_requests_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post(
    "/requests/document-access/", 
    response_model=schemas.DocumentAccessRequest, 
    status_code=status.HTTP_201_CREATED, 
    summary="Crear una nueva solicitud de acceso a un documento (Investigador)"
)
def create_document_access_request_by_researcher(
    *,
    db: Session = Depends(dependencies.get_db),
    request_in: schemas.DocumentAccessRequestCreate, 
    current_user: models.User = Depends(dependencies.require_researcher_user) 
):
    """
    Permite a un investigador crear una solicitud para acceder a un documento restringido
    """

    document = crud.document.get_document(db=db, document_id=request_in.document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")


    if document.document_level == 1: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este documento es público y no requiere solicitud de acceso.",
        )
    

    if document.uploader_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Eres el propietario de este documento y ya tienes acceso",
        )


    existing_pending_request = crud.document_access_request.get_pending_document_access_request(
        db=db, user_id=current_user.id, document_id=request_in.document_id
    )
    if existing_pending_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una solicitud de acceso pendiente para este documento.",
        )


    existing_approved_request = crud.document_access_request.get_approved_document_access_request(
        db=db, user_id=current_user.id, document_id=request_in.document_id
    )
    if existing_approved_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes acceso aprobado para este documento.",
        )


    return crud.document_access_request.create_document_access_request(
        db=db, obj_in=request_in, user_id=current_user.id
    )

@router.get(
    "/requests/document-access/mine", 
    response_model=List[schemas.DocumentAccessRequest], 
    summary="Listar mis solicitudes de acceso a documentos (Investigador)"
)
def read_my_document_access_requests(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.require_researcher_user) 
):
    """
    Obtiene la lista de todas las solicitudes de acceso a documentos
    """

    return crud.document_access_request.get_document_access_requests_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )