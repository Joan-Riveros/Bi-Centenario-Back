from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime


from .epoca import Epoca
from .region import Region
# from .document import Document 
class HistoricalEventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_date: Optional[datetime.date] = None
    epoca_id: Optional[int] = None 
    region_id: Optional[int] = None 

class HistoricalEventCreate(HistoricalEventBase):
    pass

class HistoricalEventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime.date] = None
    epoca_id: Optional[int] = None
    region_id: Optional[int] = None

class HistoricalEventInDBBase(HistoricalEventBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class HistoricalEvent(HistoricalEventInDBBase):
    epoca: Optional[Epoca] = None 
    region: Optional[Region] = None 
    # documents: List[Document] = [] # Para mostrar documentos asociados