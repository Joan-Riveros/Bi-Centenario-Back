from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import relationship 

from app.db.base import Base

class Epoca(Base):
    __tablename__ = "epocas" #

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Relaciones 
    # historical_events = relationship("HistoricalEvent", back_populates="epoca")
    # documents = relationship("Document", back_populates="epoca")