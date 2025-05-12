from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user import User
from app.schemas.user import UserCreate, AdminUserCreate, AdminUserUpdate 
from app.core.security import get_password_hash
from app.core.enums import UserRole
from app.schemas.user import UserUpdateProfile

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()


# Funcion para el registro publico "endpoint /users/register"
def create_public_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        nombre=user_in.nombre,
        role=UserRole.VISITANTE,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Funcion para la creacion de usuarios por un admin
def create_user_by_admin(db: Session, user_in: AdminUserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        nombre=user_in.nombre,
        role=user_in.role,
        is_active=user_in.is_active 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_by_admin(db: Session, db_user_to_update: User, user_in: AdminUserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)

    # Si se permite la actualizacion de contrase;a por admin:
    # if "new_password" in update_data and update_data["new_password"]:
    #     hashed_password = get_password_hash(update_data["new_password"])
    #     db_user_to_update.hashed_password = hashed_password
    #     del update_data["new_password"] # Para que no se intente aplicar con setattr

    for field, value in update_data.items():
        setattr(db_user_to_update, field, value)

    db.add(db_user_to_update)
    db.commit()
    db.refresh(db_user_to_update)
    return db_user_to_update


def delete_user_by_admin(db: Session, user_id_to_delete: int) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id_to_delete).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user 

# Funcion para actualizar el perfil del propio usuario (endpoint /users/profile)
def update_own_profile(db: Session, db_user_to_update: User, user_in: UserUpdateProfile) -> User:
    """
    Actualiza el perfil del propio usuario (nombre, email).
    """
    
    update_data = user_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user_to_update, field, value)
    
    db.add(db_user_to_update)
    db.commit()
    db.refresh(db_user_to_update)
    return db_user_to_update

def update_password(db: Session, db_user: User, new_password: str) -> User:
    hashed_password = get_password_hash(new_password)
    db_user.hashed_password = hashed_password
    db.add(db_user)
    db.commit()
    return db_user