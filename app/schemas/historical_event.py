from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime

from .epoca import Epoca as EpocaSchema
from .region import Region as RegionSchema


class HistoricalEventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_date: Optional[datetime.date] = None
    epoca_id: Optional[int] = None 

class HistoricalEventCreate(HistoricalEventBase):
    region_ids: Optional[List[int]] = None

class HistoricalEventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime.date] = None
    epoca_id: Optional[int] = None

    region_ids: Optional[List[int]] = None

class HistoricalEventInDBBase(HistoricalEventBase):
    id: int


    model_config = ConfigDict(from_attributes=True)

class HistoricalEvent(HistoricalEventInDBBase):
    epoca: Optional[EpocaSchema] = None
    regions: List[RegionSchema] = [] 