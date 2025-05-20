from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import logging
import traceback
from app import crud, models, schemas 
from app.core import dependencies
from app.core.config import (
    UPLOAD_DOCUMENTS_DIR,
    UPLOAD_COVERS_DIR,
    MAX_DOCUMENT_SIZE_MB,
    MAX_COVER_SIZE_MB,
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_COVER_EXTENSIONS,
)
from app.core.file_utils import save_upload_file
from app.core.enums import RequestStatusEnum, UserRole

router = APIRouter()

@router.post(
    "/{proposal_id}/upload-files",
    response_model=schemas.Document,
    status_code=status.HTTP_201_CREATED,
    summary="Subir archivos para una propuesta de documento aprobada y crear el documento"
)
async def upload_files_for_approved_proposal(
    *,
    db: Session = Depends(dependencies.get_db),
    proposal_id: int,
    document_file: UploadFile = File(...),
    cover_image_file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(dependencies.get_current_active_user) 
):

    db_proposal = crud.get_upload_privilege_request(db=db, request_id=proposal_id)

    if not db_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propuesta de documento no encontrada"
        )

    if db_proposal.status != RequestStatusEnum.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La propuesta no esta aprobada. Estado actual: {db_proposal.status}",
        )

    if not (current_user.id == db_proposal.user_id or current_user.role == UserRole.ADMINISTRADOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para subir archivos para esta propuesta",
        )

    try:
        document_file_path_rel = save_upload_file(
            upload_file=document_file,
            destination_dir=UPLOAD_DOCUMENTS_DIR,
            max_size_mb=MAX_DOCUMENT_SIZE_MB,
            allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
        )
    except HTTPException as e:
        raise e
    except Exception: 
        error_message = f"Error completo al guardar el archivo del documento: {traceback.format_exc()}"
        print(error_message) 
        traceback.print_exc() 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar el archivo del documento")
        
    cover_image_file_path_rel: Optional[str] = None
    if cover_image_file and cover_image_file.filename: 
        try:
            cover_image_file_path_rel = save_upload_file(
                upload_file=cover_image_file,
                destination_dir=UPLOAD_COVERS_DIR,
                max_size_mb=MAX_COVER_SIZE_MB,
                allowed_extensions=ALLOWED_COVER_EXTENSIONS,
            )
        except HTTPException as e:
            raise e
        except Exception:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar la imagen de portada.")

    document_metadata_from_proposal = schemas.DocumentBase(
        title=db_proposal.title,
        author=db_proposal.author,
        short_description=db_proposal.short_description,
        publisher=db_proposal.publisher,
        isbn=db_proposal.isbn,
        page_count=db_proposal.page_count,
        is_scanned=db_proposal.is_scanned if db_proposal.is_scanned is not None else False,
        edition_details=db_proposal.edition_details,
        document_level=db_proposal.proposed_document_level,
    )
    

    document_in_create = schemas.DocumentCreate(
        **document_metadata_from_proposal.model_dump(),
        # category_ids=[], # Deja
        # tag_ids=[],
        # historical_event_ids=[],
    )

    created_document = crud.create_document(
        db=db,
        obj_in=document_in_create,
        uploader_id=db_proposal.user_id, 
        file_path=document_file_path_rel,
        cover_image_path=cover_image_file_path_rel,
    )

    crud.update_upload_privilege_request(
        db=db,
        db_obj=db_proposal,
        obj_in=schemas.UploadPrivilegeRequestUpdate(status=RequestStatusEnum.COMPLETED, admin_notes=db_proposal.admin_notes or "Archivo(s) subido(s) y documento creado")
    )

    return created_document