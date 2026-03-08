from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl


class ListFilesUseCase:
    def __init__(self, file_repo: FileRepositoryImpl):
        self._file_repo = file_repo

    async def execute(self, user_id: int):
        owned_files = self._file_repo.list_owned_files(user_id)
        shared_files = self._file_repo.list_shared_files(user_id)

        return {
            "owned_files": owned_files,
            "shared_with_me": shared_files,
        }
