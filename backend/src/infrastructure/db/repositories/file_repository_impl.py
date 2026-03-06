from sqlalchemy.orm import Session
from infrastructure.db.models import FileModel, FileVersionModel

class FileRepositoryImpl:
    def __init__(self, session: Session):
        self.session = session

    def create_file(self, filename: str, owner_id: int) -> FileModel:
        db_file = FileModel(filename=filename, owner_id=owner_id)
        self.session.add(db_file)
        self.session.commit()
        self.session.refresh(db_file)
        return db_file

    def add_version(self, file_id: int, file_path: str, version_num: int):
        db_version = FileVersionModel(file_id=file_id, file_path=file_path, version_number=version_num)
        self.session.add(db_version)
        self.session.commit()