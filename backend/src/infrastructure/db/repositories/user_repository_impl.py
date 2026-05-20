from domain.entities.user import User
from domain.interfaces.user_repository import UserRepository
from infrastructure.db.models import UserModel
from sqlalchemy.orm import Session


class UserRepositoryImpl(UserRepository):

    def __init__(self, session: Session):
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        model = self._session.query(UserModel).filter(UserModel.email == email).first()
        if not model:
            return None
        return self._to_entity(model)

    def save(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
            updated_at=user.updated_at,
            password_changed_at=user.password_changed_at,
            password_expires_at=user.password_expires_at,
            failed_login_attempts=user.failed_login_attempts,
            last_failed_login_at=user.last_failed_login_at,
            locked_until=user.locked_until,
            token_version=user.token_version,
            email_verified=user.email_verified,
            email_verification_code_hash=user.email_verification_code_hash,
            email_verification_expires_at=user.email_verification_expires_at,
            email_verification_sent_at=user.email_verification_sent_at,
        )

        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def update(self, user: User) -> User:
        model = self._session.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError("User not found for update")

        model.email = user.email
        model.password_hash = user.password_hash
        model.updated_at = user.updated_at
        model.password_changed_at = user.password_changed_at
        model.password_expires_at = user.password_expires_at
        model.failed_login_attempts = user.failed_login_attempts
        model.last_failed_login_at = user.last_failed_login_at
        model.locked_until = user.locked_until
        model.token_version = user.token_version
        model.email_verified = user.email_verified
        model.email_verification_code_hash = user.email_verification_code_hash
        model.email_verification_expires_at = user.email_verification_expires_at
        model.email_verification_sent_at = user.email_verification_sent_at

        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
            password_changed_at=model.password_changed_at,
            password_expires_at=model.password_expires_at,
            failed_login_attempts=model.failed_login_attempts,
            last_failed_login_at=model.last_failed_login_at,
            locked_until=model.locked_until,
            token_version=model.token_version,
            email_verified=model.email_verified,
            email_verification_code_hash=model.email_verification_code_hash,
            email_verification_expires_at=model.email_verification_expires_at,
            email_verification_sent_at=model.email_verification_sent_at,
        )
