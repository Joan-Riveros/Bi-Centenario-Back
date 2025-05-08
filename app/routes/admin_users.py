
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List


from app.core.dependencies import get_db, require_admin_user
from app.models.user import User 
from app.schemas.user import UserOut, AdminUserCreate, AdminUserUpdate
from app.crud import crud_user 

router = APIRouter()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_as_admin(
    user_in: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin_user) # Protege la ruta
):
    """
    Crear un nuevo usuario como administrador.
    """
    existing_user = crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un usuario con este email ya existe en el sistema.",
        )
    user = crud_user.create_user_by_admin(db=db, user_in=user_in)
    return user


@router.get("/", response_model=List[UserOut])
def read_users_as_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin_user) # Protege la ruta
):
    """
    Obtener una lista de usuarios. (Acceso de Administrador)
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserOut)
def read_user_as_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin_user) # Protege la ruta
):
    """
    Obtener un usuario específico por ID. (Acceso de Administrador)
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return db_user


@router.put("/{user_id}", response_model=UserOut)
def update_user_as_admin(
    user_id: int,
    user_in: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin_user) # Protege la ruta
):
    """
    Actualizar un usuario. (Acceso de Administrador)
    """
    db_user_to_update = crud_user.get_user(db, user_id=user_id)
    if not db_user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Validar que el email, si se cambia, no E ya en uso por otro usuario
    if user_in.email and user_in.email != db_user_to_update.email:
        existing_user_with_new_email = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_with_new_email and existing_user_with_new_email.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nuevo email ya está registrado por otro usuario.",
            )
    

    updated_user = crud_user.update_user_by_admin(db=db, db_user_to_update=db_user_to_update, user_in=user_in)
    return updated_user


@router.delete("/{user_id}", response_model=UserOut) 
def delete_user_as_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin_user) # Protege la ruta
):
    """
    Eliminar un usuario. (Acceso de Administrador)
    """
    if user_id == current_admin.id: # Evita QUE UN ADMIN SE AUTOELIMINE
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los administradores no pueden eliminar su propia cuenta a través de este endpoint.",
        )
        
    db_user_to_delete = crud_user.get_user(db, user_id=user_id)
    if not db_user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    

 
    deleted_user_obj = crud_user.delete_user_by_admin(db=db, user_id_to_delete=user_id)
    if not deleted_user_obj: # Doble verificacion
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado al intentar eliminar.")
    return deleted_user_obj 