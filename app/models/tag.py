from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship 
from app.models.association_tables import document_tags_table
from app.db.base import Base

class Tag(Base):
    __tablename__ = "tags" 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True) 

    documents = relationship(
        "Document",
        secondary=document_tags_table,
        back_populates="tags"
    )