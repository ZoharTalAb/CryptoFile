from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class ShareRequest(BaseModel):
    file_id: UUID
    target_email: EmailStr  

class ShareResponse(BaseModel):
    id: Optional[UUID] = None
    file_id: UUID
    shared_with_email: str
    status: str = "success"

    class Config:
        from_attributes = True