from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.models.user import User
from app.core.security import (
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user,
    require_role,
)
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Solo admin puede registrar usuarios con rol "admin"
    if user.role == "admin":
        if not current_user or current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Solo administradores pueden registrar a otros admins"
            )

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin-only")
def only_admin(current_user: User = Depends(require_role(["admin"]))):
    return {"message": f"Bienvenido, {current_user.email}"}

# Ruta solo para administradores
@router.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_role(["admin"]))):
    return {"msg": f"Bienvenido al panel de administrador, {current_user.email}"}

# Ruta para administradores y editores
@router.get("/editor/panel")
def editor_panel(current_user: User = Depends(require_role(["admin", "editor"]))):
    return {"msg": f"Bienvenido al panel del editor, {current_user.email}"}

# Ruta accesible para cualquier usuario autenticado
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "role": current_user.role,
        "active": current_user.is_active
    }
