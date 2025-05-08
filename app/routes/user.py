from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import SessionLocal 
from app.schemas.user import UserCreate, UserOut, UserLogin, UserUpdateProfile
from app.models.user import User 
from app.core.security import get_password_hash, create_access_token, authenticate_user
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
# from app.core.enums import UserRole
from app.crud import crud_user


from app.core.dependencies import get_current_active_user, get_db #


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



# Modificaciones para el CRUD de usuarios por el usuario mismo
@router.get("/me", response_model=UserOut)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener el perfil del usuario actualmente autenticado.
    """
    return current_user


@router.put("/me", response_model=UserOut)
async def update_users_me(
    user_in: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) 
):
    """
    Actualizar el perfil del usuario actualmente autenticado (nombre, email).
    """
    
    if user_in.email and user_in.email != current_user.email:
        existing_user_with_new_email = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_with_new_email: 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este correo electronico ya está registrado por otro usuario",
            )
    
    updated_user = crud_user.update_own_profile(db=db, db_user_to_update=current_user, user_in=user_in)
    return updated_user

#recuperacion contraseña
from app.schemas.user import PasswordResetRequest, PasswordReset
from app.core.security import create_password_reset_token, verify_password_reset_token
from app.services import email_service

@router.post("/password-recovery", status_code=status.HTTP_200_OK)
async def request_password_recovery(
    password_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = crud_user.get_user_by_email(db, email=password_request.email)

    if user and user.is_active:
        password_reset_token = create_password_reset_token(email=user.email)
        # ¡Aquí se llama a tu servicio de email actualizado!
        success = await email_service.send_password_reset_email(
            email_to=user.email, username=user.nombre, token=password_reset_token
        )
        if not success:
            print(f"Fallo al intentar enviar el correo de reseteo a {user.email}")
            
    else:
        print(f"Solicitud de reseteo para email no encontrado o usuario inactivo: {password_request.email}")

    return {"msg": "Si tu correo electronico está registrado y activo, recibiras instrucciones para restablecer tu contraseña en breve"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def perform_password_reset(
    password_data: PasswordReset,
    db: Session = Depends(get_db)
):
    email = verify_password_reset_token(token=password_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de restablecimiento es invalido o ha expirado.",
        )
    
    user = crud_user.get_user_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado, inactivo, o el token es incorrecto",
        )
    
    crud_user.update_password(db=db, db_user=user, new_password=password_data.new_password)
    return {"msg": "Tu contraseña ha sido actualizada con exito"}