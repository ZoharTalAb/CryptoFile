from fastapi import APIRouter, Depends, HTTPException
from presentation.dependencies import get_current_user, get_db
from presentation.schemas.sharing_schemas import ShareRequest, ShareResponse 
from application.files.share_use_case import ShareFileUseCase
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl

router = APIRouter(prefix="/share", tags=["Sharing"])

@router.post("/", response_model=ShareResponse)
async def share_file(
    request: ShareRequest,
    current_user = Depends(get_current_user), # מוודא שהמשתמש מחובר
    db = Depends(get_db) # מקבל Session של ה-DB
):
    # הזרקת ה-Repository וה-Use Case
    user_repo = UserRepositoryImpl(db) 
    use_case = ShareFileUseCase(user_repo)
    
    try:
        result = await use_case.execute(
            owner_id=current_user.id,
            file_id=request.file_id,
            target_email=request.target_email
        )
    
        return ShareResponse(
            file_id=result["file_id"],
            shared_with_email=result["shared_with_email"],
            status=result["status"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))