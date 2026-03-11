from abc import ABC, abstractmethod

from domain.entities.auth_audit_log import AuthAuditLog


class AuthAuditRepository(ABC):

    @abstractmethod
    def save(self, event: AuthAuditLog) -> AuthAuditLog:
        pass
