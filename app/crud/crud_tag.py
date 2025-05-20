from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate

def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id).first()

def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.name == name).first()

def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    return db.query(Tag).offset(skip).limit(limit).all()

def create_tag(db: Session, *, obj_in: TagCreate) -> Tag:
    db_obj = Tag(name=obj_in.name)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_tag(
    db: Session, *, db_obj: Tag, obj_in: Union[TagUpdate, Dict[str, Any]]
) -> Tag:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_tag(db: Session, *, tag_id: int) -> Optional[Tag]:
    db_obj = db.query(Tag).get(tag_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj