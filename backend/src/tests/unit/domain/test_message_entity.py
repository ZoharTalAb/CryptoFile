from datetime import datetime, timezone
from uuid import uuid4

import pytest

from domain.entities.message import Message
from domain.enums.message_status import MessageStatus
from domain.exceptions import DomainError


def create_message(status: MessageStatus = MessageStatus.SENT) -> Message:
    now = datetime.now(timezone.utc)
    return Message(
        id=uuid4(),
        sender_id=1,
        recipient_id=2,
        file_path="test.bin",
        file_hash="abc123",
        stego_type="audio",
        key_version=1,
        status=status,
        created_at=now,
    )


# ------------------------
# SENT → DELIVERED
# ------------------------


def test_mark_delivered_from_sent():
    message = create_message(MessageStatus.SENT)
    now = datetime.now(timezone.utc)

    message.mark_delivered(now)

    assert message.status == MessageStatus.DELIVERED
    assert message.delivered_at == now


# ------------------------
# SENT → READ (auto-delivered)
# ------------------------


def test_mark_read_from_sent():
    message = create_message(MessageStatus.SENT)
    now = datetime.now(timezone.utc)

    message.mark_read(now)

    assert message.status == MessageStatus.READ
    assert message.delivered_at == now
    assert message.read_at == now


# ------------------------
# DELIVERED → READ
# ------------------------


def test_mark_read_from_delivered():
    message = create_message(MessageStatus.DELIVERED)
    now = datetime.now(timezone.utc)

    message.mark_read(now)

    assert message.status == MessageStatus.READ
    assert message.read_at == now


# ------------------------
# Idempotency
# ------------------------


def test_mark_delivered_idempotent():
    message = create_message(MessageStatus.DELIVERED)
    now = datetime.now(timezone.utc)

    message.mark_delivered(now)

    assert message.status == MessageStatus.DELIVERED


def test_mark_read_idempotent():
    message = create_message(MessageStatus.READ)
    now = datetime.now(timezone.utc)

    message.mark_read(now)

    assert message.status == MessageStatus.READ


# ------------------------
# Invalid transition
# ------------------------


def test_invalid_transition():
    message = create_message(MessageStatus.READ)

    with pytest.raises(DomainError):
        message.mark_delivered(datetime.now(timezone.utc))
