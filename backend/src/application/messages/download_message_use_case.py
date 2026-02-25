from datetime import datetime, timezone
from uuid import UUID

from domain.interfaces.message_repository import MessageRepository
from domain.exceptions import DomainError


class DownloadMessageUseCase:

    def __init__(self, repository: MessageRepository):
        self._repository = repository

    def execute(self, message_id: UUID, current_user_id: int):
        message = self._repository.get_by_id(message_id)

        if not message:
            raise DomainError("Message not found")

        if message.recipient_id != current_user_id:
            raise DomainError("Not allowed to download this message")

        message.mark_delivered(datetime.now(timezone.utc))

        self._repository.update(message)

        return message
