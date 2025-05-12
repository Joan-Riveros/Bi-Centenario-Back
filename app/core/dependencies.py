from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import logging
from typing import List, Optional 

from app.core.config import SECRET_KEY, ALGORITHM
from app.models.user import User
from app.crud import crud_user
from app.db.session import SessionLocal
from app.core.enums import UserRole 
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            logger.warning("Token JWT no contiene 'sub' (email).")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"Error de decodificación/validacion de JWT: {e}")
        raise credentials_exception
        
    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        logger.warning(f"Usuario no encontrado en la base de datos para el email del token: {email}")
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        logger.warning(f"Intento de acceso por usuario inactivo: {current_user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user

def require_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != UserRole.ADMINISTRADOR:
        logger.warning(
            f"Acceso de administrador denegado para el usuario {current_user.email}. Rol actual: {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios (se requiere administrador).",
        )
    return current_user


def require_role(required_roles: List[UserRole]):
    """
    Factoria de dependencias que verifica si el usuario actual (activo)
    tiene uno de los roles requeridos
    """
    def role_checker(current_active_user: User = Depends(get_current_active_user)): 
        if not current_active_user: 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado"
            )
        if current_active_user.role not in required_roles:
            logger.warning(
                f"Acceso denegado para el usuario {current_active_user.email}. Rol actual: {current_active_user.role}. Roles requeridos: {required_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para acceder a este recurso. Roles requeridos: {', '.join(role.value for role in required_roles)}."
            )
        return current_active_user
    return role_checker