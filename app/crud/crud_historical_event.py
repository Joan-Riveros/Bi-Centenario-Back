from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.models.historical_event import HistoricalEvent
from app.models.region import Region 
from app.schemas.historical_event import HistoricalEventCreate, HistoricalEventUpdate

def get_historical_event(db: Session, historical_event_id: int) -> Optional[HistoricalEvent]:
    return db.query(HistoricalEvent).filter(HistoricalEvent.id == historical_event_id).first()

def get_historical_events(
    db: Session, skip: int = 0, limit: int = 100
) -> List[HistoricalEvent]:
    return db.query(HistoricalEvent).offset(skip).limit(limit).all()

def create_historical_event(db: Session, *, obj_in: HistoricalEventCreate) -> HistoricalEvent:
    historical_event_data = obj_in.model_dump(exclude={"region_ids"})
    db_obj = HistoricalEvent(**historical_event_data)

    if obj_in.region_ids:
        regions = db.query(Region).filter(Region.id.in_(obj_in.region_ids)).all()
        db_obj.regions = regions  

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_historical_event(
    db: Session,
    *,
    db_obj: HistoricalEvent,
    obj_in: Union[HistoricalEventUpdate, Dict[str, Any]],
) -> HistoricalEvent:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"region_ids"})

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    if not isinstance(obj_in, dict) and hasattr(obj_in, "region_ids") and obj_in.region_ids is not None:
        if obj_in.region_ids: 
            regions = db.query(Region).filter(Region.id.in_(obj_in.region_ids)).all()
            db_obj.regions = regions
        else: 
            db_obj.regions = []
    elif isinstance(obj_in, dict) and "region_ids" in obj_in and obj_in["region_ids"] is not None:
        if obj_in["region_ids"]:
            regions = db.query(Region).filter(Region.id.in_(obj_in["region_ids"])).all()
            db_obj.regions = regions
        else:
            db_obj.regions = []


    db.add(db_obj) 
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove_historical_event(db: Session, *, historical_event_id: int) -> Optional[HistoricalEvent]:
    db_obj = db.query(HistoricalEvent).get(historical_event_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj