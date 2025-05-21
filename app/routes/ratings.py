from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import dependencies

router = APIRouter(
    prefix="/ratings",
    tags=["Ratings"],
)

@router.post("/", response_model=schemas.Rating, status_code=status.HTTP_201_CREATED, summary="Crear o actualizar una calificacion para un documento")
def create_or_update_rating(
    *,
    db: Session = Depends(dependencies.get_db),
    rating_in: schemas.RatingCreate, 
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Permite a un usuario autenticado calificar un documento 
    """
    if not crud.document.get_document(db, document_id=rating_in.document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id {rating_in.document_id} no encontrado")

    existing_rating = crud.rating.get_rating_by_user_and_document(
        db, user_id=current_user.id, document_id=rating_in.document_id
    )

    if existing_rating:

        rating_update_schema = schemas.RatingUpdate(score=rating_in.score)
        return crud.rating.update_rating(db=db, db_obj=existing_rating, obj_in=rating_update_schema)
    else:

        new_rating = crud.rating.create_rating(db=db, obj_in=rating_in, user_id=current_user.id)
        if not new_rating: 
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se pudo crear la calificacion, es posible que ya exista (conflicto)")
        return new_rating


@router.get("/document/{document_id}", response_model=List[schemas.Rating], summary="Listar calificaciones de un documento")
def read_ratings_for_document(
    document_id: int,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100

):

    # Opcional: verificar si el documento existe
    # if not crud.document.get_document(db, document_id=document_id):
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id {document_id} no encontrado.")
        
    return crud.rating.get_ratings_for_document(db=db, document_id=document_id, skip=skip, limit=limit)

@router.get("/document/{document_id}/average", response_model=Dict[str, Optional[float]], summary="Obtener la calificacion promedio de un documento")
def get_average_rating_for_document(
    document_id: int,
    db: Session = Depends(dependencies.get_db)
):

    ratings = crud.rating.get_ratings_for_document(db=db, document_id=document_id, limit=0) 
    if not ratings:
        return {"average_score": None, "count": 0}
    
    average_score = sum(r.score for r in ratings) / len(ratings)
    return {"average_score": round(average_score, 2), "count": len(ratings)}


@router.get("/document/{document_id}/my-rating", response_model=Optional[schemas.Rating], summary="Obtener mi calificacion para un documento")
def read_my_rating_for_document(
    document_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Obtiene la calificacion que el usuario autenticado ha dado a un documento especifico
    """
    return crud.rating.get_rating_by_user_and_document(db=db, user_id=current_user.id, document_id=document_id)

@router.delete("/document/{document_id}/my-rating", response_model=schemas.Rating, summary="Eliminar mi calificacion para un documento")
def delete_my_rating_for_document(
    document_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Elimina la calificacion que el usuario autenticado ha dado a un documento especifico
    """
    rating_to_delete = crud.rating.get_rating_by_user_and_document(
        db, user_id=current_user.id, document_id=document_id
    )
    if not rating_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No has calificado este documento")
    

    deleted_rating = crud.rating.remove_rating(db=db, rating_id=rating_to_delete.id)
    if not deleted_rating:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error al eliminar la calificacipn")
    return deleted_rating
