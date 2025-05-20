import datetime 
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 

from app.models.association_tables import (
    document_categories_table,
    document_tags_table,
    document_historical_events_table
)


from app.db.base import Base

from app.core.enums import OCRStatusEnum 

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), nullable=True, index=True) 
    short_description = Column(Text, nullable=True)
    publisher = Column(String(255), nullable=True)
    isbn = Column(String(20), nullable=True, index=True) 
    page_count = Column(Integer, nullable=True)
    is_scanned = Column(Boolean, default=False, nullable=False)
    
    file_path = Column(String(1024), nullable=False) 
    cover_image_path = Column(String(1024), nullable=True) 
    
    edition_details = Column(Text, nullable=True) 
    
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    document_level = Column(Integer, default=1, nullable=False) 

    # Campos OCR
    ocr_text = Column(Text, nullable=True)
    ocr_status = Column(SQLAlchemyEnum(OCRStatusEnum), nullable=True, default=OCRStatusEnum.PENDING)
    #role = Column(SAEnum(UserRole), nullable=False, default=UserRole.VISITANTE)
    uploader = relationship("User", back_populates="uploaded_documents")

    access_requests = relationship(
        "DocumentAccessRequest",
        back_populates="document",
        cascade="all, delete-orphan" 
    )

    categories = relationship(
        "Category", 
        secondary=document_categories_table,
        back_populates="documents"
    )

    tags = relationship(
        "Tag",
        secondary=document_tags_table,
        back_populates="documents"
    )

    historical_events = relationship(
        "HistoricalEvent",
        secondary=document_historical_events_table,
        back_populates="documents"
    )

    # Otras relaciones 
    # ratings = relationship("Rating", back_populates="document")
    # comments = relationship("Comment", back_populates="document")
    # collections = relationship("Collection", secondary="collection_documents", back_populates="documents")