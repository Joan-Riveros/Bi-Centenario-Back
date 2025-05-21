from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime

from app.core.enums import RequestStatusEnum
from .user import UserOut as UserSchema



class UploadPrivilegeRequestBase(BaseModel):
    
    title: str
    author: Optional[str] = None
    short_description: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    page_count: Optional[int] = None
    is_scanned: Optional[bool] = False
    edition_details: Optional[str] = None
    proposed_document_level: int = 1

    
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    historical_event_ids: Optional[List[int]] = None


    pending_file_path: str
    pending_cover_image_path: Optional[str] = None

class UploadPrivilegeRequestCreate(UploadPrivilegeRequestBase):
    pass

class UploadPrivilegeRequestUpdate(BaseModel):
    status: RequestStatusEnum
    admin_notes: Optional[str] = None

class UploadPrivilegeRequestInDBBase(UploadPrivilegeRequestBase):
    id: int
    user_id: int
    request_date: datetime.datetime
    status: RequestStatusEnum
    admin_notes: Optional[str] = None


    created_document_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class UploadPrivilegeRequest(UploadPrivilegeRequestInDBBase): 
    requester: UserSchema
