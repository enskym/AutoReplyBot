from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class MessageTemplateBase(BaseModel):
    trigger_text: str
    response_text: str
    is_active: bool = True

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateUpdate(MessageTemplateBase):
    trigger_text: Optional[str] = None
    response_text: Optional[str] = None
    is_active: Optional[bool] = None

class MessageTemplate(MessageTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageLog(BaseModel):
    id: int
    user_id: str
    incoming_message: str
    response_message: str
    template_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_messages: int
    active_templates: int
    response_rate: float
    recent_messages: List[MessageLog]

class ApiResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None 