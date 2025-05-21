from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False) # Ej. 1 a 5

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    rater = relationship("User", back_populates="ratings")
    document = relationship("Document", back_populates="ratings")

    __table_args__ = (UniqueConstraint('user_id', 'document_id', name='uq_user_document_rating'),)
