from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime

class EpocaBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

class EpocaCreate(EpocaBase):
    pass

class EpocaUpdate(BaseModel): 
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

class EpocaInDBBase(EpocaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Epoca(EpocaInDBBase):
    pass 