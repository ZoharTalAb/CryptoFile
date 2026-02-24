from uuid import uuid4
from datetime import datetime, timezone

from domain.entities.message import Message
from domain.enums.message_status import MessageStatus
from domain.interfaces.message_repository import MessageRepository
from application.messages.list_inbox_use_case import ListInboxUseCase


class FakeMessageRepository(MessageRepository):

    def __init__(self, messages):
        self._messages = messages

    def save(self, message):
        return message

    def get_by_id(self, message_id):
        return None

    def list_for_recipient(self, recipient_id):
        return [m for m in self._messages if m.recipient_id == recipient_id]

    def update(self, message):
        return message


def create_message(recipient_id):
    return Message(
        id=uuid4(),
        sender_id=1,
        recipient_id=recipient_id,
        file_path="file.bin",
        file_hash="hash",
        stego_type="audio",
        key_version=1,
        status=MessageStatus.SENT,
        created_at=datetime.now(timezone.utc),
    )


def test_list_inbox_returns_only_recipient_messages():
    messages = [
        create_message(2),
        create_message(3),
        create_message(2),
    ]

    repo = FakeMessageRepository(messages)
    use_case = ListInboxUseCase(repo)

    result = use_case.execute(recipient_id=2)

    assert len(result) == 2
    assert all(m.recipient_id == 2 for m in result)
