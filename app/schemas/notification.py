from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    recipient_id: int 

class NotificationOut(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime


    model_config = {"from_attributes": True}
   