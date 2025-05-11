from pydantic import BaseModel, EmailStr
from app.core.enums import UserRole
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[UserRole] = UserRole.VISITANTE  # ✅ usa el Enum

class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    role: UserRole  # ✅ ya está bien

    class Config:
        from_attributes = True  # si usas Pydantic v2
        # orm_mode = True  # si usas Pydantic v1 (opcional si ya tienes from_attributes)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    email: Optional[str] = None

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole  # Obligatorio para el admin crear con rol definido

class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
