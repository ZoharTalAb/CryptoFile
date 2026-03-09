import asyncio
import pytest
from sqlalchemy import text

from infrastructure.db.session import SessionLocal
from infrastructure.db.models import (
    UserModel,
    FileModel,
    FileVersionModel,
    FileShareModel,
    FileKeyModel,
    MessageModel,
    ConversationModel,
    ConversationParticipantModel,
    ChatMessageModel,
)
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from infrastructure.db.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)

from application.users.user_service import UserService
from application.chat.send_text_message_use_case import SendTextMessageUseCase
from domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
)
from domain.enums.chat_message_type import ChatMessageType
from domain.enums.chat_message_status import ChatMessageStatus


def clear_tables(session):
    session.query(ChatMessageModel).delete()
    session.query(ConversationParticipantModel).delete()
    session.query(ConversationModel).delete()
    session.query(FileShareModel).delete()
    session.query(FileVersionModel).delete()
    session.query(FileKeyModel).delete()
    session.query(FileModel).delete()
    session.query(MessageModel).delete()
    session.execute(text("DELETE FROM trusted_relations"))
    session.query(UserModel).delete()
    session.commit()


def create_user(service, email, password="12345678"):
    return service.register(email=email, password=password)


def test_send_text_message_success():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        sender = create_user(user_service, "sender@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=sender.id,
            user_b_id=recipient.id,
        )

        use_case = SendTextMessageUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        result = asyncio.run(
            use_case.execute(
                conversation_id=conversation.id,
                sender_id=sender.id,
                text="hello there",
            )
        )

        message = result["message"]

        assert result["conversation"].id == conversation.id
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.sender_id == sender.id
        assert message.text_content == "hello there"
        assert message.message_type == ChatMessageType.TEXT.value
        assert message.status == ChatMessageStatus.SENT.value
    finally:
        session.close()


def test_send_text_message_conversation_not_found():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        sender = create_user(user_service, "sender@example.com")

        use_case = SendTextMessageUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        with pytest.raises(ConversationNotFoundError):
            asyncio.run(
                use_case.execute(
                    conversation_id=9999,
                    sender_id=sender.id,
                    text="hello",
                )
            )
    finally:
        session.close()


def test_send_text_message_access_denied_for_non_participant():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        user_a = create_user(user_service, "a@example.com")
        user_b = create_user(user_service, "b@example.com")
        outsider = create_user(user_service, "outsider@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=user_a.id,
            user_b_id=user_b.id,
        )

        use_case = SendTextMessageUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        with pytest.raises(ConversationAccessDeniedError):
            asyncio.run(
                use_case.execute(
                    conversation_id=conversation.id,
                    sender_id=outsider.id,
                    text="i should not send this",
                )
            )
    finally:
        session.close()
