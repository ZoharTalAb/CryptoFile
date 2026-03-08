from sqlalchemy.orm import Session
from sqlalchemy import select
from infrastructure.db.models import FileShareModel


class FileShareRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def create_share(
        self, file_id: int, owner_id: int, target_user_id: int
    ) -> FileShareModel:
        db_share = FileShareModel(
            file_id=file_id,
            owner_id=owner_id,
            target_user_id=target_user_id,
        )
        self.session.add(db_share)
        self.session.commit()
        self.session.refresh(db_share)
        return db_share

    def share_exists(self, file_id: int, target_user_id: int) -> bool:
        stmt = select(FileShareModel).where(
            FileShareModel.file_id == file_id,
            FileShareModel.target_user_id == target_user_id,
        )
        share = self.session.execute(stmt).scalar_one_or_none()
        return share is not None

    def is_shared_with(self, file_id: int, user_id: int) -> bool:
        stmt = select(FileShareModel).where(
            FileShareModel.file_id == file_id,
            FileShareModel.target_user_id == user_id,
        )
        share = self.session.execute(stmt).scalar_one_or_none()
        return share is not None
