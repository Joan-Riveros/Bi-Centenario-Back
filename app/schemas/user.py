from pydantic import BaseModel, EmailStr
from typing import Optional
class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "visitante"

class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True  # O 'orm_mode = True' si estás usando Pydantic v1


    
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    email: Optional[str] = None
