from pydantic import BaseModel, EmailStr
from typing import Optional, List 
from app.core.enums import UserRole

from pydantic import Field

# --- Esquemas Base  ---
class UserBase(BaseModel):
    email: EmailStr
    nombre: str

# --- Esquemas para operaciones especificas  ---
class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    role: UserRole
    model_config = {"from_attributes": True} 

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Esquemas para autenticación y tokens ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# --- Esquema para actualizacion de perfil por usuario ---
class UserUpdateProfile(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None

# --- ESQUEMAN ADMIN ---

# Esquema administrador nuevo usuario
class AdminUserCreate(UserBase): 
    password: str
    role: UserRole
    is_active: Optional[bool] = True


# Esquema administrador actualziar usuario

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    #descomentar para que admin cambie contrase;a
    # new_password: Optional[str] = None

# recuperacion contraseña
from pydantic import BaseModel, EmailStr, Field
class PasswordResetRequest(BaseModel):
    email: EmailStr 

class PasswordReset(BaseModel):
    token: str 
    new_password: str = Field(..., min_length=8)

# --- Nuevo esquema para incluir estado 2FA ---
class UserOutWith2FA(UserOut):
    is_2fa_enabled: bool
    model_config = {"from_attributes": True}

# --- Necesario para llamar los nombres de los comentarios del foro ---
class UserOutShort(BaseModel):
    id: int
    nombre: Optional[str] = None
    email: EmailStr

    model_config = {"from_attributes": True}