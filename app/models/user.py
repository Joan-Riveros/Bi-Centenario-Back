from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from app.db.base import Base
from app.core.enums import UserRole 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    nombre = Column(String(100), nullable=False) 

    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.VISITANTE)
    #
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")