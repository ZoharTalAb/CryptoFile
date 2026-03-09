from domain.exceptions import (
    ConversationNotFoundError,
    ConversationAccessDeniedError,
)
from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from infrastructure.db.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)


class MarkConversationReadUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryImpl,
        chat_message_repo: ChatMessageRepositoryImpl,
    ):
        self._conversation_repo = conversation_repo
        self._chat_message_repo = chat_message_repo

    async def execute(self, conversation_id: int, current_user_id: int):
        conversation = self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        if not self._conversation_repo.user_is_participant(
            conversation_id=conversation_id,
            user_id=current_user_id,
        ):
            raise ConversationAccessDeniedError(
                "You do not have access to this conversation"
            )

        updated_count = self._chat_message_repo.mark_conversation_messages_as_read(
            conversation_id=conversation_id,
            reader_user_id=current_user_id,
        )

        return {
            "conversation": conversation,
            "updated_count": updated_count,
        }
