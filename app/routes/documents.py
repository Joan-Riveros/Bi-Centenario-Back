from typing import List, Optional
import os 
from pathlib import Path 
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form 
from fastapi.responses import FileResponse 
from sqlalchemy.orm import Session
from pathlib import Path 
import logging 
import traceback 
from app import crud, models, schemas
from app.core import dependencies
from app.core.enums import UserRole, RequestStatusEnum
from app.core.config import MEDIA_ROOT

router = APIRouter()


from pathlib import Path
from app.core.config import UPLOAD_DOCUMENTS_DIR
# --- NUEVOS ENDPOINTS DE DESCARGA ---
@router.get("/", response_model=List[schemas.Document], summary="Listar documentos con filtros y búsqueda")
def read_documents(
    db: Session = Depends(dependencies.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    search: Optional[str] = Query(None, alias="q", description="Termino de busqueda en titulo, autor, descripcion o tags"),
    category_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    event_id: Optional[int] = Query(None),
    uploader_id: Optional[int] = Query(None),
    level: Optional[int] = Query(None, description="Filtrar por nivel de documento especifico"),
    current_user: Optional[models.User] = Depends(dependencies.get_current_user_or_none), 
):

    documents = crud.get_documents(
        db=db,
        skip=skip,
        limit=limit,
        current_user=current_user,
        search_query=search,
        category_id=category_id,
        tag_id=tag_id,
        event_id=event_id,
        uploader_id=uploader_id,
        document_level=level
    )
    return documents

@router.get("/{document_id}", response_model=schemas.Document, summary="Obtener un documento por ID")
def read_document(
    *,
    db: Session = Depends(dependencies.get_db),
    document_id: int,
    current_user: Optional[models.User] = Depends(dependencies.get_current_user_or_none),
):
    """
    Obtiene los detalles de un documento específico por su ID
    El acceso esta restringido segun el nivel del documento y el rol del usuario
    """
    db_document = crud.get_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    #Control de acceso
    if db_document.document_level == 1: 
        return db_document
    
    if not current_user: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no permitido")

    if current_user.role == UserRole.ADMINISTRADOR: # Admin ve todo
        return db_document
    
    if current_user.id == db_document.uploader_id: # El propietario ve su documento
        return db_document

    if current_user.role == UserRole.INVESTIGADOR:
        approved_request = crud.get_approved_document_access_request(
            db=db, user_id=current_user.id, document_id=document_id
        )
        if approved_request:
            return db_document
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver este documento")


@router.put("/{document_id}", response_model=schemas.Document, summary="Actualizar un documento (Solo Administradores)")
def update_document_by_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    document_id: int,
    document_in: schemas.DocumentUpdate,
    current_user: models.User = Depends(dependencies.require_admin_user),
):

    db_document = crud.get_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    
    if document_in.category_ids:
        for cat_id in document_in.category_ids:
            if not crud.get_category(db, cat_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria con id {cat_id} no encontrada")
    if document_in.tag_ids:
        for tag_id in document_in.tag_ids:
            if not crud.get_tag(db, tag_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag con id {tag_id} no encontrado")
    if document_in.historical_event_ids:
        for event_id in document_in.historical_event_ids:
            if not crud.get_historical_event(db, event_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evento historico con id {event_id} no encontrado")

    updated_document = crud.update_document(db=db, db_obj=db_document, obj_in=document_in)
    return updated_document


@router.delete("/{document_id}", response_model=schemas.Document, summary="Eliminar un documento (Solo Administradores)")
def delete_document_by_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    document_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user),
):
    db_document = crud.get_document(db=db, document_id=document_id) 
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    
    deleted_document_data = schemas.Document.model_validate(db_document) 

    crud.remove_document(db=db, document_id=document_id) 
    return deleted_document_data 

@router.get(
    "/{document_id}/download",
    response_class=FileResponse, 
    summary="Descargar el archivo principal de un documento"
)
async def download_document_file( 
    *,
    db: Session = Depends(dependencies.get_db),
    document_id: int,
    current_user: Optional[models.User] = Depends(dependencies.get_current_user_or_none),
):

    db_document = crud.get_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    can_access = False
    if db_document.document_level == 1: 
        can_access = True
    elif current_user:
        if current_user.role == UserRole.ADMINISTRADOR:
            can_access = True
        elif current_user.id == db_document.uploader_id:
            can_access = True
        elif current_user.role == UserRole.INVESTIGADOR:
            approved_request = crud.get_approved_document_access_request(
                db=db, user_id=current_user.id, document_id=document_id
            )
            if approved_request:
                can_access = True
    
    if not can_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para descargar este archivo")

    # --- Preparar y enviar el archivo ---
    if not db_document.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El documento no tiene un archivo asociado")

    file_location_on_disk = MEDIA_ROOT / db_document.file_path
    
    if not file_location_on_disk.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado en el servidor")


    file_name_for_download = Path(db_document.file_path).name

    return FileResponse(
        path=str(file_location_on_disk),
        filename=file_name_for_download,
        media_type='application/octet-stream' 
    )


@router.get(
    "/{document_id}/cover/download",
    response_class=FileResponse,
    summary="Descargar la imagen de portada de un documento"
)
async def download_document_cover_image(
    *,
    db: Session = Depends(dependencies.get_db),
    document_id: int,
    current_user: Optional[models.User] = Depends(dependencies.get_current_user_or_none),
):

    db_document = crud.get_document(db=db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    if not db_document.cover_image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El documento no tiene una imagen de portada asociada")

    can_access = False
    if db_document.document_level == 1: 
        can_access = True
    elif current_user:
        if current_user.role == UserRole.ADMINISTRADOR:
            can_access = True
        elif current_user.id == db_document.uploader_id:
            can_access = True
        elif current_user.role == UserRole.INVESTIGADOR:
            approved_request = crud.get_approved_document_access_request(
                db=db, user_id=current_user.id, document_id=document_id
            )
            if approved_request:
                can_access = True
    
    if not can_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para descargar esta imagen de portada.")


    cover_location_on_disk = MEDIA_ROOT / db_document.cover_image_path

    if not cover_location_on_disk.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de portada no encontrado en el servidor")

    cover_name_for_download = Path(db_document.cover_image_path).name
    
    # detectar el medyatype
    # import mimetypes
    # media_type, _ = mimetypes.guess_type(str(cover_location_on_disk))
    # if not media_type: media_type = 'application/octet-stream'

    return FileResponse(
        path=str(cover_location_on_disk),
        filename=cover_name_for_download,
        media_type='application/octet-stream' 
    )

#post document
from app.core.config import ( 
    UPLOAD_DOCUMENTS_DIR,
    UPLOAD_COVERS_DIR,
    MAX_DOCUMENT_SIZE_MB,
    MAX_COVER_SIZE_MB,
    ALLOWED_DOCUMENT_EXTENSIONS,
    ALLOWED_COVER_EXTENSIONS,
    MEDIA_ROOT
)
from app.core.file_utils import save_upload_file 
@router.post(
    "/direct-upload/", 
    response_model=schemas.Document,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo documento con subida directa de archivo (Solo Administradores)"
)
async def create_document_directly_by_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    title: str = Form(...),
    author: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    publisher: Optional[str] = Form(None),
    isbn: Optional[str] = Form(None),
    page_count: Optional[int] = Form(None),
    is_scanned: bool = Form(False),
    edition_details: Optional[str] = Form(None),
    document_level: int = Form(1, ge=1), 
    category_ids: Optional[List[int]] = Form(None),
    tag_ids: Optional[List[int]] = Form(None),
    historical_event_ids: Optional[List[int]] = Form(None),
    # Archivos
    document_file: UploadFile = File(...),
    cover_image_file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(dependencies.require_admin_user) 
):

    # 1. Validar y guardar archivo del documento
    try:
        path_destination_dir = Path(UPLOAD_DOCUMENTS_DIR)
        document_file_path_rel = save_upload_file(
            upload_file=document_file,
            destination_dir=path_destination_dir,
            max_size_mb=MAX_DOCUMENT_SIZE_MB,
            allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
        )
    except HTTPException as e:
        raise e
    except Exception as exc:
        error_message = f"Error completo al guardar el archivo del documento: {traceback.format_exc()}"
        print(error_message) 
        traceback.print_exc() 
        # Opcionalmente, usa logging si lo tienes configurado:
        #logging.error(error_message, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar el archivo del documento")

    # 2. Validar y guardar imagen de portada 
    cover_image_file_path_rel: Optional[str] = None
    if cover_image_file and cover_image_file.filename:
        try:

            path_obj_covers_dir = Path(UPLOAD_COVERS_DIR)
            cover_image_file_path_rel = save_upload_file(
                upload_file=cover_image_file,
                destination_dir=path_obj_covers_dir,
                max_size_mb=MAX_COVER_SIZE_MB,
                allowed_extensions=ALLOWED_COVER_EXTENSIONS,
            )
        except HTTPException as e:
            raise e
        except Exception as exc:
            error_message = f"Error completo al guardar el archivo del documento: {traceback.format_exc()}"
            print(error_message) 
            traceback.print_exc() 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al guardar la imagen de portada")

    # 3. Validar IDs de entidades relacionadas
    if category_ids:
        for cat_id in category_ids:
            if not crud.get_category(db, cat_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria con id {cat_id} no encontrada")
    if tag_ids:
        for tag_id in tag_ids:
            if not crud.get_tag(db, tag_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag con id {tag_id} no encontrado")
    if historical_event_ids:
        for event_id in historical_event_ids:
            if not crud.get_historical_event(db, event_id): 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evento historico con id {event_id} no encontrado")

    # 4. Crear el objeto DocumentCreate a partir de los Form data
    document_in_create = schemas.DocumentCreate(
        title=title,
        author=author,
        short_description=short_description,
        publisher=publisher,
        isbn=isbn,
        page_count=page_count,
        is_scanned=is_scanned,
        edition_details=edition_details,
        document_level=document_level,
        category_ids=category_ids or [],
        tag_ids=tag_ids or [],
        historical_event_ids=historical_event_ids or [],
    )

    # 5. Llamar al CRUD para crear el documento en la base de datos
    created_document = crud.create_document(
        db=db,
        obj_in=document_in_create,
        uploader_id=current_user.id, 
        file_path=document_file_path_rel,
        cover_image_path=cover_image_file_path_rel,
    )
    
    return created_document