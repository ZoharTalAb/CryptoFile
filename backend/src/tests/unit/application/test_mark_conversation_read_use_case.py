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
from application.chat.mark_conversation_read_use_case import (
    MarkConversationReadUseCase,
)
from domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
)
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


def test_mark_conversation_read_updates_only_incoming_messages():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")
        other_user = create_user(user_service, "other@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=current_user.id,
            user_b_id=other_user.id,
        )

        incoming_1 = chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=other_user.id,
            text_content="incoming one",
        )
        incoming_2 = chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=other_user.id,
            text_content="incoming two",
        )
        own_message = chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=current_user.id,
            text_content="my own message",
        )

        use_case = MarkConversationReadUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        result = asyncio.run(
            use_case.execute(
                conversation_id=conversation.id,
                current_user_id=current_user.id,
            )
        )

        refreshed_incoming_1 = chat_message_repo.get_by_id(incoming_1.id)
        refreshed_incoming_2 = chat_message_repo.get_by_id(incoming_2.id)
        refreshed_own_message = chat_message_repo.get_by_id(own_message.id)

        assert result["conversation"].id == conversation.id
        assert result["updated_count"] == 2

        assert refreshed_incoming_1.status == ChatMessageStatus.READ.value
        assert refreshed_incoming_1.read_at is not None

        assert refreshed_incoming_2.status == ChatMessageStatus.READ.value
        assert refreshed_incoming_2.read_at is not None

        assert refreshed_own_message.status == ChatMessageStatus.SENT.value
        assert refreshed_own_message.read_at is None
    finally:
        session.close()


def test_mark_conversation_read_conversation_not_found():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")

        use_case = MarkConversationReadUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        with pytest.raises(ConversationNotFoundError):
            asyncio.run(
                use_case.execute(
                    conversation_id=9999,
                    current_user_id=current_user.id,
                )
            )
    finally:
        session.close()


def test_mark_conversation_read_access_denied_for_non_participant():
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

        chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=user_a.id,
            text_content="hello",
        )

        use_case = MarkConversationReadUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        with pytest.raises(ConversationAccessDeniedError):
            asyncio.run(
                use_case.execute(
                    conversation_id=conversation.id,
                    current_user_id=outsider.id,
                )
            )
    finally:
        session.close()
