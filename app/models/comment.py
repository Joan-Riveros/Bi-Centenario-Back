from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 

from app.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True) 

    # Relaciones
    commenter = relationship("User", back_populates="comments")
    document = relationship("Document", back_populates="comments")
    

    replies = relationship(
        "Comment", 
        back_populates="parent_comment",
        cascade="all, delete-orphan",
        single_parent=True,
        remote_side=[id] 
    )

    parent_comment = relationship(
        "Comment",
        back_populates="replies",
        remote_side=[parent_comment_id] 
    )
