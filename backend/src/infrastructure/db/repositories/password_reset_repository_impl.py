from datetime import datetime, timezone

from sqlalchemy.orm import Session

from domain.entities.password_reset_token import PasswordResetToken
from domain.interfaces.password_reset_repository import PasswordResetRepository
from infrastructure.db.models import PasswordResetTokenModel


class PasswordResetRepositoryImpl(PasswordResetRepository):

    def __init__(self, session: Session):
        self._session = session

    def save(self, token: PasswordResetToken) -> PasswordResetToken:
        model = PasswordResetTokenModel(
            user_id=token.user_id,
            token_hash=token.token_hash,
            expires_at=token.expires_at,
            used_at=token.used_at,
            created_at=token.created_at,
        )

        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def get_active_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        now = datetime.now(timezone.utc)

        model = (
            self._session.query(PasswordResetTokenModel)
            .filter(PasswordResetTokenModel.token_hash == token_hash)
            .filter(PasswordResetTokenModel.used_at.is_(None))
            .filter(PasswordResetTokenModel.expires_at > now)
            .order_by(
                PasswordResetTokenModel.created_at.desc(),
                PasswordResetTokenModel.id.desc(),
            )
            .first()
        )

        if not model:
            return None

        return self._to_entity(model)

    def get_active_by_user_id(self, user_id: int) -> PasswordResetToken | None:
        now = datetime.now(timezone.utc)

        model = (
            self._session.query(PasswordResetTokenModel)
            .filter(PasswordResetTokenModel.user_id == user_id)
            .filter(PasswordResetTokenModel.used_at.is_(None))
            .filter(PasswordResetTokenModel.expires_at > now)
            .order_by(
                PasswordResetTokenModel.created_at.desc(),
                PasswordResetTokenModel.id.desc(),
            )
            .first()
        )

        if not model:
            return None

        return self._to_entity(model)

    def count_recent_by_user_id(self, user_id: int, since: datetime) -> int:
        return (
            self._session.query(PasswordResetTokenModel)
            .filter(PasswordResetTokenModel.user_id == user_id)
            .filter(PasswordResetTokenModel.created_at >= since)
            .count()
        )

    def mark_used(self, token_id: int, used_at: datetime) -> None:
        model = (
            self._session.query(PasswordResetTokenModel)
            .filter(PasswordResetTokenModel.id == token_id)
            .first()
        )

        if not model:
            raise ValueError("Password reset token not found")

        model.used_at = used_at
        self._session.commit()

    def _to_entity(self, model: PasswordResetTokenModel) -> PasswordResetToken:
        return PasswordResetToken(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            used_at=model.used_at,
            created_at=model.created_at,
        )
