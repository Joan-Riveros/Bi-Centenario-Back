from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime


from .user import UserOut as UserSchema
from .category import Category as CategorySchema
from .tag import Tag as TagSchema
from .historical_event import HistoricalEvent as HistoricalEventSchema
from app.core.enums import OCRStatusEnum 
from pydantic import Field

class DocumentBase(BaseModel):
    title: str
    author: Optional[str] = None
    short_description: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    page_count: Optional[int] = None
    is_scanned: bool = False
    edition_details: Optional[str] = None
    document_level: int = 1


class DocumentCreate(DocumentBase):
    
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    historical_event_ids: Optional[List[int]] = None
    


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    short_description: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    page_count: Optional[int] = None
    is_scanned: Optional[bool] = None
    edition_details: Optional[str] = None
    document_level: Optional[int] = None
    # Para actualizar relaciones
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    historical_event_ids: Optional[List[int]] = None
    # ocr_status y ocr_text no van a ser actualizados por el usuario


class DocumentInDBBase(DocumentBase):
    id: int
    uploader_id: int
    upload_date: datetime.datetime
    file_path: str 
    cover_image_path: Optional[str] = None 
    ocr_text: Optional[str] = None
    ocr_status: Optional[OCRStatusEnum] = None
    
    model_config = ConfigDict(from_attributes=True)



class Document(DocumentInDBBase):
    uploader: UserSchema 
    categories: List[CategorySchema] = []
    tags: List[TagSchema] = []
    historical_events: List[HistoricalEventSchema] = []
    # access_requests: List[DocumentAccessRequestSchema] = []

class DocumentMinimal(BaseModel): 
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class DocumentLevelUpdate(BaseModel):
    document_level: int = Field(..., ge=1, le=3)
