import uuid

from domain.enums.stego_type import StegoType
from domain.exceptions import UnsupportedAudioFormatError
from domain.interfaces.storage_interface import StorageInterface
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.stego.stego_dispatcher import StegoDispatcher


class CreateStegoFileUseCase:
    def __init__(
        self,
        file_repo: FileRepositoryImpl,
        storage: StorageInterface,
        stego_service: StegoDispatcher,
    ):
        self._file_repo = file_repo
        self._storage = storage
        self._stego_service = stego_service

    async def execute(
        self,
        owner_id: int,
        original_filename: str,
        stego_type: StegoType,
        secret_data: str,
        file_bytes: bytes,
    ):
        normalized_name = (original_filename or "").lower()

        if stego_type == StegoType.AUDIO and not normalized_name.endswith(".wav"):
            raise UnsupportedAudioFormatError(
                "Audio stego currently supports WAV files only"
            )

        payload = b"TXT" + secret_data.encode("utf-8")

        result_bytes = self._stego_service.dispatch_embed(
            stego_type,
            file_bytes,
            payload,
        )

        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        file_key = self._storage.save(result_bytes, unique_filename)

        db_file = self._file_repo.create_file(
            filename=unique_filename,
            owner_id=owner_id,
        )

        self._file_repo.add_version(
            file_id=db_file.id,
            file_path=file_key,
            version_num=1,
        )

        return {
            "file": db_file,
            "saved_path": file_key,
            "filename": unique_filename,
            "stego_type": (
                stego_type.value if hasattr(stego_type, "value") else str(stego_type)
            ),
        }
