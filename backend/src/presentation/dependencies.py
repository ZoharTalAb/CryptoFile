from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from infrastructure.db.session import SessionLocal
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from application.users.user_service import UserService
from application.auth.jwt_service import JWTService
from domain.exceptions import UserNotFoundError

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = JWTService.verify_token(token)
        print("PAYLOAD:", payload)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    repo = UserRepositoryImpl(db)
    service = UserService(repo)

    user_id = int(payload["sub"])
    user = service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
