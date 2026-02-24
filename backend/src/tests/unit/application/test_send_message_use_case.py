from uuid import uuid4
from typing import List

from domain.entities.message import Message
from domain.interfaces.message_repository import MessageRepository
from domain.enums.message_status import MessageStatus
from application.messages.send_message_use_case import SendMessageUseCase


class FakeMessageRepository(MessageRepository):

    def __init__(self):
        self.saved_messages: List[Message] = []

    def save(self, message: Message) -> Message:
        self.saved_messages.append(message)
        return message

    def get_by_id(self, message_id):
        return None

    def list_for_recipient(self, recipient_id):
        return []

    def update(self, message: Message) -> Message:
        return message


def test_send_message_creates_and_saves_message():
    repo = FakeMessageRepository()
    use_case = SendMessageUseCase(repo)

    message = use_case.execute(
        sender_id=1,
        recipient_id=2,
        file_path="file.bin",
        file_hash="hash123",
        stego_type="audio",
        key_version=1,
    )

    assert message.sender_id == 1
    assert message.recipient_id == 2
    assert message.status == MessageStatus.SENT
    assert message.delivered_at is None
    assert message.read_at is None
    assert len(repo.saved_messages) == 1
