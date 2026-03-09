from domain.exceptions import (
    UserNotFoundError,
    InvalidConversationParticipantError,
)
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)


class CreateOrGetConversationUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryImpl,
        conversation_repo: ConversationRepositoryImpl,
    ):
        self._user_repo = user_repo
        self._conversation_repo = conversation_repo

    async def execute(self, current_user_id: int, target_email: str):
        target_user = self._user_repo.get_by_email(target_email)
        if not target_user:
            raise UserNotFoundError(f"User with email {target_email} not found")

        if target_user.id == current_user_id:
            raise InvalidConversationParticipantError(
                "You cannot create a conversation with yourself"
            )

        existing_conversation = (
            self._conversation_repo.get_existing_one_to_one_conversation(
                current_user_id,
                target_user.id,
            )
        )
        if existing_conversation:
            return {
                "conversation": existing_conversation,
                "other_user": target_user,
                "created": False,
            }

        conversation = self._conversation_repo.create_conversation_with_participants(
            user_a_id=current_user_id,
            user_b_id=target_user.id,
        )

        return {
            "conversation": conversation,
            "other_user": target_user,
            "created": True,
        }
