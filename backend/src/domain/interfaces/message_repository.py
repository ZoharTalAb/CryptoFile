from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities.message import Message


class MessageRepository(ABC):

    @abstractmethod
    def save(self, message: Message) -> Message:
        pass

    @abstractmethod
    def get_by_id(self, message_id: UUID) -> Message | None:
        pass

    @abstractmethod
    def list_for_recipient(self, recipient_id: int) -> List[Message]:
        pass

    @abstractmethod
    def update(self, message: Message) -> Message:
        pass
