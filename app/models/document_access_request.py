from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 

from app.db.base import Base
from app.core.enums import RequestStatusEnum
class DocumentAccessRequest(Base):
    __tablename__ = "document_access_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    
    request_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(SQLAlchemyEnum(RequestStatusEnum), nullable=False, default=RequestStatusEnum.PENDING, index=True)
    admin_notes = Column(Text, nullable=True) 

    requester = relationship("User", back_populates="document_access_requests")
    document = relationship("Document", back_populates="access_requests")