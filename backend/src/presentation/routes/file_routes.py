from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from presentation.dependencies import get_current_user, get_db
from presentation.schemas.file_schema import FilesListResponse, FileItemResponse
from application.files.list_files_use_case import ListFilesUseCase
from application.files.download_file_use_case import DownloadFileUseCase
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from domain.exceptions import (
    FileNotFoundError,
    FileVersionNotFoundError,
    FileAccessDeniedError,
)

router = APIRouter(prefix="/files", tags=["Files Management"])


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
    current_user=Depends(get_current_user),
    db=Depends(get_db),
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

        return FileResponse(
            path=version.file_path,
            filename=file_obj.filename,
            media_type="application/octet-stream",
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileVersionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
