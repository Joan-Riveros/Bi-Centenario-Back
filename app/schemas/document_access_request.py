from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime

from app.core.enums import RequestStatusEnum
from .user import UserOut as UserSchema
from .document import DocumentMinimal as DocumentMinimalSchema

class DocumentAccessRequestBase(BaseModel):
    document_id: int 

class DocumentAccessRequestCreate(DocumentAccessRequestBase):

    pass

class DocumentAccessRequestUpdate(BaseModel): 
    status: RequestStatusEnum
    admin_notes: Optional[str] = None

class DocumentAccessRequestInDBBase(DocumentAccessRequestBase):
    id: int
    user_id: int 
    request_date: datetime.datetime
    status: RequestStatusEnum
    admin_notes: Optional[str] = None
    

    model_config = ConfigDict(from_attributes=True)

class DocumentAccessRequest(DocumentAccessRequestInDBBase):
    requester: UserSchema
    document: DocumentMinimalSchema