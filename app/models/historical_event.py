from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.association_tables import document_historical_events_table
from app.db.base import Base

class HistoricalEvent(Base):
    __tablename__ = "historical_events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=True) 

    epoca_id = Column(Integer, ForeignKey("epocas.id"), nullable=True)
    region_id = Column(Integer, ForeignKey("regiones.id"), nullable=True)

  
    epoca = relationship("Epoca", backref="historical_events") 
    region = relationship("Region", backref="historical_events") 

    documents = relationship(
        "Document",
        secondary=document_historical_events_table,
        back_populates="historical_events"
    )