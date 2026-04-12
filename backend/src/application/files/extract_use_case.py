from domain.exceptions import (
    MessageNotFoundError,
    ConversationAccessDeniedError,
    FileNotFoundError,
    CorruptedPayloadError,
)
from domain.interfaces.storage_interface import StorageInterface
from infrastructure.db.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)
from infrastructure.db.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.stego.stego_dispatcher import StegoDispatcher


class ExtractChatMessageUseCase:
    def __init__(
        self,
        chat_message_repo: ChatMessageRepositoryImpl,
        conversation_repo: ConversationRepositoryImpl,
        file_repo: FileRepositoryImpl,
        stego_service: StegoDispatcher,
        storage: StorageInterface,  # 🔥 חדש
    ):
        self._chat_message_repo = chat_message_repo
        self._conversation_repo = conversation_repo
        self._file_repo = file_repo
        self._stego_service = stego_service
        self._storage = storage

    async def execute(self, message_id: int, current_user_id: int):
        message = self._chat_message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundError("Message not found")

        if not self._conversation_repo.user_is_participant(
            conversation_id=message.conversation_id,
            user_id=current_user_id,
        ):
            raise ConversationAccessDeniedError(
                "You do not have access to this conversation"
            )

        if not message.file_id or not message.stego_type:
            raise FileNotFoundError("This message does not contain a stego file")

        latest_version = self._file_repo.get_latest_version(message.file_id)
        if not latest_version:
            raise FileNotFoundError("File version not found")

        # 🔥 במקום open → R2 / storage
        file_bytes = self._storage.get_file(latest_version.file_path)

        extracted_bytes = self._stego_service.dispatch_extract(
            message.stego_type,
            file_bytes,
        )

        if len(extracted_bytes) < 3:
            raise CorruptedPayloadError("Extracted payload is invalid")

        prefix = extracted_bytes[:3]
        payload = extracted_bytes[3:]

        if prefix == b"TXT":
            extracted_message = payload.decode("utf-8", errors="replace")
        else:
            extracted_message = extracted_bytes.decode("utf-8", errors="replace")

        return {
            "message_id": message.id,
            "file_id": message.file_id,
            "stego_type": message.stego_type,
            "extracted_message": extracted_message,
        }
