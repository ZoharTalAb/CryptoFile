from sqlalchemy.orm import Session
from sqlalchemy import select
from infrastructure.db.models import FileModel, FileVersionModel, FileShareModel, UserModel


class FileRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def create_file(self, filename: str, owner_id: int) -> FileModel:
        db_file = FileModel(filename=filename, owner_id=owner_id)
        self.session.add(db_file)
        self.session.commit()
        self.session.refresh(db_file)
        return db_file

    def add_version(
        self, file_id: int, file_path: str, version_num: int
    ) -> FileVersionModel:
        db_version = FileVersionModel(
            file_id=file_id,
            file_path=file_path,
            version_number=version_num,
        )
        self.session.add(db_version)
        self.session.commit()
        self.session.refresh(db_version)
        return db_version

    def get_by_id(self, file_id: int) -> FileModel | None:
        stmt = select(FileModel).where(FileModel.id == file_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_owned_files(self, owner_id: int) -> list[FileModel]:
        stmt = (
            select(FileModel)
            .where(FileModel.owner_id == owner_id)
            .order_by(FileModel.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def list_shared_files(self, user_id: int) -> list[FileModel]:
        stmt = (
            select(FileModel)
            .join(FileShareModel, FileShareModel.file_id == FileModel.id)
            .where(FileShareModel.target_user_id == user_id)
            .order_by(FileModel.created_at.desc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_share_owner_email(self, file_id: int, target_user_id: int) -> str | None:
        stmt = (
            select(UserModel.email)
            .join(FileShareModel, FileShareModel.owner_id == UserModel.id)
            .where(
                FileShareModel.file_id == file_id,
                FileShareModel.target_user_id == target_user_id,
            )
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_latest_version(self, file_id: int) -> FileVersionModel | None:
        stmt = (
            select(FileVersionModel)
            .where(FileVersionModel.file_id == file_id)
            .order_by(FileVersionModel.version_number.desc())
        )
        return self.session.execute(stmt).scalars().first()

    def user_can_access(self, file_id: int, user_id: int) -> bool:
        file_obj = self.get_by_id(file_id)
        if not file_obj:
            return False

        if file_obj.owner_id == user_id:
            return True

        stmt = select(FileShareModel).where(
            FileShareModel.file_id == file_id,
            FileShareModel.target_user_id == user_id,
        )
        share = self.session.execute(stmt).scalar_one_or_none()
        return share is not None
