from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from app.db.base import Base
from app.models.notification import Notification
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="visitante")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")
 
