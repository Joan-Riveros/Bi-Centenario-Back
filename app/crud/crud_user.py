from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import AdminUserCreate, AdminUserUpdate
from app.core.security import get_password_hash
from typing import Optional
from app.core.enums import UserRole


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user_by_admin(db: Session, user_in: AdminUserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_by_admin(db: Session, db_user_to_update: User, user_in: AdminUserUpdate) -> User:
    if user_in.email is not None:
        db_user_to_update.email = user_in.email

    if user_in.password is not None:
        db_user_to_update.hashed_password = get_password_hash(user_in.password)

    if user_in.role is not None:
        db_user_to_update.role = user_in.role

    if user_in.is_active is not None:
        db_user_to_update.is_active = user_in.is_active

    db.commit()
    db.refresh(db_user_to_update)
    return db_user_to_update

def delete_user_by_admin(db: Session, user_id_to_delete: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id_to_delete).first()
    if user:
        db.delete(user)
        db.commit()
    return user
