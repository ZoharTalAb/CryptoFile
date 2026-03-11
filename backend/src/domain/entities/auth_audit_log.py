from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthAuditLog:
    id: int | None
    user_id: int | None
    email: str | None
    event_type: str
    success: bool
    reason_code: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
