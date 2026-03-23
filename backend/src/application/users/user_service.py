from datetime import datetime, timedelta, timezone

from application.auth.login_protection_service import LoginProtectionService
from application.auth.password_hasher import PasswordHasherService
from application.auth.password_policy_service import PasswordPolicyService
from application.auth.password_reset_service import PasswordResetService
from backend.src.application.email.email_service import EmailService
from core.config import (
    ENVIRONMENT,
    PASSWORD_EXPIRY_DAYS,
    PASSWORD_HISTORY_LIMIT,
    PASSWORD_RESET_MAX_REQUESTS,
    PASSWORD_RESET_WINDOW_MINUTES,
    RESET_TOKEN_DEV_RETURN,
    RESET_TOKEN_EXP_MINUTES,
)
from domain.entities.auth_audit_log import AuthAuditLog
from domain.entities.password_history_entry import PasswordHistoryEntry
from domain.entities.password_reset_token import PasswordResetToken
from domain.entities.user import User
from domain.exceptions import (
    AccountLockedError,
    InvalidCredentialsError,
    PasswordExpiredError,
    PasswordResetTokenInvalidError,
    PasswordReuseError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from domain.interfaces.auth_audit_repository import AuthAuditRepository
from domain.interfaces.password_history_repository import PasswordHistoryRepository
from domain.interfaces.password_reset_repository import PasswordResetRepository
from domain.interfaces.user_repository import UserRepository
from infrastructure.db.repositories.auth_audit_repository_impl import (
    AuthAuditRepositoryImpl,
)
from infrastructure.db.repositories.password_history_repository_impl import (
    PasswordHistoryRepositoryImpl,
)
from infrastructure.db.repositories.password_reset_repository_impl import (
    PasswordResetRepositoryImpl,
)


class _NullAuthAuditRepository(AuthAuditRepository):
    def save(self, event: AuthAuditLog) -> AuthAuditLog:
        return event


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_history_repository: PasswordHistoryRepository | None = None,
        password_reset_repository: PasswordResetRepository | None = None,
        auth_audit_repository: AuthAuditRepository | None = None,
    ):
        self._user_repository = user_repository

        session = getattr(user_repository, "_session", None)

        self._password_history_repository = password_history_repository
        if self._password_history_repository is None and session is not None:
            self._password_history_repository = PasswordHistoryRepositoryImpl(session)

        self._password_reset_repository = password_reset_repository
        if self._password_reset_repository is None and session is not None:
            self._password_reset_repository = PasswordResetRepositoryImpl(session)

        self._auth_audit_repository = auth_audit_repository
        if self._auth_audit_repository is None and session is not None:
            self._auth_audit_repository = AuthAuditRepositoryImpl(session)

        if self._auth_audit_repository is None:
            self._auth_audit_repository = _NullAuthAuditRepository()

        self._password_hasher = PasswordHasherService()
        self._password_policy = PasswordPolicyService()
        self._login_protection = LoginProtectionService()
        self._password_reset_service = PasswordResetService()

    def register(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        if not email or not password:
            raise ValueError("Email and password are required")

        if self._password_history_repository is None:
            raise RuntimeError("Password history repository is not configured")

        normalized_email = self._normalize_email(email)

        existing_user = self._user_repository.get_by_email(normalized_email)
        if existing_user:
            self._audit(
                user_id=existing_user.id,
                email=normalized_email,
                event_type="register_failure",
                success=False,
                reason_code="user_already_exists",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise UserAlreadyExistsError("User already exists")

        self._password_policy.validate(normalized_email, password)

        now = datetime.now(timezone.utc)
        hashed_password = self._password_hasher.hash_password(password)

        user = User(
            id=None,
            email=normalized_email,
            password_hash=hashed_password,
            created_at=now,
            updated_at=now,
            password_changed_at=now,
            password_expires_at=now + timedelta(days=PASSWORD_EXPIRY_DAYS),
            failed_login_attempts=0,
            last_failed_login_at=None,
            locked_until=None,
            token_version=0,
        )

        created_user = self._user_repository.save(user)

        self._password_history_repository.save(
            PasswordHistoryEntry(
                id=None,
                user_id=created_user.id,
                password_hash=hashed_password,
                created_at=now,
            )
        )

        self._audit(
            user_id=created_user.id,
            email=normalized_email,
            event_type="register_success",
            success=True,
            reason_code="user_created",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return created_user

    def login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        normalized_email = self._normalize_email(email)
        user = self._user_repository.get_by_email(normalized_email)

        if not user:
            self._audit(
                user_id=None,
                email=normalized_email,
                event_type="login_failure",
                success=False,
                reason_code="user_not_found_or_invalid_credentials",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise InvalidCredentialsError("Invalid credentials")

        if self._login_protection.is_locked(user):
            self._audit(
                user_id=user.id,
                email=user.email,
                event_type="login_failure",
                success=False,
                reason_code="account_locked",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise AccountLockedError("Account is temporarily locked")

        if not self._password_hasher.verify_password(password, user.password_hash):
            user = self._login_protection.register_failed_attempt(user)
            updated_user = self._user_repository.update(user)

            if updated_user.locked_until is not None:
                self._audit(
                    user_id=updated_user.id,
                    email=updated_user.email,
                    event_type="account_locked",
                    success=False,
                    reason_code="too_many_failed_attempts",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

            self._audit(
                user_id=updated_user.id,
                email=updated_user.email,
                event_type="login_failure",
                success=False,
                reason_code="user_not_found_or_invalid_credentials",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise InvalidCredentialsError("Invalid credentials")

        user = self._login_protection.reset_failures(user)

        if self._password_hasher.needs_rehash(user.password_hash):
            user.password_hash = self._password_hasher.hash_password(password)

        user.updated_at = datetime.now(timezone.utc)
        updated_user = self._user_repository.update(user)

        if self._is_password_expired(updated_user):
            self._audit(
                user_id=updated_user.id,
                email=updated_user.email,
                event_type="password_expired_block",
                success=False,
                reason_code="password_expired",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise PasswordExpiredError("Password expired")

        self._audit(
            user_id=updated_user.id,
            email=updated_user.email,
            event_type="login_success",
            success=True,
            reason_code="authenticated",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return updated_user

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        if self._password_history_repository is None:
            raise RuntimeError("Password history repository is not configured")

        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        if not self._password_hasher.verify_password(
            current_password, user.password_hash
        ):
            self._audit(
                user_id=user.id,
                email=user.email,
                event_type="change_password_failure",
                success=False,
                reason_code="invalid_current_password",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise InvalidCredentialsError("Invalid current password")

        self._password_policy.validate(user.email, new_password)
        self._assert_not_reused_password(user.id, new_password)

        now = datetime.now(timezone.utc)
        new_password_hash = self._password_hasher.hash_password(new_password)

        user.password_hash = new_password_hash
        user.password_changed_at = now
        user.password_expires_at = now + timedelta(days=PASSWORD_EXPIRY_DAYS)
        user.updated_at = now
        user.token_version += 1

        self._user_repository.update(user)

        self._password_history_repository.save(
            PasswordHistoryEntry(
                id=None,
                user_id=user.id,
                password_hash=new_password_hash,
                created_at=now,
            )
        )
        self._password_history_repository.delete_older_than_latest(
            user_id=user.id,
            keep_latest=PASSWORD_HISTORY_LIMIT,
        )

        self._audit(
            user_id=user.id,
            email=user.email,
            event_type="change_password_success",
            success=True,
            reason_code="password_changed",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    from application.email.email_service import EmailService

    def request_password_reset(
        self,
        email: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        if self._password_reset_repository is None:
            raise RuntimeError("Password reset repository is not configured")

        normalized_email = self._normalize_email(email)
        user = self._user_repository.get_by_email(normalized_email)

        if not user:
            self._audit(
                user_id=None,
                email=normalized_email,
                event_type="password_reset_requested",
                success=False,
                reason_code="user_not_found",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            return

        active_token = self._password_reset_repository.get_active_by_user_id(user.id)
        if active_token:
            return

        since = datetime.now(timezone.utc) - timedelta(
            minutes=PASSWORD_RESET_WINDOW_MINUTES
        )
        recent_count = self._password_reset_repository.count_recent_by_user_id(
            user.id, since
        )

        if recent_count >= PASSWORD_RESET_MAX_REQUESTS:
            return

        now = datetime.now(timezone.utc)

        raw_token = self._password_reset_service.generate_raw_token()
        token_hash = self._password_reset_service.hash_token(raw_token)

        self._password_reset_repository.save(
            PasswordResetToken(
                id=None,
                user_id=user.id,
                token_hash=token_hash,
                expires_at=now + timedelta(minutes=RESET_TOKEN_EXP_MINUTES),
                used_at=None,
                created_at=now,
            )
        )

        # 🔥 NEW: send email instead of returning token
        email_service = EmailService()
        email_service.send_password_reset_email(user.email, raw_token)

        self._audit(
            user_id=user.id,
            email=user.email,
            event_type="password_reset_requested",
            success=True,
            reason_code="email_sent",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def confirm_password_reset(
        self,
        token: str,
        new_password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        if (
            self._password_reset_repository is None
            or self._password_history_repository is None
        ):
            raise RuntimeError("Password reset dependencies are not configured")

        token_hash = self._password_reset_service.hash_token(token)
        reset_token = self._password_reset_repository.get_active_by_token_hash(
            token_hash
        )

        if not reset_token:
            self._audit(
                user_id=None,
                email=None,
                event_type="password_reset_failed",
                success=False,
                reason_code="token_invalid",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise PasswordResetTokenInvalidError(
                "Invalid or expired password reset token"
            )

        user = self._user_repository.get_by_id(reset_token.user_id)
        if not user:
            self._audit(
                user_id=reset_token.user_id,
                email=None,
                event_type="password_reset_failed",
                success=False,
                reason_code="user_not_found",
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise UserNotFoundError("User not found")

        self._password_policy.validate(user.email, new_password)
        self._assert_not_reused_password(user.id, new_password)

        now = datetime.now(timezone.utc)
        new_password_hash = self._password_hasher.hash_password(new_password)

        user.password_hash = new_password_hash
        user.password_changed_at = now
        user.password_expires_at = now + timedelta(days=PASSWORD_EXPIRY_DAYS)
        user.updated_at = now
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.locked_until = None
        user.token_version += 1

        self._user_repository.update(user)

        self._password_history_repository.save(
            PasswordHistoryEntry(
                id=None,
                user_id=user.id,
                password_hash=new_password_hash,
                created_at=now,
            )
        )
        self._password_history_repository.delete_older_than_latest(
            user_id=user.id,
            keep_latest=PASSWORD_HISTORY_LIMIT,
        )

        self._password_reset_repository.mark_used(
            token_id=reset_token.id,
            used_at=now,
        )

        self._audit(
            user_id=user.id,
            email=user.email,
            event_type="password_reset_confirmed",
            success=True,
            reason_code="password_reset_completed",
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def get_by_email(self, email: str) -> User | None:
        return self._user_repository.get_by_email(self._normalize_email(email))

    def get_by_id(self, user_id: int) -> User | None:
        return self._user_repository.get_by_id(user_id)

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def _is_password_expired(self, user: User) -> bool:
        expires_at = user.password_expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return expires_at <= datetime.now(timezone.utc)

    def _assert_not_reused_password(self, user_id: int, new_password: str) -> None:
        if self._password_history_repository is None:
            raise RuntimeError("Password history repository is not configured")

        recent_entries = self._password_history_repository.list_recent_by_user_id(
            user_id=user_id,
            limit=PASSWORD_HISTORY_LIMIT,
        )

        for entry in recent_entries:
            if self._password_hasher.verify_password(new_password, entry.password_hash):
                raise PasswordReuseError("Password was already used recently")

    def _audit(
        self,
        user_id: int | None,
        email: str | None,
        event_type: str,
        success: bool,
        reason_code: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        self._auth_audit_repository.save(
            AuthAuditLog(
                id=None,
                user_id=user_id,
                email=email,
                event_type=event_type,
                success=success,
                reason_code=reason_code,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.now(timezone.utc),
            )
        )
