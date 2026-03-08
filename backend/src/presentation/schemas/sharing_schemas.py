from datetime import datetime

from pydantic import BaseModel, EmailStr


class ShareRequest(BaseModel):
    file_id: int
    target_email: EmailStr


class ShareResponse(BaseModel):
    share_id: int
    file_id: int
    shared_with_email: str
    status: str = "success"
    created_at: datetime

    class Config:
        from_attributes = True
