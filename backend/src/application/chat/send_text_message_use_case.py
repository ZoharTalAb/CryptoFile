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


class SendTextMessageUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryImpl,
        chat_message_repo: ChatMessageRepositoryImpl,
    ):
        self._conversation_repo = conversation_repo
        self._chat_message_repo = chat_message_repo

    async def execute(
        self,
        conversation_id: int,
        sender_id: int,
        text: str,
    ):
        conversation = self._conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundError("Conversation not found")

        if not self._conversation_repo.user_is_participant(
            conversation_id=conversation_id,
            user_id=sender_id,
        ):
            raise ConversationAccessDeniedError(
                "You do not have access to this conversation"
            )

        message = self._chat_message_repo.create_text_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            text_content=text,
        )

        return {
            "conversation": conversation,
            "message": message,
        }
