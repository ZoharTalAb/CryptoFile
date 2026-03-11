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
from application.chat.list_messages_use_case import ListMessagesUseCase
from domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
)
from tests.conftest import TEST_PASSWORD


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


def create_user(service, email, password=TEST_PASSWORD):
    return service.register(email=email, password=password)


def test_list_messages_returns_conversation_messages_in_order():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        user_a = create_user(user_service, "a@example.com")
        user_b = create_user(user_service, "b@example.com")

        conversation = conversation_repo.create_conversation_with_participants(
            user_a_id=user_a.id,
            user_b_id=user_b.id,
        )

        msg1 = chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=user_a.id,
            text_content="first",
        )
        msg2 = chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=user_b.id,
            text_content="second",
        )

        use_case = ListMessagesUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        result = asyncio.run(
            use_case.execute(
                conversation_id=conversation.id,
                current_user_id=user_a.id,
            )
        )

        assert result["conversation"].id == conversation.id
        assert len(result["messages"]) == 2
        assert result["messages"][0].id == msg1.id
        assert result["messages"][0].text_content == "first"
        assert result["messages"][1].id == msg2.id
        assert result["messages"][1].text_content == "second"
    finally:
        session.close()


def test_list_messages_conversation_not_found():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        user = create_user(user_service, "user@example.com")

        use_case = ListMessagesUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        with pytest.raises(ConversationNotFoundError):
            asyncio.run(
                use_case.execute(
                    conversation_id=9999,
                    current_user_id=user.id,
                )
            )
    finally:
        session.close()


def test_list_messages_access_denied_for_non_participant():
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

        use_case = ListMessagesUseCase(
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
