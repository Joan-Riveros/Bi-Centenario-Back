from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))  

    recipient = relationship("User", back_populates="notifications")
