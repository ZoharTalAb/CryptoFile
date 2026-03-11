from datetime import datetime, timedelta, timezone

from core.config import (
    LOGIN_MAX_FAILED_ATTEMPTS,
    LOGIN_LOCKOUT_MINUTES,
)
from domain.entities.user import User


class LoginProtectionService:

    def is_locked(self, user: User) -> bool:
        if user.locked_until is None:
            return False
        return user.locked_until > datetime.now(timezone.utc)

    def register_failed_attempt(self, user: User) -> User:
        now = datetime.now(timezone.utc)

        user.failed_login_attempts += 1
        user.last_failed_login_at = now

        if user.failed_login_attempts >= LOGIN_MAX_FAILED_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)

        user.updated_at = now
        return user

    def reset_failures(self, user: User) -> User:
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.locked_until = None
        user.updated_at = datetime.now(timezone.utc)
        return user
