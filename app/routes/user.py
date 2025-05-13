from fastapi import APIRouter, Depends, HTTPException, status, request
from jose import JWTError
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.two_factor import AccessTokenResponse, TwoFactorChallengeResponse
from app.db.session import SessionLocal 
from app.schemas.user import UserCreate, UserOut, UserLogin, UserUpdateProfile
from app.models.user import User 
from app.core.security import get_password_hash, create_access_token, authenticate_user, create_remember_device_token, verify_remember_device_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.crud import crud_2fa
from app.crud import crud_user
from app.core.enums import UserRole
from app.core.config import REMEMBER_DEVICE_COOKIE_NAME, REMEMBER_DEVICE_TOKEN_EXPIRE_DAYS , PROJECT_NAME
from fastapi.responses import JSONResponse
from app.schemas.two_factor import TwoFactorChallengeResponse, TwoFactorSetupInitiateResponse, TwoFactorSetupVerifyEnableRequest, TwoFactorDisableResponse, TwoFactorLoginVerifyRequest
from app.core.dependencies import get_current_active_user, get_db, require_admin_user
from jose import jwt
import pyotp
import qrcode
import qrcode.image.pil
import io
import base64
import secrets
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS
)


router = APIRouter()
# Dependencia obtener sesion BD
""""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
"""
@router.post("/login")
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, form_data.email, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
"""


@router.post("/login") 
async def login(
    response: JSONResponse, 
    form_data: UserLogin, 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.email, form_data.password) 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")

    
    if user.role == UserRole.ADMINISTRADOR:
        two_fa_settings = crud_2fa.get_2fa_settings(db, user_id=user.id)
        if two_fa_settings and two_fa_settings.is_enabled:
            
            
            remember_token_cookie = request.cookies.get(REMEMBER_DEVICE_COOKIE_NAME) 
            if remember_token_cookie:
                try:
                    
                    payload = verify_remember_device_token(remember_token_cookie)
                    if payload.get("sub") == user.email: # o user.id
                        
                        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                        access_token = create_access_token(
                            data={"sub": user.email, "role": user.role.value}, 
                            expires_delta=access_token_expires
                        )
                        
                        return AccessTokenResponse(access_token=access_token)
                except JWTError:
                    
                    pass 

            
            two_fa_token_expires = timedelta(minutes=5) 
            two_fa_token = create_access_token(
                data={"sub": user.email, "scope": "2fa_pending"}, 
                expires_delta=two_fa_token_expires
            )
            return TwoFactorChallengeResponse(two_factor_token=two_fa_token)

   
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, # Incluir rol
        expires_delta=access_token_expires
    )
    
    return AccessTokenResponse(access_token=access_token)


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)): 
    db_user = crud_user.get_user_by_email(db, email=user_in.email) 
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    
   
    new_user = crud_user.create_public_user(db=db, user_in=user_in)
    return new_user



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
    Actualizar el perfil del usuario actualmente autenticado (nombre, email)
    """
    
    if user_in.email and user_in.email != current_user.email:
        existing_user_with_new_email = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_with_new_email: 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este correo electronico ya esta registrado por otro usuario",
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
        #
        print(f"Token de reseteo para {user.email}: {password_reset_token}")

        success = await email_service.send_password_reset_email(
            email_to=user.email, username=user.nombre, token=password_reset_token
        )
        if not success:
            print(f"Fallo al intentar enviar el correo de reseteo a {user.email}")
            
    else:
        print(f"Solicitud de reseteo para email no encontrado o usuario inactivo: {password_request.email}")

    return {"msg": "Si tu correo electronico esta registrado y activo, recibiras instrucciones para restablecer tu contraseña en breve"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def perform_password_reset(
    password_data: PasswordReset,
    db: Session = Depends(get_db)
):
    email = verify_password_reset_token(token=password_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de restablecimiento es invalido o ha expirado",
        )
    
    user = crud_user.get_user_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado, inactivo, o el token es incorrecto",
        )
    
    crud_user.update_password(db=db, db_user=user, new_password=password_data.new_password)
    return {"msg": "Tu contraseña ha sido actualizada con exito"}

#2fa
@router.post(
    "/me/2fa/initiate-setup",
    response_model=TwoFactorSetupInitiateResponse,
    summary="Iniciar la configuracion de 2FA para el administrador actual",
    dependencies=[Depends(require_admin_user)] 
)
async def initiate_2fa_setup(
    current_user: User = Depends(require_admin_user) 
):
    
    # 1. Generar un nuevo secreto TOTP
    totp_secret = pyotp.random_base32() 

    # 2. Generar la URI otpauth://
    
    otpauth_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=current_user.email, #
        issuer_name=PROJECT_NAME
    )

    # 3. Generar el codigo QR como una imagen base64
    img = qrcode.make(otpauth_uri, image_factory=qrcode.image.pil.PilImage)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    qr_code_data_uri = f"data:image/png;base64,{qr_code_image_base64}"

    # 4. Generar codigos de respaldo 
    backup_codes = [secrets.token_hex(4) for _ in range(10)] 


    return TwoFactorSetupInitiateResponse(
        otpauth_uri=otpauth_uri,
        totp_secret=totp_secret,
        qr_code_image=qr_code_data_uri,
        backup_codes=backup_codes
    )

