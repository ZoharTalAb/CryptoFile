from dataclasses import dataclass
from datetime import datetime


@dataclass
class PasswordHistoryEntry:
    id: int | None
    user_id: int
    password_hash: str
    created_at: datetime
