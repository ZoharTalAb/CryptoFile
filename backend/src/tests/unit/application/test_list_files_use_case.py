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
)
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.db.repositories.file_share_repository_impl import (
    FileShareRepositoryImpl,
)

from application.users.user_service import UserService
from application.files.list_files_use_case import ListFilesUseCase
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


def test_list_files_returns_owned_and_shared():
    session = SessionLocal()
    try:
        clear_tables(session)

        user_repo = UserRepositoryImpl(session)
        file_repo = FileRepositoryImpl(session)
        file_share_repo = FileShareRepositoryImpl(session)
        user_service = UserService(user_repo)

        owner = create_user(user_service, "owner@example.com")
        recipient = create_user(user_service, "recipient@example.com")

        owned_file = file_repo.create_file(filename="owned.png", owner_id=recipient.id)
        file_repo.add_version(
            file_id=owned_file.id, file_path="/tmp/owned.png", version_num=1
        )

        shared_file = file_repo.create_file(filename="shared.png", owner_id=owner.id)
        file_repo.add_version(
            file_id=shared_file.id, file_path="/tmp/shared.png", version_num=1
        )

        file_share_repo.create_share(
            file_id=shared_file.id,
            owner_id=owner.id,
            target_user_id=recipient.id,
        )

        use_case = ListFilesUseCase(file_repo)

        result = asyncio.run(use_case.execute(user_id=recipient.id))

        owned_ids = [f.id for f in result["owned_files"]]
        shared_ids = [f.id for f in result["shared_with_me"]]

        assert owned_file.id in owned_ids
        assert shared_file.id in shared_ids
    finally:
        session.close()
