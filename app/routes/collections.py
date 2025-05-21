from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import dependencies

router = APIRouter(
    prefix="/collections",
    tags=["Collections"],

)

@router.post("/", response_model=schemas.Collection, status_code=status.HTTP_201_CREATED, summary="Crear una nueva coleccipn")
def create_collection(
    *,
    db: Session = Depends(dependencies.get_db),
    collection_in: schemas.CollectionCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user) 
):

    # Verificar si ya existe una colección con el mismo nombre para este usuario
    # existing_collection = crud.collection.get_collection_by_name_and_user(db, name=collection_in.name, user_id=current_user.id)
    # if existing_collection:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Ya tienes una colección con este nombre.",
    #     )


    if collection_in.document_ids:
        for doc_id in collection_in.document_ids:
            if not crud.document.get_document(db, document_id=doc_id): 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id {doc_id} no encontrado")

    return crud.collection.create_collection(db=db, obj_in=collection_in, user_id=current_user.id)

@router.get("/mine", response_model=List[schemas.Collection], summary="Listar mis colecciones")
def read_my_collections(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):

    return crud.collection.get_collections_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{collection_id}", response_model=schemas.Collection, summary="Obtener una coleccion por ID")
def read_collection(
    *,
    db: Session = Depends(dependencies.get_db),
    collection_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Obtiene los detalles de una coleccio
    """
    db_collection = crud.collection.get_collection(db, collection_id=collection_id)
    if not db_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colección no encontrada")
    
    if db_collection.user_id != current_user.id and current_user.role != models.UserRole.ADMINISTRADOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver esta coleccion")
    
    return db_collection

@router.put("/{collection_id}", response_model=schemas.Collection, summary="Actualizar una coleccion")
def update_collection(
    *,
    db: Session = Depends(dependencies.get_db),
    collection_id: int,
    collection_in: schemas.CollectionUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Actualiza los detalles de una coleccion 
    """
    db_collection = crud.collection.get_collection(db, collection_id=collection_id)
    if not db_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coleccion no encontrada")
    
    if db_collection.user_id != current_user.id:

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar esta coleccion")


    if collection_in.document_ids is not None: 
        for doc_id in collection_in.document_ids:
            if not crud.document.get_document(db, document_id=doc_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id {doc_id} no encontrado")

    return crud.collection.update_collection(db=db, db_obj=db_collection, obj_in=collection_in)

@router.delete("/{collection_id}", response_model=schemas.Collection, summary="Eliminar una coleccion")
def delete_collection(
    *,
    db: Session = Depends(dependencies.get_db),
    collection_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Elimina una coleccio
    """
    db_collection = crud.collection.get_collection(db, collection_id=collection_id)
    if not db_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coleccion no encontrada")
    
    if db_collection.user_id != current_user.id and current_user.role != models.UserRole.ADMINISTRADOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar esta coleccion")
    
    deleted_collection = crud.collection.remove_collection(db=db, collection_id=collection_id)
    if not deleted_collection: 
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error al eliminar la coleccion")
    return deleted_collection


@router.post("/{collection_id}/documents/{document_id}", response_model=schemas.Collection, summary="Añadir un documento a una coleccion")
def add_document_to_collection(
    *,
    db: Session = Depends(dependencies.get_db),
    collection_id: int,
    document_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Añade un documento existente a una coleccion
    """
    db_collection = crud.collection.get_collection(db, collection_id=collection_id)
    if not db_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coleccion no encontrada")
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar esta coleccion")

    db_document = crud.document.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")

    return crud.collection.add_document_to_collection(db=db, db_obj_collection=db_collection, db_obj_document=db_document)


@router.delete("/{collection_id}/documents/{document_id}", response_model=schemas.Collection, summary="Eliminar un documento de una coleccion")
def remove_document_from_collection(
    *,
    db: Session = Depends(dependencies.get_db),
    collection_id: int,
    document_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Elimina un documento de una coleccion
    """
    db_collection = crud.collection.get_collection(db, collection_id=collection_id)
    if not db_collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coleccion no encontrada")
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar esta coleccion")

    db_document = crud.document.get_document(db, document_id=document_id)
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
        
    return crud.collection.remove_document_from_collection(db=db, db_obj_collection=db_collection, db_obj_document=db_document)