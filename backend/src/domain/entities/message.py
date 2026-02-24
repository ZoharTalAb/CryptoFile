from datetime import datetime
from typing import Optional
from uuid import UUID

from domain.enums.message_status import MessageStatus
from domain.exceptions import DomainError


class Message:
    def __init__(
        self,
        id: UUID,
        sender_id: int,
        recipient_id: int,
        file_path: str,
        file_hash: str,
        stego_type: str,
        key_version: int,
        status: MessageStatus,
        created_at: datetime,
        delivered_at: Optional[datetime] = None,
        read_at: Optional[datetime] = None,
    ):
        self.id = id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.file_path = file_path
        self.file_hash = file_hash
        self.stego_type = stego_type
        self.key_version = key_version
        self.status = status
        self.created_at = created_at
        self.delivered_at = delivered_at
        self.read_at = read_at

    # -----------------------
    # Domain Logic
    # -----------------------

    def mark_delivered(self, now: datetime) -> None:
        if self.status == MessageStatus.READ:
            raise DomainError("Cannot mark READ message as DELIVERED")

        if self.status == MessageStatus.DELIVERED:
            return  # idempotent

        if self.status != MessageStatus.SENT:
            raise DomainError("Invalid state transition to DELIVERED")

        self.status = MessageStatus.DELIVERED
        self.delivered_at = now

    def mark_read(self, now: datetime) -> None:
        if self.status == MessageStatus.READ:
            return  # idempotent

        # If message was not delivered yet, mark delivered first
        if self.status == MessageStatus.SENT:
            self.mark_delivered(now)

        if self.status != MessageStatus.DELIVERED:
            raise DomainError("Invalid state transition to READ")

        self.status = MessageStatus.READ
        self.read_at = now
