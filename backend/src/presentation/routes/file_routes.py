from mimetypes import guess_type
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from application.files.download_file_use_case import DownloadFileUseCase
from application.files.list_files_use_case import ListFilesUseCase
from domain.exceptions import (
    FileAccessDeniedError,
    FileNotFoundError,
    FileVersionNotFoundError,
)
from domain.interfaces.storage_interface import StorageInterface
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from presentation.dependencies import get_current_user, get_db, get_storage
from presentation.schemas.file_schema import FileItemResponse, FilesListResponse

router = APIRouter(prefix="/files", tags=["Files Management"])


INLINE_PREVIEW_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "bmp",
    "mp3",
    "wav",
    "ogg",
    "m4a",
    "aac",
    "mp4",
    "webm",
}


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _media_type_for_filename(filename: str) -> str:
    media_type, _ = guess_type(filename)

    if media_type:
        return media_type

    extension = _get_extension(filename)

    fallback_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "m4a": "audio/mp4",
        "aac": "audio/aac",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mov": "video/quicktime",
    }

    return fallback_types.get(extension, "application/octet-stream")


def _content_disposition_for_filename(filename: str, force_download: bool) -> str:
    extension = _get_extension(filename)

    disposition_type = (
        "attachment"
        if force_download or extension not in INLINE_PREVIEW_EXTENSIONS
        else "inline"
    )

    quoted_filename = quote(filename)

    return (
        f'{disposition_type}; filename="{filename}"; '
        f"filename*=UTF-8''{quoted_filename}"
    )


@router.get("/", response_model=FilesListResponse)
async def list_my_files(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    file_repo = FileRepositoryImpl(db)
    use_case = ListFilesUseCase(file_repo)

    result = await use_case.execute(user_id=current_user.id)

    owned_files = [
        FileItemResponse(
            id=file.id,
            filename=file.filename,
            created_at=file.created_at,
            is_owner=True,
            download_url=f"/files/{file.id}/download",
        )
        for file in result["owned_files"]
    ]

    shared_files = [
        FileItemResponse(
            id=file.id,
            filename=file.filename,
            created_at=file.created_at,
            is_owner=False,
            download_url=f"/files/{file.id}/download",
        )
        for file in result["shared_with_me"]
    ]

    return FilesListResponse(
        owned_files=owned_files,
        shared_with_me=shared_files,
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    download: bool = Query(
        default=False,
        description="When true, force browser download instead of inline preview.",
    ),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    storage: StorageInterface = Depends(get_storage),
):
    file_repo = FileRepositoryImpl(db)
    use_case = DownloadFileUseCase(file_repo)

    try:
        result = await use_case.execute(
            file_id=file_id,
            user_id=current_user.id,
        )

        file_obj = result["file"]
        version = result["version"]

        file_bytes = storage.get_file(version.file_path)
        media_type = _media_type_for_filename(file_obj.filename)

        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": _content_disposition_for_filename(
                    file_obj.filename,
                    force_download=download,
                ),
                "X-Content-Type-Options": "nosniff",
            },
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileVersionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}",
        )
