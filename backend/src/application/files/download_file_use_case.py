from domain.exceptions import (
    FileNotFoundError,
    FileAccessDeniedError,
    FileVersionNotFoundError,
)
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl


class DownloadFileUseCase:
    def __init__(self, file_repo: FileRepositoryImpl):
        self._file_repo = file_repo

    async def execute(self, file_id: int, user_id: int):
        file_obj = self._file_repo.get_by_id(file_id)
        if not file_obj:
            raise FileNotFoundError("File not found")

        if not self._file_repo.user_can_access(file_id=file_id, user_id=user_id):
            raise FileAccessDeniedError("You do not have access to this file")

        latest_version = self._file_repo.get_latest_version(file_id)
        if not latest_version:
            raise FileVersionNotFoundError("No file version found")

        return {
            "file": file_obj,
            "version": latest_version,
        }
