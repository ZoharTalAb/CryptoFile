from abc import ABC, abstractmethod

from domain.entities.password_history_entry import PasswordHistoryEntry


class PasswordHistoryRepository(ABC):

    @abstractmethod
    def list_recent_by_user_id(
        self,
        user_id: int,
        limit: int,
    ) -> list[PasswordHistoryEntry]:
        pass

    @abstractmethod
    def save(self, entry: PasswordHistoryEntry) -> PasswordHistoryEntry:
        pass

    @abstractmethod
    def delete_older_than_latest(
        self,
        user_id: int,
        keep_latest: int,
    ) -> None:
        pass
