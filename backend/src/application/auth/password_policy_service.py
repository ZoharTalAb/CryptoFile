import re

from core.config import (
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
)
from domain.exceptions import PasswordPolicyViolationError


class PasswordPolicyService:

    def validate(self, email: str, password: str) -> None:
        normalized_email = email.strip().lower()
        local_part = (
            normalized_email.split("@")[0]
            if "@" in normalized_email
            else normalized_email
        )

        if len(password) < PASSWORD_MIN_LENGTH:
            raise PasswordPolicyViolationError(
                f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
            )

        if len(password) > PASSWORD_MAX_LENGTH:
            raise PasswordPolicyViolationError(
                f"Password must be at most {PASSWORD_MAX_LENGTH} characters long"
            )

        if not re.search(r"[A-Za-z]", password):
            raise PasswordPolicyViolationError(
                "Password must contain at least one English letter"
            )

        if not re.search(r"\d", password):
            raise PasswordPolicyViolationError(
                "Password must contain at least one digit"
            )

        lowered_password = password.lower()
        if normalized_email and normalized_email in lowered_password:
            raise PasswordPolicyViolationError(
                "Password must not contain the email address"
            )

        if local_part and len(local_part) >= 3 and local_part in lowered_password:
            raise PasswordPolicyViolationError(
                "Password must not contain the email username"
            )


import re
from pathlib import Path

from core.config import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from domain.exceptions import PasswordPolicyViolationError


class PasswordPolicyService:
    def __init__(self) -> None:
        self._blocklist = self._load_blocklist()

    def validate(self, email: str, password: str) -> None:
        normalized_email = email.strip().lower()
        local_part = (
            normalized_email.split("@")[0]
            if "@" in normalized_email
            else normalized_email
        )

        if len(password) < PASSWORD_MIN_LENGTH:
            raise PasswordPolicyViolationError(
                f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
            )

        if len(password) > PASSWORD_MAX_LENGTH:
            raise PasswordPolicyViolationError(
                f"Password must be at most {PASSWORD_MAX_LENGTH} characters long"
            )

        if not re.search(r"[A-Za-z]", password):
            raise PasswordPolicyViolationError(
                "Password must contain at least one English letter"
            )

        if not re.search(r"\d", password):
            raise PasswordPolicyViolationError(
                "Password must contain at least one digit"
            )

        lowered_password = password.lower()

        if normalized_email and normalized_email in lowered_password:
            raise PasswordPolicyViolationError(
                "Password must not contain the email address"
            )

        if local_part and len(local_part) >= 3 and local_part in lowered_password:
            raise PasswordPolicyViolationError(
                "Password must not contain the email username"
            )

        if lowered_password in self._blocklist:
            raise PasswordPolicyViolationError("Password is too common or insecure")

    def _load_blocklist(self) -> set[str]:
        blocklist_path = (
            Path(__file__).resolve().parents[2] / "core" / "password_blocklist.txt"
        )

        if not blocklist_path.exists():
            return set()

        with blocklist_path.open("r", encoding="utf-8") as file:
            return {
                line.strip().lower()
                for line in file
                if line.strip() and not line.strip().startswith("#")
            }
