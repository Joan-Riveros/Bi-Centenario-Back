from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

def get_comment(db: Session, comment_id: int) -> Optional[Comment]:

    return db.query(Comment).filter(Comment.id == comment_id).first()

def get_comments_for_document(
    db: Session, document_id: int, skip: int = 0, limit: int = 100
) -> List[Comment]:

    return (
        db.query(Comment)
        .filter(Comment.document_id == document_id, Comment.parent_comment_id == None)
        .order_by(Comment.created_at.asc()) 
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_replies_for_comment(
    db: Session, parent_comment_id: int, skip: int = 0, limit: int = 25
) -> List[Comment]:

    return (
        db.query(Comment)
        .filter(Comment.parent_comment_id == parent_comment_id)
        .order_by(Comment.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_comment(db: Session, *, obj_in: CommentCreate, user_id: int) -> Comment:

    db_obj = Comment(
        user_id=user_id,
        document_id=obj_in.document_id,
        text_content=obj_in.text_content,
        parent_comment_id=obj_in.parent_comment_id

    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_comment(
    db: Session, *, db_obj: Comment, obj_in: Union[CommentUpdate, Dict[str, Any]]
) -> Optional[Comment]:

    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    if "text_content" in update_data: 
        db_obj.text_content = update_data["text_content"]
    else: 
        return None


    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_comment(db: Session, *, comment_id: int) -> Optional[Comment]:

    db_obj = db.query(Comment).get(comment_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
