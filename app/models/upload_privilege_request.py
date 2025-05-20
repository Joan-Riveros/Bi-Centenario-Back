from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 

from app.db.base import Base
from app.core.enums import RequestStatusEnum

class UploadPrivilegeRequest(Base):
    __tablename__ = "upload_privilege_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    request_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(SQLAlchemyEnum(RequestStatusEnum), nullable=False, default=RequestStatusEnum.PENDING, index=True)
    admin_notes = Column(Text, nullable=True)
    
    title = Column(String(500), nullable=False)
    author = Column(String(255), nullable=True)
    short_description = Column(Text, nullable=True)
    publisher = Column(String(255), nullable=True)
    isbn = Column(String(20), nullable=True)
    page_count = Column(Integer, nullable=True)
    is_scanned = Column(Boolean, default=False, nullable=True) 
    edition_details = Column(Text, nullable=True)
    proposed_document_level = Column(Integer, default=1, nullable=False) 

    requester = relationship("User", back_populates="upload_privilege_requests")