from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship 
from app.models.association_tables import document_categories_table
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories" 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    documents = relationship(
        "Document",
        secondary=document_categories_table,
        back_populates="categories"
    )