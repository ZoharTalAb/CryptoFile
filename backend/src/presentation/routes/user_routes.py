from fastapi import APIRouter, Depends

from presentation.dependencies import get_current_user
from presentation.schemas.user_schema import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user=Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
