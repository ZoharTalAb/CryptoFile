from domain.interfaces.user_repository import UserRepository
from uuid import UUID

class ShareFileUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def execute(self, owner_id: int, file_id: UUID, target_email: str):
        target_user = self._user_repo.get_by_email(target_email)
        if not target_user:
            raise Exception(f"User with email {target_email} not found")

        if target_user.id == owner_id:
            raise Exception("You cannot share a file with yourself!")

        return {
            "file_id": file_id,
            "shared_with_email": target_user.email,
            "status": "access_granted"
        }