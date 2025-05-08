from pydantic import BaseModel, EmailStr
from typing import Optional, List 
from app.core.enums import UserRole

# --- Esquemas Base  ---
class UserBase(BaseModel):
    email: EmailStr
    nombre: str
    role: UserRole

# --- Esquemas para Operaciones Especificas  ---
class UserCreate(UserBase): # Para registro publico
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    model_config = {"from_attributes": True} # Pydantic V2

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Esquemas para Autenticación y Tokens ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# --- Esquema para Actualización de Perfil por el propio usuario ---
class UserUpdateProfile(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None

# --- ESQUEMAN ADMIN ---

# Esquema administrador nuevo usuario
class AdminUserCreate(UserBase): # Hereda email, nombre, role
    password: str
    is_active: Optional[bool] = True


# Esquema administrador actualziar usuario

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    #descomentar para que admin cambie contrase;a
    # new_password: Optional[str] = None
