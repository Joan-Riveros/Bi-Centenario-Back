from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    return db.query(Category).offset(skip).limit(limit).all()

def create_category(db: Session, *, obj_in: CategoryCreate) -> Category:
    db_obj = Category(name=obj_in.name, description=obj_in.description)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_category(
    db: Session, *, db_obj: Category, obj_in: Union[CategoryUpdate, Dict[str, Any]]
) -> Category:
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

def remove_category(db: Session, *, category_id: int) -> Optional[Category]:
    db_obj = db.query(Category).get(category_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj