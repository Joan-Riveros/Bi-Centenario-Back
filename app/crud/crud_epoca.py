from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session

from app.models.epoca import Epoca
from app.schemas.epoca import EpocaCreate, EpocaUpdate

def get_epoca(db: Session, epoca_id: int) -> Optional[Epoca]:
    return db.query(Epoca).filter(Epoca.id == epoca_id).first()

def get_epocas(db: Session, skip: int = 0, limit: int = 100) -> List[Epoca]:
    return db.query(Epoca).offset(skip).limit(limit).all()

def create_epoca(db: Session, *, obj_in: EpocaCreate) -> Epoca:
    db_obj = Epoca(
        name=obj_in.name,
        description=obj_in.description,
        start_date=obj_in.start_date,
        end_date=obj_in.end_date,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_epoca(
    db: Session, *, db_obj: Epoca, obj_in: Union[EpocaUpdate, Dict[str, Any]]
) -> Epoca:
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

def remove_epoca(db: Session, *, epoca_id: int) -> Optional[Epoca]:
    db_obj = db.query(Epoca).get(epoca_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj