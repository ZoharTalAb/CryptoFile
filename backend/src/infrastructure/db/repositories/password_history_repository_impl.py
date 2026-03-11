from sqlalchemy.orm import Session

from domain.entities.password_history_entry import PasswordHistoryEntry
from domain.interfaces.password_history_repository import PasswordHistoryRepository
from infrastructure.db.models import PasswordHistoryModel


class PasswordHistoryRepositoryImpl(PasswordHistoryRepository):

    def __init__(self, session: Session):
        self._session = session

    def list_recent_by_user_id(
        self,
        user_id: int,
        limit: int,
    ) -> list[PasswordHistoryEntry]:
        models = (
            self._session.query(PasswordHistoryModel)
            .filter(PasswordHistoryModel.user_id == user_id)
            .order_by(
                PasswordHistoryModel.created_at.desc(), PasswordHistoryModel.id.desc()
            )
            .limit(limit)
            .all()
        )

        return [self._to_entity(model) for model in models]

    def save(self, entry: PasswordHistoryEntry) -> PasswordHistoryEntry:
        model = PasswordHistoryModel(
            user_id=entry.user_id,
            password_hash=entry.password_hash,
            created_at=entry.created_at,
        )

        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def delete_older_than_latest(
        self,
        user_id: int,
        keep_latest: int,
    ) -> None:
        models = (
            self._session.query(PasswordHistoryModel)
            .filter(PasswordHistoryModel.user_id == user_id)
            .order_by(
                PasswordHistoryModel.created_at.desc(), PasswordHistoryModel.id.desc()
            )
            .all()
        )

        if len(models) <= keep_latest:
            return

        models_to_delete = models[keep_latest:]
        for model in models_to_delete:
            self._session.delete(model)

        self._session.commit()

    def _to_entity(self, model: PasswordHistoryModel) -> PasswordHistoryEntry:
        return PasswordHistoryEntry(
            id=model.id,
            user_id=model.user_id,
            password_hash=model.password_hash,
            created_at=model.created_at,
        )
