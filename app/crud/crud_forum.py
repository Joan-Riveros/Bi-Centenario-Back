from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.models.forum import ForumCategory, ForumTopic, ForumPost
from app.models.user import User 
from app.models.notification import Notification
from app.schemas.forum import ForumCategoryCreate, ForumTopicCreate, ForumPostCreate

# -------- CATEGORiAS --------

def get_forum_category_by_name(db: Session, name: str) -> Optional[ForumCategory]:
    return db.query(ForumCategory).filter(ForumCategory.name == name).first()

def create_forum_category(db: Session, category_in: ForumCategoryCreate) -> ForumCategory:
    db_category = ForumCategory(**category_in.model_dump())
    db.add(db_category)
    return db_category

def get_forum_categories(db: Session, skip: int = 0, limit: int = 10) -> List[ForumCategory]:
    return db.query(ForumCategory).order_by(ForumCategory.name).offset(skip).limit(limit).all()

# -------- TEMAS--------

def get_forum_topic_by_id(db: Session, topic_id: int) -> Optional[ForumTopic]:
    return db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

def create_forum_topic(db: Session, topic_in: ForumTopicCreate, author_id: int) -> ForumTopic:
    db_topic = ForumTopic(**topic_in.model_dump(), author_id=author_id)
    db.add(db_topic)
    return db_topic

def get_forum_topics(
    db: Session,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10
) -> List[ForumTopic]:
    query = db.query(ForumTopic)
    if category_id is not None:
        query = query.filter(ForumTopic.category_id == category_id)
    return query.order_by(ForumTopic.created_at.desc()).offset(skip).limit(limit).all()

# -------- RESPUESTAS--------

def create_forum_post_with_notification(
    db: Session,
    post_in: ForumPostCreate,
    author: User 
) -> ForumPost:
 
    db_post = ForumPost(**post_in.model_dump(), author_id=author.id)
    db.add(db_post)

   
    topic = get_forum_topic_by_id(db, topic_id=post_in.topic_id) 
                                                                 
    
    if topic and topic.author_id != author.id:
        author_display_name = author.nombre if author.nombre else author.email
        db_notification = Notification(
            user_id=topic.author_id,
            message=f"'{author_display_name}' respondió a tu tema: '{topic.title[:50]}...'"
        )
        db.add(db_notification)
        
    
    return db_post


def get_forum_posts(
    db: Session,
    topic_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10
) -> List[ForumPost]:
    query = db.query(ForumPost)
    if topic_id is not None:
        query = query.filter(ForumPost.topic_id == topic_id)
    return query.order_by(ForumPost.created_at.asc()).offset(skip).limit(limit).all()


# -------- BuSQUEDA --------

def search_forum_topics(
    db: Session,
    keyword: str,
    skip: int = 0,
    limit: int = 10
) -> List[ForumTopic]:
    search_term = f"%{keyword}%"
    return db.query(ForumTopic).filter(
        (ForumTopic.title.ilike(search_term)) |
        (ForumTopic.content.ilike(search_term))
    ).order_by(ForumTopic.created_at.desc()).offset(skip).limit(limit).all()

def search_forum_posts(
    db: Session,
    keyword: str,
    topic_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10
) -> List[ForumPost]:
    search_term = f"%{keyword}%"
    query = db.query(ForumPost).filter(ForumPost.content.ilike(search_term))
    if topic_id is not None:
        query = query.filter(ForumPost.topic_id == topic_id)
    return query.order_by(ForumPost.created_at.desc()).offset(skip).limit(limit).all()