from app.crud import crud_2fa 

@router.post(
    "/me/2fa/verify-enable",
    summary="Verificar el codigo TOTP y habilitar 2FA para el administrador actual",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_user)]
)
async def verify_and_enable_2fa(
    payload: TwoFactorSetupVerifyEnableRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user)
):
    
    # 1. Verificar el codigo TOTP usando el secreto que el cliente envia de vuelta
    totp = pyotp.TOTP(payload.totp_secret)
    if not totp.verify(payload.totp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código TOTP es invalido o ha expirado"
        )

    # 2. Si el codigo es valido, guardar la configuración y habilitar 2FA
    try:
        crud_2fa.enable_2fa(
            db=db,
            user_id=current_user.id,
            unencrypted_totp_secret=payload.totp_secret,
            unencrypted_backup_codes=payload.backup_codes
        )
        db.commit() 
    except Exception as e: 
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo habilitar la 2FA Intentalo de nuevo"
        )

    return {"detail": "2FA habilitada exitosamente."}


@router.post(
    "/me/2fa/disable",
    response_model=TwoFactorDisableResponse, 
    summary="Deshabilitar 2FA para el administrador actual",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin_user)]
)
async def disable_2fa_endpoint( 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user)
):

    settings = crud_2fa.get_2fa_settings(db, user_id=current_user.id)
    if not settings or not settings.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA no esta habilitada para esta cuenta"
        )

    try:
        crud_2fa.disable_2fa(db=db, user_id=current_user.id)
        db.commit()
    except Exception as e:
        db.rollback()
        # logger.error(f"Error al deshabilitar 2FA para {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo deshabilitar la 2FA Intentalo de nuevo"
        )

    return TwoFactorDisableResponse()


#
@router.post("/users/2fa/verify-login") 
async def verify_2fa_login(
    payload: TwoFactorLoginVerifyRequest,
    response: JSONResponse, 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de 2FA invalido, codigo incorrecto, o error de autenticacion",
        headers={"WWW-Authenticate": "Bearer"},
    )
    invalid_code_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, #
        detail="El cóodigo proporcionado es invalido o ya ha sido utilizado"
    )

    try:
        token_payload = jwt.decode(
            payload.two_factor_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}
        )
        if token_payload.get("scope") != "2fa_pending":
            # logger.warning("Token 2FA con scope incorrecto recibido")
            raise credentials_exception
        user_email: str = token_payload.get("sub")
        if not user_email:
            # logger.warning("Token 2FA no contiene 'sub' (email)")
            raise credentials_exception
    except JWTError:
        # logger.warning("Error de decodificacion/validacion de JWT para token 2FA")
        raise credentials_exception

    user = crud_user.get_user_by_email(db, email=user_email)
    if not user or not user.is_active or user.role != UserRole.ADMINISTRADOR:
        # logger.warning(f"Usuario no encontrado, inactivo o no admin durante verificacion 2FA: {user_email}")
        raise credentials_exception

    two_fa_settings = crud_2fa.get_2fa_settings(db, user_id=user.id)
    if not two_fa_settings or not two_fa_settings.is_enabled:
        # logger.error(f"Verificacion 2FA intentada para usuario {user_email} sin 2FA habilitada")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA no esta habilitada para este usuario")

    login_successful = False

    if payload.backup_code:
        
        # logger.info(f"Intentando verificar codigo de respaldo para {user_email}")
        if crud_2fa.verify_and_use_backup_code(db, user_id=user.id, submitted_code=payload.backup_code):
            login_successful = True
            
        else:
            # logger.warning(f"Codigo de respaldo invalido para {user_email}")
            raise invalid_code_exception

    elif payload.totp_code:
        # logger.info(f"Intentando verificar cóodigo TOTP para {user_email}")
        decrypted_totp_secret = crud_2fa.get_decrypted_totp_secret(db, user_id=user.id)
        if not decrypted_totp_secret:
            # logger.error(f"No se pudo obtener el secreto TOTP para {user_email} durante la verificacion de login")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al verificar 2FA")

        totp = pyotp.TOTP(decrypted_totp_secret)
        if not totp.verify(payload.totp_code):
            # logger.warning(f"Código TOTP inválido para {user_email}")
            
            raise invalid_code_exception
        login_successful = True

    else:
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe proporcionar un codigo TOTP o un codigo de respaldo")

    if login_successful:
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        response_content = AccessTokenResponse(access_token=access_token).model_dump()

        if payload.remember_device:
            remember_token_expires = timedelta(days=REMEMBER_DEVICE_TOKEN_EXPIRE_DAYS)
            remember_token = create_remember_device_token( 
                data={"sub": user.email}, expires_delta=remember_token_expires
            )
            response.set_cookie(
                key=REMEMBER_DEVICE_COOKIE_NAME,
                value=remember_token,
                httponly=True,
                max_age=int(remember_token_expires.total_seconds()), 
                samesite="lax",
                secure=True 
            )

        try:
            db.commit() 
        except Exception as e:
            db.rollback()
            
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al finalizar el proceso de login")

        return JSONResponse(content=response_content)


    raise credentials_exception