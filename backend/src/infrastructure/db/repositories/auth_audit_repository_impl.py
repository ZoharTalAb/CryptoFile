from sqlalchemy.orm import Session

from domain.entities.auth_audit_log import AuthAuditLog
from domain.interfaces.auth_audit_repository import AuthAuditRepository
from infrastructure.db.models import AuthAuditLogModel


class AuthAuditRepositoryImpl(AuthAuditRepository):

    def __init__(self, session: Session):
        self._session = session

    def save(self, event: AuthAuditLog) -> AuthAuditLog:
        model = AuthAuditLogModel(
            user_id=event.user_id,
            email=event.email,
            event_type=event.event_type,
            success=event.success,
            reason_code=event.reason_code,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            created_at=event.created_at,
        )

        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        return self._to_entity(model)

    def _to_entity(self, model: AuthAuditLogModel) -> AuthAuditLog:
        return AuthAuditLog(
            id=model.id,
            user_id=model.user_id,
            email=model.email,
            event_type=model.event_type,
            success=model.success,
            reason_code=model.reason_code,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            created_at=model.created_at,
        )
