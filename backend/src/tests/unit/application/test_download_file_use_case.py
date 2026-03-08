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
from application.files.download_file_use_case import DownloadFileUseCase


def clear_tables(session):
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


def test_owner_can_download_file():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")

        db_file = file_repo.create_file(filename="secret.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/v1.png", version_num=1
        )

        use_case = DownloadFileUseCase(file_repo)

        result = asyncio.run(use_case.execute(file_id=db_file.id, user_id=owner.id))

        assert result["file"].id == db_file.id
        assert result["version"].file_path == "/tmp/v1.png"
    finally:
        session.close()


def test_shared_recipient_can_download_file():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        file_share_repo = FileShareRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        db_file = file_repo.create_file(filename="shared.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/shared.png", version_num=1
        )

        file_share_repo.create_share(
            file_id=db_file.id,
            owner_id=owner.id,
            target_user_id=recipient.id,
        )

        use_case = DownloadFileUseCase(file_repo)

        result = asyncio.run(use_case.execute(file_id=db_file.id, user_id=recipient.id))

        assert result["file"].id == db_file.id
        assert result["version"].file_path == "/tmp/shared.png"
    finally:
        session.close()


def test_stranger_cannot_download_file():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        stranger = create_user(user_service, "stranger@example.com")

        db_file = file_repo.create_file(filename="secret.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=db_file.id, file_path="/tmp/secret.png", version_num=1
        )

        use_case = DownloadFileUseCase(file_repo)

        with pytest.raises(Exception, match="You do not have access to this file"):
            asyncio.run(use_case.execute(file_id=db_file.id, user_id=stranger.id))
    finally:
        session.close()


def test_download_missing_file_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        user_service = UserService(user_repo)
        user = create_user(user_service, "user@example.com")

        file_repo = FileRepositoryImpl(session)
        use_case = DownloadFileUseCase(file_repo)

        with pytest.raises(Exception, match="File not found"):
            asyncio.run(use_case.execute(file_id=9999, user_id=user.id))
    finally:
        session.close()


def test_download_without_version_fails():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        db_file = file_repo.create_file(filename="noversion.png", owner_id=owner.id)

        use_case = DownloadFileUseCase(file_repo)

        with pytest.raises(Exception, match="No file version found"):
            asyncio.run(use_case.execute(file_id=db_file.id, user_id=owner.id))
    finally:
        session.close()
