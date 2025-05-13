from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional 
import logging
from app.core.config import REMEMBER_DEVICE_TOKEN_EXPIRE_DAYS
from sqlalchemy.orm import Session

from app.models.user import User

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS
)

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.debug(f"Intento de autenticacipn fallido: Usuario no encontrado - {email}")
        return None
    if not verify_password(password, user.hashed_password):
        logger.debug(f"Intento de autenticacipn fallido: Contraseña incorrecta para el usuario - {email}")
        return None
    logger.info(f"Usuario autenticado exitosamente: {email}")
    return user


def create_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "exp": expire,
        "nbf": datetime.utcnow(),
        "sub": email,
        "scope": "password_reset"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") == "password_reset":
            email: Optional[str] = payload.get("sub")
            return email
        logger.warning("Intento de verificación de token de reseteo con scope incorrecto")
        return None
    except JWTError as e:
        logger.error(f"Error al decodificar token de reseteo de contraseña: {e}")
        return None



#2fa
def create_remember_device_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REMEMBER_DEVICE_TOKEN_EXPIRE_DAYS) 
    to_encode.update({"exp": expire, "scope": "remember_device"}) 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 
    return encoded_jwt

def verify_remember_device_token(token: str) -> Optional[dict]: 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": False})
        if payload.get("scope") == "remember_device":
            return payload
        logger.warning("Token 'remember_device' con scope incorrecto.")
        return None
    except JWTError as e:
        logger.info(f"Token 'remember_device' inválido o expirado: {e}") 
        return None