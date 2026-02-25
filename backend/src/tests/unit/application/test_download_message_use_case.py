from uuid import uuid4
from datetime import datetime, timezone

import pytest

from domain.entities.message import Message
from domain.enums.message_status import MessageStatus
from domain.enums.stego_type import StegoType
from domain.interfaces.message_repository import MessageRepository
from domain.exceptions import DomainError
from application.messages.download_message_use_case import DownloadMessageUseCase


class FakeMessageRepository(MessageRepository):

    def __init__(self, message: Message | None):
        self._message = message
        self.updated = False

    def save(self, message):
        return message

    def get_by_id(self, message_id):
        return self._message

    def list_for_recipient(self, recipient_id):
        return []

    def update(self, message):
        self.updated = True
        return message


def create_message():
    return Message(
        id=uuid4(),
        sender_id=1,
        recipient_id=2,
        file_path="file.bin",
        file_hash="hash",
        stego_type=StegoType.AUDIO,
        key_version=1,
        status=MessageStatus.SENT,
        created_at=datetime.now(timezone.utc),
    )


def test_download_marks_delivered():
    message = create_message()
    repo = FakeMessageRepository(message)
    use_case = DownloadMessageUseCase(repo)

    result = use_case.execute(message.id, current_user_id=2)

    assert result.status == MessageStatus.DELIVERED
    assert repo.updated is True


def test_download_wrong_user():
    message = create_message()
    repo = FakeMessageRepository(message)
    use_case = DownloadMessageUseCase(repo)

    with pytest.raises(DomainError):
        use_case.execute(message.id, current_user_id=99)


def test_download_not_found():
    repo = FakeMessageRepository(None)
    use_case = DownloadMessageUseCase(repo)

    with pytest.raises(DomainError):
        use_case.execute(uuid4(), current_user_id=2)
