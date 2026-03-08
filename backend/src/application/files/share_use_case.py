from domain.exceptions import (
    UserNotFoundError,
    FileNotFoundError,
    FileOwnershipError,
    FileAlreadySharedError,
    SelfShareNotAllowedError,
)
from domain.interfaces.user_repository import UserRepository
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.db.repositories.file_share_repository_impl import (
    FileShareRepositoryImpl,
)


class ShareFileUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        file_repo: FileRepositoryImpl,
        file_share_repo: FileShareRepositoryImpl,
    ):
        self._user_repo = user_repo
        self._file_repo = file_repo
        self._file_share_repo = file_share_repo

    async def execute(self, owner_id: int, file_id: int, target_email: str):
        target_user = self._user_repo.get_by_email(target_email)
        if not target_user:
            raise UserNotFoundError(f"User with email {target_email} not found")

        if target_user.id == owner_id:
            raise SelfShareNotAllowedError("You cannot share a file with yourself!")

        file_obj = self._file_repo.get_by_id(file_id)
        if not file_obj:
            raise FileNotFoundError(f"File with id {file_id} not found")

        if file_obj.owner_id != owner_id:
            raise FileOwnershipError("You can only share files that you own")

        if self._file_share_repo.share_exists(
            file_id=file_id, target_user_id=target_user.id
        ):
            raise FileAlreadySharedError("File is already shared with this user")

        share = self._file_share_repo.create_share(
            file_id=file_id,
            owner_id=owner_id,
            target_user_id=target_user.id,
        )

        return {
            "share_id": share.id,
            "file_id": file_id,
            "shared_with_email": target_user.email,
            "status": "access_granted",
            "created_at": share.created_at,
        }
