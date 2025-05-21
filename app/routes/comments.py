from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import dependencies

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)

@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo comentario o respuesta")
def create_comment(
    *,
    db: Session = Depends(dependencies.get_db),
    comment_in: schemas.CommentCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user) 
):
    """
    Crea un nuevo comentario en un documento o una respuesta a un comentario existente
    """

    if not crud.document.get_document(db, document_id=comment_in.document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id {comment_in.document_id} no encontrado")


    if comment_in.parent_comment_id:
        parent_comment = crud.comment.get_comment(db, comment_id=comment_in.parent_comment_id)
        if not parent_comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comentario padre con id {comment_in.parent_comment_id} no encontrado")
  
        if parent_comment.document_id != comment_in.document_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La respuesta debe pertenecer al mismo documento que el comentario padre")
            
    return crud.comment.create_comment(db=db, obj_in=comment_in, user_id=current_user.id)

@router.get("/document/{document_id}", response_model=List[schemas.Comment], summary="Listar comentarios de un documento")
def read_comments_for_document(
    document_id: int,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 50,

):
    """
    Obtiene los comentarios de nivel superior para un documento especifico
    """
    # Verificar que el documento exista 
    # if not crud.document.get_document(db, document_id=document_id):
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documento con id {document_id} no encontrado.")
        
    return crud.comment.get_comments_for_document(db=db, document_id=document_id, skip=skip, limit=limit)

@router.get("/{comment_id}/replies", response_model=List[schemas.Comment], summary="Listar respuestas de un comentario")
def read_replies_for_comment(
    comment_id: int,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 25
):
    """
    Obtiene las respuestas directas a un comentario especifico.
    """
    if not crud.comment.get_comment(db, comment_id=comment_id):
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comentario padre con id {comment_id} no encontrado.")
    return crud.comment.get_replies_for_comment(db=db, parent_comment_id=comment_id, skip=skip, limit=limit)


@router.put("/{comment_id}", response_model=schemas.Comment, summary="Actualizar un comentario")
def update_comment(
    *,
    db: Session = Depends(dependencies.get_db),
    comment_id: int,
    comment_in: schemas.CommentUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Actualiza el contenido de un comentario existente
    """
    db_comment = crud.comment.get_comment(db, comment_id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
    
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para modificar este comentario")
        
    updated_comment = crud.comment.update_comment(db=db, db_obj=db_comment, obj_in=comment_in)
    if not updated_comment: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron datos válidos para actualizar")
    return updated_comment

@router.delete("/{comment_id}", response_model=schemas.Comment, summary="Eliminar un comentario")
def delete_comment(
    *,
    db: Session = Depends(dependencies.get_db),
    comment_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Elimina un comentario
    """
    db_comment = crud.comment.get_comment(db, comment_id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
    
    if db_comment.user_id != current_user.id and current_user.role != models.UserRole.ADMINISTRADOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este comentario")
        
    deleted_comment = crud.comment.remove_comment(db=db, comment_id=comment_id)
    if not deleted_comment: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error al eliminar el comentario")
    return deleted_comment