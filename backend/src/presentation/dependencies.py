from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from application.auth.jwt_service import JWTService
from application.users.user_service import UserService
from infrastructure.db.repositories.auth_audit_repository_impl import (
    AuthAuditRepositoryImpl,
)
from infrastructure.db.repositories.password_history_repository_impl import (
    PasswordHistoryRepositoryImpl,
)
from infrastructure.db.repositories.password_reset_repository_impl import (
    PasswordResetRepositoryImpl,
)
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.session import SessionLocal

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
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
        user_id = int(payload["sub"])
        token_version = int(payload.get("ver", -1))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepositoryImpl(db)
    password_history_repo = PasswordHistoryRepositoryImpl(db)
    password_reset_repo = PasswordResetRepositoryImpl(db)
    auth_audit_repo = AuthAuditRepositoryImpl(db)

    service = UserService(
        user_repository=user_repo,
        password_history_repository=password_history_repo,
        password_reset_repository=password_reset_repo,
        auth_audit_repository=auth_audit_repo,
    )

    user = service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
