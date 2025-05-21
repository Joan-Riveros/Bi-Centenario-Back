from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.core.enums import RequestStatusEnum 

class UploadPrivilegeRequest(Base):
    __tablename__ = "document_approval_requests" 

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) 

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

    pending_file_path = Column(String(1024), nullable=False)


    pending_cover_image_path = Column(String(1024), nullable=True)


    created_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True, unique=True) 

    # --- Relaciones ---
    requester = relationship("User", back_populates="document_approval_requests") 

    created_document = relationship("Document", backref="approval_request") 

    def __repr__(self):
        return f"<DocumentApprovalRequest id={self.id} title='{self.title}' status='{self.status}'>"