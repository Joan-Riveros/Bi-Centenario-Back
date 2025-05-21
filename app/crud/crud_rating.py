from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingUpdate

def get_rating(db: Session, rating_id: int) -> Optional[Rating]:

    return db.query(Rating).filter(Rating.id == rating_id).first()

def get_rating_by_user_and_document(
    db: Session, *, user_id: int, document_id: int
) -> Optional[Rating]:

    return db.query(Rating).filter(Rating.user_id == user_id, Rating.document_id == document_id).first()

def get_ratings_for_document(
    db: Session, document_id: int, skip: int = 0, limit: int = 100
) -> List[Rating]:

    return (
        db.query(Rating)
        .filter(Rating.document_id == document_id)
        .order_by(Rating.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_ratings_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Rating]:

    return (
        db.query(Rating)
        .filter(Rating.user_id == user_id)
        .order_by(Rating.id.desc()) 
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_rating(db: Session, *, obj_in: RatingCreate, user_id: int) -> Optional[Rating]:

    existing_rating = get_rating_by_user_and_document(db, user_id=user_id, document_id=obj_in.document_id)
    if existing_rating:

        return None 

    db_obj = Rating(
        user_id=user_id,
        document_id=obj_in.document_id,
        score=obj_in.score
    )
    db.add(db_obj)
    try:
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except IntegrityError: 
        db.rollback()

        return None


def update_rating(
    db: Session, *, db_obj: Rating, obj_in: Union[RatingUpdate, Dict[str, Any]]
) -> Rating:

    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    if "score" in update_data: 
        db_obj.score = update_data["score"]

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_rating(db: Session, *, rating_id: int) -> Optional[Rating]:

    db_obj = db.query(Rating).get(rating_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

def remove_rating_by_user_and_document(db: Session, *, user_id: int, document_id: int) -> Optional[Rating]:

    db_obj = get_rating_by_user_and_document(db, user_id=user_id, document_id=document_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
