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

from application.users.user_service import UserService
from application.chat.create_or_get_conversation_use_case import (
    CreateOrGetConversationUseCase,
)
from domain.exceptions import (
    UserNotFoundError,
    InvalidConversationParticipantError,
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


def test_create_new_conversation_success():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")
        target_user = create_user(user_service, "target@example.com")

        use_case = CreateOrGetConversationUseCase(
            user_repo=user_repo,
            conversation_repo=conversation_repo,
        )

        result = asyncio.run(
            use_case.execute(
                current_user_id=current_user.id,
                target_email=target_user.email,
            )
        )

        conversation = result["conversation"]

        assert result["created"] is True
        assert result["other_user"].id == target_user.id
        assert conversation.id is not None
        assert (
            conversation_repo.user_is_participant(conversation.id, current_user.id)
            is True
        )
        assert (
            conversation_repo.user_is_participant(conversation.id, target_user.id)
            is True
        )
    finally:
        session.close()


def test_return_existing_conversation_instead_of_creating_new_one():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")
        target_user = create_user(user_service, "target@example.com")

        existing = conversation_repo.create_conversation_with_participants(
            user_a_id=current_user.id,
            user_b_id=target_user.id,
        )

        use_case = CreateOrGetConversationUseCase(
            user_repo=user_repo,
            conversation_repo=conversation_repo,
        )

        result = asyncio.run(
            use_case.execute(
                current_user_id=current_user.id,
                target_email=target_user.email,
            )
        )

        assert result["created"] is False
        assert result["conversation"].id == existing.id
    finally:
        session.close()


def test_create_conversation_target_user_not_found():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")

        use_case = CreateOrGetConversationUseCase(
            user_repo=user_repo,
            conversation_repo=conversation_repo,
        )

        with pytest.raises(UserNotFoundError):
            asyncio.run(
                use_case.execute(
                    current_user_id=current_user.id,
                    target_email="missing@example.com",
                )
            )
    finally:
        session.close()


def test_create_conversation_with_yourself_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        conversation_repo = ConversationRepositoryImpl(session)
        user_service = UserService(user_repo)

        current_user = create_user(user_service, "current@example.com")

        use_case = CreateOrGetConversationUseCase(
            user_repo=user_repo,
            conversation_repo=conversation_repo,
        )

        with pytest.raises(InvalidConversationParticipantError):
            asyncio.run(
                use_case.execute(
                    current_user_id=current_user.id,
                    target_email=current_user.email,
                )
            )
    finally:
        session.close()
