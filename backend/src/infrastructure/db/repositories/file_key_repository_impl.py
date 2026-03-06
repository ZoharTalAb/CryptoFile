from sqlalchemy.orm import Session
from infrastructure.db.models import FileKeyModel

class FileKeyRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def save_key(self, file_id: int, user_id: int, encrypted_key: bytes) -> FileKeyModel:
        """שומר מפתח מוצפן עבור משתמש ספציפי לקובץ ספציפי"""
        db_key = FileKeyModel(
            file_id=file_id,
            user_id=user_id,
            encrypted_key=encrypted_key
        )
        self.session.add(db_key)
        self.session.commit()
        self.session.refresh(db_key)
        return db_key

    def get_key_for_user(self, file_id: int, user_id: int) -> bytes | None:
        """שולף את המפתח המוצפן של משתמש לקובץ מסוים"""
        result = self.session.query(FileKeyModel).filter(
            FileKeyModel.file_id == file_id,
            FileKeyModel.user_id == user_id
        ).first()
        return result.encrypted_key if result else None