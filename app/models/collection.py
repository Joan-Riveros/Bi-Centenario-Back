from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)


    owner = relationship("User", back_populates="collections")

  
    documents = relationship(
        "Document",
        secondary="collection_documents", 
        back_populates="collections_containing_document"
    )
    
