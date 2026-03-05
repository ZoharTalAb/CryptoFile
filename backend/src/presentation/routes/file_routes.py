from fastapi import APIRouter, Depends
from presentation.dependencies import get_current_user

# הגדרת ה-router ש-main.py מחפש
router = APIRouter(prefix="/files", tags=["Files Management"])

@router.get("/")
async def list_my_files(current_user = Depends(get_current_user)):
    return {
        "user": current_user.email,
        "files": [],
        "message": "Files list will be populated once Repositories are ready"
    }