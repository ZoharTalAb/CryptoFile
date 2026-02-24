from datetime import datetime, timezone
from uuid import uuid4

from domain.entities.message import Message
from domain.enums.message_status import MessageStatus
from domain.interfaces.message_repository import MessageRepository


class SendMessageUseCase:

    def __init__(self, repository: MessageRepository):
        self._repository = repository

    def execute(
        self,
        sender_id: int,
        recipient_id: int,
        file_path: str,
        file_hash: str,
        stego_type: str,
        key_version: int,
    ) -> Message:

        message = Message(
            id=uuid4(),
            sender_id=sender_id,
            recipient_id=recipient_id,
            file_path=file_path,
            file_hash=file_hash,
            stego_type=stego_type,
            key_version=key_version,
            status=MessageStatus.SENT,
            created_at=datetime.now(timezone.utc),
            delivered_at=None,
            read_at=None,
        )

        return self._repository.save(message)
