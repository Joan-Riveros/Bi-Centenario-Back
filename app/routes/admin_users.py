from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserOut, AdminUserCreate, AdminUserUpdate
from app.crud import crud_user
from app.core.security import require_role, get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_as_admin(
    user_in: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"]))
):
    existing_user = crud_user.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Este email ya está registrado.")
    return crud_user.create_user_by_admin(db=db, user_in=user_in)

@router.get("/", response_model=List[UserOut])
def read_users_as_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"]))
):
    return crud_user.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserOut)
def read_user_as_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"]))
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user_as_admin(
    user_id: int,
    user_in: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"]))
):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user_in.email and user_in.email != user.email:
        if crud_user.get_user_by_email(db, email=user_in.email):
            raise HTTPException(status_code=409, detail="Email ya en uso.")

    return crud_user.update_user_by_admin(db, db_user_to_update=user, user_in=user_in)

@router.delete("/{user_id}", response_model=UserOut)
def delete_user_as_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(["admin"]))
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=403, detail="No puedes eliminarte a ti mismo.")
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return crud_user.delete_user_by_admin(db, user_id_to_delete=user_id)
