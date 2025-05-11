from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base

class ForumCategory(Base):
    __tablename__ = "forum_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    topics = relationship("ForumTopic", back_populates="category", cascade="all, delete-orphan")

class ForumTopic(Base):
    __tablename__ = "forum_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("forum_categories.id"))

    author = relationship("User", backref="topics")
    category = relationship("ForumCategory", back_populates="topics")
    posts = relationship("ForumPost", back_populates="topic", cascade="all, delete-orphan")

class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_moderated = Column(Boolean, default=False)

    author_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("forum_topics.id"))

    author = relationship("User", backref="posts")
    topic = relationship("ForumTopic", back_populates="posts")
