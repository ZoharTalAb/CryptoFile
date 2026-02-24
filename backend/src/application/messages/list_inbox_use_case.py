from typing import List

from domain.entities.message import Message
from domain.interfaces.message_repository import MessageRepository


class ListInboxUseCase:

    def __init__(self, repository: MessageRepository):
        self._repository = repository

    def execute(self, recipient_id: int) -> List[Message]:
        return self._repository.list_for_recipient(recipient_id)
