import asyncio
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
from application.chat.list_conversations_use_case import ListConversationsUseCase
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


def test_list_conversations_returns_other_user_last_message_and_unread_count():
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

        chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=other_user.id,
            text_content="hello from other user",
        )

        chat_message_repo.create_text_message(
            conversation_id=conversation.id,
            sender_id=current_user.id,
            text_content="reply from current user",
        )

        use_case = ListConversationsUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        result = asyncio.run(use_case.execute(current_user_id=current_user.id))

        assert len(result) == 1

        item = result[0]
        assert item["conversation"].id == conversation.id
        assert item["other_user"] is not None
        assert item["other_user"].id == other_user.id
        assert item["last_message"] is not None
        assert item["last_message"].text_content == "reply from current user"
        assert item["unread_count"] == 1
    finally:
        session.close()


def test_list_conversations_returns_empty_when_user_has_no_conversations():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        chat_message_repo = ChatMessageRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")

        use_case = ListConversationsUseCase(
            conversation_repo=conversation_repo,
            chat_message_repo=chat_message_repo,
        )

        result = asyncio.run(use_case.execute(current_user_id=current_user.id))

        assert result == []
    finally:
        session.close()
