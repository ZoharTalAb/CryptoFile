from uuid import uuid4
from datetime import datetime, timezone

import pytest

from domain.entities.message import Message
from domain.enums.message_status import MessageStatus
from domain.enums.stego_type import StegoType
from domain.interfaces.message_repository import MessageRepository
from domain.exceptions import DomainError
from application.messages.mark_read_use_case import MarkReadUseCase


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


def create_message(status=MessageStatus.SENT):
    return Message(
        id=uuid4(),
        sender_id=1,
        recipient_id=2,
        file_path="file.bin",
        file_hash="hash",
        stego_type=StegoType.AUDIO,
        key_version=1,
        status=status,
        created_at=datetime.now(timezone.utc),
    )


def test_mark_read_from_sent():
    message = create_message(MessageStatus.SENT)
    repo = FakeMessageRepository(message)
    use_case = MarkReadUseCase(repo)

    result = use_case.execute(message.id, current_user_id=2)

    assert result.status == MessageStatus.READ
    assert repo.updated is True


def test_mark_read_from_delivered():
    message = create_message(MessageStatus.DELIVERED)
    repo = FakeMessageRepository(message)
    use_case = MarkReadUseCase(repo)

    result = use_case.execute(message.id, current_user_id=2)

    assert result.status == MessageStatus.READ
    assert repo.updated is True


def test_mark_read_wrong_user():
    message = create_message()
    repo = FakeMessageRepository(message)
    use_case = MarkReadUseCase(repo)

    with pytest.raises(DomainError):
        use_case.execute(message.id, current_user_id=99)


def test_mark_read_not_found():
    repo = FakeMessageRepository(None)
    use_case = MarkReadUseCase(repo)

    with pytest.raises(DomainError):
        use_case.execute(uuid4(), current_user_id=2)
