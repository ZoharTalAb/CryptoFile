from fastapi import APIRouter, Depends

from presentation.dependencies import get_current_user
from domain.entities.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }
