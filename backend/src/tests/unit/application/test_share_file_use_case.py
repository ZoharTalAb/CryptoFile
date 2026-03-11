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
)
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.db.repositories.file_share_repository_impl import (
    FileShareRepositoryImpl,
)

from application.users.user_service import UserService
from application.files.share_use_case import ShareFileUseCase
from tests.conftest import TEST_PASSWORD


def clear_tables(session):
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


def test_share_file_success():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        file_share_repo = FileShareRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        db_file = file_repo.create_file(filename="secret.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/secret.png", version_num=1
        )

        use_case = ShareFileUseCase(user_repo, file_repo, file_share_repo)

        result = asyncio.run(
            use_case.execute(
                owner_id=owner.id,
                file_id=db_file.id,
                target_email=recipient.email,
            )
        )

        assert result["file_id"] == db_file.id
        assert result["shared_with_email"] == recipient.email
        assert result["status"] == "access_granted"
        assert "share_id" in result
        assert file_share_repo.is_shared_with(db_file.id, recipient.id) is True
    finally:
        session.close()


def test_share_file_with_yourself_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        file_share_repo = FileShareRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")

        db_file = file_repo.create_file(filename="secret.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/secret.png", version_num=1
        )

        use_case = ShareFileUseCase(user_repo, file_repo, file_share_repo)

        with pytest.raises(Exception, match="You cannot share a file with yourself!"):
            asyncio.run(
                use_case.execute(
                    owner_id=owner.id,
                    file_id=db_file.id,
                    target_email=owner.email,
                )
            )
    finally:
        session.close()


def test_share_file_by_non_owner_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        file_share_repo = FileShareRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        attacker = create_user(user_service, "attacker@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        db_file = file_repo.create_file(filename="secret.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/secret.png", version_num=1
        )

        use_case = ShareFileUseCase(user_repo, file_repo, file_share_repo)

        with pytest.raises(Exception, match="You can only share files that you own"):
            asyncio.run(
                use_case.execute(
                    owner_id=attacker.id,
                    file_id=db_file.id,
                    target_email=recipient.email,
                )
            )
    finally:
        session.close()


def test_duplicate_share_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        file_share_repo = FileShareRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        db_file = file_repo.create_file(filename="secret.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/secret.png", version_num=1
        )

        use_case = ShareFileUseCase(user_repo, file_repo, file_share_repo)

        asyncio.run(
            use_case.execute(
                owner_id=owner.id,
                file_id=db_file.id,
                target_email=recipient.email,
            )
        )

        with pytest.raises(Exception, match="File is already shared with this user"):
            asyncio.run(
                use_case.execute(
                    owner_id=owner.id,
                    file_id=db_file.id,
                    target_email=recipient.email,
                )
            )
    finally:
        session.close()
