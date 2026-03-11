from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.password_reset_token import PasswordResetToken


class PasswordResetRepository(ABC):

    @abstractmethod
    def save(self, token: PasswordResetToken) -> PasswordResetToken:
        pass

    @abstractmethod
    def get_active_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        pass

    @abstractmethod
    def get_active_by_user_id(self, user_id: int) -> PasswordResetToken | None:
        pass

    @abstractmethod
    def count_recent_by_user_id(self, user_id: int, since: datetime) -> int:
        pass

    @abstractmethod
    def mark_used(self, token_id: int, used_at: datetime) -> None:
        pass
