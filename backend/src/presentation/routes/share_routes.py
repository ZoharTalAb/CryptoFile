from fastapi import APIRouter, Depends, HTTPException, status

from presentation.dependencies import get_current_user, get_db
from presentation.schemas.sharing_schemas import ShareRequest, ShareResponse
from application.files.share_use_case import ShareFileUseCase
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.file_repository_impl import FileRepositoryImpl
from infrastructure.db.repositories.file_share_repository_impl import (
    FileShareRepositoryImpl,
)
from domain.exceptions import (
    UserNotFoundError,
    FileNotFoundError,
    FileOwnershipError,
    FileAlreadySharedError,
    SelfShareNotAllowedError,
)

router = APIRouter(prefix="/share", tags=["Sharing"])


@router.post("/", response_model=ShareResponse, status_code=201)
async def share_file(
    request: ShareRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    user_repo = UserRepositoryImpl(db)
    file_repo = FileRepositoryImpl(db)
    file_share_repo = FileShareRepositoryImpl(db)

    use_case = ShareFileUseCase(
        user_repo=user_repo,
        file_repo=file_repo,
        file_share_repo=file_share_repo,
    )

    try:
        result = await use_case.execute(
            owner_id=current_user.id,
            file_id=request.file_id,
            target_email=request.target_email,
        )

        return ShareResponse(
            share_id=result["share_id"],
            file_id=result["file_id"],
            shared_with_email=result["shared_with_email"],
            status=result["status"],
            created_at=result["created_at"],
        )

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SelfShareNotAllowedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileOwnershipError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except FileAlreadySharedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
