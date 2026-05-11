import os
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse

from infrastructure.stego.stego_dispatcher import StegoDispatcher
from infrastructure.storage.local_storage import LocalStorage
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl

from domain.exceptions import (
    CorruptedPayloadError,
    PayloadTooLargeError,
    UnsupportedAudioFormatError,
)
from domain.enums.stego_type import StegoType

from presentation.dependencies import get_current_user, get_db
from presentation.schemas.file_schema import (
    EmbeddedFileResponse,
    ExtractResponse,
    StegoFilesResponse,
)

storage = LocalStorage()
router = APIRouter(prefix="/stego", tags=["Steganography"])
stego_service = StegoDispatcher()


@router.post("/embed", response_model=EmbeddedFileResponse)
async def embed_message(
    stego_type: StegoType = Form(..., description="image, audio, or video"),
    secret_data: str = Form(..., description="The message you want to hide"),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        if stego_type == StegoType.AUDIO and not file.filename.lower().endswith(".wav"):
            raise UnsupportedAudioFormatError(
                "Audio stego currently supports WAV files only"
            )

        file_bytes = await file.read()
        payload = b"TXT" + secret_data.encode("utf-8")
        result_bytes = stego_service.dispatch_embed(stego_type, file_bytes, payload)

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        saved_path = storage.save(result_bytes, unique_filename)

        file_repo = FileRepositoryImpl(db)
        db_file = file_repo.create_file(
            filename=unique_filename,
            owner_id=current_user.id,
        )

        file_repo.add_version(
            file_id=db_file.id,
            file_path=saved_path,
            version_num=1,
        )

        return EmbeddedFileResponse(
            file_id=db_file.id,
            filename=unique_filename,
            original_filename=file.filename,
            stego_type=(
                stego_type.value if hasattr(stego_type, "value") else str(stego_type)
            ),
            download_url=f"/files/{db_file.id}/download",
            created_at=db_file.created_at,
        )

    except PayloadTooLargeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except UnsupportedAudioFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/extract", response_model=ExtractResponse)
async def extract_message(
    stego_type: StegoType = Form(..., description="image, audio, or video"),
    file: UploadFile = File(...),
):
    try:
        file_bytes = await file.read()
        extracted_bytes = stego_service.dispatch_extract(stego_type, file_bytes)

        if len(extracted_bytes) >= 3 and extracted_bytes[:3] == b"TXT":
            message = extracted_bytes[3:].decode("utf-8", errors="replace")
        else:
            message = extracted_bytes.decode("utf-8", errors="replace")

        return ExtractResponse(
            stego_type=stego_type.value,
            extracted_message=message,
        )
    except CorruptedPayloadError:
        raise HTTPException(
            status_code=400, detail="Could not find a valid message in this file."
        )
    except UnsupportedAudioFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get(
    "/files",
    response_model=StegoFilesResponse,
    summary="List raw files in local stego storage (legacy/debug endpoint)",
)
async def list_stego_storage_files():
    try:
        upload_dir = storage.base_path
        if not os.path.exists(upload_dir):
            return StegoFilesResponse(total_files=0, files=[])

        files = os.listdir(upload_dir)
        return StegoFilesResponse(total_files=len(files), files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/download/{filename}",
    summary="Download raw file from local stego storage (legacy/debug endpoint)",
)
async def download_stego_storage_file(filename: str):
    file_path = os.path.join(storage.base_path, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
