from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    whatsapp_message_id: str
    from_number: str
    message_text: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    status: str
    response_text: Optional[str] = None

    class Config:
        from_attributes = True

class WebhookLogBase(BaseModel):
    webhook_type: str
    payload: str
    status: str
    error_message: Optional[str] = None

class WebhookLogCreate(WebhookLogBase):
    pass

class WebhookLog(WebhookLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
