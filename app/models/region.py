from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship 

from app.db.base import Base

class Region(Base):
    __tablename__ = "regiones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True) 
    longitude = Column(Float, nullable=True) 

    # Relaciones
    # historical_events = relationship("HistoricalEvent", back_populates="region")
    # documents = relationship("Document", back_populates="region")