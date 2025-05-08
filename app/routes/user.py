from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import SessionLocal 
from app.schemas.user import UserCreate, UserOut, UserLogin 
from app.models.user import User 
from app.core.security import get_password_hash, create_access_token, authenticate_user
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
# from app.core.enums import UserRole
from app.crud import crud_user


router = APIRouter()

# Dependencia obtener sesion BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut) 
def register(user_in: UserCreate, db: Session = Depends(get_db)): 
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")

    hashed_password = get_password_hash(user_in.password)


    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        nombre=user_in.nombre, 
        role=user_in.role     
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 


@router.post("/login")
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.email, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)): 
    db_user = crud_user.get_user_by_email(db, email=user_in.email) 
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    
   
    new_user = crud_user.create_public_user(db=db, user_in=user_in)
    return new_user