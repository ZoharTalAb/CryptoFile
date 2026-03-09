from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from infrastructure.db.models import ChatMessageModel
from domain.enums.chat_message_type import ChatMessageType
from domain.enums.chat_message_status import ChatMessageStatus


class ChatMessageRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def create_text_message(
        self,
        conversation_id: int,
        sender_id: int,
        text_content: str,
    ) -> ChatMessageModel:
        message = ChatMessageModel(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_type=ChatMessageType.TEXT.value,
            text_content=text_content,
            file_id=None,
            stego_type=None,
            status=ChatMessageStatus.SENT.value,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def create_stego_file_message(
        self,
        conversation_id: int,
        sender_id: int,
        file_id: int,
        stego_type: str,
        caption: str | None = None,
    ) -> ChatMessageModel:
        message = ChatMessageModel(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message_type=ChatMessageType.STEGO_FILE.value,
            text_content=caption,
            file_id=file_id,
            stego_type=stego_type,
            status=ChatMessageStatus.SENT.value,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> ChatMessageModel | None:
        return (
            self.session.query(ChatMessageModel)
            .filter(ChatMessageModel.id == message_id)
            .first()
        )

    def list_conversation_messages(
        self, conversation_id: int
    ) -> list[ChatMessageModel]:
        return (
            self.session.query(ChatMessageModel)
            .filter(ChatMessageModel.conversation_id == conversation_id)
            .order_by(ChatMessageModel.created_at.asc(), ChatMessageModel.id.asc())
            .all()
        )

    def mark_as_delivered(self, message_id: int) -> ChatMessageModel | None:
        message = self.get_by_id(message_id)
        if not message:
            return None

        if message.status == ChatMessageStatus.SENT.value:
            message.status = ChatMessageStatus.DELIVERED.value
            message.delivered_at = datetime.now(timezone.utc)
            self.session.commit()
            self.session.refresh(message)

        return message

    def mark_as_read(self, message_id: int) -> ChatMessageModel | None:
        message = self.get_by_id(message_id)
        if not message:
            return None

        if message.status != ChatMessageStatus.READ.value:
            now = datetime.now(timezone.utc)
            if message.delivered_at is None:
                message.delivered_at = now
            message.status = ChatMessageStatus.READ.value
            message.read_at = now
            self.session.commit()
            self.session.refresh(message)

        return message

    def mark_conversation_messages_as_read(
        self, conversation_id: int, reader_user_id: int
    ) -> int:
        messages = (
            self.session.query(ChatMessageModel)
            .filter(
                ChatMessageModel.conversation_id == conversation_id,
                ChatMessageModel.sender_id != reader_user_id,
                ChatMessageModel.status != ChatMessageStatus.READ.value,
            )
            .all()
        )

        now = datetime.now(timezone.utc)
        updated_count = 0

        for message in messages:
            if message.delivered_at is None:
                message.delivered_at = now
            message.status = ChatMessageStatus.READ.value
            message.read_at = now
            updated_count += 1

        if updated_count > 0:
            self.session.commit()

        return updated_count

    def count_unread_messages(self, conversation_id: int, user_id: int) -> int:
        return (
            self.session.query(func.count(ChatMessageModel.id))
            .filter(
                ChatMessageModel.conversation_id == conversation_id,
                ChatMessageModel.sender_id != user_id,
                ChatMessageModel.status != ChatMessageStatus.READ.value,
            )
            .scalar()
            or 0
        )
