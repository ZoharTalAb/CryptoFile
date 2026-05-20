from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
    password_changed_at: datetime
    password_expires_at: datetime
    failed_login_attempts: int
    last_failed_login_at: datetime | None
    locked_until: datetime | None
    token_version: int
    email_verified: bool = True
    email_verification_code_hash: str | None = None
    email_verification_expires_at: datetime | None = None
    email_verification_sent_at: datetime | None = None
