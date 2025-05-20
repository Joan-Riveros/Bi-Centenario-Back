from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.models.historical_event import HistoricalEvent
from app.schemas.historical_event import HistoricalEventCreate, HistoricalEventUpdate

def get_historical_event(db: Session, historical_event_id: int) -> Optional[HistoricalEvent]:
    return db.query(HistoricalEvent).filter(HistoricalEvent.id == historical_event_id).first()

def get_historical_events(
    db: Session, skip: int = 0, limit: int = 100
) -> List[HistoricalEvent]:
    return db.query(HistoricalEvent).offset(skip).limit(limit).all()

def create_historical_event(db: Session, *, obj_in: HistoricalEventCreate) -> HistoricalEvent:
    db_obj = HistoricalEvent(
        name=obj_in.name,
        description=obj_in.description,
        event_date=obj_in.event_date,
        epoca_id=obj_in.epoca_id,
        region_id=obj_in.region_id,
    )
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
        update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

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