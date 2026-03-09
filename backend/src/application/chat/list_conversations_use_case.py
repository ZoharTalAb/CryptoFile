from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from infrastructure.db.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)


class ListConversationsUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryImpl,
        chat_message_repo: ChatMessageRepositoryImpl,
    ):
        self._conversation_repo = conversation_repo
        self._chat_message_repo = chat_message_repo

    async def execute(self, current_user_id: int):
        conversations = self._conversation_repo.list_user_conversations(current_user_id)

        results = []

        for conversation in conversations:
            other_participant = self._conversation_repo.get_other_participant(
                conversation_id=conversation.id,
                current_user_id=current_user_id,
            )
            last_message = self._conversation_repo.get_last_message(conversation.id)
            unread_count = self._chat_message_repo.count_unread_messages(
                conversation_id=conversation.id,
                user_id=current_user_id,
            )

            results.append(
                {
                    "conversation": conversation,
                    "other_user": other_participant.user if other_participant else None,
                    "last_message": last_message,
                    "unread_count": unread_count,
                }
            )

        return results
