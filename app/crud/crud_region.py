from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.models.region import Region
from app.schemas.region import RegionCreate, RegionUpdate

def get_region(db: Session, region_id: int) -> Optional[Region]:
    return db.query(Region).filter(Region.id == region_id).first()

def get_regiones(db: Session, skip: int = 0, limit: int = 100) -> List[Region]:
    return db.query(Region).offset(skip).limit(limit).all()

def create_region(db: Session, *, obj_in: RegionCreate) -> Region:
    db_obj = Region(
        name=obj_in.name,
        description=obj_in.description,
        latitude=obj_in.latitude,
        longitude=obj_in.longitude,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_region(
    db: Session, *, db_obj: Region, obj_in: Union[RegionUpdate, Dict[str, Any]]
) -> Region:
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

def remove_region(db: Session, *, region_id: int) -> Optional[Region]:
    db_obj = db.query(Region).get(region_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj