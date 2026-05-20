from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from application.auth.jwt_service import JWTService
from application.users.user_service import UserService
from domain.exceptions import (
    AccountLockedError,
    EmailNotVerifiedError,
    EmailVerificationCodeExpiredError,
    EmailVerificationCodeInvalidError,
    InvalidCredentialsError,
    PasswordExpiredError,
    PasswordPolicyViolationError,
    PasswordResetTokenInvalidError,
    PasswordReuseError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
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
from presentation.dependencies import get_current_user, get_db
from presentation.schemas.auth_schema import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RegisterRequest,
    ResendVerificationCodeRequest,
    TokenResponse,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_user_service(db: Session) -> UserService:
    return UserService(
        user_repository=UserRepositoryImpl(db),
        password_history_repository=PasswordHistoryRepositoryImpl(db),
        password_reset_repository=PasswordResetRepositoryImpl(db),
        auth_audit_repository=AuthAuditRepositoryImpl(db),
    )


def _get_client_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


def _get_user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(
    request_body: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    try:
        service.register(
            email=request_body.email,
            password=request_body.password,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        return MessageResponse(message="User created. Verification code sent to email.")
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    except PasswordPolicyViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    request_body: VerifyEmailRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    try:
        service.verify_email(
            email=request_body.email,
            code=request_body.code,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        return MessageResponse(message="Email verified successfully")
    except EmailVerificationCodeExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. Please request a new code.",
        )
    except EmailVerificationCodeInvalidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )


@router.post("/resend-verification-code", response_model=MessageResponse)
def resend_verification_code(
    request_body: ResendVerificationCodeRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    service.resend_email_verification_code(
        email=request_body.email,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )

    return MessageResponse(
        message="If the account exists and is not verified, a new code has been sent."
    )


@router.post("/login", response_model=TokenResponse)
def login(
    request_body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    try:
        user = service.login(
            email=request_body.email,
            password=request_body.password,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        token = JWTService.create_token(user.id, user.email, user.token_version)
        return TokenResponse(access_token=token)
    except AccountLockedError:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Login temporarily unavailable",
        )
    except PasswordExpiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Password expired",
                "code": "PASSWORD_EXPIRED",
            },
        )
    except EmailNotVerifiedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Email address is not verified",
                "code": "EMAIL_NOT_VERIFIED",
            },
        )
    except (InvalidCredentialsError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    request_body: ChangePasswordRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    try:
        service.change_password(
            user_id=current_user.id,
            current_password=request_body.current_password,
            new_password=request_body.new_password,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        return MessageResponse(message="Password changed successfully")
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password",
        )
    except PasswordPolicyViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except PasswordReuseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/password-reset/request", response_model=PasswordResetRequestResponse)
def request_password_reset(
    request_body: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    service.request_password_reset(
        email=request_body.email,
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
    )

    return PasswordResetRequestResponse(
        message="If the account exists, a reset email has been sent",
        reset_token=None,
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(
    request_body: PasswordResetConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    service = _build_user_service(db)

    try:
        service.confirm_password_reset(
            token=request_body.token,
            new_password=request_body.new_password,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        return MessageResponse(message="Password reset successfully")
    except PasswordPolicyViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except PasswordReuseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except PasswordResetTokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
