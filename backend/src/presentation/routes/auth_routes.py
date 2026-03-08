from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from presentation.dependencies import get_db
from presentation.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    MessageResponse,
)

from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl

from application.users.user_service import UserService
from application.auth.jwt_service import JWTService
from domain.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    repo = UserRepositoryImpl(db)
    service = UserService(repo)

    try:
        service.register(request.email, request.password)
        return MessageResponse(message="User created")
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepositoryImpl(db)
    service = UserService(repo)

    try:
        user = service.login(request.email, request.password)
        token = JWTService.create_token(user.id, user.email)
        return TokenResponse(access_token=token)
    except (InvalidCredentialsError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
