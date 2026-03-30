import uuid

from domain.enums.stego_type import StegoType
from domain.exceptions import UnsupportedAudioFormatError
from infrastructure.stego.stego_dispatcher import StegoDispatcher
from infrastructure.storage.local_storage import LocalStorage
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl


class CreateStegoFileUseCase:
    def __init__(
        self,
        file_repo: FileRepositoryImpl,
        storage: LocalStorage,
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
        saved_path = self._storage.save(result_bytes, unique_filename)

        db_file = self._file_repo.create_file(
            filename=unique_filename,
            owner_id=owner_id,
        )

        self._file_repo.add_version(
            file_id=db_file.id,
            file_path=saved_path,
            version_num=1,
        )

        return {
            "file": db_file,
            "saved_path": saved_path,
            "filename": unique_filename,
            "stego_type": (
                stego_type.value if hasattr(stego_type, "value") else str(stego_type)
            ),
        }
