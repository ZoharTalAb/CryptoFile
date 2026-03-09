from domain.enums.stego_type import StegoType
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
from application.files.create_stego_file_use_case import CreateStegoFileUseCase


class SendStegoFileMessageUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryImpl,
        chat_message_repo: ChatMessageRepositoryImpl,
        create_stego_file_use_case: CreateStegoFileUseCase,
    ):
        self._conversation_repo = conversation_repo
        self._chat_message_repo = chat_message_repo
        self._create_stego_file_use_case = create_stego_file_use_case

    async def execute(
        self,
        conversation_id: int,
        sender_id: int,
        original_filename: str,
        stego_type: StegoType,
        secret_data: str,
        file_bytes: bytes,
        caption: str | None = None,
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

        stego_result = await self._create_stego_file_use_case.execute(
            owner_id=sender_id,
            original_filename=original_filename,
            stego_type=stego_type,
            secret_data=secret_data,
            file_bytes=file_bytes,
        )

        chat_message = self._chat_message_repo.create_stego_file_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            file_id=stego_result["file"].id,
            stego_type=stego_result["stego_type"],
            caption=caption,
        )

        return {
            "conversation": conversation,
            "message": chat_message,
            "file": stego_result["file"],
        }
