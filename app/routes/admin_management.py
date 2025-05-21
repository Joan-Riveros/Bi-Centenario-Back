from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import dependencies 
from app.core.enums import RequestStatusEnum 

router = APIRouter()
# --- Gestión de epocas ---
@router.post("/epocas/", response_model=schemas.Epoca, status_code=status.HTTP_201_CREATED, summary="Crear nueva epoca")
def create_epoca(
    *,
    db: Session = Depends(dependencies.get_db),
    epoca_in: schemas.EpocaCreate,
    current_user: models.User = Depends(dependencies.require_admin_user) 
):

    return crud.create_epoca(db=db, obj_in=epoca_in)

@router.get("/epocas/", response_model=List[schemas.Epoca], summary="Listar epocas")
def read_epocas(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.get_epocas(db=db, skip=skip, limit=limit)

@router.get("/epocas/{epoca_id}", response_model=schemas.Epoca, summary="Obtener epoca por ID")
def read_epoca(
    *,
    db: Session = Depends(dependencies.get_db),
    epoca_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_epoca = crud.get_epoca(db=db, epoca_id=epoca_id)
    if not db_epoca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Epoca no encontrada")
    return db_epoca

@router.put("/epocas/{epoca_id}", response_model=schemas.Epoca, summary="Actualizar epoca")
def update_epoca(
    *,
    db: Session = Depends(dependencies.get_db),
    epoca_id: int,
    epoca_in: schemas.EpocaUpdate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_epoca = crud.get_epoca(db=db, epoca_id=epoca_id)
    if not db_epoca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Epoca no encontrada")
    return crud.update_epoca(db=db, db_obj=db_epoca, obj_in=epoca_in)

@router.delete("/epocas/{epoca_id}", response_model=schemas.Epoca, summary="Eliminar epoca")
def delete_epoca(
    *,
    db: Session = Depends(dependencies.get_db),
    epoca_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_epoca = crud.get_epoca(db=db, epoca_id=epoca_id)
    if not db_epoca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Epoca no encontrada")

    return crud.remove_epoca(db=db, epoca_id=epoca_id)

# --- Gestion de Regiones  ---
@router.post("/regiones/", response_model=schemas.Region, status_code=status.HTTP_201_CREATED, summary="Crear nueva Region")
def create_region(
    *,
    db: Session = Depends(dependencies.get_db),
    region_in: schemas.RegionCreate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.create_region(db=db, obj_in=region_in)

@router.get("/regiones/", response_model=List[schemas.Region], summary="Listar Regiones")
def read_regiones(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.get_regiones(db=db, skip=skip, limit=limit)

@router.get("/regiones/{region_id}", response_model=schemas.Region, summary="Obtener Region por ID")
def read_region(
    *,
    db: Session = Depends(dependencies.get_db),
    region_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_region = crud.get_region(db=db, region_id=region_id)
    if not db_region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region no encontrada")
    return db_region

@router.put("/regiones/{region_id}", response_model=schemas.Region, summary="Actualizar Region")
def update_region(
    *,
    db: Session = Depends(dependencies.get_db),
    region_id: int,
    region_in: schemas.RegionUpdate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_region = crud.get_region(db=db, region_id=region_id)
    if not db_region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Region no encontrada")
    return crud.update_region(db=db, db_obj=db_region, obj_in=region_in)

@router.delete("/regiones/{region_id}", response_model=schemas.Region, summary="Eliminar Region")
def delete_region(
    *,
    db: Session = Depends(dependencies.get_db),
    region_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_region = crud.get_region(db=db, region_id=region_id)
    if not db_region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Región no encontrada")
    return crud.remove_region(db=db, region_id=region_id)


# --- Gestión de Categorias ---
@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED, summary="Crear nueva Categoroa")
def create_category(
    *,
    db: Session = Depends(dependencies.get_db),
    category_in: schemas.CategoryCreate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_category = crud.get_category_by_name(db, name=category_in.name)
    if db_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria con este nombre ya existe")
    return crud.create_category(db=db, obj_in=category_in)

@router.get("/categories/", response_model=List[schemas.Category], summary="Listar Categorias")
def read_categories(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.get_categories(db=db, skip=skip, limit=limit)

@router.get("/categories/{category_id}", response_model=schemas.Category, summary="Obtener Categoria por ID")
def read_category(
    *,
    db: Session = Depends(dependencies.get_db),
    category_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_category = crud.get_category(db=db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.Category, summary="Actualizar Categoria")
def update_category(
    *,
    db: Session = Depends(dependencies.get_db),
    category_id: int,
    category_in: schemas.CategoryUpdate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_category = crud.get_category(db=db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    if category_in.name:
        existing_category = crud.get_category_by_name(db, name=category_in.name)
        if existing_category and existing_category.id != category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria con este nombre ya existe")
    return crud.update_category(db=db, db_obj=db_category, obj_in=category_in)

@router.delete("/categories/{category_id}", response_model=schemas.Category, summary="Eliminar Categoria")
def delete_category(
    *,
    db: Session = Depends(dependencies.get_db),
    category_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_category = crud.get_category(db=db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    return crud.remove_category(db=db, category_id=category_id)

# --- Gestión de Tags ---
@router.post("/tags/", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED, summary="Crear nuevo Tag")
def create_tag(
    *,
    db: Session = Depends(dependencies.get_db),
    tag_in: schemas.TagCreate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_tag = crud.get_tag_by_name(db, name=tag_in.name)
    if db_tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag con este nombre ya existe")
    return crud.create_tag(db=db, obj_in=tag_in)

@router.get("/tags/", response_model=List[schemas.Tag], summary="Listar Tags")
def read_tags(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.get_tags(db=db, skip=skip, limit=limit)

@router.get("/tags/{tag_id}", response_model=schemas.Tag, summary="Obtener Tag por ID")
def read_tag(
    *,
    db: Session = Depends(dependencies.get_db),
    tag_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_tag = crud.get_tag(db=db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")
    return db_tag

@router.put("/tags/{tag_id}", response_model=schemas.Tag, summary="Actualizar Tag")
def update_tag(
    *,
    db: Session = Depends(dependencies.get_db),
    tag_id: int,
    tag_in: schemas.TagUpdate,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_tag = crud.get_tag(db=db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")
    if tag_in.name:
        existing_tag = crud.get_tag_by_name(db, name=tag_in.name)
        if existing_tag and existing_tag.id != tag_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag con este nombre ya existe")
    return crud.update_tag(db=db, db_obj=db_tag, obj_in=tag_in)

@router.delete("/tags/{tag_id}", response_model=schemas.Tag, summary="Eliminar Tag")
def delete_tag(
    *,
    db: Session = Depends(dependencies.get_db),
    tag_id: int,
    current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_tag = crud.get_tag(db=db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado")
    return crud.remove_tag(db=db, tag_id=tag_id)


# --- Gestion de Eventos Históricos ---
@router.post("/historical-events/", response_model=schemas.HistoricalEvent, status_code=status.HTTP_201_CREATED, summary="Crear nuevo Evento Histórico (Admin)")
def create_historical_event_admin( 
    *,
    db: Session = Depends(dependencies.get_db),
    event_in: schemas.HistoricalEventCreate,
    
):
    
    if event_in.epoca_id and not crud.epoca.get_epoca(db, epoca_id=event_in.epoca_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Epoca con id {event_in.epoca_id} no encontrada")
    
    if event_in.region_ids:
        for region_id_val in event_in.region_ids:
            if not crud.region.get_region(db, region_id=region_id_val):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Region con id {region_id_val} no encontrada")
    

    return crud.historical_event.create_historical_event(db=db, obj_in=event_in)

@router.get("/historical-events/", response_model=List[schemas.HistoricalEvent], summary="Listar Eventos Historicos (Admin)")
def read_historical_events_admin(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,

):
    return crud.historical_event.get_historical_events(db=db, skip=skip, limit=limit)

@router.get("/historical-events/{event_id}", response_model=schemas.HistoricalEvent, summary="Obtener Evento Historico por ID (Admin)")
def read_historical_event_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,

):
    db_event = crud.historical_event.get_historical_event(db=db, historical_event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento Historico no encontrado")
    return db_event

@router.put("/historical-events/{event_id}", response_model=schemas.HistoricalEvent, summary="Actualizar Evento Historico (Admin)")
def update_historical_event_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,
    event_in: schemas.HistoricalEventUpdate, 
):
    db_event = crud.historical_event.get_historical_event(db=db, historical_event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento Historico no encontrado")
    

    if event_in.epoca_id is not None and not crud.epoca.get_epoca(db, epoca_id=event_in.epoca_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Epoca con id {event_in.epoca_id} no encontrada")
    

    if event_in.region_ids is not None: 
        for region_id_val in event_in.region_ids:
            if not crud.region.get_region(db, region_id=region_id_val):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Región con id {region_id_val} no encontrada")
    
    return crud.historical_event.update_historical_event(db=db, db_obj=db_event, obj_in=event_in)

@router.delete("/historical-events/{event_id}", response_model=schemas.HistoricalEvent, summary="Eliminar Evento Historico (Admin)")
def delete_historical_event_admin(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,

):
    db_event = crud.historical_event.get_historical_event(db=db, historical_event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento Historico no encontrado")
    

    removed_event = crud.historical_event.remove_historical_event(db=db, historical_event_id=event_id)
    if not removed_event: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento Historico no encontrado durante la eliminación")
    return removed_event


# --- Gestion de Solicitudes de Propuesta de Documento  ---
@router.get("/upload-privilege-requests/", response_model=List[schemas.UploadPrivilegeRequest], summary="Listar todas las propuestas de subida de documentos (Admin)")
def read_all_upload_privilege_requests_admin(
    status_filter: Optional[RequestStatusEnum] = Query(None, alias="status"), 
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.upload_privilege_request.get_all_upload_privilege_requests(db=db, skip=skip, limit=limit, status=status_filter)

@router.get("/upload-privilege-requests/{request_id}", response_model=schemas.UploadPrivilegeRequest, summary="Obtener una propuesta de subida por ID (Admin)")
def read_single_upload_privilege_request_admin(
    request_id: int,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_request = crud.upload_privilege_request.get_upload_privilege_request(db=db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propuesta de subida no encontrada")
    return db_request

@router.put("/upload-privilege-requests/{request_id}/status", response_model=schemas.UploadPrivilegeRequest, summary="Actualizar estado de una propuesta de documento (Admin)")
def update_upload_request_status_admin( 
    request_id: int,
    request_update: schemas.UploadPrivilegeRequestUpdate, 
    db: Session = Depends(dependencies.get_db),
    # current_admin_user: models.User = Depends(dependencies.require_admin_user)
):
    db_request = crud.upload_privilege_request.get_upload_privilege_request(db=db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propuesta de documento no encontrada")
    

    return crud.upload_privilege_request.update_upload_privilege_request_status( 
        db=db, db_obj=db_request, status=request_update.status, admin_notes=request_update.admin_notes
    )


# --- Gestion de Solicitudes de Acceso a Documentos (Admin) ---
@router.get("/document-access-requests/", response_model=List[schemas.DocumentAccessRequest], summary="Listar todas las solicitudes de acceso a documentos (Admin)")
def read_all_document_access_requests_admin(
    status_filter: Optional[RequestStatusEnum] = Query(None, alias="status"),
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: models.User = Depends(dependencies.require_admin_user)
):
    return crud.document_access_request.get_all_document_access_requests(db=db, skip=skip, limit=limit, status=status_filter)

@router.get("/document-access-requests/{request_id}", response_model=schemas.DocumentAccessRequest, summary="Obtener una solicitud de acceso por ID (Admin)")
def read_single_document_access_request_admin(
    request_id: int,
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_request = crud.document_access_request.get_document_access_request(db=db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de acceso no encontrada")
    return db_request

@router.put("/document-access-requests/{request_id}/status", response_model=schemas.DocumentAccessRequest, summary="Actualizar estado de solicitud de acceso (Admin)")
def update_document_access_request_status_admin( 
    request_id: int,
    request_update: schemas.DocumentAccessRequestUpdate, 
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user)
):
    db_request = crud.document_access_request.get_document_access_request(db=db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de acceso no encontrada")


    return crud.document_access_request.update_document_access_request(
        db=db, db_obj=db_request, obj_in=request_update
    )


# --- Gestion de Nivel de Documento (Admin) ---
@router.patch("/documents/{document_id}/level", response_model=schemas.Document, summary="Actualizar el nivel de acceso de un documento (Admin)")
def update_document_access_level_admin( 
    document_id: int,
    level_update: schemas.DocumentLevelUpdate, 
    db: Session = Depends(dependencies.get_db),
    # current_user: models.User = Depends(dependencies.require_admin_user), # Covered by router dependency
):
    db_document = crud.document.get_document(db=db, document_id=document_id) 
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    
    updated_document = crud.document.update_document(
        db=db, db_obj=db_document, obj_in={"document_level": level_update.document_level}
    )
    return updated_document
