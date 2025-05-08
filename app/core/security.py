from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import TokenData
from app.db.session import SessionLocal

# Cargar variables de entorno
load_dotenv()

# Seguridad para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración del token JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Middleware de seguridad para obtener el token
oauth2_scheme = HTTPBearer()

# Hashear contraseña
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Verificar contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Crear token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Autenticar usuario al hacer login
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Obtener conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener usuario actual desde el token
def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    
    
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# Middleware de rol requerido
def require_role(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta ruta")
        return current_user
    return role_checker


