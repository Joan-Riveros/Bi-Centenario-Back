# app/schemas/region.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class RegionBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RegionCreate(RegionBase):
    pass

class RegionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RegionInDBBase(RegionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Region(RegionInDBBase):
    pass